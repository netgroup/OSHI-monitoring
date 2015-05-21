import logging

import json
import rrdtool
import sys

import os
from os import path
import time

from webob import Response

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.lib import ofctl_v1_0
from ryu.lib import ofctl_v1_2
from ryu.lib import ofctl_v1_3
from ryu.app.wsgi import ControllerBase, WSGIApplication


LOG = logging.getLogger('ryu.app.ofctl_rest')

# REST API
#

# Retrieve the switch stats
#
# get the list of all switches
# GET /stats/switches
#
# get the desc stats of the switch
# GET /stats/desc/<dpid>
#
# get flows stats of the switch
# GET /stats/flow/<dpid>
#
# get flows stats of the switch filtered by the fields
# POST /stats/flow/<dpid>
#
# get ports stats of the switch
# GET /stats/port/<dpid>
#
# get meter features stats of the switch
# GET /stats/meterfeatures/<dpid>
#
# get meter config stats of the switch
# GET /stats/meterconfig/<dpid>
#
# get meters stats of the switch
# GET /stats/meter/<dpid>
#
# get group features stats of the switch
# GET /stats/groupfeatures/<dpid>
#
# get groups desc stats of the switch
# GET /stats/groupdesc/<dpid>
#
# get groups stats of the switch
# GET /stats/group/<dpid>
#
# get ports description of the switch
# GET /stats/portdesc/<dpid>

# Update the switch stats
#
# add a flow entry
# POST /stats/flowentry/add
#
# modify all matching flow entries
# POST /stats/flowentry/modify
#
# modify flow entry strictly matching wildcards and priority
# POST /stats/flowentry/modify_strict
#
# delete all matching flow entries
# POST /stats/flowentry/delete
#
# delete flow entry strictly matching wildcards and priority
# POST /stats/flowentry/delete_strict
#
# delete all flow entries of the switch
# DELETE /stats/flowentry/clear/<dpid>
#
# add a meter entry
# POST /stats/meterentry/add
#
# modify a meter entry
# POST /stats/meterentry/modify
#
# delete a meter entry
# POST /stats/meterentry/delete
#
# add a group entry
# POST /stats/groupentry/add
#
# modify a group entry
# POST /stats/groupentry/modify
#
# delete a group entry
# POST /stats/groupentry/delete
#
# modify behavior of the physical port
# POST /stats/portdesc/modify
#
# send a experimeter message
# POST /stats/experimenter/<dpid>
#
# request list of rrd databases
# GET /stats/listdb
#
# fetch data of requested database "filename", between "start" and "end" time expressed in unix time.
# GET stats/rrdview/{filename}/{start}/{end}
#
# Get an rrd graph
# GET stats/rrdgraph


