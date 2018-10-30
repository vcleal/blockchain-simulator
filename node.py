#!/usr/bin/env python

import zmq
import threading
import time
import sys
#import hashlib
#import random
import argparse
import block
import blockchain
import consensus
import sqlite3
import pickle
from collections import deque
#
#import logging

#TODO blockchain class and database decision (move to only db solution)
#TODO change db key order
#TODO check possible db error overwriting

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
        self.port = port
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
        self.balance = 0
        self.stake = 0
        self.synced = False
        self.peers = deque()
        # Flags and thread events
        self.k = threading.Event()
        self.e = threading.Event()
        self.f = threading.Event()

    # Node as client
    def connect(self,d_ip='127.0.0.1',d_port=9000):
        self.subsocket.connect("tcp://%s:%s" % (d_ip, d_port))
        self.reqsocket.connect("tcp://%s:%s" % (d_ip, d_port+1))

    def disconnect(self,d_ip='127.0.0.1',d_port=9000):
        self.subsocket.disconnect("tcp://%s:%s" % (d_ip, d_port))
        self.reqsocket.disconnect("tcp://%s:%s" % (d_ip, d_port+1))

    def listen(self, bchain):
        db = sqlite3.connect('blocks/blockchain.db')
        c = db.cursor()
        while True and not self.k.is_set():
            try:
                # TODO messages types
                msg, block_recv = self.subsocket.recv_multipart()
                b = pickle.loads(block_recv)
                self.e.set()
                # maybe request block here
                print("Got block")
                print(b.hash)
                # lock?
                if bchain.getLastBlock().index < b.index:
                    self.writeBlock(b, c)
                    bchain.addBlocktoBlockchain(b)
                    db.commit()
                #self.checkBlock(e)
                self.e.clear()
            except (zmq.ContextTerminated):
                break
        db.close()

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
        self.ctx.term()

    def addPeer(self, ipaddr, port=9000):
        peer = {'ipaddr': ipaddr}
        if peer not in self.peers:
            self.peers.appendleft(peer)
            self.connect(d_ip=ipaddr,d_port=self.port)
            return "Peer %s connected" % ipaddr
        else:
            print("Peer %s already connected" % ipaddr)
            return "Peer %s already connected" % ipaddr

    def removePeer(self, ipaddr):
        peer = {'ipaddr': ipaddr}
        try:
            self.peers.remove(peer)
            self.disconnect(d_ip=ipaddr,d_port=self.port)
        except ValueError:
            return "Peer %s not connected" % ipaddr
        return "Peer %s removed" % ipaddr

    def getPeers(self):
        return self.peers

    def setBalance(self, value):
        self.balance = value

    def mine(self, bchain, cons):
        # target = 2 ** (20) - 1
        name = threading.current_thread().getName()
        db = sqlite3.connect('blocks/blockchain.db')
        c = db.cursor()
        while True and not self.k.is_set():
            stop = self.e.is_set() # move e flag inside generate?
            self.f.wait()
            lastblock = bchain.getLastBlock()
            b = cons.generateNewblock(lastblock,stop)
            if b and not self.e.is_set():
                self.writeBlock(b, c)
                bchain.addBlocktoBlockchain(b)
                self.psocket.send_multipart(['block', pickle.dumps(b, 2)])
                db.commit()
        db.close()

    def writeBlock(self, b, c):
        if isinstance(b, list):
            c.executemany('INSERT INTO blocks VALUES (?,?,?,?,?)', b)
        else:
            c.execute('INSERT INTO blocks VALUES (?,?,?,?,?)', (
                    b.__dict__['index'],
                    b.__dict__['timestamp'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['nonce']))
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

    def doConsensus(self, bchain, cons):
        m1 = threading.Thread(name='Miner',target=self.mine,
         kwargs={'bchain': bchain, 'cons': cons})
        m1.start()
        return m1

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
        if not lastBlock_db:
            b = block.Block(0,"",0,timestamp="2018-10-10 00:00:0.0")
            self.writeBlock(b, cursor)
            lastBlock_db = [0]
        # Last block from other nodes
        rBlock = self.reqLastBlock()
        if rBlock and lastBlock_db and (rBlock.index > lastBlock_db[0]):
            first = lastBlock_db[0]
            last = rBlock.index
            if (last-first) == 1:
                self.writeBlock(rBlock, cursor)
            else:
                l = self.reqBlocks(first+1, last)
                if  l:
                    self.writeBlock(l, cursor)
            lastBlock_db = rBlock
            # set flag to request other blocks?
            #self.synced = True
        db.commit()
        db.close()
        return blockchain.Blockchain(lastBlock_db)

    def sync(self, bchain):
        # Sync with other nodes
        sy = threading.Thread(target=self.reqrepServer,
         kwargs={'blockchain': bchain})
        sy.start()
        return sy

    def reqrepServer(self, blockchain):
        db = sqlite3.connect('blocks/blockchain.db')
        cursor = db.cursor()
        self.bind(self.repsocket, port=self.port+1)
        time.sleep(1)
        while True and not self.k.is_set():
            try:
                messages = self.repsocket.recv_multipart()
            except zmq.ContextTerminated:
                break
            time.sleep(1)
            cmd = messages[0]
            if cmd == 'getlastblock':
                self.repsocket.send_pyobj(blockchain.getLastBlock())
            elif cmd == 'getblocks':
                # check blocks in db
                cursor.execute('SELECT * FROM blocks WHERE id BETWEEN ? AND ?', (messages[1],messages[2]))
                l = cursor.fetchall()
                self.repsocket.send_pyobj(l)
            elif cmd == 'block':
                # change to isolated function
                cursor.execute('SELECT * FROM blocks WHERE id = ?', (messages[1],))
                b = cursor.fetchone()
                self.repsocket.send_pyobj(b)
            else:
                pass

    def rpcServer(self, blockchain):
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
                self.rpcsocket.send_pyobj(blockchain.getLastBlock())
            elif cmd == 'getblock':
                cursor.execute('SELECT * FROM blocks WHERE id = ?', (messages[1],))
                b = cursor.fetchone()
                self.rpcsocket.send_pyobj(b)
            elif cmd == 'getblocks':
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
                self.f.set()
            elif cmd == 'stopmining':
                self.f.clear()
                self.rpcsocket.send_string('Stopping mining...')
            elif cmd == 'exit':
                self.rpcsocket.send_string('Exiting...')
                #sys.exit(0)
                raise StopException
            else:
                self.rpcsocket.send_string('Command unknown')
                print 'Command unknown'

# Client request-reply functions

    def reqLastBlock(self):
        self.reqsocket.send("getlastblock")
        try:
            evts = dict(self.poller.poll(5000))
            print evts
        except KeyboardInterrupt:
            return None
        if self.reqsocket in evts and evts[self.reqsocket] == zmq.POLLIN:
            b = self.reqsocket.recv_pyobj()
            return b
        else:
            return None
        # try:
        #     # non-blocking
        #     b = self.reqsocket.recv_pyobj(zmq.NOBLOCK)
        #     return b
        # except zmq.ZMQError:
        #     return None

    def reqBlock(self, index):
        # TODO check zmq timeout
        self.reqsocket.send_multipart(["block", index])
        b = self.reqsocket.recv_pyobj()
        return block.Block(b[0],b[2],b[4],b[3],b[1])

    def reqBlocks(self, first, last):
        # TODO check zmq timeout
        self.reqsocket.send_multipart(["getblocks", str(first), str(last)])
        try:
            evts = dict(self.poller.poll(5000))
            print evts
        except KeyboardInterrupt:
            return None
        if self.reqsocket in evts and evts[self.reqsocket] == zmq.POLLIN:
            b = self.reqsocket.recv_pyobj()
            return b
        else:
            return None

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
    args = parser.parse_args()

    threads = []
    cons = consensus.Consensus(5)
    n = Node(args.ipaddr, args.port)

    # Connect to predefined peers
    if args.peers:
        iplist = args.peers if isinstance(args.peers, list) else [args.peers]
        for ipaddr in iplist:
            n.addPeer(ipaddr)
    else: # Connect to localhost
        n.connect()
    time.sleep(1)
    # Connect and check own node database
    bchain = n.dbConnect()

    # Thread to listen request messages
    t = n.sync(bchain)
    #threads.append(t)

    # Thread to listen broadcast messages
    listen_thread = threading.Thread(target=n.listen,
     kwargs={'bchain': bchain})
    listen_thread.start()
    #
    n.bind(n.psocket)
    time.sleep(1)
    #
    # Maybe check last block again before mining
    # Miner thread
    t = n.doConsensus(bchain, cons)
    #threads.append(t)
    if args.miner:
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
        n.k.set()
        n.e.set()
        n.f.set()
        #for t in threads:
        #    t.join()
        n.close()
        print bchain.Info()

if __name__ == '__main__':
    main()