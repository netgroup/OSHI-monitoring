import config


class SwitchStats:
    def __init__(self, datapath):
        self.dp = datapath
        self.ports = {}
        self.__seconds_from_start = 0

    def add_port(self, port_number):
        """
        Add a single port to stats.

        :param port_number: port number of the port to add
        """
        self.ports[port_number] = {}
        self.ports[port_number]['rx_bytes'] = 0
        self.ports[port_number]['rx_bytes_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['rx_bytes_buffer_index'] = 0
        self.ports[port_number]['tx_bytes'] = 0
        self.ports[port_number]['tx_bytes_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['tx_bytes_buffer_index'] = 0
        self.ports[port_number]['rx_packets'] = 0
        self.ports[port_number]['rx_packets_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['rx_packets_buffer_index'] = 0
        self.ports[port_number]['tx_packets'] = 0
        self.ports[port_number]['tx_packets_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['tx_packets_buffer_index'] = 0
        # SDN BUFFERS
        self.ports[port_number]['sdn_rx_bytes_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['sdn_rx_bytes_buffer_index'] = 0
        self.ports[port_number]['sdn_tx_bytes_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['sdn_tx_bytes_buffer_index'] = 0
        self.ports[port_number]['sdn_rx_packets_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['sdn_rx_packets_buffer_index'] = 0
        self.ports[port_number]['sdn_tx_packets_buffer'] = [0] * config.DELTA_WINDOW
        self.ports[port_number]['sdn_tx_packets_buffer_index'] = 0

    def delete_port(self, port_number):
        """
        Remove specified port from stats.

        :param port_number: port number of the port to remove
        """
        del self.ports[port_number]

    def get_port(self, port_number):
        """
        Return the specified port.

        :param port_number:
        :return: the specified port
        """
        return self.ports[port_number]

    def set_port_name(self, port_number, port_name):
        """
        Set name for the specified port.

        :param port_number
        :param port_name: name to set
        """
        self.ports[port_number]['name'] = port_name

    def get_port_name(self, port_number):
        """
        Return the name of the specified port.

        :param port_number:
        :return: port name
        """
        return self.ports[port_number]['name']

    def get_datapath(self):
        """
        Return the datapath of the SwitchStats object.

        :return: datapath
        """
        return self.dp

    def set_ip_partner_port_number(self, port_number, partner_port_number):
        """
        Set the port number of the IP partner for a given port.

        This can be used to match ports between partners like:
            ss.set_ip_partner_port_number(in_port, out_port)
            ss.set_ip_partner_port_number(out_port, in_port)

        :param port_number:
        :param partner_port_number:
        """
        self.ports[port_number]['ip_partner_port_number'] = partner_port_number

    def get_ip_partner_port_number(self, port_number):
        """
        Return the port number of the IP partner, given a port number.

        :param port_number:
        :return: Partner port number or -1 if no relationship has been defined for the specified port number.
        """
        if 'ip_partner_port_number' in self.ports[port_number]:
            return self.ports[port_number]['ip_partner_port_number']
        else:
            raise KeyError('IP partner not found for port ' + port_number)

    def get_rx_bytes(self, port_number):
        """
        Return received bytes count for the specified port.

        :param port_number:
        :return: bytes count
        """
        return self.ports[port_number]['rx_bytes']

    def get_tx_bytes(self, port_number):
        """
        Return transmitted bytes count for the specified port.

        :param port_number:
        :return: bytes count
        """
        return self.ports[port_number]['tx_bytes']

    def get_rx_packets(self, port_number):
        """
        Return received packet count for the specified port.

        :param port_number:
        :return: packet count
        """
        return self.ports[port_number]['rx_packets']

    def get_tx_packets(self, port_number):
        """
        Return transmitted packet count for the specified port.

        :param port_number:
        :return: packet count
        """
        return self.ports[port_number]['tx_packets']

    def _update_stat(self, port_number, buffer_index_key, buffer_key, stat_key, stat_value, lldp_noise=0):
        """
        Update stat value filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param stat_value:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        port = self.ports[port_number]
        # Time interval definition
        time_interval_end = port[buffer_index_key]
        time_interval_start = (time_interval_end - 1) % config.DELTA_WINDOW

        # byte count recorded @ time_interval_start
        time_interval_start_rx = port[buffer_key][time_interval_start]

        # update rx_bytes if necessary (time_interval_start_rx == 0 if the buffer is partially empty)
        if time_interval_start_rx != 0:
            self.ports[port_number][stat_key] += stat_value - time_interval_start_rx - lldp_noise

        # update time interval start
        port[buffer_index_key] = (port[buffer_index_key] + 1) % config.DELTA_WINDOW

        # update byte count received @ time_interval_end
        port[buffer_key][time_interval_end] = stat_value

    def set_rx_bytes(self, port_number, rx_bytes, lldp_noise=0):
        """
        Update received byte count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param rx_bytes:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, 'rx_bytes_buffer_index', 'rx_bytes_buffer', 'rx_bytes', rx_bytes, lldp_noise)

    def set_tx_bytes(self, port_number, tx_bytes, lldp_noise=0):
        """
        Update transmitted byte count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param tx_bytes:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, 'tx_bytes_buffer_index', 'tx_bytes_buffer', 'tx_bytes', tx_bytes, lldp_noise)

    def set_rx_packets(self, port_number, rx_packets, lldp_noise=0):
        """
        Update received packet count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param rx_packets:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, 'rx_packets_buffer_index', 'rx_packets_buffer', 'rx_packets', rx_packets,
                          lldp_noise)

    def set_tx_packets(self, port_number, tx_packets, lldp_noise=0):
        """
        Update transmitted packet count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param tx_packets:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, 'tx_packets_buffer_index', 'tx_packets_buffer', 'tx_packets', tx_packets,
                          lldp_noise)

    def _get_sdn_stat(self, port_number, stat_index_key, stat_key):
        port = self.ports[port_number]
        index = (port[stat_index_key] - 1) % config.DELTA_WINDOW
        return port[stat_key][index]

    def get_sdn_rx_bytes(self, port_number):
        """
        Return the received SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in bytes
        """
        return self._get_sdn_stat(port_number, 'sdn_rx_bytes_buffer_index', 'sdn_rx_bytes_buffer')

    def get_sdn_rx_packets(self, port_number):
        """
        Return the received SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in packets
        """
        return self._get_sdn_stat(port_number, 'sdn_rx_packets_buffer_index', 'sdn_rx_packets_buffer')

    def get_sdn_tx_bytes(self, port_number):
        """
        Return the transmitted SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in bytes
        """
        return self._get_sdn_stat(port_number, 'sdn_tx_bytes_buffer_index', 'sdn_tx_bytes_buffer')

    def get_sdn_tx_packets(self, port_number):
        """
        Return the transmitted SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in packets
        """
        return self._get_sdn_stat(port_number, 'sdn_tx_packets_buffer_index', 'sdn_tx_packets_buffer')

    def __get_sdn_rx_bytes(self, port_number):
        """
        Compute and return received SDN traffic for the specified port.

        :param port_number:
        :return: Received SDN traffic in bytes
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        # received total - ip sent to partner
        return self.get_rx_bytes(port_number) - self.get_tx_bytes(ip_partner_port_number)

    def __get_sdn_rx_packets(self, port_number):
        """
        Compute and return received SDN traffic for the specified port.

        :param port_number:
        :return: Received SDN traffic in packets
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        # received total - ip sent to partner
        return self.get_rx_packets(port_number) - self.get_tx_packets(ip_partner_port_number)

    def __get_sdn_tx_bytes(self, port_number):
        """
        Compute and return transmitted SDN traffic for the specified port.

        :param port_number:
        :return: Transmitted SDN traffic in bytes
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        sdn_bytes = 0
        # sent total - ip received by partner
        sdn_bytes += self.get_tx_bytes(port_number) - self.get_rx_bytes(ip_partner_port_number)
        return sdn_bytes

    def __get_sdn_tx_packets(self, port_number):
        """
        Compute and return transmitted SDN traffic for the specified port.

        :param port_number:
        :return: Transmitted SDN traffic in packets
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        sdn_packets = 0
        # sent total - ip received by partner
        sdn_packets += self.get_tx_packets(port_number) - self.get_rx_packets(ip_partner_port_number)
        return sdn_packets

    @staticmethod
    def _has_rx_lldp_noise(port_name, port_number):
        if port_name[0:3] == 'cro':
            return 0
        elif port_number != 1:
            return 1
        return 0

    def updateSDNStats(self):
        self.__seconds_from_start += 1
        for port_number in self.ports:
            p = self.ports[port_number]
            rx_noise = SwitchStats._has_rx_lldp_noise(self.get_port_name(port_number), port_number)
            t1_sdn = p['sdn_rx_bytes_buffer_index']
            p['sdn_rx_bytes_buffer_index'] = (p['sdn_rx_bytes_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_rx_bytes_buffer'][t1_sdn] = self.__get_sdn_rx_bytes(port_number) + (
                self.__seconds_from_start * config.LLDP_NOISE_BYTE_S * rx_noise)
            t1_sdn = p['sdn_tx_bytes_buffer_index']
            p['sdn_tx_bytes_buffer_index'] = (p['sdn_tx_bytes_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_tx_bytes_buffer'][t1_sdn] = self.__get_sdn_tx_bytes(port_number) - (
                self.__seconds_from_start * config.LLDP_NOISE_BYTE_S)
            t1_sdn = p['sdn_rx_packets_buffer_index']
            p['sdn_rx_packets_buffer_index'] = (p['sdn_rx_packets_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_rx_packets_buffer'][t1_sdn] = self.__get_sdn_rx_packets(port_number) + (
                self.__seconds_from_start * config.LLDP_NOISE_PACK_S * rx_noise)
            t1_sdn = p['sdn_tx_packets_buffer_index']
            p['sdn_tx_packets_buffer_index'] = (p['sdn_tx_packets_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_tx_packets_buffer'][t1_sdn] = self.__get_sdn_tx_packets(port_number) - (
                self.__seconds_from_start * config.LLDP_NOISE_PACK_S)