class StatsController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(StatsController, self).__init__(req, link, data, **config)
        self.dpset = data['dpset']
        self.waiters = data['waiters']

    def get_dpids(self, req, **_kwargs):
        dps = self.dpset.dps.keys()
        body = json.dumps(dps)
        return Response(content_type='application/json', body=body)

    def get_desc_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            desc = ofctl_v1_0.get_desc_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            desc = ofctl_v1_2.get_desc_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            desc = ofctl_v1_3.get_desc_stats(dp, self.waiters)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(desc)
        return Response(content_type='application/json', body=body)

    def get_flow_stats(self, req, dpid, **_kwargs):
        if req.body == '':
            flow = {}
        else:
            try:
                flow = eval(req.body)
            except SyntaxError:
                LOG.debug('invalid syntax %s', req.body)
                return Response(status=400)

        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flows = ofctl_v1_0.get_flow_stats(dp, self.waiters, flow)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flows = ofctl_v1_2.get_flow_stats(dp, self.waiters, flow)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            flows = ofctl_v1_3.get_flow_stats(dp, self.waiters, flow)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(flows)
        return Response(content_type='application/json', body=body)

    def get_port_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ports = ofctl_v1_0.get_port_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ports = ofctl_v1_2.get_port_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ports = ofctl_v1_3.get_port_stats(dp, self.waiters)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(ports)
        return Response(content_type='application/json', body=body)

    def get_meter_features(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            meters = ofctl_v1_3.get_meter_features(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                        dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_meter_config(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            meters = ofctl_v1_3.get_meter_config(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                        dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_meter_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            meters = ofctl_v1_3.get_meter_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                        dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_group_features(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_group_features(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_group_features(dp, self.waiters)
        elif do.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_group_desc(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_group_desc(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_group_desc(dp, self.waiters)
        elif do.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_group_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_group_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_group_stats(dp, self.waiters)
        elif do.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_port_desc(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            groups = ofctl_v1_0.get_port_desc(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_port_desc(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_port_desc(dp, self.waiters)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def mod_flow_entry(self, req, cmd, **_kwargs):
        try:
            flow = eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = flow.get('dpid')
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if cmd == 'add':
            cmd = dp.ofproto.OFPFC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPFC_MODIFY
        elif cmd == 'modify_strict':
            cmd = dp.ofproto.OFPFC_MODIFY_STRICT
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPFC_DELETE
        elif cmd == 'delete_strict':
            cmd = dp.ofproto.OFPFC_DELETE_STRICT
        else:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ofctl_v1_0.mod_flow_entry(dp, flow, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_flow_entry(dp, flow, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_flow_entry(dp, flow, cmd)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def delete_flow_entry(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ofctl_v1_0.delete_flow_entry(dp)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_flow_entry(dp, {}, dp.ofproto.OFPFC_DELETE)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_flow_entry(dp, {}, dp.ofproto.OFPFC_DELETE)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def mod_meter_entry(self, req, cmd, **_kwargs):
        try:
            flow = eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = flow.get('dpid')
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if cmd == 'add':
            cmd = dp.ofproto.OFPMC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPMC_MODIFY
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPMC_DELETE
        else:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_meter_entry(dp, flow, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                        dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def mod_group_entry(self, req, cmd, **_kwargs):
        try:
            group = eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = group.get('dpid')
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)

        if cmd == 'add':
            cmd = dp.ofproto.OFPGC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPGC_MODIFY
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPGC_DELETE
        else:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_group_entry(dp, group, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_group_entry(dp, group, cmd)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def mod_port_behavior(self, req, cmd, **_kwargs):
        try:
            port_config = eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = port_config.get('dpid')

        port_no = int(port_config.get('port_no', 0))
        port_info = self.dpset.port_state[int(dpid)].get(port_no)

        if 'hw_addr' not in port_config:
            if port_info is not None:
                port_config['hw_addr'] = port_info.hw_addr
            else:
                return Response(status=404)

        if 'advertise' not in port_config:
            if port_info is not None:
                port_config['advertise'] = port_info.advertised
            else:
                return Response(status=404)

        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if cmd != 'modify':
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ofctl_v1_0.mod_port_behavior(dp, port_config)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_port_behavior(dp, port_config)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_port_behavior(dp, port_config)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

    def send_experimenter(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        try:
            exp = eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.send_experimenter(dp, exp)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.send_experimenter(dp, exp)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    ''' 
    Chiamata REST che recupera i dati da un Database RR.
    L'output si trova nel 'body' della risposta. Va interpretato come segue:
        - La prima riga rappresenta il vettore contenente i parametri di (start time, end time, step)
        - La seconda riga contiene i nomi dei datasource all'interno del Database
        - La terza riga e' il vettore contenente le associazioni (valore, tempo)

    Tali valori sono calcolati eseguendo le medie nei vari intervalli di tempo e sulla base dei campioni raccolti.

    I parametri da passare alla chiamata REST sono i seguenti tre:
        1) 'filename' : il nome del file in cui e' contenuto il Database
        2) 'start'    : il tempo di inizio, espresso in secondi dal 1 Gennaio 1970 (come da standard UNIX),
            dell'osservazione
        3) 'end'      : il tempo di fine, espresso in secondi dal 1 Gennaio 1970 (come da standard UNIX),
            dell'osservazione

    Qualora uno dei tempi non fosse specificato, allora la chiamata prenderebbe in automatico il valore 'N' che sta per
    'NOW' (ovvero il tempo corrente).
    '''
    def rrdviewer(self, req, **_kwargs):
        filename = _kwargs.get('filename', 'empty')
        start_time = _kwargs.get('start', 'N')
        end_time = _kwargs.get('end', 'N')
        body = ''

        try:
            data = rrdtool.fetch(str(filename), 'AVERAGE', '--start', str(start_time), '--end', str(end_time))

            for temp in data:
                body += str(temp) + '\n'
        except Exception as e:
            body = str(e)
            pass

        body += '\n'

        return Response(content_type='application/json', body=body)

    def get_rrdgraph(self, **_kwargs):
        # Graph config
        start_time = _kwargs.get('start', '-86400')
        end_time = _kwargs.get('end', 'now')
        width = _kwargs.get('width', '785')
        height = _kwargs.get('height', '120')
        color = _kwargs.get('color', '0000FF')
        switch_id = _kwargs.get('switch_id', '')
        traffic_direction = _kwargs.get('direction', 'rx')  # So far this can be only be either rx or tx
        protocol = _kwargs.get('protocol', '0000')  # This is not used now
        data_source_name = _kwargs.get('data_source', '')

        LOG.debug("start_time:{0}".format(start_time))
        LOG.debug("end_time:{0}".format(end_time))
        LOG.debug("width:{0}".format(width))
        LOG.debug("height:{0}".format(height))
        LOG.debug("color:{0}".format(color))
        LOG.debug("switch_id:{0}".format(switch_id))
        LOG.debug("traffic_direction:{0}".format(traffic_direction))
        LOG.debug("protocol:{0}".format(protocol))
        LOG.debug("data_source_name:{0}".format(data_source_name))

        # check for validity
        if len(switch_id) == 0:
            return Response(status=404, body="switch id empty")

        if len(data_source_name) == 0:
            return Response(status=404, body="data_source_name id empty")

        # The file naming convention used in this project states: switchidtraffic_direction.rrd
        rrd_input = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(switch_id + traffic_direction + ".rrd")))
        LOG.debug("RRD input file:{}".format(rrd_input))
        if path.isfile(rrd_input) is not True:
            return Response(status=404, body="rrd_input id empty")

        output_file = '/tmp/rrd_graph_{0}.png'.format(int(time.time() * 1000))
        LOG.debug("Graph output file:{}".format(output_file))

        data_definition = "DEF:vname={0}:{1}:AVERAGE LINE1:vname#{2}:{3}".format(rrd_input, data_source_name, color,
                                                                                 data_source_name)
        LOG.debug("data_definition:{}".format(data_definition))
        data = rrdtool.graph(output_file, '--start', str(start_time), '--end', str(end_time),
                             '-a', 'PNG',
                             '--lower-limit', '0',
                             '-w', str(width), '-h', str(height),
                             '--x-grid', 'MINUTE:10:HOUR:1:MINUTE:120:0:%R',
                             data_definition)
        return Response(content_type='image/png', body=data)

    '''
    Chiamata REST che lista i Database RRD presenti nella cartella corrente.
    L'output si trova nel 'body' della risposta ed e' una lista semplice di file cn estensione '.rrd'.
    '''
    def listdb(self, req, **_kwargs):
        body = ''

        files = [f for f in os.listdir('.') if path.isfile(f)]

        for dbentry in files:
            if dbentry.endswith('.rrd'):
                body += str(dbentry) + "\n"

        return Response(content_type='application/json', body=body)


class RestStatsApi(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION,
                    ofproto_v1_2.OFP_VERSION,
                    ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(RestStatsApi, self).__init__(*args, **kwargs)
        self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters
        mapper = wsgi.mapper

        wsgi.registory['StatsController'] = self.data
        path = '/stats'
        uri = path + '/switches'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_dpids',
                       conditions=dict(method=['GET']))

        uri = path + '/desc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_desc_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/flow/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_flow_stats',
                       conditions=dict(method=['GET', 'POST']))

        uri = path + '/port/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_port_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/meterfeatures/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_features',
                       conditions=dict(method=['GET']))

        uri = path + '/meterconfig/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_config',
                       conditions=dict(method=['GET']))

        uri = path + '/meter/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/groupfeatures/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_features',
                       conditions=dict(method=['GET']))

        uri = path + '/groupdesc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_desc',
                       conditions=dict(method=['GET']))

        uri = path + '/group/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/portdesc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_port_desc',
                       conditions=dict(method=['GET']))

        uri = path + '/flowentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_flow_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/flowentry/clear/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='delete_flow_entry',
                       conditions=dict(method=['DELETE']))

        uri = path + '/meterentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_meter_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/groupentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_group_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/portdesc/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_port_behavior',
                       conditions=dict(method=['POST']))

        uri = path + '/experimenter/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='send_experimenter',
                       conditions=dict(method=['POST']))

        uri = path + '/rrdview/{filename}/{start}/{end}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='rrdviewer',
                       conditions=dict(method=['GET']))

        uri = path + '/listdb'
        mapper.connect('stats', uri,
                       controller=StatsController, action='listdb',
                       conditions=dict(method=['GET']))

        uri = path + '/rrdgraph'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_rrdgraph',
                       conditions=dict(method=['GET']))

    @set_ev_cls([ofp_event.EventOFPStatsReply,
                 ofp_event.EventOFPDescStatsReply,
                 ofp_event.EventOFPFlowStatsReply,
                 ofp_event.EventOFPPortStatsReply,
                 ofp_event.EventOFPMeterStatsReply,
                 ofp_event.EventOFPMeterFeaturesStatsReply,
                 ofp_event.EventOFPMeterConfigStatsReply,
                 ofp_event.EventOFPGroupStatsReply,
                 ofp_event.EventOFPGroupFeaturesStatsReply,
                 ofp_event.EventOFPGroupDescStatsReply,
                 ofp_event.EventOFPPortDescStatsReply
                 ], MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = 0
        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()

    @set_ev_cls([ofp_event.EventOFPSwitchFeatures], MAIN_DISPATCHER)
    def features_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        del self.waiters[dp.id][msg.xid]
        lock.set()
