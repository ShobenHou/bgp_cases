# bgp_cases/5_community_attr
quagga bgp community example


### NOTE:change absolute path into your own path

in init_mininet.py:
> DIRPREFIX='/home/mininet/git_workspace/bgp_cases/5_community_attr' 

in zebra.conf and bgpd.conf:
> log file /home/mininet/git_workspace/bgp_cases/5_community_attr/r1/bgpd.log

### NOTE: make sure your user has the permission to create and delete files in this directory

### How to run
> sudo python init_mininet.py 
