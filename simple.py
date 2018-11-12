from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel, info

from functools import partial
from time import sleep, time

from signal import SIGINT


# Sample usage

def testHostWithPrivateDirs():
    "Test bind mounts"
    topo = SingleSwitchTopo( 3 )
    # change to pwd
    privateDirs = privateDirs=[('/media/mininet/blockchain-simulator/blocks', '/media/mininet/blockchain-simulator/tmp/%(name)s/blocks'), '/media/mininet/blockchain-simulator/tmp/log']
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    net.start()
    popens = {}
    startServer(net)
    CLI( net )
    #stopServer(net.hosts)
    net.stop()

def startServer(net):
    for h in net.hosts:
        o = net.hosts[:]
        o.remove(h)
        ips = map(lambda x: x.IP(),o)
        peers = ' '.join(ips)
        #sleep(1)
        info('*** Blockchain node starting on %s\n' % h)
        h.cmd('python node.py -i', h.IP(), '-p 9000 --peers %s &' % peers)
        # subprocessing
        # popens[ h ] = h.popen('python node.py -i', h.IP(), '-p 9000 --peers', ' '.join(ips))

def stopServer(hosts):
    for h in hosts:
        # TODO
        h.cmd('')
        info('*** Blockchain server stopping on %s\n' % h)

if __name__ == '__main__':
    setLogLevel( 'info' )
    testHostWithPrivateDirs()
    info( 'Done.\n')
