import re
from traffic_monitor_params import *


class SwitchStats:
    def __init__(self, datapath):
        self.dp = datapath
        self.ports = {}
        self.__seconds_from_start = 0

    def get_datapath(self):
        return self.dp

    def getBytesStats(self):
        s = ' Name      | Port      |IP |    TOT_rx |    TOT_tx |     rx_rate |     tx_rate |'
        s += '    SDN_rx |    SDN_tx | SDN_rx_rate | SDN_tx_rate | \n'
        s += '-----------+-----------+---+-----------+-----------+-------------+-------------+'
        s += '-----------+-----------+-------------+-------------+--\n'
        for p in self.ports:
            s += "%10s" % (self.getPortName(p)) + " |"
            s += "%10d" % (p) + " |"
            s += "%2d" % (self.getIPPartner(p)) + " |"
            s += "%1s%3d.%02d %2s" % (self.__format_bytes(self.getRxBytes(p))) + " |"
            s += "%1s%3d.%02d %2s" % (self.__format_bytes(self.getTxBytes(p))) + " |"
            s += "%1s%3d.%02d %2s/s" % (self.__format_bytes(self.getRxBytesRate(p))) + " |"
            s += "%1s%3d.%02d %2s/s" % (self.__format_bytes(self.getTxBytesRate(p))) + " |"
            if not len(re.findall(r"vi+[0-9]", self.getPortName(p), flags=0)) == 1:
                s += "%1s%3d.%02d %2s" % (self.__format_bytes(self.getSDNRxBytes(p))) + " |"
                s += "%1s%3d.%02d %2s" % (self.__format_bytes(self.getSDNTxBytes(p))) + " |"
                s += "%1s%3d.%02d %2s/s" % (self.__format_bytes(self.getSDNRxBytesRate(p))) + " |"
                s += "%1s%3d.%02d %2s/s" % (self.__format_bytes(self.getSDNTxBytesRate(p))) + " |"
            else:
                s += "           |           |             |             |"
            s += "\n"
        s += "\n"
        return s

    def getPacketsStats(self):
        s = ' Name      | Port      |IP |    TOT_rx |    TOT_tx |      rx_rate |      tx_rate |'
        s += '    SDN_rx |    SDN_tx |  SDN_rx_rate |  SDN_tx_rate | \n'
        s += '-----------+-----------+---+-----------+-----------+--------------+--------------+'
        s += '-----------+-----------+--------------+--------------+--\n'
        for p in self.ports:
            s += "%10s" % (self.getPortName(p)) + " |"
            s += "%10d" % (p) + " |"
            s += "%2d" % (self.getIPPartner(p)) + " |"
            s += "%10d" % (self.getRxPackets(p)) + " |"
            s += "%10d" % (self.getTxPackets(p)) + " |"
            s += "%1s%5d.%02d P/s" % (self.__format_packets(self.getRxPacketsRate(p))) + " |"
            s += "%1s%5d.%02d P/s" % (self.__format_packets(self.getTxPacketsRate(p))) + " |"
            if not len(re.findall(r"vi+[0-9]", self.getPortName(p), flags=0)) == 1:
                s += "%10d" % (self.getSDNRxPackets(p)) + " |"
                s += "%10d" % (self.getSDNTxPackets(p)) + " |"
                s += "%1s%5d.%02d P/s" % (self.__format_packets(self.getSDNRxPacketsRate(p))) + " |"
                s += "%1s%5d.%02d P/s" % (self.__format_packets(self.getSDNTxPacketsRate(p))) + " |"
            else:
                s += "           |           |              |              |"
            s += "\n"
        s += "\n"
        return s

    def __format_packets(self, number):
        sign = ' ' if number >= 0 else '-'
        number = number if number >= 0 else number * -1
        return sign, number, int((number - int(number)) * 100)

    def __format_bytes(self, number):
        sign = ' ' if number >= 0 else '-'
        number = number if number >= 0 else number * -1
        if number < 1000 and number > -1000:
            return (sign, number, int((number - int(number)) * 100), 'B')
        elif number < 1000000 and number > -1000000:
            return (sign, int(float(number) / 1000), int(float(number) / 10) - (int(float(number) / 1000) * 100), 'KB')
        elif number < 1000000000 and number > -1000000000:
            return (
                sign, int(float(number) / 1000000), int(float(number) / 10000) - (int(float(number) / 1000000) * 100),
                'MB')
        elif number < 1000000000000 and number > -1000000000000:
            return (sign, int(float(number) / 1000000000),
                    int(float(number) / 10000000) - (int(float(number) / 1000000000) * 100), 'GB')
        else:
            return (sign, int(float(number) / 1000000000000),
                    int(float(number) / 10000000000) - (int(float(number) / 1000000000000) * 100), 'TB')

    def setIPPartner(self, portNumber, partnerPortNumber):
        self.ports[portNumber]['IP_partner'] = partnerPortNumber

    def getIPPartner(self, portNumber):
        if 'IP_partner' in self.ports[portNumber]:
            return self.ports[portNumber]['IP_partner']
        else:
            return -1;

    def getPort(self, portNumber):
        return self.ports[portNumber]

    def addPort(self, portNumber):
        self.ports[portNumber] = {}
        self.ports[portNumber]['rx_bytes'] = 0
        self.ports[portNumber]['rx_bytes_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['rx_bytes_buffer_index'] = 0
        self.ports[portNumber]['tx_bytes'] = 0
        self.ports[portNumber]['tx_bytes_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['tx_bytes_buffer_index'] = 0
        self.ports[portNumber]['rx_packets'] = 0
        self.ports[portNumber]['rx_packets_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['rx_packets_buffer_index'] = 0
        self.ports[portNumber]['tx_packets'] = 0
        self.ports[portNumber]['tx_packets_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['tx_packets_buffer_index'] = 0
        # SDN BUFFERS
        self.ports[portNumber]['sdn_rx_bytes_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['sdn_rx_bytes_buffer_index'] = 0
        self.ports[portNumber]['sdn_tx_bytes_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['sdn_tx_bytes_buffer_index'] = 0
        self.ports[portNumber]['sdn_rx_packets_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['sdn_rx_packets_buffer_index'] = 0
        self.ports[portNumber]['sdn_tx_packets_buffer'] = [0] * DELTA_WINDOW
        self.ports[portNumber]['sdn_tx_packets_buffer_index'] = 0

    def delPort(self, portNumber):
        del self.ports[portNumber]

    def setPortName(self, portNumber, portName):
        self.ports[portNumber]['name'] = portName

    def getPortName(self, portNumber):
        return self.ports[portNumber]['name']

    def __getSDNRxBytes(self, portNumber):
        IP_partner = self.getIPPartner(portNumber)
        if IP_partner == -1:
            return -1
        return self.getRxBytes(portNumber) - self.getTxBytes(IP_partner)

    def __getSDNRxPackets(self, portNumber):
        IP_partner = self.getIPPartner(portNumber)
        if IP_partner == -1:
            return -1
        return self.getRxPackets(portNumber) - self.getTxPackets(IP_partner)

    def getSDNRxBytes(self, portNumber):
        p = self.ports[portNumber]
        index = (p['sdn_rx_bytes_buffer_index'] - 1) % DELTA_WINDOW
        return p['sdn_rx_bytes_buffer'][index]

    def getSDNRxPackets(self, portNumber):
        p = self.ports[portNumber]
        index = (p['sdn_rx_packets_buffer_index'] - 1) % DELTA_WINDOW
        return p['sdn_rx_packets_buffer'][index]

    def __getSDNTxBytes(self, portNumber):
        sdn_bytes = 0
        IP_partner = self.getIPPartner(portNumber)
        if IP_partner == -1:
            return -1
        sdn_bytes += self.getTxBytes(portNumber) - self.getRxBytes(IP_partner)
        return sdn_bytes

    def __getSDNTxPackets(self, portNumber):
        sdn_packets = 0
        IP_partner = self.getIPPartner(portNumber)
        if IP_partner == -1:
            return -1
        sdn_packets += self.getTxPackets(portNumber) - self.getRxPackets(IP_partner)
        return sdn_packets

    def getSDNTxBytes(self, portNumber):
        p = self.ports[portNumber]
        index = (p['sdn_tx_bytes_buffer_index'] - 1) % DELTA_WINDOW
        return p['sdn_tx_bytes_buffer'][index]

    def getSDNTxPackets(self, portNumber):
        p = self.ports[portNumber]
        index = (p['sdn_tx_packets_buffer_index'] - 1) % DELTA_WINDOW
        return p['sdn_tx_packets_buffer'][index]

    def getRxBytes(self, portNumber):
        return self.ports[portNumber]['rx_bytes']

    def getTxBytes(self, portNumber):
        return self.ports[portNumber]['tx_bytes']

    def getRxBytesRate(self, portNumber, lldp_noise=0):
        p = self.ports[portNumber]
        t2 = p['rx_bytes_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_rx = p['rx_bytes_buffer'][t1]
        t2_rx = p['rx_bytes_buffer'][t2]
        if t2_rx == 0:
            return 0
        return float(t1_rx - t2_rx - lldp_noise) / DELTA_WINDOW

    def getRxPacketsRate(self, portNumber, lldp_noise=0):
        p = self.ports[portNumber]
        t2 = p['rx_packets_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_rx = p['rx_packets_buffer'][t1]
        t2_rx = p['rx_packets_buffer'][t2]
        if t2_rx == 0:
            return 0
        return float(t1_rx - t2_rx - lldp_noise) / DELTA_WINDOW

    def getTxBytesRate(self, portNumber, lldp_noise=0):
        p = self.ports[portNumber]
        t2 = p['tx_bytes_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_tx = p['tx_bytes_buffer'][t1]
        t2_tx = p['tx_bytes_buffer'][t2]
        if t2_tx == 0:
            return 0
        return float(t1_tx - t2_tx - lldp_noise) / DELTA_WINDOW

    def getTxPacketsRate(self, portNumber, lldp_noise=0):
        p = self.ports[portNumber]
        t2 = p['tx_packets_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_tx = p['tx_packets_buffer'][t1]
        t2_tx = p['tx_packets_buffer'][t2]
        if t2_tx == 0:
            return 0
        return float(t1_tx - t2_tx - lldp_noise) / DELTA_WINDOW

    def getSDNRxBytesRate(self, portNumber):
        p = self.ports[portNumber]
        t2 = p['sdn_rx_bytes_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_rx = p['sdn_rx_bytes_buffer'][t1]
        t2_rx = p['sdn_rx_bytes_buffer'][t2]
        if t2_rx == 0:
            return 0
        return float(t1_rx - t2_rx) / DELTA_WINDOW

    def getSDNRxPacketsRate(self, portNumber):
        p = self.ports[portNumber]
        t2 = p['sdn_rx_packets_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_rx = p['sdn_rx_packets_buffer'][t1]
        t2_rx = p['sdn_rx_packets_buffer'][t2]
        if t2_rx == 0:
            return 0
        return float(t1_rx - t2_rx) / DELTA_WINDOW

    def getSDNTxBytesRate(self, portNumber):
        p = self.ports[portNumber]
        t2 = p['sdn_tx_bytes_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_tx = p['sdn_tx_bytes_buffer'][t1]
        t2_tx = p['sdn_tx_bytes_buffer'][t2]
        if t2_tx == 0:
            return 0
        return float(t1_tx - t2_tx) / DELTA_WINDOW

    def getSDNTxPacketsRate(self, portNumber):
        p = self.ports[portNumber]
        t2 = p['sdn_tx_packets_buffer_index']
        t1 = (t2 - 1) % DELTA_WINDOW
        t1_tx = p['sdn_tx_packets_buffer'][t1]
        t2_tx = p['sdn_tx_packets_buffer'][t2]
        if t2_tx == 0:
            return 0
        return float(t1_tx - t2_tx) / DELTA_WINDOW

    def setRxBytes(self, portNumber, rx_bytes, lldp_noise=0):
        p = self.ports[portNumber]
        t1 = p['rx_bytes_buffer_index']
        p['rx_bytes_buffer_index'] = (p['rx_bytes_buffer_index'] + 1) % DELTA_WINDOW
        p['rx_bytes_buffer'][t1] = rx_bytes
        t2 = (t1 - 1) % DELTA_WINDOW
        old_rx = p['rx_bytes_buffer'][t2]
        if old_rx != 0:
            self.ports[portNumber]['rx_bytes'] += rx_bytes - old_rx - lldp_noise
            # update sdn
            # t1_sdn = p['sdn_rx_bytes_buffer_index']
            # p['sdn_rx_bytes_buffer_index'] = (p['sdn_rx_bytes_buffer_index']+1)%DELTA_WINDOW
            # p['sdn_rx_bytes_buffer'][t1_sdn] = self.__getSDNRxBytes(portNumber)

    def setTxBytes(self, portNumber, tx_bytes, lldp_noise=0):
        p = self.ports[portNumber]
        t1 = p['tx_bytes_buffer_index']
        p['tx_bytes_buffer_index'] = (p['tx_bytes_buffer_index'] + 1) % DELTA_WINDOW
        p['tx_bytes_buffer'][t1] = tx_bytes
        t2 = (t1 - 1) % DELTA_WINDOW
        old_tx = p['tx_bytes_buffer'][t2]
        if old_tx != 0:
            self.ports[portNumber]['tx_bytes'] += tx_bytes - old_tx - lldp_noise
            # update sdn
            # t1_sdn = p['sdn_tx_bytes_buffer_index']
            # p['sdn_tx_bytes_buffer_index'] = (p['sdn_tx_bytes_buffer_index']+1)%DELTA_WINDOW
            # p['sdn_tx_bytes_buffer'][t1_sdn] = self.__getSDNTxBytes(portNumber)

    def setRxPackets(self, portNumber, rx_packets, lldp_noise=0):
        p = self.ports[portNumber]
        t1 = p['rx_packets_buffer_index']
        p['rx_packets_buffer_index'] = (p['rx_packets_buffer_index'] + 1) % DELTA_WINDOW
        p['rx_packets_buffer'][t1] = rx_packets
        t2 = (t1 - 1) % DELTA_WINDOW
        old_rx = p['rx_packets_buffer'][t2]
        if old_rx != 0:
            self.ports[portNumber]['rx_packets'] += rx_packets - old_rx - lldp_noise
            # update sdn
            # t1_sdn = p['sdn_rx_packets_buffer_index']
            # p['sdn_rx_packets_buffer_index'] = (p['sdn_rx_packets_buffer_index']+1)%DELTA_WINDOW
            # p['sdn_rx_packets_buffer'][t1_sdn] = self.__getSDNRxPackets(portNumber)

    def setTxPackets(self, portNumber, tx_packets, lldp_noise=0):
        p = self.ports[portNumber]
        t1 = p['tx_packets_buffer_index']
        p['tx_packets_buffer_index'] = (p['tx_packets_buffer_index'] + 1) % DELTA_WINDOW
        p['tx_packets_buffer'][t1] = tx_packets
        t2 = (t1 - 1) % DELTA_WINDOW
        old_tx = p['tx_packets_buffer'][t2]
        if old_tx != 0:
            self.ports[portNumber]['tx_packets'] += tx_packets - old_tx - lldp_noise
            # update sdn
            # t1_sdn = p['sdn_tx_packets_buffer_index']
            # p['sdn_tx_packets_buffer_index'] = (p['sdn_tx_packets_buffer_index']+1)%DELTA_WINDOW
            # p['sdn_tx_packets_buffer'][t1_sdn] = self.__getSDNTxPackets(portNumber)

    def getRxPackets(self, portNumber):
        return self.ports[portNumber]['rx_packets']

    def getTxPackets(self, portNumber):
        return self.ports[portNumber]['tx_packets']

    def __has_rx_lldp_noise(self, portName, portNumber):
        if portName[0:3] == 'cro':
            return 0
        elif portNumber != 1:
            return 1
        return 0

    def updateSDNStats(self):
        self.__seconds_from_start += 1
        for portNumber in self.ports:
            p = self.ports[portNumber]
            rx_noise = self.__has_rx_lldp_noise(self.getPortName(portNumber), portNumber)
            t1_sdn = p['sdn_rx_bytes_buffer_index']
            p['sdn_rx_bytes_buffer_index'] = (p['sdn_rx_bytes_buffer_index'] + 1) % DELTA_WINDOW
            p['sdn_rx_bytes_buffer'][t1_sdn] = self.__getSDNRxBytes(portNumber) + (
                self.__seconds_from_start * LLDP_NOISE_BYTE_S * rx_noise)
            t1_sdn = p['sdn_tx_bytes_buffer_index']
            p['sdn_tx_bytes_buffer_index'] = (p['sdn_tx_bytes_buffer_index'] + 1) % DELTA_WINDOW
            p['sdn_tx_bytes_buffer'][t1_sdn] = self.__getSDNTxBytes(portNumber) - (
                self.__seconds_from_start * LLDP_NOISE_BYTE_S)
            t1_sdn = p['sdn_rx_packets_buffer_index']
            p['sdn_rx_packets_buffer_index'] = (p['sdn_rx_packets_buffer_index'] + 1) % DELTA_WINDOW
            p['sdn_rx_packets_buffer'][t1_sdn] = self.__getSDNRxPackets(portNumber) + (
                self.__seconds_from_start * LLDP_NOISE_PACK_S * rx_noise)
            t1_sdn = p['sdn_tx_packets_buffer_index']
            p['sdn_tx_packets_buffer_index'] = (p['sdn_tx_packets_buffer_index'] + 1) % DELTA_WINDOW
            p['sdn_tx_packets_buffer'][t1_sdn] = self.__getSDNTxPackets(portNumber) - (
                self.__seconds_from_start * LLDP_NOISE_PACK_S)
