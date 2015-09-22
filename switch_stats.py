import config


class SwitchStats:
    def __init__(self, datapath):
        self.dp = datapath
        self.ports = {}
        self.__seconds_from_start = 0

    def get_datapath(self):
        return self.dp

    def setIPPartner(self, port_number, partner_port_number):
        self.ports[port_number]['IP_partner'] = partner_port_number

    def getIPPartner(self, port_number):
        if 'IP_partner' in self.ports[port_number]:
            return self.ports[port_number]['IP_partner']
        else:
            return -1

    def getPort(self, port_number):
        return self.ports[port_number]

    def addPort(self, port_number):
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

    def delPort(self, port_number):
        del self.ports[port_number]

    def setport_name(self, port_number, port_name):
        self.ports[port_number]['name'] = port_name

    def getport_name(self, port_number):
        return self.ports[port_number]['name']

    def __getSDNRxBytes(self, port_number):
        IP_partner = self.getIPPartner(port_number)
        if IP_partner == -1:
            return -1
        return self.getRxBytes(port_number) - self.getTxBytes(IP_partner)

    def __getSDNRxPackets(self, port_number):
        IP_partner = self.getIPPartner(port_number)
        if IP_partner == -1:
            return -1
        return self.getRxPackets(port_number) - self.getTxPackets(IP_partner)

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
        IP_partner = self.getIPPartner(port_number)
        if IP_partner == -1:
            return -1
        sdn_bytes += self.getTxBytes(port_number) - self.getRxBytes(IP_partner)
        return sdn_bytes

    def __getSDNTxPackets(self, port_number):
        sdn_packets = 0
        IP_partner = self.getIPPartner(port_number)
        if IP_partner == -1:
            return -1
        sdn_packets += self.getTxPackets(port_number) - self.getRxPackets(IP_partner)
        return sdn_packets

    def getSDNTxBytes(self, port_number):
        p = self.ports[port_number]
        index = (p['sdn_tx_bytes_buffer_index'] - 1) % config.DELTA_WINDOW
        return p['sdn_tx_bytes_buffer'][index]

    def getSDNTxPackets(self, port_number):
        p = self.ports[port_number]
        index = (p['sdn_tx_packets_buffer_index'] - 1) % config.DELTA_WINDOW
        return p['sdn_tx_packets_buffer'][index]

    def getRxBytes(self, port_number):
        return self.ports[port_number]['rx_bytes']

    def getTxBytes(self, port_number):
        return self.ports[port_number]['tx_bytes']

    def setRxBytes(self, port_number, rx_bytes, lldp_noise=0):
        p = self.ports[port_number]
        t1 = p['rx_bytes_buffer_index']
        p['rx_bytes_buffer_index'] = (p['rx_bytes_buffer_index'] + 1) % config.DELTA_WINDOW
        p['rx_bytes_buffer'][t1] = rx_bytes
        t2 = (t1 - 1) % config.DELTA_WINDOW
        old_rx = p['rx_bytes_buffer'][t2]
        if old_rx != 0:
            self.ports[port_number]['rx_bytes'] += rx_bytes - old_rx - lldp_noise

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

    def getRxPackets(self, port_number):
        return self.ports[port_number]['rx_packets']

    def getTxPackets(self, port_number):
        return self.ports[port_number]['tx_packets']

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
            rx_noise = self.__has_rx_lldp_noise(self.getport_name(port_number), port_number)
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
