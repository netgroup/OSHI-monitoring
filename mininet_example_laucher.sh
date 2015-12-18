#!/bin/bash

######################################################################
# mininet_example_launcher.sh  
#
# launch a mininet instance
# first parameter is the IP address of the controller
# if no parameters are provided the default IP address is 10.255.248.1
# ####################################################################

TOPOLOGY=/home/user/workspace/OSHI-monitoring/example_topologies/simple_topology.json
 
sudo ./manager.sh --mode runmininet --topology $TOPOLOGY