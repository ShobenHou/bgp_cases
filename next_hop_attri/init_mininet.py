#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import os

N=3
DIRPREFIX='/home/mininet/git_workspace/bgp_cases/next_hop_attri' 
#TODO: Change the absolute path
#NOTE: if using relative path, there would be error when creating .pid and .api files

def prefix(address, length):
    return "%s/%s" % (address, str(length))


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

        r1_eth1 = '150.10.0.1'
        r1_eth2 = '150.10.30.1'
        r1_eth3 = '170.10.20.1'

        r2_eth1 = '150.10.50.1'
        r2_eth2 = '150.10.30.2'

        r3_eth1 = '170.10.0.1'
        r3_eth2 = '170.10.20.2'

        h1_eth1 = '150.10.0.2'
        h2_eth1 = '150.10.50.2'
        h3_eth1 = '170.10.0.2'

        r1 = self.addNode( 'r1', cls=LinuxRouter, ip=prefix(r1_eth1, 24)) 
        r2 = self.addNode( 'r2', cls=LinuxRouter, ip=prefix(r2_eth1, 24))
        r3 = self.addNode( 'r3', cls=LinuxRouter, ip=prefix(r3_eth1, 24))

        h1 = self.addHost( 'h1', ip=prefix(h1_eth1, 24), defaultRoute='via {}'.format(r1_eth1)) 
        h2 = self.addHost( 'h2', ip=prefix(h2_eth1, 24), defaultRoute='via {}'.format(r2_eth1))
        h3 = self.addHost( 'h3', ip=prefix(h3_eth1, 24), defaultRoute='via {}'.format(r3_eth1))
        self.addLink(r1, h1,
                     intfName1='r1-eth1', params1={'ip': prefix(r1_eth1, 24)},
                     intfName2='h1-eth1', params2={'ip': prefix(h1_eth1, 24)})
        self.addLink(r2, h2,
                     intfName1='r2-eth1', params1={'ip': prefix(r2_eth1, 24)},
                     intfName2='h2-eth1', params2={'ip': prefix(h2_eth1, 24)})
        self.addLink(r3, h3,
                     intfName1='r3-eth1', params1={'ip': prefix(r3_eth1, 24)},
                     intfName2='h3-eth1', params2={'ip': prefix(h3_eth1, 24)})

        self.addLink(r1, r2,
                     intfName1='r1-eth2', params1={'ip': prefix(r1_eth2, 24)},
                     intfName2='r2-eth2', params2={'ip': prefix(r2_eth2, 24)})
        self.addLink(r3, r1,
                     intfName1='r3-eth2', params1={'ip': prefix(r3_eth2, 24)},
                     intfName2='r1-eth3', params2={'ip': prefix(r1_eth3, 24)})
        
      
	

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet(controller = None, topo=topo )  # controller is used by s1-s3
    net.start()
    info( '*** Routing Table on Router:\n' )
#    info( net[ 'r1' ].cmd( 'route' ) )

    BGPnodelist = []		
    for i in range(1, N+1):
        nodename = 'r{}'.format(i)
        node = net[nodename]
        BGPnodelist.append(node)
    print('BGPnodelist:', BGPnodelist)


    '''
    # now we build zebra.conf
    zconflist = []
    # Create "zebra.conf" file for each router 
    for r in BGPnodelist:
        zconf = create_zebra_conf(r, ndict) 
        zconflist.append(zconf)
    '''
    '''
    bgpconflist = []    
    # Create "bgpd.conf" file for each router
    for r in BGPnodelist:
        bgpconf = create_bgpd_conf(r, ndict, addrdict, ASdict) 
        bgpconflist.append(bgpconf)
    '''
 
    info('starting zebra and bgpd service:\n')
    for r in BGPnodelist:
        start_zebra(r)
        start_bgpd(r)
    
    
    # print routing table
    for node, type in net.items():
        if isinstance(type, Node):
            info('*** Routing Table on Router %s:\n' % node)
            info(net[node].cmd('route'))    


    CLI( net )
    #os.system("killall -9 bgpd zebra")
    # stop and erase .api .pid files
    
    

    for r in BGPnodelist:
        stop_bgpd(r)
        stop_zebra(r)

    net.stop()
    '''
    for zconf in zconflist:
        print('removing file {}'.format(zconf))
        os.remove(zconf)
    '''
    '''
    for bgpconf in bgpconflist:
        print('removing file {}'.format(bgpconf))
        os.remove(bgpconf)
    '''
    os.system('stty erase {}'.format(chr(8)))

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()




