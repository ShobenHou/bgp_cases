# bgp_cases/00_01_broadcast_and_filter
quagga bgp broadcast and filtering demo
### NOTE:change absolute path into your own path

in init_mininet.py:
> DIRPREFIX='/home/mininet/git_workspace/bgp_cases/00_01_broadcast_and_filter' 

in zebra.conf and bgpd.conf:
> log file /home/mininet/git_workspace/bgp_cases/00_01_broadcast_and_filter/r1/bgpd.log

### NOTE: make sure your user has the permission to create and delete files in this directory

### How to run
> sudo python init_mininet.py 
