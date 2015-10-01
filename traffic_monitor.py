import os
import re
from operator import attrgetter

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.base import app_manager
import config
from rrd_data_source import RRDDataSource
from rrdmanager import RRDManager
from switch_stats import SwitchStats
import logging

log = logging.getLogger('oshi.monitoring.traffic_monitor')
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(os.path.join(config.TRAFFIC_MONITOR_LOG_PATH, "traffic_monitor.log"))
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
log.addHandler(ch)
log.addHandler(fh)


class SimpleMonitor(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.switch_stats = {}
        self.rrd_managers = {}
        self.monitor_thread = hub.spawn(self._monitor)

    def _monitor(self):
        log.info("Started monitor thread.")
        while True:
            log.debug("Sending PORT stats requests")
            for switch_stat in self.switch_stats.values():
                data_path = switch_stat.data_path
                open_flow_protocol = data_path.ofproto
                parser = data_path.ofproto_parser
                req = parser.OFPPortStatsRequest(data_path, 0, open_flow_protocol.OFPP_ANY)
                log.debug("Sending PORT stats request: %s", str(req))
                data_path.send_msg(req)
            hub.sleep(config.REQUEST_INTERVAL)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        ofp_parser = datapath.ofproto_parser
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.switch_stats:
                log.info("Received MAIN_DISPATCHER event. Register datapath: %s", datapath.id)
                self.switch_stats[datapath.id] = SwitchStats(datapath)
                req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
                datapath.send_msg(req)
                open_flow_protocol = datapath.ofproto
                parser = datapath.ofproto_parser
                cookie = cookie_mask = 0
                req = parser.OFPFlowStatsRequest(datapath, 0,
                                                 open_flow_protocol.OFPTT_ALL,
                                                 open_flow_protocol.OFPP_ANY, open_flow_protocol.OFPG_ANY, cookie,
                                                 cookie_mask)
                datapath.send_msg(req)
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.switch_stats:
                log.info("Received DEAD_DISPATCHER event. De-register datapath: %s", datapath.id)
                del self.switch_stats[datapath.id]

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        data_path_id = ev.msg.datapath.id
        ss = self.switch_stats[data_path_id]
        """ :type : SwitchStats """
        for p in sorted(ev.msg.body, key=attrgetter('port_no')):
            if int(p.port_no) > 1000:
                continue
            ss.add_port(p.port_no)
            ss.set_port_name(p.port_no, p.name)
            log.info("Added port (%s, %s) to %s ", p.port_no, p.name, ev.msg.datapath.id)
            # TODO: init RRD data sources according to stats defined in SwitchStats

            log.info("Creating RRD Manager for %s ", ev.msg.datapath.id)
            # TODO: create an RRD manager with the defined RRD data sources for port

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        log.debug("FLOW stats received from %s", ev.msg.datapath.id)
        ss = self.switch_stats[ev.msg.datapath.id]
        body = ev.msg.body
        for flow_stat in body:
            try:
                in_port = flow_stat.match.fields[0].value
                out_port = flow_stat.instructions[0].actions[0].port
                out_port_name = ss.getPortName(out_port)
                if len(re.findall(r"vi+[0-9]", out_port_name, flags=0)) == 1:
                    ss.set_ip_partner_port_number(in_port, out_port)
                    ss.set_ip_partner_port_number(out_port, in_port)
            except Exception as e:
                log.error("Error while handling stat reply: %s", str(e))
                continue

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        switch_stats = self.switch_stats[ev.msg.datapath.id]
        """ :type : SwitchStats """
        for stat in sorted(body, key=attrgetter('port_no')):
            if int(stat.port_no) > 1000:
                continue
            switch_stats.set_rx_bytes(stat.port_no, stat.rx_bytes)
            switch_stats.set_tx_bytes(stat.port_no, stat.tx_bytes)
            switch_stats.set_rx_packets(stat.port_no, stat.rx_packets)
            switch_stats.set_tx_packets(stat.port_no, stat.tx_packets)
        switch_stats.update_sdn_stats()
        # save stats
        # f_b.write(ss.getBytesStats())
        # f_p.write(ss.getPacketsStats())
