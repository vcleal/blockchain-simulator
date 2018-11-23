#!/usr/bin/env python

import zmq
import sys
from messages import *

#TODO argparse

if __name__ == '__main__':
    ctx = zmq.Context.instance()
    reqsocket = ctx.socket(zmq.REQ)
    # check error
    reqsocket.setsockopt(zmq.RCVTIMEO, 5000)
    #repsocket = self.ctx.socket(zmq.REP)
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
            else:
                print "Unknown command"
                sys.exit(2)
        except zmq.Again:
            print "Command failed"
        sys.exit(0)
        reqsocket.close(linger=0)
        ctx.term()
    else:
        print "usage: %s getlastblock|startmining|stopmining|addpeer <peer>|removepeer <peer>|getpeerinfo" % sys.argv[0]
        sys.exit(2)