#!/bin/bash

args=("$@")

if [args[0] == "setup"]; then
  echo "Setting up environment..."
  apt-get install rrdtool librrds-perl librrd-dev
  pip install rrdtool
  cd /home/user/workspace
  git clone https://github.com/ferrarimarco/tpin-2015-project.git
elif [args[0] == "install"]; then
  cd /home/user/workspace/tpin-2015-project
  git pull
  cp *.py /home/user/workspace/ryu/ryu/app/
  cd /home/user/workspace/ryu
  python ./setup.py install
elif [args[0] == "run-mininet"]; then
  cd /home/user/workspace/Dreamer-Mininet-Extensions
  ./mininet_deployer.py --topology topo/topo_vll_pw.json
elif [args[0] == "run-ryu"]; then
  cd /home/user/workspace/tpin-2015-project
  ryu-manager --observe-links traffic_monitor.py ofctl_rest.py rrdmanager.py
else
  echo "Mode not supported."
