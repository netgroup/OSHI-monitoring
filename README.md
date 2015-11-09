# OSHI-Monitoring
## Setup instructions

1. Download the VirtualBox VM from [Uniroma2 Netgroup](http://netgroup.uniroma2.it/twiki/bin/view/Oshi/WebHome#AnchorSoftDown)
2. After starting the VM, run the following command as user `user`:
    ```
    cd /home/user/workspace
    
    git clone https://github.com/netgroup/OSHI-monitoring.git
    ```
3. Setup the environment:
    ```
    cd /home/user/workspace/OSHI-monitoring
    
    sudo ./OSHI-monitoring.sh --mode setup
    ```

## Run instructions

1. Run mininet:
    ```
    cd /home/user/workspace/OSHI-monitoring
    
    sudo ./OSHI-monitoring.sh -mode runmininet -t /path/to/topology.json
    ```
2. xterm to a controller (from the mininet console), i.e. ctr8:
    ```
    xterm ctr8
    ```
    
    *Note that the controller must be defined in the topology*
3. Run RYU (from the controller):
    ```
    cd /home/user/workspace/monitoring
    
    sudo ./OSHI-monitoring.sh --mode runryu
    ```