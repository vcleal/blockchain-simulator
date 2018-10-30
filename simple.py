from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel, info
from mininet.util import pmonitor

from functools import partial
from time import sleep, time

from signal import SIGINT


# Sample usage

def testHostWithPrivateDirs():
    "Test bind mounts"
    topo = SingleSwitchTopo( 3 )
    privateDirs = privateDirs=[('/media/mininet/blockchain-simulator/blocks', '/media/mininet/blockchain-simulator/tmp/%(name)s/blocks')]
    host = partial( Host,
                    privateDirs=privateDirs )
    net = Mininet( topo=topo, host=host )
    net.start()
    popens = {}
    sleep(1)
    for h in net.hosts:
        o = net.hosts[:]
        o.remove(h)
        ips = map(lambda x: x.IP(),o)
        sleep(1)
        info('*** Blockchain node starting on %s\n' % h)
        h.cmd('python node.py -i', h.IP(), '-p 9000 --peers', ' '.join(ips), ' &')
        # popens[ h ] = h.popen('python node.py -i', h.IP(), '-p 9000 --peers', ' '.join(ips))
        # endTime = time() + 60
        # for h, line in pmonitor( popens, timeoutms=500 ):
        #     if h:
        #         print '%s: %s' % ( h.name, line ),
        #         if time() >= endTime:
        #             for p in popens.values():
        #                 p.send_signal( SIGINT )
    # info(popens)
    CLI( net )
    #stopServer(net.hosts)
    net.stop()

def addPeers(hosts):
    for h in hosts:
        h.cmd('')
        #others = hosts[:]
        #others.remove(h)
        #for o in others:
        #        h.cmd('bitcoin-cli -regtest addnode', o.IP(), 'onetry')

def stopServer(hosts):
    for h in hosts:
        h.cmd('')
        info('*** Bitcoin server stopping on %s\n' % h)

if __name__ == '__main__':
    setLogLevel( 'info' )
    testHostWithPrivateDirs()
    info( 'Done.\n')
