#!/bin/bash
# first parameter is the IP address of the controller
# if no parameters are provided the default IP address is 10.255.248.1

DEFAULT_CONTROLLER_IP='10.255.248.1'
CONTROLLER_IP=$1

printandexec () {
		echo "$@"
		eval "$@"
}

if [ $# -eq 0 ]
  then
    CONTROLLER_IP=$DEFAULT_CONTROLLER_IP
fi


#sshpass -p 'root' ssh -t root@10.255.248.1 'cd /home/user/workspace/OSHI-monitoring; ./manager.sh --mode runryu'
printandexec "sshpass -p 'root' ssh -t root@$CONTROLLER_IP -o StrictHostKeyChecking=no 'cd /home/user/workspace/OSHI-monitoring; ./manager.sh --mode runryu'"
