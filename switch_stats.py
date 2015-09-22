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
            return -1

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

    def set_rx_bytes(self, port_number, rx_bytes, lldp_noise=0):
        """
        Update received byte count filling a circular buffer of config.DELTA_WINDOW

        :param port_number:
        :param rx_bytes:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        port = self.ports[port_number]
        # Time interval definition
        time_interval_end = port['rx_bytes_buffer_index']
        time_interval_start = (time_interval_end - 1) % config.DELTA_WINDOW

        # byte count recorded @ time_interval_start
        time_interval_start_rx = port['rx_bytes_buffer'][time_interval_start]

        # update rx_bytes if necessary (time_interval_start_rx == 0 if the buffer is partially empty)
        if time_interval_start_rx != 0:
            self.ports[port_number]['rx_bytes'] += rx_bytes - time_interval_start_rx - lldp_noise

        # update time interval start
        port['rx_bytes_buffer_index'] = (port['rx_bytes_buffer_index'] + 1) % config.DELTA_WINDOW

        # update byte count received @ time_interval_end
        port['rx_bytes_buffer'][time_interval_end] = rx_bytes

    def setTxBytes(self, port_number, tx_bytes, lldp_noise=0):
        p = self.ports[port_number]
        t1 = p['tx_bytes_buffer_index']
        p['tx_bytes_buffer_index'] = (p['tx_bytes_buffer_index'] + 1) % config.DELTA_WINDOW
        p['tx_bytes_buffer'][t1] = tx_bytes
        t2 = (t1 - 1) % config.DELTA_WINDOW
        old_tx = p['tx_bytes_buffer'][t2]
        if old_tx != 0:
            self.ports[port_number]['tx_bytes'] += tx_bytes - old_tx - lldp_noise

    def setRxPackets(self, port_number, rx_packets, lldp_noise=0):
        p = self.ports[port_number]
        t1 = p['rx_packets_buffer_index']
        p['rx_packets_buffer_index'] = (p['rx_packets_buffer_index'] + 1) % config.DELTA_WINDOW
        p['rx_packets_buffer'][t1] = rx_packets
        t2 = (t1 - 1) % config.DELTA_WINDOW
        old_rx = p['rx_packets_buffer'][t2]
        if old_rx != 0:
            self.ports[port_number]['rx_packets'] += rx_packets - old_rx - lldp_noise

    def setTxPackets(self, port_number, tx_packets, lldp_noise=0):
        p = self.ports[port_number]
        t1 = p['tx_packets_buffer_index']
        p['tx_packets_buffer_index'] = (p['tx_packets_buffer_index'] + 1) % config.DELTA_WINDOW
        p['tx_packets_buffer'][t1] = tx_packets
        t2 = (t1 - 1) % config.DELTA_WINDOW
        old_tx = p['tx_packets_buffer'][t2]
        if old_tx != 0:
            self.ports[port_number]['tx_packets'] += tx_packets - old_tx - lldp_noise

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

    def __getSDNRxBytes(self, port_number):
        ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        if ip_partner_port_number == -1:
            return -1
        return self.get_rx_bytes(port_number) - self.get_tx_bytes(ip_partner_port_number)

    def __getSDNRxPackets(self, port_number):
        ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        if ip_partner_port_number == -1:
            return -1
        return self.get_rx_packets(port_number) - self.get_tx_packets(ip_partner_port_number)

    def getSDNRxBytes(self, port_number):
        p = self.ports[port_number]
        index = (p['sdn_rx_bytes_buffer_index'] - 1) % config.DELTA_WINDOW
        return p['sdn_rx_bytes_buffer'][index]

    def getSDNRxPackets(self, port_number):
        p = self.ports[port_number]
        index = (p['sdn_rx_packets_buffer_index'] - 1) % config.DELTA_WINDOW
        return p['sdn_rx_packets_buffer'][index]

    def __getSDNTxBytes(self, port_number):
        sdn_bytes = 0
        ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        if ip_partner_port_number == -1:
            return -1
        sdn_bytes += self.get_tx_bytes(port_number) - self.get_rx_bytes(ip_partner_port_number)
        return sdn_bytes

    def __getSDNTxPackets(self, port_number):
        sdn_packets = 0
        ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        if ip_partner_port_number == -1:
            return -1
        sdn_packets += self.get_tx_packets(port_number) - self.get_rx_packets(ip_partner_port_number)
        return sdn_packets

    def getSDNTxBytes(self, port_number):
        p = self.ports[port_number]
        index = (p['sdn_tx_bytes_buffer_index'] - 1) % config.DELTA_WINDOW
        return p['sdn_tx_bytes_buffer'][index]

    def getSDNTxPackets(self, port_number):
        p = self.ports[port_number]
        index = (p['sdn_tx_packets_buffer_index'] - 1) % config.DELTA_WINDOW
        return p['sdn_tx_packets_buffer'][index]

    def __has_rx_lldp_noise(self, port_name, port_number):
        if port_name[0:3] == 'cro':
            return 0
        elif port_number != 1:
            return 1
        return 0

    def updateSDNStats(self):
        self.__seconds_from_start += 1
        for port_number in self.ports:
            p = self.ports[port_number]
            rx_noise = self.__has_rx_lldp_noise(self.get_port_name(port_number), port_number)
            t1_sdn = p['sdn_rx_bytes_buffer_index']
            p['sdn_rx_bytes_buffer_index'] = (p['sdn_rx_bytes_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_rx_bytes_buffer'][t1_sdn] = self.__getSDNRxBytes(port_number) + (
                self.__seconds_from_start * config.LLDP_NOISE_BYTE_S * rx_noise)
            t1_sdn = p['sdn_tx_bytes_buffer_index']
            p['sdn_tx_bytes_buffer_index'] = (p['sdn_tx_bytes_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_tx_bytes_buffer'][t1_sdn] = self.__getSDNTxBytes(port_number) - (
                self.__seconds_from_start * config.LLDP_NOISE_BYTE_S)
            t1_sdn = p['sdn_rx_packets_buffer_index']
            p['sdn_rx_packets_buffer_index'] = (p['sdn_rx_packets_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_rx_packets_buffer'][t1_sdn] = self.__getSDNRxPackets(port_number) + (
                self.__seconds_from_start * config.LLDP_NOISE_PACK_S * rx_noise)
            t1_sdn = p['sdn_tx_packets_buffer_index']
            p['sdn_tx_packets_buffer_index'] = (p['sdn_tx_packets_buffer_index'] + 1) % config.DELTA_WINDOW
            p['sdn_tx_packets_buffer'][t1_sdn] = self.__getSDNTxPackets(port_number) - (
                self.__seconds_from_start * config.LLDP_NOISE_PACK_S)
