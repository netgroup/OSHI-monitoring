from os.path import join
import config
from rrd_data_source import RRDDataSource
from rrdmanager import RRDManager


class TestRRDManager(object):

    def test_rrdmanager_init(self):
        print("RRDManager Initialization Test: RDD file name")
        device_name = "device_name"
        port_number = 100
        rrd_data_source = RRDDataSource("port_stat_name", config.RRD_DATA_SOURCE_TYPE,
                                        config.RRD_DATA_SOURCE_HEARTBEAT)
        rrd_data_sources = [rrd_data_source]
        rrd_manager = RRDManager(device_name, port_number, rrd_data_sources)
        assert rrd_manager.filename == join(config.RRD_STORE_PATH, str(device_name) + "_" + str(port_number) + ".rrd")
        print("Built RRD file name: {}".format(rrd_manager.filename))
