from os.path import join
import config
from rrd_data_source import RRDDataSource
from rrdmanager import RRDManager


class TestRRDManager(object):

    def test_rrdmanager_init(self):
        print("RRDManager Initialization Test: RDD file name")
        port_name = "port_name"
        rrd_file_name = port_name + '.rrd'
        rrd_data_source = RRDDataSource("port_stat_name", config.RRD_DATA_SOURCE_TYPE,
                                        config.RRD_DATA_SOURCE_HEARTBEAT)
        rrd_data_sources = [rrd_data_source]
        rrd_manager = RRDManager(rrd_file_name, rrd_data_sources)
        assert rrd_manager.filename == join(config.RRD_STORE_PATH, rrd_file_name)
        print("Built RRD file name: {}".format(rrd_manager.filename))
