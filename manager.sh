#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

while [[ $# > 1 ]]
do
key="$1"

case $key in
    -m|--mode)
    MODE="$2"
    shift # past argument
    ;;
    -t|--topology)
    TOPOLOGY="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

if [ -z ${MODE+x} ]
	then
		echo "MODE is unset. Set it with -m or --mode. Available options are: setup, runmininet and runryu. This script will now terminate."
		exit 1
fi

if [[ ${MODE} = 'runmininet' ]] && [ -z ${TOPOLOGY+x} ]
	then
		echo "Mode is set to runmininet but you did not supply a topology. Set it with -t or --topology. This script will now terminate."
		exit 1
fi

if [[ ${MODE} = 'setup' ]]
	then
	  echo "Setting up environment..."
	  apt-get install rrdtool librrds-perl librrd-dev
	  pip install rrdtool
elif [[ ${MODE} = 'runmininet' ]]
	then
	  echo "Running mininet with topology ${TOPOLOGY}"
	  cd /home/user/workspace/OSHI-monitoring
	  find . -name \*.cp -exec cp {} /home/user/workspace/dreamer-ryu/ryu/app/ \;
	  cd /home/user/workspace/dreamer-ryu
	  python ./setup.py install
	  cd /home/user/workspace/Dreamer-Mininet-Extensions
	  ./mininet_deployer.py --topology ${TOPOLOGY}
elif [[ ${MODE} = 'runryu' ]]
	then
	  echo "Running RYU..."
	  cd /home/user/workspace/OSHI-monitoring
	  ryu-manager --observe-links traffic_monitor.py rrdmanager.py
else 
          echo "Unrecognized option. Available options are: setup, runmininet and runryu. This script will now terminate."
          exit 1
fi
