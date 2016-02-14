import json
from collections import defaultdict
import re
from operator import attrgetter
import time
import logging

import datetime
import requests
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.base import app_manager
import config
from rrd_data_source import RRDDataSource
from rrdmanager import RRDManager
from switch_stats import SwitchStats
import switch_stats

log = logging.getLogger('oshi_monitoring')
logstash_log = logging.getLogger('oshi_monitoring_logstash')


class SimpleMonitor(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.switch_stats = {}
        self.rrd_managers = defaultdict()
        self.monitor_thread = hub.spawn(self._monitor)
        self.last_update_times = {}
        self.rrd_updates_since_last_log = {}

    def _monitor(self):
        log.info("Started monitoring with REQUEST_INTERVAL %s seconds and RRD_STEP %s seconds", config.REQUEST_INTERVAL,
                 config.RRD_STEP)
        log.info("Current output level is %s", config.OUTPUT_LEVEL)
        while True:
            log.debug("Sending PORT stats requests")
            for switch_stat in self.switch_stats.values():
                data_path = switch_stat.data_path
                open_flow_protocol = data_path.ofproto
                parser = data_path.ofproto_parser
                req = parser.OFPPortStatsRequest(data_path, 0, open_flow_protocol.OFPP_ANY)
                log.debug("Sending PORT stats request for data_path: %s", data_path.id)
                data_path.send_msg(req)
            hub.sleep(config.REQUEST_INTERVAL)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        ofp_parser = datapath.ofproto_parser
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.switch_stats:
                log.debug("Received MAIN_DISPATCHER event. Register datapath: %s", datapath.id)
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
            log.debug("Received DEAD_DISPATCHER event.")
            if datapath.id in self.switch_stats:
                log.debug("De-register %s datapath", datapath.id)
                del self.switch_stats[datapath.id]

    @staticmethod
    def _init_rrd_data_sources(port_stat_names, data_source_values=None):
        rrd_data_sources = []
        for port_stat_name in port_stat_names:
            log.debug("Building RRD data source for stat: %s", port_stat_name)
            rrd_data_source = RRDDataSource(port_stat_name, config.RRD_DATA_SOURCE_TYPE,
                                            config.RRD_DATA_SOURCE_HEARTBEAT)
            # add an eventual value to the data source. Useful for rrd updates
            if data_source_values is not None and port_stat_name in data_source_values:
                rrd_data_source.temp_value = data_source_values[port_stat_name]
            rrd_data_sources.append(rrd_data_source)
        return rrd_data_sources

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        log.debug("Received event (EventOFPPortDescStatsReply). Body: %s", str(ev.msg.body))
        log.debug("PORT stats received from %s", ev.msg.datapath.id)
        data_path_id = ev.msg.datapath.id
        device_name = data_path_id
        log.debug("Searching for device name for %s", str(data_path_id))
        # search for device name (PHY ports are named using device-port, while virtual ports are named just viX)
        for p in sorted(ev.msg.body, key=attrgetter('port_no')):
            if '-' in p.name and int(p.port_no) <= 1000:
                device_name = p.name.split('-')[0]
                break
        log.debug("Device name for %s: %s", str(data_path_id), device_name)

        ss = self.switch_stats[data_path_id]
        """ :type : SwitchStats """
        ss.device_name = device_name
        for p in sorted(ev.msg.body, key=attrgetter('port_no')):
            if int(p.port_no) > 1000:
                log.debug("Skipping port. Port number: %s", str(p.port_no))
                continue
            virtual = 'vi' in p.name
            port_name = (device_name + '-' + p.name) if virtual else p.name
            log.debug("Initializing port %s (%s). Virtual: %s", port_name, p.port_no, virtual)
            ss.add_port(p.port_no, virtual, port_name)
            if port_name not in self.rrd_managers:
                log.debug("Initializing RRD data sources for %s", port_name)
                port_stats_names = switch_stats.PORT_STATS
                """ :type : list """
                rrd_data_sources = self._init_rrd_data_sources(port_stats_names)
                log.debug("Initialized RRD data sources for %s", port_name)
                log.debug("Creating RRD Manager for port %s of %s", port_name, device_name)
                self.rrd_managers[port_name] = RRDManager(port_name + '.rrd', rrd_data_sources)
            else:
                log.debug("Skip RRD Manager creation for port %s of %s as it's already available",
                          port_name, data_path_id)
            log.debug("Completed port %s initialization", port_name)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        log.debug("Received event (EventOFPFlowStatsReply). Body: %s", str(ev.msg.body))
        log.debug("FLOW stats received from %s", ev.msg.datapath.id)
        ss = self.switch_stats[ev.msg.datapath.id]
        body = ev.msg.body
        log.debug("Setting IP partners info for %s", ss.device_name)
        for flow_stat in body:
            log.debug("Getting port info from flow stat: %s", str(flow_stat))
            try:
                in_port = flow_stat.match.fields[0].value
                log.debug("Got IN port: %s", str(in_port))
                if long(in_port) > 1000:
                    log.debug("Skipping flow_stat. IN port: %s", str(in_port))
                    continue
                out_port = flow_stat.instructions[0].actions[0].port
                if long(out_port) > 1000:
                    log.debug("Skipping flow_stat. OUT port: %s", str(out_port))
                    continue
                log.debug("Got OUT port: %s", str(out_port))
                out_port_name = ss.get_port_name(out_port)
                if len(re.findall(r"vi+[0-9]", out_port_name, flags=0)) == 1:
                    log.debug("Setting IN/OUT ports for %s, IN port: %s, OUT port: %s", ss.device_name, in_port,
                              out_port)
                    ss.set_ip_partner_port_number(in_port, out_port)
                    ss.set_ip_partner_port_number(out_port, in_port)
            except Exception:
                log.exception("Error while handling stat reply.")
                continue

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        data_path_id = ev.msg.datapath.id
        body = ev.msg.body
        log.debug("Received event (EventOFPPortStatsReply). Body: %s", str(body))
        switch_stat = self.switch_stats[data_path_id]
        """ :type : SwitchStats """
        log.debug("PORT STATS reply for %s. Updating stats...", switch_stat.device_name)
        for port in sorted(body, key=attrgetter('port_no')):
            if int(port.port_no) > 1000:
                log.debug("Skipping port. Port number: %s. Port: %s", str(port.port_no), str(port))
                continue
            log.debug("Updating stats for %s port", switch_stat.get_port_name(port.port_no))
            switch_stat.set_rx_bytes(port.port_no, port.rx_bytes)
            switch_stat.set_tx_bytes(port.port_no, port.tx_bytes)
            switch_stat.set_rx_packets(port.port_no, port.rx_packets)
            switch_stat.set_tx_packets(port.port_no, port.tx_packets)

        # update RRD if necessary
        log.debug("Checking if a RRD update is necessary. Current last update times: %s", str(self.last_update_times))
        log.debug("Last RRD update time for %s: %s",
                  switch_stat.device_name,
                  self.last_update_times[switch_stat.device_name]
                  if switch_stat.device_name in self.last_update_times
                  else "never")
        current_time = time.time()
        if switch_stat.device_name not in self.last_update_times or current_time - self.last_update_times[
                switch_stat.device_name] >= config.RRD_STEP:
            log.debug("Updating RRDs for %s", switch_stat.device_name)
            port_numbers = switch_stat.ports.keys()
            switch_stat.update_sdn_stats()
            for port_number in port_numbers:
                log.debug("Updating port %s", switch_stat.get_port_name(port_number))
                current_stats = switch_stat.get_current_values(port_number)
                log.debug("Current stats for port %s : %s", switch_stat.get_port_name(port_number),
                          str(current_stats))
                rrd_data_sources_to_update = []
                log.debug("Building RRD data source for port %s and stats: %s", switch_stat.get_port_name(port_number),
                          str(current_stats))
                for stat_name in current_stats:
                    log.debug("Building RRD data source to update %s", stat_name)
                    # use RRDDataSource object as DTO, so we need only data source name and data source current value
                    rrd_data_sources_to_update.append(RRDDataSource(stat_name, None, None, current_stats[stat_name]))
                log.debug("Completed RRD data sources initialization to update %s",
                          switch_stat.get_port_name(port_number))
                if switch_stat.get_port_name(port_number) in self.rrd_managers:
                    log.debug("Found RRD manager for %s.", switch_stat.get_port_name(port_number))
                    rrd_manager = self.rrd_managers[switch_stat.get_port_name(port_number)]
                    """ :type : RRDManager """
                    rrd_manager.update(rrd_data_sources_to_update, current_time)
                    if switch_stat.device_name not in self.rrd_updates_since_last_log:
                        log.debug("Initializing last updates since last log for %s", switch_stat.device_name)
                        self.rrd_updates_since_last_log[switch_stat.device_name] = set()
                    self.rrd_updates_since_last_log[switch_stat.device_name].add(
                        switch_stat.device_name + ":" + switch_stat.get_port_name(port_number))

                    # Build the dict to send to elasticsearch
                    update_data = {'device_name': switch_stat.device_name,
                                   'port_number': port_number,
                                   'port_name': switch_stat.get_port_name(port_number),
                                   'current_values': switch_stat.get_current_values(port_number),
                                   'timestamp': datetime.datetime.fromtimestamp(time.time()).isoformat()
                                   }
                    log.debug("Data to send to Elasticsearch: %s", update_data)

                    log.info("Sending data to Elasticsearch @ %s", config.ELASTIC_SEARCH_URL)
                    r = None
                    try:
                        r = requests.post(config.ELASTIC_SEARCH_URL, json=update_data)
                        log.info("Request sent to Elasticsearch. Response code: %s", r.status_code)
                    except requests.ConnectionError:
                        log.warn("Connection error while sending data to Elasticsearch.")

                    # if HTTP connection is not available, write on file to use logstash file handler
                    if r is None or r.status_code != 200:
                        log.warn("Logstash is not available via HTTP. Falling back to file output.")
                        logstash_line = json.dumps(update_data)
                        log.info("Writing on results file for Logstash in %s. Data: %s", config.LOGSTASH_OUTPUT_PATH,
                                 logstash_line)
                        logstash_log.info(logstash_line)
                else:
                    log.debug("Cannot find RRD manager for %s. Available managers: %s",
                              switch_stat.get_port_name(port_number),
                              str(self.rrd_managers))
            self.last_update_times[switch_stat.device_name] = time.time()
            log.debug("Update last update time for %s: %s",
                      switch_stat.device_name, str(self.last_update_times[switch_stat.device_name]))

            if config.OUTPUT_LEVEL == config.SUMMARY_OUTPUT or config.OUTPUT_LEVEL == config.DETAILED_OUTPUT:
                log.info("Updated %d RRDs since last log for %s: %s",
                         len(self.rrd_updates_since_last_log[switch_stat.device_name]), switch_stat.device_name,
                         self.rrd_updates_since_last_log[switch_stat.device_name])

            if config.OUTPUT_LEVEL == config.DETAILED_OUTPUT:
                log.info("Current values for %s (IP):", switch_stat.device_name)
                for port_number in port_numbers:
                    log.info("Port %s (IP): %s:%d, %s:%d, %s:%d, %s:%d", switch_stat.get_port_name(port_number),
                             switch_stats.RX_BYTES, switch_stat.get_rx_bytes(port_number),
                             switch_stats.TX_BYTES, switch_stat.get_tx_bytes(port_number),
                             switch_stats.RX_PACKETS, switch_stat.get_rx_packets(port_number),
                             switch_stats.TX_PACKETS, switch_stat.get_tx_packets(port_number))
                    log.info("Port %s (SDN): %s:%d, %s:%d, %s:%d, %s:%d", switch_stat.get_port_name(port_number),
                             switch_stats.SDN_RX_BYTES, switch_stat.get_sdn_rx_bytes(port_number),
                             switch_stats.SDN_TX_BYTES, switch_stat.get_sdn_tx_bytes(port_number),
                             switch_stats.SDN_RX_PACKETS, switch_stat.get_sdn_rx_packets(port_number),
                             switch_stats.SDN_TX_PACKETS, switch_stat.get_sdn_tx_packets(port_number))
            self.rrd_updates_since_last_log[switch_stat.device_name].clear()
        else:
            log.debug("Queueing up RRD update. Last update time: %s", self.last_update_times[switch_stat.device_name])
