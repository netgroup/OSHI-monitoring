import os
import rrdtool
import math
import time
import logging
from os.path import join
import config

log = logging.getLogger('oshi_monitoring')


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
    def _get_time_in_seconds(self, current_time):
        return int(math.floor(current_time))

    # noinspection PyMethodMayBeStatic
    def _build_rrd_data_source(self, data_source_name, data_source_type, heartbeat):
        """

        :rtype : str
        """
        return 'DS:' + data_source_name + ':' + data_source_type + ':' + heartbeat + ':U:U'

    def __init__(self, rrd_file_name, data_source_definitions):
        """
        Build a new RRD manager for the specified device:port.

        :param rrd_file_name: RRD file name
        :param data_source_definitions: list of RRDDataSource
        :return:

        :type data_source_definitions: list

        """
        self.filename = join(config.RRD_STORE_PATH, rrd_file_name)
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
            log.debug("Built RRD data source. Name: %s, type: %s, heartbeat: %s. Result: %s", data_source_name,
                      data_source_type, data_source_heartbeat, data_source_definition)
        log.debug("Prepared RRD initialization. Data sources: %s", data_sources)
        if len(data_sources) > 0:
            # noinspection PyArgumentList
            start_time = str(self._get_time_in_seconds(time.time()))
            rrdtool.create(self.filename,
                           '--step',
                           str(config.RRD_STEP),
                           '--start',
                           start_time,
                           data_sources,
                           'RRA:AVERAGE:' + self.XFF1 + ':' + self.STEP1 + ':' + self.ROWS1,  # every 5 mins for 2 hrs
                           'RRA:AVERAGE:' + self.XFF2 + ':' + self.STEP2 + ':' + self.ROWS2,  # every 30 mins for 5 hrs
                           'RRA:AVERAGE:' + self.XFF3 + ':' + self.STEP3 + ':' + self.ROWS3,  # every 1 hrs for 1 day
                           'RRA:AVERAGE:' + self.XFF4 + ':' + self.STEP4 + ':' + self.ROWS4,  # every day for a week
                           'RRA:AVERAGE:' + self.XFF5 + ':' + self.STEP5 + ':' + self.ROWS5)  # every week for 4 weeks
            log.debug("%s initialized with start time: %s", self.filename, start_time)
            # sleep for 1 second to avoid update conflicts (minimum step is 1 second)
            time.sleep(1)
        else:
            log.debug("No data sources initialized, skipping RRD file creation.")

    def update(self, rrd_data_sources, update_time):
        if len(rrd_data_sources) > 0:
            data_source_names = []
            data_source_values = []
            for rrd_data_source in rrd_data_sources:
                data_source_names.append(rrd_data_source.name)
                data_source_values.append(rrd_data_source.temp_value)

            template = ':'.join(data_source_names)
            values = ':'.join(str(value) for value in data_source_values)
            update_time = self._get_time_in_seconds(update_time)
            log.debug("Updating %s. Update time: %s, template: %s, values: %s", self.filename, update_time,
                      template, values)
            try:
                # noinspection PyArgumentList
                rrdtool.update(self.filename, '-t', template, str(update_time) + ':' + values)
                log.debug("%s Updated", self.filename)
            except rrdtool.OperationalError:
                log.exception("Error while updating RRD.")
        else:
            log.debug("No update is necessary as no data sources are defined.")
