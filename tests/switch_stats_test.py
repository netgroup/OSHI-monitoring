import config
from switch_stats import SwitchStats


class TestSwitchStats(object):
    def test_switch_stats_init(self):
        print("Testing SwitchStats initialization")
        test_datapath_id = 'datapath-id'
        switch_stat = SwitchStats(test_datapath_id)
        assert switch_stat.data_path_id == test_datapath_id
        # check if ports is empty
        assert not switch_stat.ports

    def test_add_port(self):
        print("Testing SwitchStats add port")
        switch_stat = SwitchStats('datapath-id')
        port_number = '10'
        switch_stat.add_port(port_number)
        assert port_number in switch_stat.ports
        assert switch_stat.get_rx_bytes(port_number) is 0
        assert switch_stat.get_rx_packets(port_number) is 0
        assert switch_stat.get_tx_bytes(port_number) is 0
        assert switch_stat.get_tx_packets(port_number) is 0
        assert switch_stat.get_sdn_rx_bytes(port_number) is 0
        assert switch_stat.get_sdn_rx_packets(port_number) is 0
        assert switch_stat.get_sdn_tx_bytes(port_number) is 0
        assert switch_stat.get_sdn_tx_packets(port_number) is 0

    def test_update_rx_bytes(self):
        print("Testing SwitchStats add port")
        switch_stat = SwitchStats('datapath-id')
        port_number = '10'
        switch_stat.add_port(port_number)
        rx_bytes_value_init = 100
        for rx_bytes_value in range(rx_bytes_value_init, rx_bytes_value_init + config.DELTA_WINDOW):
            switch_stat.set_rx_bytes(port_number, rx_bytes_value)
        print("Current value for rx_bytes: " + str(switch_stat.get_rx_bytes(port_number)))
        assert switch_stat.get_rx_bytes(port_number) is rx_bytes_value
