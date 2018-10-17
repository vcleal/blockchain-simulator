#!/usr/bin/env python

import zmq
import threading
import time
import hashlib
import block
import random
import argparse
import blockchain
import consensus
import sqlite3
from collections import deque
#
#import logging

#TODO peer connection handler
#TODO database request and send
#TODO blockchain class and database decision
#TODO messages type and zmq multipart

class Node(object):
    """docstring"""

    ctx = None
    psocket = None
    lsocket = None


    def __init__(self, ipaddr, port):
        self.ipaddr = ipaddr
        self.port = port
        self.ctx = zmq.Context.instance()
        self.reqsocket = self.ctx.socket(zmq.REQ)
        self.repsocket = self.ctx.socket(zmq.REP)
        self.psocket = self.ctx.socket(zmq.PUB)
        self.lsocket = self.ctx.socket(zmq.SUB)
        self.lsocket.setsockopt(zmq.SUBSCRIBE, b'')
        self.balance = 0
        self.stake = 0
        self.peers = deque()

    # Node as client
    def connect(self,d_ip='127.0.0.1',d_port=9000):
        self.lsocket.connect("tcp://%s:%s" % (d_ip, d_port))

    def listen(self, k, e, bchain):
        db = sqlite3.connect('blocks/blockchain.db')
        c = db.cursor()
        while True and not k.is_set():
            try:
                block_recv = self.lsocket.recv_pyobj()
                e.set()
                print("Got block")
                print(block_recv.hash)
                # lock?
                if bchain.getLastBlock().index < block_recv.index:
                    bchain.addBlocktoBlockchain(block_recv)
                    self.writeBlock(block_recv, c, db)
                #self.checkBlock(e)
                e.clear()
            except (zmq.ContextTerminated):
                break
        db.close()

    # Node as server
    def bind(self):
        self.psocket.bind("tcp://%s:%s" % (self.ipaddr, self.port))

    def close(self):
        self.psocket.close(linger=0)
        self.lsocket.close(linger=0)
        self.repsocket.close(linger=0)
        self.reqsocket.close(linger=0)
        self.ctx.term()

    def addPeer(self, iplist, port=9000):
        iplist = iplist if isinstance(iplist, list) else [iplist]
        for ipaddr in iplist:
            peer = {'ipaddr': ipaddr}
            if peer not in self.peers:
                self.peers.appendleft(peer)
                self.connect(d_ip=ipaddr,d_port=port)
            else:
                print("Peer %s already connected" % ipaddr)

    def connectionHandler(self, f):
        while True:
            f.wait()
            # Recebeu msg com d_ip e d_port=9000
            self.addPeer(d_ip,d_port)
            f.clear()

    def removePeer(self, ipaddr):
        peer = {'ipaddr': ipaddr}
        try:
            self.peers.remove(peer)
        except ValueError:
            return False
        return True

    def getPeers(self):
        return self.peers

    def setBalance(self, value):
        self.balance = value

    def doConsensus(self, k, e, bchain, cons):
        #bchain = ''
        target = 2 ** (20) - 1
        name = threading.current_thread().getName()
        db = sqlite3.connect('blocks/blockchain.db')
        c = db.cursor()
        while True and not k.is_set():
            stop = e.is_set()
            lastblock = bchain.getLastBlock()
            b = cons.generateNewblock(lastblock,stop)
            if b:
                bchain.addBlocktoBlockchain(b)
                self.psocket.send_pyobj(b)
                self.writeBlock(b, c, db)
        db.close()

    def writeBlock(self, b, c, db):
        c.execute('INSERT INTO blocks VALUES (?,?,?,?,?)', (
                b.__dict__['index'],
                b.__dict__['timestamp'],
                b.__dict__['prev_hash'],
                b.__dict__['hash'],
                b.__dict__['nonce']))
        db.commit()

    def readBlock(self):
        pass

    def checkBlock(self, e):
        #if new_hash == (hashlib.sha256(str(name+bchain[0])+str(nonce)).hexdigest()):
        #raise StopMineException("")
        #self.psocket.send_string("ok")
        #e.set()
        return True
        #else:
        #    return False

    def run(self, kill, e, bchain, cons):
        m1 = threading.Thread(name='Miner',target=self.doConsensus,
        kwargs={'k': kill, 'e': e, 'bchain': bchain, 'cons': cons})
        m1.start()
        return [m1]

    def dbConnect(self):
        db = sqlite3.connect('blocks/blockchain.db')
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS blocks (
            id integer primary key, 
            ctime text, 
            phash text, 
            hash text, 
            nonce integer)""")
        db.commit()
        cursor.execute('SELECT * FROM blocks WHERE id = (SELECT MAX(id) FROM blocks)')
        # Last block from own database
        lastBlock_db = cursor.fetchone()
        # Last block from other nodes
        rBlock = self.reqrepClient()
        if rBlock and (rBlock.index > lastBlock_db.index):
            self.writeBlock(rBlock, cursor, db)
            lastBlock_db = rBlock
            # set flag to request other blocks?
        db.close()
        return blockchain.Blockchain(lastBlock_db)

    def reqrepServer(self, blockchain, kill, e, cons, threads):
        self.repsocket.bind("tcp://127.0.0.1:9001")
        while True:
            try:
                messages = self.repsocket.recv_multipart()
            except zmq.ContextTerminated:
                break
            time.sleep (1)
            cmd = messages[0]
            if cmd == 'getlastblock':  
                self.repsocket.send_pyobj(blockchain.getLastBlock())
            elif cmd == 'addpeer':
                self.addPeer(messages[1])
                self.repsocket.send_string("Peer added")
            elif cmd == 'getpeerinfo':
                self.repsocket.send_pyobj(self.getPeers())
            elif cmd == 'startmining':
                t = self.run(kill, e, blockchain, cons)
                threads.append(t)
            else:
                print 'Command unknown'

    def reqrepClient(self):
        self.reqsocket.connect("tcp://127.0.0.1:9001")
        self.reqsocket.send("getlastblock")
        try:
            b = self.reqsocket.recv_pyobj(zmq.NOBLOCK)
            return b
        except zmq.ZMQError:
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
    args = parser.parse_args()

    threads = []
    cons = consensus.Consensus(5)
    n = Node(args.ipaddr, args.port)
    # Flags and thread events
    kill = threading.Event()
    e = threading.Event()
    f = threading.Event()

    #test = threading.Thread(target=n.reqrepServer, kwargs={'blockchain': blockchain.Blockchain()})
    #test.start()
    # Connect and check own node database
    bchain = n.dbConnect()

    # Connection handler thread
    #connect_thread = threading.Thread(target=n.connectionHandler)
    #connect_thread.start()

    if args.peers:
        n.addPeer(args.peers)
    else: # Connect to localhost
        n.connect()

    # Sync for other nodes
    sync_thread = threading.Thread(target=n.reqrepServer, kwargs={'blockchain': bchain})
    # sync_thread.start()

    # Thread to listen after block messages
    listen_thread = threading.Thread(target=n.listen,
     kwargs={'k': kill, 'e': e, 'bchain': bchain})
    listen_thread.start()
    #
    n.bind()
    #
    # Miner thread
    #threads = n.run(kill, e, bchain, cons)
    # Exit main and threads
    try:
        while True:
            n.reqrepServer(bchain, kill, e, cons, threads)
    except KeyboardInterrupt:
        pass
    finally:
        kill.set()
        for t in threads:
            t.join()
        n.close()
        print bchain.Info()

if __name__ == '__main__':
    main()