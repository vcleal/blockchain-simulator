#!/usr/bin/env python

import zmq
import threading
import time
#import sys
import argparse
import block
import blockchain
import consensus
import sqlite3
import pickle
from collections import deque
import logging

#TODO blockchain class and database decision (move to only db solution)
#TODO old peers subscribe to new peer? [addr msg]
#TODO better peer management and limit

#TODO check python 3+ compatibility

class StopException(Exception):
    pass

class Node(object):
    """docstring"""

    ctx = None
    # psocket = None
    # subsocket = None
    # rpcsocket = None
    # reqsocket = None

    def __init__(self, ipaddr='127.0.0.1', port=9000):
        self.ipaddr = ipaddr
        self.port = int(port)
        self.ctx = zmq.Context.instance()
        self.poller = zmq.Poller()
        self.reqsocket = self.ctx.socket(zmq.REQ)
        self.repsocket = self.ctx.socket(zmq.REP)
        self.rpcsocket = self.ctx.socket(zmq.REP)
        self.psocket = self.ctx.socket(zmq.PUB)
        self.subsocket = self.ctx.socket(zmq.SUB)
        self.subsocket.setsockopt(zmq.SUBSCRIBE, b'')
        self.poller.register(self.reqsocket, zmq.POLLIN)
        #self.reqsocket.RCVTIMEO = 3000 # in milliseconds
        self.reqsocket.setsockopt(zmq.LINGER, 0)
        self.reqsocket.setsockopt(zmq.REQ_RELAXED, 1)
        self.balance = 0
        self.stake = 0
        self.synced = False
        self.peers = deque()
        # Flags and thread events TODO pass some to consensus?
        self.k = threading.Event()
        self.e = threading.Event()
        self.f = threading.Event()
        self.start = threading.Event()

    # Node as client
    def connect(self,d_ip='127.0.0.1',d_port=9000):
        self.subsocket.connect("tcp://%s:%s" % (d_ip, d_port))
        self.reqsocket.connect("tcp://%s:%s" % (d_ip, d_port+1))

    def disconnect(self,d_ip='127.0.0.1',d_port=9000):
        self.subsocket.disconnect("tcp://%s:%s" % (d_ip, d_port))
        self.reqsocket.disconnect("tcp://%s:%s" % (d_ip, d_port+1))

    # Node as server
    def bind(self, socket, ip=None, port=None):
        if port and ip:
            socket.bind("tcp://%s:%s" % (ip, port))
        elif port:
            socket.bind("tcp://%s:%s" % (self.ipaddr, port))
        else:
            socket.bind("tcp://%s:%s" % (self.ipaddr, self.port))

    def close(self):
        self.psocket.close(linger=0)
        self.subsocket.close(linger=0)
        self.repsocket.close(linger=0)
        self.rpcsocket.close(linger=0)
        self.reqsocket.close(linger=0)
        #self.ctx.term()

    def addPeer(self, ipaddr, port=9000):
        peer = {'ipaddr': ipaddr}
        if peer not in self.peers:
            self.peers.appendleft(peer)
            self.connect(d_ip=ipaddr,d_port=self.port)
            return "Peer %s connected" % ipaddr
        else:
            logging.warning("Peer %s already connected" % ipaddr)
            return "Peer %s already connected" % ipaddr

    def removePeer(self, ipaddr):
        peer = {'ipaddr': ipaddr}
        try:
            self.peers.remove(peer)
            self.disconnect(d_ip=ipaddr,d_port=self.port)
            time.sleep(1)
        except ValueError:
            logging.warning("Peer %s not connected" % ipaddr)
            return "Peer %s not connected" % ipaddr
        return "Peer %s removed" % ipaddr

    def getPeers(self):
        return self.peers

    def setBalance(self, value):
        self.balance = value

    def listen(self, bchain):
        db = sqlite3.connect('blocks/blockchain.db')
        c = db.cursor()
        while True and not self.k.is_set():
            try:
                msg, block_recv = self.subsocket.recv_multipart()
                self.e.set()
                self.f.clear()
                b = pickle.loads(block_recv)
                logging.info("Got block %s" % b.hash)
                #logging.info(b.hash)
                # Verify block
                if bchain.getLastBlock().index < b.index:
                    self.writeBlock(b, c)
                    bchain.addBlocktoBlockchain(b)
                    db.commit()
                #
                self.f.set()
            except (zmq.ContextTerminated):
                break
        db.close()

    def mine(self, bchain, cons):
        # target = 2 ** (20) - 1
        name = threading.current_thread().getName()
        db = sqlite3.connect('blocks/blockchain.db')
        c = db.cursor()
        while True and not self.k.is_set():
            # move e flag inside generate?
            self.start.wait()
            self.f.wait()
            lastblock = bchain.getLastBlock()
            b = cons.generateNewblock(lastblock,self.e)
            if b and not self.e.is_set():
                self.writeBlock(b, c)
                bchain.addBlocktoBlockchain(b)
                self.psocket.send_multipart(['block', pickle.dumps(b, 2)])
                db.commit()
            else:
                self.e.clear()
        db.close()

    def doConsensus(self, bchain, cons):
        m1 = threading.Thread(name='Miner',target=self.mine,
         kwargs={'bchain': bchain, 'cons': cons})
        m1.start()
        return m1

    def writeBlock(self, b, c):
        try:
            if isinstance(b, list):
                c.executemany('INSERT INTO blocks VALUES (?,?,?,?,?)', b)
            else:
                c.execute('INSERT INTO blocks VALUES (?,?,?,?,?)', (
                        b.__dict__['index'],
                        b.__dict__['timestamp'],
                        b.__dict__['prev_hash'],
                        b.__dict__['hash'],
                        b.__dict__['nonce']))
        except sqlite3.IntegrityError:
            logging.warning('db insert duplicated block')
        #db.commit()

    def readBlock(self):
        pass

    def checkBlock(self):
        #if new_hash == (hashlib.sha256(str(name+bchain[0])+str(nonce)).hexdigest()):
        #raise StopMineException("")
        #self.psocket.send_string("ok")
        #e.set()
        return True
        #else:
        #    return False

    def dbConnect(self):
        db = sqlite3.connect('blocks/blockchain.db')
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS blocks (
            id integer primary key, 
            ctime text, 
            phash text, 
            hash text, 
            nonce integer)""")
        cursor.execute('SELECT * FROM blocks WHERE id = (SELECT MAX(id) FROM blocks)')
        # Last block from own database
        lastBlock_db = cursor.fetchone()
        bc = blockchain.Blockchain(lastBlock_db)
        # Empty database
        if not lastBlock_db:
            genesis = bc.getLastBlock()
            self.writeBlock(genesis, cursor)
        db.commit()
        db.close()
        return bc

    def sync(self, bc):
        db = sqlite3.connect('blocks/blockchain.db')
        cursor = db.cursor()
        first = bc.getLastBlock().index
        last = first
        j=0
        rBlock = None
        for i in self.peers:
            j+=1
            logging.debug('request #%d' % j)
            b = self.reqLastBlock()
            if b:
                logging.debug('Block index %s' % b.index)
            if b and (b.index > last):
                rBlock = b
                last = rBlock.index
        if rBlock:
            if (last-first) == 1:
                self.writeBlock(rBlock, cursor)
            else:
                logging.debug('requesting blocks %s to %s', first+1, last)
                l = self.reqBlocks(first+1, last)
                if  l:
                    self.writeBlock(l, cursor)
            bc.addBlocktoBlockchain(rBlock)
            # set flag to request other blocks?
            #self.synced = True
        db.commit()
        db.close()

    def reqrepServer(self, bc):
        db = sqlite3.connect('blocks/blockchain.db')
        cursor = db.cursor()
        self.bind(self.repsocket, port=self.port+1)
        time.sleep(1)
        while True and not self.k.is_set():
            try: # TODO check this socket hanging
                messages = self.repsocket.recv_multipart()
            except zmq.ContextTerminated:
                break
            #time.sleep(1)
            reply = consensus.handleMessages(bc, messages, cursor) 
            self.repsocket.send_pyobj(reply)
        db.close()

    def messageHandler(self, bchain):
        t = threading.Thread(target=self.reqrepServer,
         kwargs={'bc': bchain})
        t.start()
        return t

    def rpcServer(self, bc):
        db = sqlite3.connect('blocks/blockchain.db')
        cursor = db.cursor()
        self.bind(self.rpcsocket, ip='127.0.0.1', port=9999)
        time.sleep(1)
        while True:
            try:
                messages = self.rpcsocket.recv_multipart()
            except zmq.ContextTerminated:
                break
            time.sleep(1)
            cmd = messages[0]
            if cmd == 'getlastblock':  
                self.rpcsocket.send_pyobj(bc.getLastBlock())
            elif cmd == 'getblock':
                cursor.execute('SELECT * FROM blocks WHERE id = ?', (messages[1],))
                b = cursor.fetchone()
                self.rpcsocket.send_pyobj(b)
            elif cmd == 'getblocks':
                # TODO check SQL query
                idlist = messages[1:]
                #idlist = [int(i) for i in messages[1:]]
                cursor.execute('SELECT * FROM blocks WHERE id IN ({0})'.format(', '.join('?' for _ in idlist)), idlist)
                b = cursor.fetchall()
                self.rpcsocket.send_pyobj(b)
            elif cmd == 'addpeer':
                m = self.addPeer(messages[1])
                self.rpcsocket.send_string(m)
            elif cmd == 'removepeer':
                m = self.removePeer(messages[1])
                self.rpcsocket.send_string(m)
            elif cmd == 'getpeerinfo':
                self.rpcsocket.send_pyobj(self.getPeers())
            elif cmd == 'startmining':
                self.rpcsocket.send_string('Starting mining...')
                self.start.set()
                self.f.set()
            elif cmd == 'stopmining':
                self.start.clear()
                self.rpcsocket.send_string('Stopping mining...')
            elif cmd == 'exit':
                self.rpcsocket.send_string('Exiting...')
                raise StopException
            else:
                self.rpcsocket.send_string('Command unknown')
                logging.warning('Command unknown')
        db.close()

# Client request-reply functions

    def reqLastBlock(self):
        self.reqsocket.send(consensus.MSG_LASTBLOCK)
        try:
            evts = dict(self.poller.poll(5000))
            logging.debug('Requesting most recent block')
        except KeyboardInterrupt:
            return None
        if self.reqsocket in evts and evts[self.reqsocket] == zmq.POLLIN:
            b = self.reqsocket.recv_pyobj()
            return b
        else: # offline
            logging.debug('No response from node (empty pollin evt)')
            return None

    def reqBlock(self, index):
        # TODO check zmq timeout
        self.reqsocket.send_multipart([consensus.MSG_BLOCK, index])
        b = self.reqsocket.recv_pyobj()
        return block.Block(b[0],b[2],b[4],b[3],b[1])

    def reqBlocks(self, first, last):
        self.reqsocket.send_multipart([consensus.MSG_BLOCKS, str(first), str(last)])
        try:
            evts = dict(self.poller.poll(5000))
        except KeyboardInterrupt:
            return None
        if self.reqsocket in evts and evts[self.reqsocket] == zmq.POLLIN:
            b = self.reqsocket.recv_pyobj()
            return b
        else: # offline
            logging.debug('empty pollin evt')
            return None

    def exit(self, ip):
        pass

    def hello(self):
        pass

_LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

def _log_level_to_int(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise argparse.ArgumentTypeError('Invalid log level: %s' % loglevel)
    return numeric_level

def main():
    # Argument and command-line options parsing
    parser = argparse.ArgumentParser(description='Blockchain simulation')
    parser.add_argument('-i', '--ip', metavar='ip', dest='ipaddr',
                        help='Specify listen IP address', default='127.0.0.1')
    parser.add_argument('-p', '--port', metavar='port', dest='port',
                        help='Specify listen port', default=9000)
    parser.add_argument('--peers', dest='peers', nargs='*',
                        help='Specify peers IP addresses', default=[])
    parser.add_argument('--miner', dest='miner', action='store_true',
                        help='Start the node immediately mining')
    parser.add_argument('--log', dest='loglevel', type=_log_level_to_int, nargs='?', default='warning',
                        help='Set the logging output level {0}'.format(_LOG_LEVEL_STRINGS))
    args = parser.parse_args()
    
    logging.basicConfig(filename='tmp/log/example.log', filemode='w', level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S')
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(args.loglevel)
    logging.getLogger('').addHandler(console)

    threads = []
    cons = consensus.Consensus(5)
    n = Node(args.ipaddr, args.port)

    # Connect to predefined peers
    if args.peers:
        iplist = args.peers if isinstance(args.peers, list) else [args.peers]
        for ipaddr in iplist:
            n.addPeer(ipaddr)
    else: # Connect to localhost
        logging.info('Connecting to localhost...')
        n.connect()
    time.sleep(1)

    # Connect and check own node database
    bchain = n.dbConnect()

    # Thread to listen request messages
    t = n.messageHandler(bchain)
    threads.append(t)

    # Thread to listen broadcast messages
    listen_thread = threading.Thread(target=n.listen,
     kwargs={'bchain': bchain})
    listen_thread.start()
    #
    n.bind(n.psocket)
    time.sleep(1)

    # Check peers most recent block
    n.sync(bchain)

    # Miner thread
    t = n.doConsensus(bchain, cons)
    threads.append(t)

    if args.miner:
        n.start.set()
        n.f.set()

    # Main thread
    try:
        while True:
            # rpc-like commands
            n.rpcServer(bchain)
    # Exit main and threads
    except (KeyboardInterrupt, StopException):
        pass
    finally:
        #n.exit(args.ipaddr)
        n.k.set()
        n.e.set()
        n.f.set()
        n.start.set()
        #for t in threads:
        #    t.join()
        n.close()
        print bchain.Info()
        try: # TODO fix stucking on term or Assertion failed
            n.ctx.term()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    main()