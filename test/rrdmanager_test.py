import config
from rrd_data_source import RRDDataSource
from rrdmanager import RRDManager


class RRDManagerTest:

    def rrdmanager_init_test(self):
        device_name = "device_name"
        port_number = 100
        rrd_data_source = RRDDataSource("port_stat_name", config.RRD_DATA_SOURCE_TYPE,
                                        config.RRD_DATA_SOURCE_HEARTBEAT)
        rrd_data_sources = [rrd_data_source]
        rrd_manager = RRDManager(device_name, port_number, rrd_data_sources)
        assert rrd_manager.filename == str(device_name) + "_" + str(port_number) + ".rrd"
