#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import os

N=4
DIRPREFIX='/home/mininet/git_workspace/bgp_cases/3_local_preference' 
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

        r1_eth1 = '170.10.0.1'
        #r1_eth2 = '1.1.1.1'
        r1_eth2 = '13.13.13.1'

        r2_eth1 = '170.10.0.2'
        #r2_eth2 = '3.3.3.4'
        r2_eth2 = '24.24.24.1'

        #r3_eth1 = '1.1.1.2'
        #r3_eth2 = '128.213.11.1'
        r3_eth1 = '13.13.13.2'
        r3_eth2 = '34.34.34.1'

        #r4_eth1 = '3.3.3.3'
        #r4_eth2 = '128.213.11.2'
        r4_eth1 = '24.24.24.2'
        r4_eth2 = '34.34.34.2'



        r1 = self.addNode( 'r1', cls=LinuxRouter, ip=prefix(r1_eth1, 24)) 
        r2 = self.addNode( 'r2', cls=LinuxRouter, ip=prefix(r2_eth1, 24))
        r3 = self.addNode( 'r3', cls=LinuxRouter, ip=prefix(r3_eth1, 24))
        r4 = self.addNode( 'r4', cls=LinuxRouter, ip=prefix(r4_eth1, 24))


        self.addLink(r1, r2,
                     intfName1='r1-eth1', params1={'ip': prefix(r1_eth1, 24)},
                     intfName2='r2-eth1', params2={'ip': prefix(r2_eth1, 24)})

        self.addLink(r3, r1,
                     intfName1='r3-eth1', params1={'ip': prefix(r3_eth1, 24)},
                     intfName2='r1-eth2', params2={'ip': prefix(r1_eth2, 24)})
        self.addLink(r4, r2,
                     intfName1='r4-eth1', params1={'ip': prefix(r4_eth1, 24)},
                     intfName2='r2-eth2', params2={'ip': prefix(r2_eth2, 24)})
        
        self.addLink(r3, r4,
                     intfName1='r3-eth2', params1={'ip': prefix(r3_eth2, 24)},
                     intfName2='r4-eth2', params2={'ip': prefix(r4_eth2, 24)})

      
	

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




