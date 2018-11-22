#!/usr/bin/env python

import zmq
import threading
import time
#import sys
import argparse
import block
import blockchain
import consensus
import sqldb
import pickle
from collections import deque, Mapping
import logging
import rpc.messages as rpc

#TODO blockchain class and database decision (move to only db solution)
#TODO old peers subscribe to new peer? [addr msg]
#TODO better peer management and limit (use a p2p library - pyre?)
#TODO zmq.ROUTER type socket for REQ/REP?
#TODO connect only on request?
#TODO serialization/deserialization, change pickle to json?

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
        self.router = self.ctx.socket(zmq.REQ)
        self.rpcsocket = self.ctx.socket(zmq.REP)
        self.psocket = self.ctx.socket(zmq.PUB)
        self.subsocket = self.ctx.socket(zmq.SUB)
        # TODO add 'block' subscription type
        self.subsocket.setsockopt(zmq.SUBSCRIBE, b'')
        self.poller.register(self.reqsocket, zmq.POLLIN)
        self.poller.register(self.router, zmq.POLLIN)
        #self.reqsocket.RCVTIMEO = 3000 # in milliseconds
        #self.reqsocket.setsockopt(zmq.LINGER, 0)
        self.reqsocket.setsockopt(zmq.REQ_RELAXED, 1)
        self.balance = 0
        self.stake = 0
        self.synced = False
        self.peers = deque()
        self.bchain = {}
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
        self.router.close(linger=0)
        self.ctx.term()

    def addPeer(self, ipaddr, port=9000):
        # TODO remove port
        peer = ipaddr if isinstance(ipaddr,Mapping) else {'ipaddr': ipaddr}
        if peer not in self.peers:
            self.peers.appendleft(peer)
            self.connect(d_ip=peer['ipaddr'],d_port=self.port)
            return "Peer %s connected" % peer['ipaddr']
        else:
            logging.warning("Peer %s already connected" % peer['ipaddr'])
            return "Peer %s already connected" % peer['ipaddr']

    def removePeer(self, ipaddr):
        peer = ipaddr if isinstance(ipaddr,Mapping) else {'ipaddr': ipaddr}
        try:
            self.peers.remove(peer)
            self.disconnect(d_ip=peer['ipaddr'],d_port=self.port)
            time.sleep(1)
        except ValueError:
            logging.warning("Peer %s not connected" % peer['ipaddr'])
            return "Peer %s not connected" % peer['ipaddr']
        return "Peer %s removed" % peer['ipaddr']

    def getPeers(self):
        return self.peers

    def setBalance(self, value):
        self.balance = value

    def listen(self):
        self.bind(self.psocket)
        while True and not self.k.is_set():
            try:
                msg, block_recv = self.subsocket.recv_multipart()
                self.f.clear()
                b = pickle.loads(block_recv)
                logging.info("Got block %s" % b.hash)
                # Verify block
                if consensus.validateBlockHeader(b):
                    logging.debug('valid block')
                    lb = self.bchain.getLastBlock()
                    if (b.index - lb.index == 1) and consensus.validateBlock(b, lb):
                        self.e.set()
                        sqldb.writeBlock(b)
                        self.bchain.addBlocktoBlockchain(b)
                        # rebroadcast
                        logging.debug('rebroadcast')
                        self.psocket.send_multipart([consensus.MSG_BLOCK, pickle.dumps(b, 2)])
                    elif b.index - lb.index > 1:
                        self.synced = False
                        self.sync(b)
                    elif b.index == lb.index:
                        if b.hash == lb.hash:
                            logging.debug('retransmission')
                            pass
                        else:
                            #fork
                            pass
                    else:
                        #fork
                        pass
                #
                self.f.set()
            except (zmq.ContextTerminated):
                break

    def mine(self, cons):
        # target = 2 ** (20) - 1
        name = threading.current_thread().getName()
        while True and not self.k.is_set():
            # move e flag inside generate?
            self.start.wait()
            self.f.wait()
            lastblock = self.bchain.getLastBlock()
            b = cons.generateNewblock(lastblock, self.e)
            if b and not self.e.is_set():
                logging.info("Mined block %s" % b.hash)
                sqldb.writeBlock(b)
                self.bchain.addBlocktoBlockchain(b)
                self.psocket.send_multipart([consensus.MSG_BLOCK, pickle.dumps(b, 2)])
            else:
                self.e.clear()

    def readBlock(self):
        pass

    def probe(self):
        for i in self.peers:
            x = self.hello()
            if not x:
                self.removePeer(i)

    def sync(self, rBlock=None):
        # TODO change variables names and test again
        self.synced = True
        logging.debug('syncing...')
        # limit number of peers?
        if not rBlock:
            rBlock = self.bchain.getLastBlock()
            for i in range(0,min(len(self.peers),3)):
                i+=1
                logging.debug('request #%d' % i)
                b, ip = self.reqLastBlock()
                if b:
                    logging.debug('Block index %s' % b.index)
                if (b and (b.index > rBlock.index)):
                    rBlock = b
                    address = ip
                    logging.debug('Best index %s with ip %s' % (b.index, ip))
        last = self.bchain.getLastBlock()
        #
        if (rBlock.index > last.index):
            self.e.set()
            if (rBlock.index-last.index == 1) and consensus.validateBlock(rBlock, last):
                logging.debug('valid block')
                sqldb.writeBlock(rBlock)
                self.bchain.addBlocktoBlockchain(rBlock)
            else:
                l = self.reqBlocks(address, last.index+1, rBlock.index)
                print l
                if  l:
                    # validate here
                    error = consensus.validateChain(self.bchain, l)
                    if error:
                        logging.warning('block %s invalid', % b.index)
                        # sync again?
                    #sqldb.writeBlock(l)
        logging.debug('synced')

    def messageHandler(self):
        # reqrepServer
        self.bind(self.repsocket, port=self.port+1)
        time.sleep(1)
        while True and not self.k.is_set():
            try: # TODO check this socket hanging
                messages = self.repsocket.recv_multipart()
            except zmq.ContextTerminated:
                break
            reply = consensus.handleMessages(self.bchain, messages)
            self.repsocket.send_multipart([self.ipaddr, pickle.dumps(reply, 2)])

    def rpcServer(self, ip='127.0.0.1', port=9999):
        self.bind(self.rpcsocket, ip, port)
        time.sleep(1)
        while True:
            try:
                messages = self.rpcsocket.recv_multipart()
            except zmq.ContextTerminated:
                break
            time.sleep(1)
            cmd = messages[0].lower()
            if cmd == rpc.MSG_LASTBLOCK:
                b = self.bchain.getLastBlock()
                self.rpcsocket.send(b.blockInfo())
            elif cmd == rpc.MSG_BLOCK:
                b = sqldb.dbtoBlock(sqldb.blockQuery(messages))
                self.rpcsocket.send(b.blockInfo() if b else 'error')
            elif cmd == rpc.MSG_BLOCKS:
                # TODO add SQL query BETWEEN
                l = sqldb.blocksListQuery(messages)
                blocks = []
                for b in l:
                    # test if error
                    blocks.append(sqldb.dbtoBlock(b).blockInfo())
                self.rpcsocket.send_pyobj(blocks)
            elif cmd == rpc.MSG_ADD:
                m = self.addPeer(messages[1])
                self.rpcsocket.send_string(m)
            elif cmd == rpc.MSG_REMOVE:
                m = self.removePeer(messages[1])
                self.rpcsocket.send_string(m)
            elif cmd == rpc.MSG_PEERS:
                self.rpcsocket.send_pyobj(self.getPeers())
            elif cmd == rpc.MSG_START:
                self.rpcsocket.send_string('Starting mining...')
                self.start.set()
                self.f.set()
            elif cmd == rpc.MSG_STOP:
                self.start.clear()
                self.rpcsocket.send_string('Stopping mining...')
            elif cmd == rpc.MSG_EXIT:
                self.rpcsocket.send_string('Exiting...')
                raise StopException
            else:
                self.rpcsocket.send_string('Command unknown')
                logging.warning('Command unknown')

