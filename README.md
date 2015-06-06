# TPIN: Project (2015)
## Setup instructions

1. Download the VirtualBox VM from [Uniroma2 Netgroup](http://netgroup.uniroma2.it/twiki/bin/view/Oshi/WebHome#AnchorSoftDown)
2. After starting the VM, run the following command as user `user` (**only if it's the first time you run this software**):
    ```
    cd /home/user/workspace
    
    git clone https://github.com/ferrarimarco/tpin-2015-project.git
    ```
3. Setup the environment:
    ```
    cd /home/user/workspace/tpin-2015-project
    
    sudo ./tpin-2015-project.sh --setup
    ```
4. Setup the ryu application:
    ```
    cd /home/user/workspace/tpin-2015-project
    
    sudo ./tpin-2015-project.sh --setup
    ```
5. Run mininet:
    ```
    cd /home/user/workspace/tpin-2015-project
    
    sudo ./tpin-2015-project.sh --run-mininet
    ```
6. xterm to a controller (from the mininet console). For example we choose ctr8:
    ```
    xterm ctr8
    ```
    *ctr8 is one of the controllers described in the topology*
7. Run RYU (from the controller):
    ```
    cd /home/user/workspace/tpin-2015-project
    
    sudo ./tpin-2015-project.sh --run-ryu
    ```
    
## Test REST interface
You can call each REST endpoint implemented in ofctl_rest.py. The server runs on port 8080.

### Example
```
curl http://10.0.4.1:8080/stats/switches
```
*Note that ryu-manager must be running on the machine you want to query. 10.0.4.1 (ctr8) in this case.*

