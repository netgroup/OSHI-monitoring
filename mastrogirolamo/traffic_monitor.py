import re
from operator import attrgetter

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.base import app_manager
from debug_utils import MYPRINT_INFO, MYPRINT_DEBUG, MYPRINT_ALERT, myPrint
from switch_stats import SwitchStats
from traffic_monitor_params import *


class SimpleMonitor(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.stats = {}
        self.monitor_thread = hub.spawn(self._monitor)

    def _monitor(self):
        myPrint(MYPRINT_INFO, "THREAD", "Started monitor thread.")
        while True:
            myPrint(MYPRINT_INFO, "THREAD", "sending PORT stats requests", new_line=False)
            for ss in self.stats.values():
                self._request_stats(ss.dp)
            hub.sleep(REQUEST_INTERVAL)

    def _request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        cookie = cookie_mask = 0
        req = parser.OFPFlowStatsRequest(datapath, 0,
                                         ofproto.OFPTT_ALL,
                                         ofproto.OFPP_ANY, ofproto.OFPG_ANY, cookie, cookie_mask)
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        ofp_parser = datapath.ofproto_parser
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.stats:
                myPrint(MYPRINT_INFO, "STATECHANGE", 'register datapath: %016x' % datapath.id)
                self.stats[datapath.id] = SwitchStats(datapath)
                req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
                datapath.send_msg(req)
                ofproto = datapath.ofproto
                parser = datapath.ofproto_parser
                cookie = cookie_mask = 0
                req = parser.OFPFlowStatsRequest(datapath, 0,
                                                 ofproto.OFPTT_ALL,
                                                 ofproto.OFPP_ANY, ofproto.OFPG_ANY, cookie, cookie_mask)
                datapath.send_msg(req)
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.stats:
                myPrint(MYPRINT_INFO, "STATECHANGE", 'unregister datapath: %016x' % datapath.id)
                del self.stats[datapath.id]

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        ss = self.stats[ev.msg.datapath.id]
        for p in sorted(ev.msg.body, key=attrgetter('port_no')):
            if int(p.port_no) > 1000:
                continue
            ss.addPort(p.port_no)
            ss.setPortName(p.port_no, p.name)
            myPrint(MYPRINT_INFO, "PORTDESC", '%016x add port: %d.%s' % (ev.msg.datapath.id, p.port_no, p.name))

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        myPrint(MYPRINT_DEBUG, "FLOWSTATS", "FLOW stats received from %016x" % ev.msg.datapath.id)
        ss = self.stats[ev.msg.datapath.id]
        body = ev.msg.body
        for flow_stat in body:
            try:
                in_port = flow_stat.match.fields[0].value
                out_port = flow_stat.instructions[0].actions[0].port
                out_port_name = ss.getPortName(out_port)
                if len(re.findall(r"vi+[0-9]", out_port_name, flags=0)) == 1:
                    ss.setIPPartner(in_port, out_port)
                    ss.setIPPartner(out_port, in_port)
            except Exception as e:
                myPrint(MYPRINT_ALERT, "FLOWSTATS", str(e))
                continue

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        ss = self.stats[ev.msg.datapath.id]
        f_b = open('./port_stats/bytes_stats/dp_' + str(ev.msg.datapath.id), 'w+')
        f_p = open('./port_stats/packets_stats/dp_' + str(ev.msg.datapath.id), 'w+')
        for stat in sorted(body, key=attrgetter('port_no')):
            if int(stat.port_no) > 1000:
                continue
            ss.setRxBytes(stat.port_no, stat.rx_bytes)
            ss.setTxBytes(stat.port_no, stat.tx_bytes)
            ss.setRxPackets(stat.port_no, stat.rx_packets)
            ss.setTxPackets(stat.port_no, stat.tx_packets)
        ss.updateSDNStats()
        f_b.write(ss.getBytesStats())
        f_p.write(ss.getPacketsStats())
