import sys
import rrdtool

class RRDManager(object):

	def __init__(self, filename, device):
		# define rrd filename
		self.filename = filename

		# import port numbers for each device id
		self.device = device

		# build data sources DS:deviceID_portN:COUNTER:600:U:U
		self.data_sources = []
		self.raw_data_sources = []
		for dev_id in sorted(self.device):
			for port_n in self.device[dev_id]:
				self.raw_data_sources.append(dev_id+'_'+str(port_n))
				self.data_sources.append('DS:'+dev_id+'_'+str(port_n)+':COUNTER:600:U:U')

		# create rrd w/ default step = 300 sec
		rrdtool.create(self.filename,
		               '--start',
		               '920804400',
		               self.data_sources,
		               'RRA:AVERAGE:0.5:1:24',
		               'RRA:AVERAGE:0.5:6:10',
		               'RRA:AVERAGE:0.5:12:24')
	
	# insert values w/ timestamp NOW for a set of given DS
	def update(self, data_sources, values):
		if (len(data_sources) != len(values)) or len(data_sources) <= 0 or (len(data_sources) >= self.data_sources):
			raise Exception('Wrong number of data_sources or values')
		for DS in data_sources:
			if DS not in self.raw_data_sources:
				raise Exception('Data source not available in RRD')
		template = ':'.join(data_sources)
		values = ':'.join(str(value) for value in values)
		rrdtool.update(self.filename, '-t', template, 'N:'+values)


################
#   T E S T    #
################

device = {}
device['PEO1'] = [1,2,3,4]
device['PEO2'] = [1,2]
device['PEO3'] = [1,4,5,6]
device['PEO4'] = [2,3,5]

rrdman = RRDManager('test.rrd', device)
rrdman.update(['PEO1_1','PEO1_2','PEO1_3'],[1300,1500,1350])