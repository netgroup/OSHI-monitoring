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


'''associazione tra port number e port name per un certo datapathid'''
class PNumPName:
	def __init__(self, num, nam,dpid):

		self.number=num
		self.name=nam
		self.datapathid=dpid

class SimpleMonitor(app_manager.RyuApp):
	
	def __init__(self, *args, **kwargs):
		super(SimpleMonitor, self).__init__(*args, **kwargs)
		self.datapaths = {}
		self.monitor_thread = hub.spawn(self._monitor)
		'''lista delle associazioni tra port number port name e datapathid'''
		self.namePnumber=[]
		self.rrdManagerstx={}
		self.rrdManagersrx={}
		self.flowrrdManagerstx={}
		self.flowrrdManagersrx={}

	def color_warning(self, msg, *args, **kwargs):
		new_msg = "\033[0;34m%s\033[1;0m %s"%('DEBUG',msg)
		self.old_w(new_msg, *args, **kwargs)

	def color_info(self, msg, *args, **kwargs):
		new_msg = "\033[0;32m%s\033[1;0m %s"%('_INFO',msg)
		self.old_i(new_msg, *args, **kwargs)
		

	
	def _monitor(self):
		while True:
			for dp in self.datapaths.values():
				self._request_stats(dp)
			hub.sleep(10)

	def _request_stats(self, datapath):
		#self.logger.warning('send stats request: %016x', datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		cookie = cookie_mask = 0
		match = parser.OFPMatch(eth_type=0x0800)
		req = parser.OFPFlowStatsRequest(datapath, 0,
                                         ofproto.OFPTT_ALL,
                                         ofproto.OFPP_ANY, ofproto.OFPG_ANY,cookie,cookie_mask)
		datapath.send_msg(req)
		req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
		datapath.send_msg(req)
	
	'''restituisce per un certo switch il nome della porta indicata'''
	def getPname(self,datapathid,PNumber):
		for x in self.namePnumber:
			if x.number==PNumber and x.datapathid==datapathid:
				return x.name 

	@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
	def _flow_stats_reply_handler(self, ev):
		flows = []
		body = ev.msg.body

		rxdatasources=[]
		txdatasources=[]
		rxdata=[]
		txdata=[]

		for stat in body:
			'''per ogni flusso sottomettere tramite chiamata REST le informazioni composte da DataPathId, portName (outPort),pktCount,ethType
				usare getPname per trasformare il numero di outport nel nome della outport '''

			datapathidstr=str(ev.msg.datapath.id)
			device = {}
			if not (datapathidstr in self.flowrrdManagersrx.keys()):
				device[datapathidstr]=[]
				for i in self.namePnumber:
					if i.datapathid==ev.msg.datapath.id:
						device[datapathidstr].append(i.name)

			if not (datapathidstr in self.flowrrdManagersrx.keys()):
				print "creating managers for flow received data " + "file: " + datapathidstr+"rx" 
				rrdman = RRDManager("flow"+datapathidstr+"rx", device, ["0800"])
				self.flowrrdManagersrx[datapathidstr]=rrdman

				print "creating managers for flow transmitted data " + "file: " + datapathidstr+"tx" 
				rrdman = RRDManager("flow"+datapathidstr+"tx", device, ["0800"])
				self.flowrrdManagerstx[datapathidstr]=rrdman
				time.sleep(1)

			rrdmanagerrx=self.flowrrdManagersrx[datapathidstr]
			rrdmanagertx=self.flowrrdManagerstx[datapathidstr]
			

			InEthType=0
			InPortNumber=0
			for OXMTlv in stat.match.fields:
				if type(OXMTlv).__name__=='MTEthType':
					InEthType=OXMTlv.value
				if type(OXMTlv).__name__=='MTInPort':
					InPortNumber=OXMTlv.value

			inPortName=self.getPname(ev.msg.datapath.id,InPortNumber)
			OutEthType=InEthType
			for OFPInstructionActions in stat.instructions:

				if type(OFPInstructionActions).__name__=="OFPInstructionGotoTable":
					continue

				for action in OFPInstructionActions.actions:

					if type(action).__name__=="OFPActionPushMpls" or type(action).__name__=="OFPActionPopMpls":
						OutEthType=action.ethertype
				
				for action in OFPInstructionActions.actions:
					if type(action).__name__!="OFPActionOutput":
						continue
					if action.type!=0 : OutEthType=action.type
					outPortNumber=action.port
					outPortName=self.getPname(ev.msg.datapath.id,outPortNumber)
					if InPortNumber==0 or outPortNumber==0: continue
					if InEthType==0x0800:
						txdata.append(stat.packet_count)
						txdatasources.append(rrdmanagerrx.constructDataSource(datapathidstr,inPortName, "0800"))
						
					if OutEthType==0x0800:
						rxdata.append(stat.packet_count)
						rxdatasources.append(rrdmanagertx.constructDataSource(datapathidstr,outPortName, "0800"))

						#flows.append('PacketCount=%d ' 'ByteCount=%d ' 'InEthType=%d ' 'InPortName=%s ' 'OutEthType=%d ' 'OutPortName=%s ' % (stat.packet_count, stat.byte_count, InEthType,inPortName,OutEthType,outPortName))	
		
		if rxdatasources:
			print "updating rx flow for "+datapathidstr+" port: "+str(rxdatasources)+" data: "+str(rxdata)
			print "\n"
			rrdmanagerrx.update(rxdatasources,rxdata)
		
		if txdatasources:
			print "updating tx flow for "+datapathidstr+" port: "+str(txdatasources)+" data: "+str(txdata)
			print "\n"
			rrdmanagertx.update(txdatasources,txdata)			
		
		'''flows.append(
						'--------------------------------------------------- %016x \n\n'
						'table_id=%s \n'
						'duration_sec=%d duration_nsec=%d \n'
						'priority=%d \n'
						'idle_timeout=%d hard_timeout=%d flags=0x%04x \n'
						'cookie=%d packet_count=%d byte_count=%d \n'
						'match=%s \n' 'instructions=%s \n' %
						(ev.msg.datapath.id,
						stat.table_id,
						stat.duration_sec, stat.duration_nsec,
						stat.priority,
						stat.idle_timeout, stat.hard_timeout, stat.flags,
						stat.cookie, stat.packet_count, stat.byte_count,
						stat.match, stat.instructions))'''
		#print "\n".join(flows)

	@set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		ofp_parser=datapath.ofproto_parser
		if ev.state == MAIN_DISPATCHER:
			if not datapath.id in self.datapaths:
				self.logger.warning('register datapath: %016x', datapath.id)
				self.datapaths[datapath.id] = datapath
				'''ogni volta che un nuovo switch si registra richiedo le informazioni sulla porta per ottenere il name'''
				req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
				datapath.send_msg(req)
		elif ev.state == DEAD_DISPATCHER:
			if datapath.id in self.datapaths:
				self.logger.warning('unregister datapath: %016x', datapath.id)
				del self.datapaths[datapath.id]


	'''evento port descriptor, serve per ottenere l'associazione tra i port name e i port number '''
	@set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
	def port_desc_stats_reply_handler(self, ev):
		ports = []
		for p in ev.msg.body:
			'''aggiunge l'associazione ricevuta alla lista '''
			self.namePnumber.append(PNumPName(p.port_no,p.name,ev.msg.datapath.id))


	@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
	def _port_stats_reply_handler(self, ev):

		body = ev.msg.body
		self.logger.warning('PORT STATS')
		'''self.logger.warning('datapath\t\t   port  '
						 'rx-pkts rx-bytes rx-error  '
						 'tx-pkts tx-bytes tx-error')
		self.logger.warning('----------------  -------- '
						 '-------- -------- -------- '
						 '-------- -------- --------')'''
		rxdatasources=[]
		txdatasources=[]
		rxdata=[]
		txdata=[]
		datapathidstr=str(ev.msg.datapath.id)
		for stat in sorted(body, key=attrgetter('port_no')):
			'''per ogni porta inviare tramite chiamata REST le informazioni composte da dataPathId, portName ,pktCount
			la seguente riga trasforma il port number in port name'''
			name=self.getPname(ev.msg.datapath.id,stat.port_no)
			device = {}
			if not (datapathidstr in self.rrdManagersrx.keys()):
				device[datapathidstr]=[]
				for i in self.namePnumber:
					if i.datapathid==ev.msg.datapath.id:
						device[datapathidstr].append(i.name)

			if not (datapathidstr in self.rrdManagersrx.keys()):
				print "creating managers for agggregate received data " + "file: " + datapathidstr+"rx" 
				rrdman = RRDManager(datapathidstr+"rx", device, ["0000"])
				self.rrdManagersrx[datapathidstr]=rrdman
				print "creating managers for agggregate transmitted data " + "file: " + datapathidstr+"tx" 
				rrdman = RRDManager(datapathidstr+"tx", device, ["0000"])
				self.rrdManagerstx[datapathidstr]=rrdman
				time.sleep(1)

			rrdmanagerrx=self.rrdManagersrx[datapathidstr]
			rrdmanagertx=self.rrdManagerstx[datapathidstr]
			
			rxdatasources.append(rrdmanagerrx.constructDataSource(datapathidstr,name, "0000"))
			rxdata.append(stat.rx_packets);
			txdatasources.append(rrdmanagertx.constructDataSource(datapathidstr,name, "0000"))
			txdata.append(stat.tx_packets);


		print "updating tx data for "+datapathidstr+" ds: "+str(txdatasources)+" data: "+str(txdata)
		print "\n"
		rrdmanagertx.update(txdatasources,txdata)
		print "updating rx data for "+datapathidstr+" ds: "+str(rxdatasources)+" data: "+str(rxdata)
		print "\n"
		rrdmanagerrx.update(rxdatasources,rxdata)

			#time.sleep(1)
'''
			self.logger.warning('%016x %s %8d %8d %8d %8d %8d %8d',
							  ev.msg.datapath.id, name,
                              stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                          	  stat.tx_packets, stat.tx_bytes, stat.tx_errors) '''