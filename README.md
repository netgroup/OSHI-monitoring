# OSHI-monitoring
## Setup instructions

You can use the manager.sh script to setup and run this project.

The available options are:
- --mode (or -m) to choose the running mode: setup, runmininet or runryu
- --topology (or -t) to supply a topology descriptor when running in runmininet mode

1. Download the VirtualBox VM from [Uniroma2 Netgroup](http://netgroup.uniroma2.it/twiki/bin/view/Oshi/WebHome#AnchorSoftDown)
2. After starting the VM, run the following command as user `user`:
    ```
    cd /home/user/workspace
    
    git clone https://github.com/netgroup/OSHI-monitoring.git
    ```
3. Setup the environment:
    ```
    cd /home/user/workspace/OSHI-monitoring
    
    sudo ./manager.sh --mode setup
    ```

## Run instructions

1. Run mininet with an included example topology:
    ```
    cd /home/user/workspace/OSHI-monitoring
    
    sudo ./manager.sh --mode runmininet --topology /home/user/workspace/OSHI-monitoring/example_topologies/simple_topology.json
    ```
2. Open a shell in the controller 
    *Note that the controller must be defined in the topology*
 
option a) xterm to a controller (from the mininet console), i.e. ctr8:
    ```
    xterm ctr8
    ```
option b) ssh to the controller from a host console (you need to check ctr8 IP address in the output of the script that has launched mininet) for example, assuming that the ip address is 10.255.248.1:
    ```
    sshpass -p 'root' ssh root@10.255.248.1
    ```

3. Modify /home/user/workspace/OSHI-monitoring/config.py to set the desired output level:
    ```
    # OUTPUT Levels
    NO_OUTPUT = 'NO_OUTPUT'
    SUMMARY_OUTPUT = 'SUMMARY_OUTPUT'
    DETAILED_OUTPUT = 'DETAILED_OUTPUT'
    OUTPUT_LEVEL = NO_OUTPUT
    ```

4. Run RYU (from the controller):
    ```
    cd /home/user/workspace/OSHI-monitoring
    
    ./manager.sh --mode runryu
    ```
