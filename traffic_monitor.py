from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.base import app_manager
from rrdmanager import RRDManager
import os.path
import json
import time

# Stats request time interval.
REQUEST_INTERVAL = 10
#EthType used to collect flow stats, only flows of this eth type will be considerd.
FLOW_ETH_TYPE = "0x0800"


class SimpleMonitor(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        #list of devices to monitor
        self.datapaths = {}
        #monitor thread, peridically issues stats requests
        self.monitor_thread = hub.spawn(self._monitor)
        #list of dicts indexed by device, each dict indexed by port number contains the port name
        self.namePnumber = {}
        #list of rrd database managers, one for each device. Each manager handles an rrd file and tracks all PORT tx stats for that device.
        self.rrdManagerstx = {}
        #list of rrd database managers, one for each device. Each manager handles an rrd file and tracks all PORT rx stats for that device.
        self.rrdManagersrx = {}
        #list of rrd database managers, one for each device. Each manager handles an rrd file and tracks all FLOW tx stats for that device.
        self.flowrrdManagerstx = {}
        #list of rrd database managers, one for each device. Each manager handles an rrd file and tracks all FLOW rx stats for that device.
        self.flowrrdManagersrx = {}

    #monitor thread, issues stats requests every REQUEST_INTERVAL period.
    def _monitor(self):
        while True:
            print
            "sending stats request"
            #for each known device
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(REQUEST_INTERVAL)

    def _request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        cookie = cookie_mask = 0
        #Flow stats request, no math parameter is provided meaning all flows are retrieved.
        req = parser.OFPFlowStatsRequest(datapath, 0,
                                         ofproto.OFPTT_ALL,
                                         ofproto.OFPP_ANY, ofproto.OFPG_ANY, cookie, cookie_mask)
        datapath.send_msg(req)
        #Port stats request, requests all stats for the ports of the provided device
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    #This function traslates port numbers in port names.
    def getPname(self, datapathid, PNumber):
        try:
            return (self.namePnumber[datapathid])[PNumber]
        except:
            return "Null"

    #handler for SwitchDiscovery/SwitchDeath events.
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        ofp_parser = datapath.ofproto_parser
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.warning('register datapath: %016x', datapath.id)
                #Every time a switch discovery event is received the new switch is added to the list of know switches which will be monitored.
                self.datapaths[datapath.id] = datapath
                #For every new switch a port descriptor request is issued, this request is necessary to retrieve the PortName/PortNumber association
                req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
                datapath.send_msg(req)
        #Every time a switch dies
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.warning('unregister datapath: %016x', datapath.id)
                #The switch is deleted from the list of known devices
                del self.datapaths[datapath.id]
                #All managers are removed
                del self.rrdManagerstx[datapath.id]
                del self.rrdManagersrx[datapath.id]
                del self.flowrrdManagerstx[datapath.id]
                del self.flowrrdManagersrx[datapath.id]
                #Port Name / Port Number associations are removed
                del self.namePnumber[datapath.id]

    #Port Descriptor event, used to enstablish port name / port number association.
    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        ports = {}
        for p in ev.msg.body:
            #Received association is added to the list
            ports[p.port_no] = p.name
        self.namePnumber[ev.msg.datapath.id] = ports


    #Flow stats reception event.
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        #list of datasources in the rrd rx file for the switch associated with the reply, each datasource corresponding to a port.
        rxdatasources = []
        #list of datasources in the rrd tx file for the switch associated with the reply, each datasource corresponding to a port.
        txdatasources = []
        #list of rx data for each datasource, association of datasources and corresponding data is mantained by keeping the same order of elements.
        rxdata = []
        #list of tx data for each datasource, association of datasources and corresponding data is mantained by keeping the same order of elements.
        txdata = []

        for stat in body:
            datapathidstr = str(ev.msg.datapath.id)

            #dict indexed by datapathidstr cotaining port names for the switch this is necessary for the construction of the rrd database.
            #datapathidstr is necessary since a single file supports multiple switches however this is not adviced
            #since the update of stats for switches in the same file would require 1 second sleep time (rrd constraint)
            device = {}

            #If the switch is sending a flow reply for the first time
            if not (datapathidstr in self.flowrrdManagersrx.keys()):
                #for the switch associated with the reply a list of port names is constructed and added to device dict under key datapathidstr
                device[datapathidstr] = []
                for i in self.namePnumber[ev.msg.datapath.id].keys():
                    device[datapathidstr].append(self.getPname(ev.msg.datapath.id, i))

                #If the switch is repling for the first time its manager for rx flows is constructed. File name is as follows: flow[SwitchId]rx.rrd
                print
                "creating managers for flow received data " + "file: " + datapathidstr + "rx"
                rrdman = RRDManager("flow" + datapathidstr + "rx.rrd", device, [FLOW_ETH_TYPE])
                self.flowrrdManagersrx[datapathidstr] = rrdman

                #If the switch is repling for the first time its manager for tx flows is constructed. File name is as follows: flow[SwitchId]tx.rrd
                print
                "creating managers for flow transmitted data " + "file: " + datapathidstr + "tx"
                rrdman = RRDManager("flow" + datapathidstr + "tx.rrd", device, [FLOW_ETH_TYPE])
                self.flowrrdManagerstx[datapathidstr] = rrdman
                #Created manager may not be used instantly
                time.sleep(1)
            #Manager for the rx flow associated with the switch is retrieved
            rrdmanagerrx = self.flowrrdManagersrx[datapathidstr]
            #Manager for the tx flow associated with the switch is retrieved
            rrdmanagertx = self.flowrrdManagerstx[datapathidstr]


            #If the match for the replied switch contains input EthType and InPort then those two information are collected
            InEthType = 0
            InPortNumber = 0
            for OXMTlv in stat.match.fields:
                if type(OXMTlv).__name__ == 'MTEthType':
                    InEthType = OXMTlv.value
                if type(OXMTlv).__name__ == 'MTInPort':
                    InPortNumber = OXMTlv.value

            #Port name is retrieved from port number
            inPortName = self.getPname(ev.msg.datapath.id, InPortNumber)

            #Output EthType is initialized the same as InEthType in case no OF action will change it later.
            OutEthType = InEthType

            for OFPInstructionActions in stat.instructions:
                #discard all GotoTable instructions
                if type(OFPInstructionActions).__name__ == "OFPInstructionGotoTable":
                    continue

                #Push or Pop Mpls actions are searched in the action list to determine the eventually modified EthType of the out packet.
                for action in OFPInstructionActions.actions:
                    if type(action).__name__ == "OFPActionPushMpls" or type(action).__name__ == "OFPActionPopMpls":
                        OutEthType = action.ethertype

                for action in OFPInstructionActions.actions:
                    #This ignores all the actions which are not OutputActions, a flow is defined by inport and outport.
                    #For a certain inPort all the OutPort (each one defined in a ActionOutput) define a new flow.
                    if type(action).__name__ != "OFPActionOutput":
                        continue
                    #In a ActionOutput the type field is the EthType, in case this is 0 the the original input EthType is kept.
                    if action.type != 0: OutEthType = action.type
                    #The output port is retrieved.
                    outPortNumber = action.port
                    outPortName = self.getPname(ev.msg.datapath.id, outPortNumber)
                    #If InPort or OutPort are not defined at this point the flow is ignored (which means aggregated flow).
                    if InPortNumber == 0 or outPortNumber == 0: continue
                    #If the OutEthType is  FLOW_ETH_TYPE the flow is considered as output flow, the datasource for outPortName is added to txdatasources.
                    #The corresponding data entry is added to txdata.
                    if OutEthType == int(FLOW_ETH_TYPE, 16):
                        txdata.append(stat.packet_count)
                        txdatasources.append(
                            rrdmanagerrx.constructDataSource(datapathidstr, outPortName, FLOW_ETH_TYPE))
                    #If the InEthType is  FLOW_ETH_TYPE the flow is considered as input flow, the datasource for inPortName is added to rxdatasources.
                    #The corresponding data entry is added to rxdata.
                    if InEthType == int(FLOW_ETH_TYPE, 16):
                        rxdata.append(stat.packet_count)
                        rxdatasources.append(rrdmanagertx.constructDataSource(datapathidstr, inPortName, FLOW_ETH_TYPE))
        #insert operation are performed.
        if rxdatasources:
            print
            "updating rx flow for " + datapathidstr + " port: " + str(rxdatasources) + " data: " + str(
                rxdata) + " file: " + rrdmanagerrx.filename
            print
            "\n"
            try:
                rrdmanagerrx.update(rxdatasources, rxdata)
            except:
                time.sleep(1)
                rrdmanagerrx.update(rxdatasources, rxdata)

        if txdatasources:
            print
            "updating tx flow for " + datapathidstr + " port: " + str(txdatasources) + " data: " + str(
                txdata) + " file: " + rrdmanagertx.filename
            print
            "\n"
            try:
                rrdmanagertx.update(txdatasources, txdata)
            except:
                time.sleep(1)
                rrdmanagertx.update(txdatasources, txdata)


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):

        body = ev.msg.body
        #list of datasources in the rrd rx file for the switch associated with the reply, each datasource corresponding to a port.
        rxdatasources = []
        #list of datasources in the rrd tx file for the switch associated with the reply, each datasource corresponding to a port.
        txdatasources = []
        #list of rx data for each datasource, association of datasources and corresponding data is mantained by keeping the same order of elements.
        rxdata = []
        #list of tx data for each datasource, association of datasources and corresponding data is mantained by keeping the same order of elements.
        txdata = []

        datapathidstr = str(ev.msg.datapath.id)
        for stat in sorted(body, key=attrgetter('port_no')):

            portName = self.getPname(ev.msg.datapath.id, stat.port_no)

            #dict indexed by datapathidstr cotaining port names for the switch this is necessary for the construction of the rrd database.
            #datapathidstr is necessary since a single file supports multiple switches however this is not adviced
            #since the update of stats for switches in the same file would require 1 second sleep time (rrd constraint)
            device = {}

            #If the switch is sending a port reply for the first time
            if not (datapathidstr in self.rrdManagersrx.keys()):
                #for the switch associated with the reply a list of port names is constructed and added to device dict under key datapathidstr
                device[datapathidstr] = []
                for i in self.namePnumber[ev.msg.datapath.id].keys():
                    device[datapathidstr].append(self.getPname(ev.msg.datapath.id, i))

                #If the switch is repling for the first time its manager for rx ports is constructed. File name is as follows: [SwitchId]rx.rrd
                print
                "creating managers for agggregate received data " + "file: " + datapathidstr + "rx"
                rrdman = RRDManager(datapathidstr + "rx.rrd", device, ["0000"])
                self.rrdManagersrx[datapathidstr] = rrdman

                #If the switch is repling for the first time its manager for rx ports is constructed. File name is as follows: [SwitchId]rx.rrd
                print
                "creating managers for agggregate transmitted data " + "file: " + datapathidstr + "tx"
                rrdman = RRDManager(datapathidstr + "tx.rrd", device, ["0000"])
                self.rrdManagerstx[datapathidstr] = rrdman
                time.sleep(1)

            #rx and tx manager are retrieved for the following insertion operation
            rrdmanagerrx = self.rrdManagersrx[datapathidstr]
            rrdmanagertx = self.rrdManagerstx[datapathidstr]

            #portName is appendend to the list of datasources with new data for received packets.
            rxdatasources.append(rrdmanagerrx.constructDataSource(datapathidstr, portName, "0000"))
            #the data corresponding to portName is appended to rxdata (hence maintaining the same order).
            rxdata.append(stat.rx_packets);

            #portName is appendend to the list of datasources with new data for transmitted packets reported by datapathidstr switch.
            txdatasources.append(rrdmanagertx.constructDataSource(datapathidstr, portName, "0000"))
            #the data corresponding to portName is appended to txdata (hence maintaining the same order)
            txdata.append(stat.tx_packets);

        #the data is finally inserted in the database
        print
        "updating tx data for " + datapathidstr + " ds: " + str(txdatasources) + " data: " + str(
            txdata) + " file: " + rrdmanagertx.filename
        print
        "\n"
        try:
            rrdmanagertx.update(txdatasources, txdata)
        except:
            time.sleep(1)
            rrdmanagertx.update(txdatasources, txdata)
            pass

        print
        "updating rx data for " + datapathidstr + " ds: " + str(rxdatasources) + " data: " + str(
            rxdata) + " file: " + rrdmanagerrx.filename
        print
        "\n"
        try:
            rrdmanagerrx.update(rxdatasources, rxdata)
        except:
            time.sleep(1)
            rrdmanagerrx.update(rxdatasources, rxdata)
            pass