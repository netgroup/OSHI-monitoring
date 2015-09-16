#!/bin/bash

while test $# -gt 0
do
    case "$1" in
        --setup)
		  echo "Setting up environment..."
		  apt-get install rrdtool librrds-perl librrd-dev
		  pip install rrdtool
            ;;
        --run-mininet)
		  cd /media/sf_Shared/workspace/pycharm/OSHI-monitoring
		  cp *.py /home/user/workspace/dreamer-ryu/ryu/app/
		  cd /home/user/workspace/dreamer-ryu
		  python ./setup.py install
		 cd /home/user/workspace/Dreamer-Mininet-Extensions
		 ./mininet_deployer.py --topology /media/sf_Shared/topologies/simple_topology.json
		    ;;
        --run-ryu)
		  cd /media/sf_Shared/workspace/pycharm/OSHI-monitoring
		  ryu-manager --observe-links traffic_monitor.py ofctl_rest.py rrdmanager.py
            ;;
        --*) echo "bad option $1"
            ;;
        *) echo "argument $1"
            ;;
    esac
    shift
done
