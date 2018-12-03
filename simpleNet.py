from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel, info

from functools import partial
from time import sleep
from random import shuffle
import sys, os

# Sample usage
# sudo python simpleNet.py <n>
# n: number of hosts

# file directory path to mount private dirs
dir_path = os.path.dirname(os.path.realpath(__file__))

def testHostWithPrivateDirs(number=3):
    "Test bind mounts"
    topo = SingleSwitchTopo( number )
    privateDirs = privateDirs=[ (dir_path+'/blocks',
     dir_path+'/tmp/%(name)s/blocks'),
     dir_path+'/tmp/log' ]
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    net.start()
    startServer(net)
    CLI( net )
    stopServer(net.hosts)
    net.stop()

def startServer(net):
    """ Start node.py process passing all hosts ip addresses """
    for h in net.hosts:
        o = net.hosts[:]
        o.remove(h)
        ips = [x.IP() for x in o]
        shuffle(ips)
        peers = ' '.join(ips)
        #sleep(1)
        info('*** Blockchain node starting on %s\n' % h)
        h.cmd('python node.py -i', h.IP(), '-p 9000 --peers %s &' % peers)

def stopServer(hosts):
    """ Stop the node.py process through rpcclient """
    for h in hosts:
        #
        h.cmd('rpc/rpcclient.py exit')
        info('*** Blockchain node stopping on %s\n' % h)

if __name__ == '__main__':
    setLogLevel( 'info' )
    if len(sys.argv) >= 2:
        testHostWithPrivateDirs(int(sys.argv[1]))
    else:
        testHostWithPrivateDirs()
    info( 'Done.\n')
