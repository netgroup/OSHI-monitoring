import config
from switch_stats import SwitchStats


class _TestDataPath(object):
    def __init__(self, id):
        self.id = id


class TestSwitchStats(object):
    def test_switch_stats_init(self):
        print("Testing SwitchStats initialization")
        test_datapath = _TestDataPath('datapath-id')
        switch_stat = SwitchStats(test_datapath)
        assert switch_stat.data_path_id == test_datapath.id
        # check if ports is empty
        assert not switch_stat.ports

    def test_add_port(self):
        print("Testing SwitchStats add port")
        switch_stat = SwitchStats(_TestDataPath('datapath-id'))
        port_number = 10
        port_name = 'eth1'
        switch_stat.add_port(port_number, is_virtual=False, port_name=port_name)
        assert port_number in switch_stat.ports
        assert port_name == switch_stat.get_port_name(port_number)
        assert switch_stat.get_rx_bytes(port_number) == 0
        assert switch_stat.get_rx_packets(port_number) == 0
        assert switch_stat.get_tx_bytes(port_number) == 0
        assert switch_stat.get_tx_packets(port_number) == 0
        assert switch_stat.get_sdn_rx_bytes(port_number) == 0
        assert switch_stat.get_sdn_rx_packets(port_number) == 0
        assert switch_stat.get_sdn_tx_bytes(port_number) == 0
        assert switch_stat.get_sdn_tx_packets(port_number) == 0

    def test_update_rx_bytes(self):
        print("Testing SwitchStats Update RX bytes")
        switch_stat = SwitchStats(_TestDataPath('datapath-id'))
        port_number = '10'
        switch_stat.add_port(port_number)
        rx_bytes_value_init = 100
        rx_bytes_final_value = 0
        increment = 10
        for rx_bytes_value in range(rx_bytes_value_init, rx_bytes_value_init + increment):
            switch_stat.set_rx_bytes(port_number, rx_bytes_value)
            rx_bytes_final_value += rx_bytes_value
        assert switch_stat.get_rx_bytes(port_number) == rx_bytes_final_value
