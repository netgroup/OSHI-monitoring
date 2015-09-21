import os
import rrdtool
import math
import time
import logging
from os.path import join
import config

log = logging.getLogger('oshi.monitoring.rrdmanager')
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(os.path.join(config.RRD_LOG_PATH, "rrdmanager.log"))
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


class RRDManager(object):
    XFF1 = "0.5"
    XFF2 = "0.5"
    XFF3 = "0.5"
    XFF4 = "0.5"
    XFF5 = "0.5"
    STEP1 = "1"
    STEP2 = "6"
    STEP3 = "12"
    STEP4 = "288"
    STEP5 = "2016"
    ROWS1 = "24"
    ROWS2 = "10"
    ROWS3 = "24"
    ROWS4 = "7"
    ROWS5 = "4"

    @staticmethod
    def get_current_time():
        return int(math.floor(time.time()))

    @staticmethod
    def _build_rrd_data_source_definition(device_id, port_n):
        return str(str(device_id) + '_' + str(port_n))

    def __init__(self, filename, device):
        # define rrd filename
        self.filename = join(config.RRD_STORE_PATH, filename)

        # import port numbers for each device id
        self.device = device

        # build ALL data sources deviceID_portN:GAUGE
        self.data_sources = []
        self.raw_data_sources = []

        for dev_id in sorted(self.device):
            for port_n in self.device[dev_id]:
                    temp = str(RRDManager._build_rrd_data_source_definition(dev_id, port_n))
                    self.raw_data_sources.append(temp)
                    data_source = 'DS:' + temp + ':GAUGE:600:U:U'
                    log.debug("Build RRD data source from %s . Result: %s", temp, data_source)
                    self.data_sources.append(data_source)

        log.debug("File name: %s, Data sources: %s, Raw data sources: %s",
                  self.filename, self.data_sources, self.raw_data_sources)
        rrdtool.create(self.filename,
                       '--step',
                       config.RRD_STEP,
                       '--start',
                       str(RRDManager.get_current_time()),
                       self.data_sources,
                       'RRA:AVERAGE:' + self.XFF1 + ':' + self.STEP1 + ':' + self.ROWS1,  # i dati raccolti ogni 5 minuti per 2 ore
                       'RRA:AVERAGE:' + self.XFF2 + ':' + self.STEP2 + ':' + self.ROWS2,  # i dati raccolti ogni 30 minuti per 5 ore
                       'RRA:AVERAGE:' + self.XFF3 + ':' + self.STEP3 + ':' + self.ROWS3,  # i dati raccolti ogni ora per un giorno
                       'RRA:AVERAGE:' + self.XFF4 + ':' + self.STEP4 + ':' + self.ROWS4,  # i dati raccolti ogni giorno per una settimana
                       'RRA:AVERAGE:' + self.XFF5 + ':' + self.STEP5 + ':' + self.ROWS5)  # i dati raccolti ogni settimana per 4 settimane

    # insert values w/ timestamp NOW for a set of given DS
    def update(self, data_sources, values):
        if (len(data_sources) != len(values)) or len(data_sources) <= 0 or (len(data_sources) >= self.data_sources):
            raise Exception('Wrong number of data_sources or values')
        for DS in data_sources:
            if DS not in self.raw_data_sources:
                raise Exception('Data source not available in RRD')
        template = ':'.join(data_sources)
        values = ':'.join(str(value) for value in values)
        rrdtool.update(self.filename, '-t', template, str(self.getActualTime()) + ':' + values)
