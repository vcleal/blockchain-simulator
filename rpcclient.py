#!/usr/bin/env python

import zmq
import block
import sys

if __name__ == '__main__':
    ctx = zmq.Context.instance()
    reqsocket = ctx.socket(zmq.REQ)
    #repsocket = self.ctx.socket(zmq.REP)
    reqsocket.connect("tcp://127.0.0.1:9999")
    if len(sys.argv) >= 2:
        if 'getlastblock' == sys.argv[1]:
            reqsocket.send(sys.argv[1])
            b = reqsocket.recv_pyobj()
            print b.blockInfo()
        elif 'addpeer' == sys.argv[1]:
            reqsocket.send_multipart([sys.argv[1], sys.argv[2]])
            print reqsocket.recv_string()
        elif 'removepeer' == sys.argv[1]:
            reqsocket.send_multipart([sys.argv[1], sys.argv[2]])
            print reqsocket.recv_string()
        elif 'getblock' == sys.argv[1]:
            reqsocket.send_multipart([sys.argv[1], sys.argv[2]])
            b = reqsocket.recv_pyobj()
            print block.Block(b[0],b[2],b[4],b[3],b[1]).blockInfo()
        elif 'getblocks' == sys.argv[1]:
            reqsocket.send_multipart(sys.argv[1:])
            l = reqsocket.recv_pyobj()
            for b in l:
                print block.Block(b[0],b[2],b[4],b[3],b[1]).blockInfo()
        elif 'getpeerinfo' == sys.argv[1]:
            reqsocket.send(sys.argv[1])
            print reqsocket.recv_pyobj()
        elif 'startmining' == sys.argv[1]:
            reqsocket.send(sys.argv[1])
            print reqsocket.recv_string()
        elif 'stopmining' == sys.argv[1]:
            reqsocket.send(sys.argv[1])
            print reqsocket.recv_string()
        elif 'exit' == sys.argv[1]:
            reqsocket.send(sys.argv[1])
            print reqsocket.recv_string()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
        reqsocket.close()
        ctx.term()
    else:
        print "usage: %s getlastblock|startmining|stopmining|addpeer <peer>|removepeer <peer>|getpeerinfo" % sys.argv[0]
        sys.exit(2)