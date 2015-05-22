#!/bin/bash

while test $# -gt 0
do
    case "$1" in
        --setup)
		  echo "Setting up environment..."
		  apt-get install rrdtool librrds-perl librrd-dev
		  pip install rrdtool
		  cd /home/user/workspace
		  git clone https://github.com/ferrarimarco/tpin-2015-project.git
            ;;
        --install) 
		  cd /home/user/workspace/tpin-2015-project
		  git pull
		  cp *.py /home/user/workspace/ryu/ryu/app/
		  cd /home/user/workspace/ryu
		  python ./setup.py install
            ;;
        --run-mininet)
		 cd /home/user/workspace/Dreamer-Mininet-Extensions
		 ./mininet_deployer.py --topology topo/topo_vll_pw.json
            ;;
        --run-ryu)
		  cd /home/user/workspace/tpin-2015-project
		  ryu-manager --observe-links traffic_monitor.py ofctl_rest.py rrdmanager.py
            ;;

        --*) echo "bad option $1"
            ;;
        *) echo "argument $1"
            ;;
    esac
    shift
done
