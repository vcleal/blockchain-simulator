#!/usr/bin/env python

import zmq
import sys
from messages import *

if __name__ == '__main__':
    help_string = '''usage: %s [-h]
        <command> [<args>]

Blockchain RPC client

These are the commands available:

getlastblock        Print the last block info
getblock <index>    Print the block info with index <index>
getblocks <list>    Print the blocks info from index <list>
startmining         Start the miner thread
stopmining          Stop the miner thread
addpeer <ip>        Add <ip> to the node peers list
removepeer <ip>     Remove <ip> to the node peers list
getpeerinfo         Print the peers list
exit                Terminate and exit the node.py program running
''' % sys.argv[0]

    ctx = zmq.Context.instance()
    reqsocket = ctx.socket(zmq.REQ)
    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
    reqsocket.connect("tcp://127.0.0.1:9999")
    if len(sys.argv) >= 2:
        try:
            if MSG_LASTBLOCK == sys.argv[1]:
                reqsocket.send(sys.argv[1])
                b = reqsocket.recv()
                print b
            elif MSG_BLOCKCHAIN == sys.argv[1]:
                reqsocket.send(sys.argv[1])
                b = reqsocket.recv()
                print b
            elif MSG_ADD == sys.argv[1]:
                reqsocket.send_multipart([sys.argv[1], sys.argv[2]])
                print reqsocket.recv_string()
            elif MSG_REMOVE == sys.argv[1]:
                reqsocket.send_multipart([sys.argv[1], sys.argv[2]])
                print reqsocket.recv_string()
            elif MSG_BLOCK == sys.argv[1]:
                reqsocket.send_multipart([sys.argv[1], sys.argv[2]])
                b = reqsocket.recv()
                print b
            elif MSG_BLOCKS == sys.argv[1]:
                reqsocket.send_multipart(sys.argv[1:])
                l = reqsocket.recv_pyobj()
                for b in l:
                    print b
            elif MSG_PEERS == sys.argv[1]:
                reqsocket.send(sys.argv[1])
                print reqsocket.recv_pyobj()
            elif MSG_START == sys.argv[1]:
                reqsocket.send(sys.argv[1])
                print reqsocket.recv_string()
            elif MSG_STOP == sys.argv[1]:
                reqsocket.send(sys.argv[1])
                print reqsocket.recv_string()
            elif MSG_EXIT == sys.argv[1]:
                reqsocket.send(sys.argv[1])
                print reqsocket.recv_string()
            elif sys.argv[1] == '-h':
                print help_string
            else:
                print "Unknown command"
                sys.exit(2)
        except zmq.Again:
            print "Command failed"
        sys.exit(0)
        reqsocket.close(linger=0)
        ctx.term()
    else:
        print '''usage: %s [-h]
        <command> [<args>]''' % sys.argv[0]
        sys.exit(2)