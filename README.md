# TPIN: Project (2015)
## Setup instructions

1. Download the VirtualBox VM from [Uniroma2 Netgroup](http://netgroup.uniroma2.it/twiki/bin/view/Oshi/WebHome#AnchorSoftDown)
2. After starting the VM, run the following commands as user `user` (**only if it's the first time you run this software**):
    ```
    cd workspace/
    
    git clone https://github.com/ilDuna/tpin-2015-project.git
    
    cd tpin-2015-project/
    
    cp *.py ../ryu/ryu/app/
    
    cd ../ryu
    
    sudo python ./setup.py install
    
    sudo apt-get install rrdtool librrds-perl librrd-dev
    
    sudo pip install rrdtool
    ```
3. Run mininet with the specified topology:
    ```
    cd workspace/Dreamer-Mininet-Extensions
    
    sudo ./mininet_deployer.py --topology topo/topo_vll_pw.json
    ```
4. Open terminal for a controller in the topology:
    ```mininet> xterm ctr8```
5. Start RYU Manager (in the controller terminal):
    ```
    cd /home/user/workspace/tpin-2015-project
    
    ryu-manager --observe-links traffic_monitor.py ofctl_rest.py rrdmanager.py
    
    ```

## Test REST interface
You can call each REST endpoint implemented in ofctl_rest.py. The server runs on port 8080.

### Example
```
curl http://10.0.4.1:8080/stats/switches
```
*Note that 10.0.4.1 is the IP of the machine where ryu-manager is running.*

