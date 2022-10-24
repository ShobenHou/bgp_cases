#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import os

N = 4
DIRPREFIX='/home/mininet/git_workspace/bgp_cases/2_a_more_complex_example' 
#NOTE: if using relative path, there would be error when creating .pid and .api files

def prefix(address, length):
    return "%s/%s" % (address, str(length))

def start_ripd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    config = dir + 'ripd.conf'
    zsock  = dir + 'zserv.api'
    pid    = dir + 'ripd.pid'
    r.cmd('/usr/sbin/ripd --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))

def stop_ripd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    pidfile =  dir + 'ripd.pid'
    f = open(pidfile)
    pid = int(f.readline())
    r.cmd('kill {}'.format(pid))
    info('stoped {} ripd'.format(name))


def start_zebra(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    config = dir + 'zebra.conf'
    pid =  dir + 'zebra.pid'
    log =  dir + 'zebra.log'
    zsock=  dir + 'zserv.api'
    # r.cmd('> {}'.format(log))			# this creates the file with the wrong permissions
    r.cmd('rm -f {}'.format(pid))    	# we need to delete the pid file
    r.cmd('/usr/sbin/zebra --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))


def stop_zebra(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    pidfile =  dir + 'zebra.pid'
    f = open(pidfile)
    pid = int(f.readline())
    zsock=  dir + 'zserv.api'
    r.cmd('kill {}'.format(pid))
    r.cmd('rm {}'.format(zsock))
    info('stoped {} zebra'.format(name))

def start_bgpd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    config = dir + 'bgpd.conf'
    zsock  = dir + 'zserv.api'
    pid    = dir + 'bgpd.pid'
    r.cmd('/usr/sbin/bgpd --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))

def stop_bgpd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    pidfile =  dir + 'bgpd.pid'
    f = open(pidfile)
    pid = int(f.readline())
    r.cmd('kill {}'.format(pid))
    info('stoped {} bgpd'.format(name))

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):
        
        r1_eth1 = '12.12.12.1'
        r1_eth2 = '1.1.1.1'

        r2_eth1 = '12.12.12.2'
        r2_eth2 = '25.25.25.1'

        r3_eth1 = '34.34.34.2'
        r3_eth2 = '53.53.53.1'

        r4_eth1 = '34.34.34.1'

        r5_eth1 = '25.25.25.2'
        r5_eth2 = '53.53.53.2'
        r5_eth3 = '5.2.2.1'

        r6_eth1 = '16.16.16.2'
        r6_eth2 = '6.1.1.1'

        h1_eth0 = '1.1.1.2'
        h2_eth0 = '5.2.2.2'

        r1 = self.addNode('r1', cls=LinuxRouter, ip=prefix(r1_eth1, 24))
        r2 = self.addNode('r2', cls=LinuxRouter, ip=prefix(r2_eth1, 24))
        r3 = self.addNode('r3', cls=LinuxRouter, ip=prefix(r3_eth1, 24))
        r4 = self.addNode('r4', cls=LinuxRouter, ip=prefix(r4_eth1, 24))

        r5 = self.addNode('r5', cls=LinuxRouter, ip=prefix(r5_eth1, 24))
        r6 = self.addNode('r6', cls=LinuxRouter, ip=prefix(r6_eth1, 24))
        h1 = self.addHost('h1', ip=prefix(h1_eth0, 24), defaultRoute='via {}'.format(r1_eth2))
        h2 = self.addHost('h2', ip=prefix(h2_eth0, 24), defaultRoute='via {}'.format(r5_eth3))

        self.addLink(r1, r2,
                     intfName1='r1-eth1', params1={'ip': prefix(r1_eth1, 24)},
                     intfName2='r2-eth1', params2={'ip': prefix(r2_eth1, 24)})

        self.addLink(r3, r4,
                     intfName1='r3-eth1', params1={'ip': prefix(r3_eth1, 24)},
                     intfName2='r4-eth1', params2={'ip': prefix(r4_eth1, 24)})
             
        self.addLink(r2, r5,
                     intfName1='r2-eth2', params1={'ip': prefix(r2_eth2, 24)},
                     intfName2='r5-eth1', params2={'ip': prefix(r5_eth1, 24)})
        self.addLink(r5, r3,
                     intfName1='r5-eth2', params1={'ip': prefix(r5_eth2, 24)},
                     intfName2='r3-eth2', params2={'ip': prefix(r3_eth2, 24)})             
         
        self.addLink(h1,r1,intfName2='r1-eth2',params2={ 'ip' : prefix(r1_eth2, 24)})
        self.addLink(h2,r5,intfName2='r5-eth3',params2={ 'ip' : prefix(r5_eth3, 24)})        

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet(controller = None, topo=topo )  # controller is used by s1-s3
    net.start()
    info( '*** Routing Table on Router:\n' )

    BGPnodelist = []		
    for i in range(1, N+1):
        nodename = 'r{}'.format(i)
        node = net[nodename]
        BGPnodelist.append(node)
    print('BGPnodelist:', BGPnodelist)

 
    info('starting zebra and bgpd service:\n')
    for r in BGPnodelist:
        start_zebra(r)
        start_bgpd(r)
    

    r2Node = net['r2']
    r3Node = net['r3']
    r5Node = net['r5']


    info('starting r5 zebra, ripd service:\n')
    start_zebra(r5Node)
    start_ripd(r5Node)
    
    info('starting r3 ripd service:\n')
    start_ripd(r3Node)

    info('starting r2 ripd service:\n')
    start_ripd(r2Node)
    

    # print routing table
    for node, type in net.items():
        if isinstance(type, Node):
            info('*** Routing Table on Router %s:\n' % node)
            info(net[node].cmd('route'))    


    CLI( net )
    #os.system("killall -9 bgpd zebra")
    # stop and erase .api .pid files    

    info('stoping r5 zebra, ripd service:\n')
    stop_ripd(r5Node)
    stop_zebra(r5Node)

    
    info('starting r3 ripd service:\n')
    stop_ripd(r3Node)

    info('starting r2 ripd service:\n')
    stop_ripd(r2Node)

    for r in BGPnodelist:
        stop_bgpd(r)
        stop_zebra(r)

        


    net.stop()

    os.system('stty erase {}'.format(chr(8)))

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()




