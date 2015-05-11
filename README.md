# TPIN: Project (2015)
## Setup instructions

1. Download the VirtualBox VM from [Uniroma2 Netgroup](http://netgroup.uniroma2.it/twiki/bin/view/Oshi/WebHome#AnchorSoftDown)
2. After starting the VM, run the following commands as user `user` (**only if it's the first time you run this software**):
    ```
    1. cd workspace/
    2. git clone https://github.com/ilDuna/tpin-2015-project.git
    3. cd tpin-2015-project/
    4. cp *.py ../ryu/ryu/app/
    5. cd ../ryu
    6. sudo python ./setup.py install
    7. cd ryu/app
    8. sudo apt-get install rrdtool librrds-perl librrd-dev
    9. sudo pip install rrdtool
    ```
3. Run mininet with the specified topology:
    ```
    1. cd workspace/Dreamer-Mininet-Extensions
    2. sudo ./mininet_deployer.py --topology topo/topo_vll_pw.json
    ```
4. Open terminal for a controller in the topology: `mininet> xterm ctr8`
5. Start RYU Manager (in the controller terminal): `ryu-manager --observe-links traffic_monitor.py ofct_rest.py rrdmanager.py`
