import logging
import os
import config

RX_BYTES = 'rx_bytes'
TX_BYTES = 'tx_bytes'
RX_PACKETS = 'rx_packets'
TX_PACKETS = 'tx_packets'
SDN_RX_BYTES = 'sdn_rx_bytes'
SDN_TX_BYTES = 'sdn_tx_bytes'
SDN_RX_PACKETS = 'sdn_rx_packets'
SDN_TX_PACKETS = 'sdn_tx_packets'
IS_VIRTUAL = 'is_virtual'
PORT_NAME = 'name'

PORT_STATS = {RX_BYTES, TX_BYTES,
              RX_PACKETS, TX_PACKETS,
              SDN_RX_BYTES, SDN_TX_BYTES,
              SDN_RX_PACKETS, SDN_TX_PACKETS}

IP_PARTNER_PORT_NUMBER = 'ip_partner_port_number'

log = logging.getLogger('oshi_monitoring')


class SwitchStats:
    def __init__(self, datapath):
        log.debug("Initializing SwitchStat for %s datapath", datapath.id)
        self.data_path = datapath
        self.data_path_id = datapath.id
        self.device_name = ''
        self.ports = {}
        self.__seconds_from_start = 0

    def add_port(self, port_number, is_virtual=False, port_name=''):
        """
        Add a single port to stats.

        :param port_number: port number of the port to add
        """
        self.ports[port_number] = {}
        self.ports[port_number][RX_BYTES] = 0
        self.ports[port_number][TX_BYTES] = 0
        self.ports[port_number][RX_PACKETS] = 0
        self.ports[port_number][TX_PACKETS] = 0
        self.ports[port_number][SDN_RX_BYTES] = 0
        self.ports[port_number][SDN_TX_BYTES] = 0
        self.ports[port_number][SDN_RX_PACKETS] = 0
        self.ports[port_number][SDN_TX_PACKETS] = 0
        self.ports[port_number][IS_VIRTUAL] = is_virtual
        self.ports[port_number][PORT_NAME] = port_name

    def get_port_name(self, port_number):
        """
        Return the name of the specified port.

        :param port_number:
        :return: port name
        :rtype: str
        """
        return self.ports[port_number][PORT_NAME]

    def set_ip_partner_port_number(self, port_number, partner_port_number):
        """
        Set the port number of the IP partner for a given port.

        This can be used to match ports between partners like:
            ss.set_ip_partner_port_number(in_port, out_port)
            ss.set_ip_partner_port_number(out_port, in_port)

        :param port_number:
        :param partner_port_number:
        """
        log.debug("Setting partner port number for port %s (%s). Partner: %s (%s)", port_number,
                  self.get_port_name(port_number), partner_port_number, self.get_port_name(partner_port_number))
        self.ports[port_number][IP_PARTNER_PORT_NUMBER] = partner_port_number

    def get_ip_partner_port_number(self, port_number):
        """
        Return the port number of the IP partner, given a port number.

        :param port_number:
        :return: Partner port number or -1 if no relationship has been defined for the specified port number.
        """
        return self.ports[port_number][IP_PARTNER_PORT_NUMBER]

    def get_rx_bytes(self, port_number):
        """
        Return received bytes count for the specified port.

        :param port_number:
        :return: bytes count
        """
        return self.ports[port_number][RX_BYTES]

    def get_tx_bytes(self, port_number):
        """
        Return transmitted bytes count for the specified port.

        :param port_number:
        :return: bytes count
        """
        return self.ports[port_number][TX_BYTES]

    def get_rx_packets(self, port_number):
        """
        Return received packet count for the specified port.

        :param port_number:
        :return: packet count
        """
        return self.ports[port_number][RX_PACKETS]

    def get_tx_packets(self, port_number):
        """
        Return transmitted packet count for the specified port.

        :param port_number:
        :return: packet count
        """
        return self.ports[port_number][TX_PACKETS]

    def get_sdn_rx_bytes(self, port_number):
        return self._get_sdn_stat(port_number, SDN_RX_BYTES)

    def get_sdn_tx_bytes(self, port_number):
        return self._get_sdn_stat(port_number, SDN_TX_BYTES)

    def get_sdn_rx_packets(self, port_number):
        return self._get_sdn_stat(port_number, SDN_RX_PACKETS)

    def get_sdn_tx_packets(self, port_number):
        return self._get_sdn_stat(port_number, SDN_TX_PACKETS)

    def _get_sdn_stat(self, port_number, stat_key):
        return self.ports[port_number][stat_key]

    def _update_stat(self, port_number, stat_key, stat_value, lldp_noise=0):
        """
        Update stat value filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param stat_value:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        log.debug("Update %s stat for %s datapath, port %s with value: %s", stat_key, self.data_path_id, port_number,
                  stat_value)
        port = self.ports[port_number]
        log.debug("Current values for port %s, stat %s. Value: %s", port_number, stat_key, port[stat_key])
        updated_value = stat_value - lldp_noise
        log.debug("Updating %s for port %s with value: %s", stat_key, port_number, updated_value)
        port[stat_key] += updated_value
        log.debug("New value for %s for port %s with value: %s", stat_key, port_number, port[stat_key])
        log.debug("Current values for port %s, stat %s. Current value: %s", port_number, stat_key, port[stat_key])

    def set_rx_bytes(self, port_number, rx_bytes, lldp_noise=0):
        """
        Update received byte count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param rx_bytes:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, RX_BYTES, rx_bytes, lldp_noise)

    def set_tx_bytes(self, port_number, tx_bytes, lldp_noise=0):
        """
        Update transmitted byte count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param tx_bytes:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, TX_BYTES, tx_bytes, lldp_noise)

    def set_rx_packets(self, port_number, rx_packets, lldp_noise=0):
        """
        Update received packet count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param rx_packets:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, RX_PACKETS, rx_packets, lldp_noise)

    def set_tx_packets(self, port_number, tx_packets, lldp_noise=0):
        """
        Update transmitted packet count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param tx_packets:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, TX_PACKETS, tx_packets, lldp_noise)

    def __compute_sdn_rx_bytes(self, port_number):
        """
        Compute and return received SDN traffic for the specified port.

        :param port_number:
        :return: Received SDN traffic in bytes
        """
        # received total - ip sent to partner
        return self.__compute_sdn_stat(port_number, RX_BYTES, TX_BYTES)

    def __compute_sdn_rx_packets(self, port_number):
        """
        Compute and return received SDN traffic for the specified port.

        :param port_number:
        :return: Received SDN traffic in packets
        """
        return self.__compute_sdn_stat(port_number, RX_PACKETS, TX_PACKETS)

    def __compute_sdn_tx_bytes(self, port_number):
        """
        Compute and return transmitted SDN traffic for the specified port.

        :param port_number:
        :return: Transmitted SDN traffic in bytes
        """
        return self.__compute_sdn_stat(port_number, TX_BYTES, RX_BYTES)

    def __compute_sdn_tx_packets(self, port_number):
        """
        Compute and return transmitted SDN traffic for the specified port.

        :param port_number:
        :return: Transmitted SDN traffic in packets
        """
        # sent total - ip received by partner
        return self.__compute_sdn_stat(port_number, TX_PACKETS, RX_PACKETS)

    def __compute_sdn_stat(self, port_number, grand_total_stat, stat_to_subtract):
        try:
            # compute SDN stats for PHY ports only, not for virtual
            port_name = self.get_port_name(port_number)
            if port_name.lower().startswith('vi'):
                return 0
            else:
                ip_partner_port_number = self.get_ip_partner_port_number(port_number)
                res = self.ports[port_number][grand_total_stat] - self.ports[ip_partner_port_number][stat_to_subtract]
                log.debug("Computing SDN stat for port %s (%s): %s (%s:%s:%s) - %s (%s:%s:%s) = %s",
                          port_number, port_name,
                          self.ports[port_number][grand_total_stat], port_number, port_name, grand_total_stat,
                          self.ports[ip_partner_port_number][stat_to_subtract], port_number, port_name,
                          stat_to_subtract, res)
                return res
        except KeyError:
            return 0

    @staticmethod
    def _has_rx_lldp_noise(port_name, port_number):
        if port_name[0:3] == 'cro':
            return 0
        elif port_number != 1:
            return 1
        return 0

    def _update_sdn_stats(self):
        """
        Update SDN stats for every port registered in this SwitchStats

        :return:
        """
        self.__seconds_from_start += 1
        log.debug("Updating SDN stats for all ports of %s datapath. Seconds from start: %s", self.data_path_id,
                  self.__seconds_from_start)
        for port_number in self.ports:
            port_name = self.get_port_name(port_number)
            log.debug("Updating SDN stats for port %s (%s)", port_number, port_name)
            port = self.ports[port_number]
            log.debug("Current stats for port %s (%s): %s", port_number, port_name, str(port))
            if self.ports[port_number][IS_VIRTUAL]:
                log.debug("Skip SDN stats update for port %s (%s) because it's a virtual port", port_number, port_name)
            else:
                # initialization
                rx_noise = SwitchStats._has_rx_lldp_noise(self.get_port_name(port_number), port_number)
                lldp_noise_bytes = self.__seconds_from_start * config.LLDP_NOISE_BYTE_S
                lldp_noise_packets = self.__seconds_from_start * config.LLDP_NOISE_PACK_S
                log.debug("LLDP Noise for port %s (%s). LLDP Noise BYTES: %s, Packets: %s. RX_NOISE: %s", port_number,
                          port_name, lldp_noise_bytes, lldp_noise_packets, rx_noise)
                # update SDN stats
                port[SDN_RX_BYTES] = self.__compute_sdn_rx_bytes(port_number) + lldp_noise_bytes * rx_noise
                port[SDN_TX_BYTES] = self.__compute_sdn_tx_bytes(port_number) - lldp_noise_bytes
                port[SDN_RX_PACKETS] = self.__compute_sdn_rx_packets(port_number) + lldp_noise_packets * rx_noise
                port[SDN_TX_PACKETS] = self.__compute_sdn_tx_packets(port_number) - lldp_noise_packets
                log.debug("Updated stats for port %s (%s): %s", port_number, port_name, str(port))

    def get_current_values(self, port_number):
        self._update_sdn_stats()
        return {RX_BYTES: self.get_rx_bytes(port_number),
                TX_BYTES: self.get_tx_bytes(port_number),
                RX_PACKETS: self.get_rx_packets(port_number),
                TX_PACKETS: self.get_tx_packets(port_number),
                SDN_RX_BYTES: self.get_sdn_rx_bytes(port_number),
                SDN_TX_BYTES: self.get_sdn_tx_bytes(port_number),
                SDN_RX_PACKETS: self.get_sdn_rx_packets(port_number),
                SDN_TX_PACKETS: self.get_sdn_tx_bytes(port_number)}
