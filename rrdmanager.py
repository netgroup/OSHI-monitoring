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

    # noinspection PyMethodMayBeStatic
    def _get_current_time_in_seconds(self):
        return int(math.floor(time.time()))

    # noinspection PyMethodMayBeStatic
    def _build_rrd_file_name(self, device_name, port_number):
        """
        Build RRD file name composing device_name and port_number.

        :param device_name:
        :param port_number:
        :return:
        """
        return str(str(device_name) + "_" + str(port_number) + ".rrd")

    # noinspection PyMethodMayBeStatic
    def _build_rrd_data_source(self, data_source_name, data_source_type, heartbeat):
        """

        :rtype : str
        """
        return 'DS:' + data_source_name + ':' + data_source_type + ':' + heartbeat + ':U:U'

    def __init__(self, device_name, port_number, data_source_definitions):
        """
        Build a new RRD manager for the specified device:port.

        :param device_name:
        :param port_number:
        :param data_source_definitions: list of RRDDataSource
        :return:

        :type data_source_definitions: list

        """
        self.filename = join(config.RRD_STORE_PATH, self._build_rrd_file_name(device_name, port_number))
        log.debug("Built new RRD file name: %s", self.filename)

        # build RRD data sources
        data_sources = []

        for data_source_definition in data_source_definitions:
            try:
                data_source_name = data_source_definition.name
                data_source_type = data_source_definition.data_source_type
                data_source_heartbeat = data_source_definition.heartbeat
            except KeyError:
                log.error("Unable to initialize RRD data source. Field missing. Data source will not be available")
                continue

            data_source_definition = self._build_rrd_data_source(data_source_name, data_source_type,
                                                                 data_source_heartbeat)
            data_sources.append(data_source_definition)
            log.debug("Build RRD data source. Name: %s, type: %s, heartbeat: %s. Result: %s", data_source_name,
                      data_source_type, data_source_heartbeat, data_source_definition)
        log.debug("Prepared RRD initialization. Data sources: %s", data_sources)
        if len(data_sources) > 0:
            # noinspection PyArgumentList
            rrdtool.create(self.filename,
                           '--step',
                           config.RRD_STEP,
                           '--start',
                           str(self._get_current_time_in_seconds()),
                           data_sources,
                           'RRA:AVERAGE:' + self.XFF1 + ':' + self.STEP1 + ':' + self.ROWS1,  # every 5 mins for 2 hrs
                           'RRA:AVERAGE:' + self.XFF2 + ':' + self.STEP2 + ':' + self.ROWS2,  # every 30 mins for 5 hrs
                           'RRA:AVERAGE:' + self.XFF3 + ':' + self.STEP3 + ':' + self.ROWS3,  # every 1 hrs for 1 day
                           'RRA:AVERAGE:' + self.XFF4 + ':' + self.STEP4 + ':' + self.ROWS4,  # every day for a week
                           'RRA:AVERAGE:' + self.XFF5 + ':' + self.STEP5 + ':' + self.ROWS5)  # every week for 4 weeks
            log.debug("%s initialized", self.filename)
        else:
            log.debug("No data sources initialized, skipping RRD file creation.")

    def update(self, rrd_data_sources):
        if len(rrd_data_sources) > 0:
            data_source_names = []
            data_source_values = []

            for rrd_data_source in rrd_data_sources:
                data_source_names.append(rrd_data_source.name)
                data_source_values.append(rrd_data_source.temp_value)

            template = ':'.join(data_source_names)
            values = ':'.join(str(value) for value in data_source_values)
            log.debug("Update %s . Template: %s . Values: %s", self.filename, template, values)
            # noinspection PyArgumentList
            rrdtool.update(self.filename, '-t', template, str(self._get_current_time_in_seconds()) + ':' + values)
            log.debug("%s Updated", self.filename)
        else:
            log.info("No update is necessary as no data sources are defined.")