# Client request-reply functions

    def _poll(self, socket=None):
        #
        s = socket if socket else self.reqsocket
        try:
            evts = dict(self.poller.poll(5000))
        except KeyboardInterrupt:
            return None, None
        if s in evts and evts[s] == zmq.POLLIN:
            m = s.recv_multipart()
            logging.debug(m[-2])
            return pickle.loads(m[-1]), m[-2]
        else:
            logging.debug('No response from node (empty pollin evt)')
            return None, None

    def reqLastBlock(self):
        self.reqsocket.send_multipart([consensus.MSG_LASTBLOCK,])
        logging.debug('Requesting most recent block')
        m, address = self._poll()
        return sqldb.dbtoBlock(m), address

    def reqBlock(self, index):
        self.reqsocket.send_multipart([consensus.MSG_BLOCK, str(index)])
        logging.debug('Requesting block index %s' % index)
        m = self._poll()[0]
        return sqldb.dbtoBlock(m)

    def reqBlocks(self, address, first, last):
        # using another socket for direct connect
        self.router.connect("tcp://%s:%s" % (address, self.port+1))
        time.sleep(1)
        logging.debug('Requesting blocks %s to %s', first, last)
        self.router.send_multipart([consensus.MSG_BLOCKS, str(first), str(last)])
        m = self._poll(self.router)[0]
        self.router.disconnect("tcp://%s:%s" % (address, self.port+1))
        return m

    def hello(self):
        self.reqsocket.send_multipart([consensus.MSG_HELLO,])
        logging.debug('Probing peer alive')
        m = self._poll()[0]
        return m

# Main program

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
    #sqldb.databaseLocation = 'blocks/blockchain.db'
    cons = consensus.Consensus(difficulty=5)
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
    n.bchain = sqldb.dbCheck()

    # Thread to listen request messages
    msg_thread = threading.Thread(name='REQ/REP', target=n.messageHandler)
    msg_thread.start()
    threads.append(msg_thread)

    # Thread to listen broadcast messages
    listen_thread = threading.Thread(name='PUB/SUB', target=n.listen)
    listen_thread.start()
    threads.append(listen_thread)
    #

    # Check peers most recent block (thread to check periodically)
    n.sync()

    # Miner thread
    miner_thread = threading.Thread(name='Miner', target=n.mine,
         kwargs={'cons': cons})
    miner_thread.start()
    threads.append(miner_thread)

    #sync_thread = threading.Thread(name='sync', target=n.sync)
    #sync_thread.start()
    #threads.append(listen_thread)
    if args.miner:
        n.start.set()
        n.f.set()

    # Main thread
    try:
        while True:
            # rpc-like commands (#TODO pass ip/port)
            n.rpcServer()
    # Exit main and threads
    except (KeyboardInterrupt, StopException):
        pass
    finally:
        #n.exit(args.ipaddr)
        #n.timer.cancel()
        n.k.set()
        n.e.set()
        n.f.set()
        n.start.set()
        n.close()
        for t in threads:
           t.join()
        print n.bchain.Info()
        # try: # TODO fix stucking on term or Assertion failed
        #     n.ctx.term()
        # except KeyboardInterrupt:
        #     pass

if __name__ == '__main__':
    main()