# Log config
RRD_LOG_PATH = "/home/user/workspace/OSHI-Monitoring/logs/"
TRAFFIC_MONITOR_LOG_PATH = "/home/user/workspace/OSHI-Monitoring/logs/"

# RRD config
RRD_STEP = "300"
RRD_STORE_PATH = "/home/user/workspace/OSHI-Monitoring/rrd/"  # /home/user/workspace/OSHI-Monitoring/rrd/

# Traffic monitor config
PORT_BYTES_STATS_PATH = "/home/user/workspace/OSHI-Monitoring/port_stats/bytes_stats"
PORT_PACKETS_STATS_PATH = "/home/user/workspace/OSHI-Monitoring/port_stats/packets_stats"
REQUEST_INTERVAL = 1  # Stats request time interval. MUST BE 1
DELTA_WINDOW = 20  # RATE WINDOWS
LLDP_NOISE_BYTE_S = 19
LLDP_NOISE_PACK_S = 0.365

'''

                                                OUT=out+lldp        OUT=out+lldp
                                                IN =in              IN =in

                                          +-------|vi0 |------|vi1 |------|vi2 |----------------+
                                          |                                                     |
                                          |                                                     |
    OUT=out+lldp                        ----                                                    |
    IN =in                              eth0                 SWITCH                             |
                                        ----                                                    |
    sdn_out=out-in(vi)=OUT-lldp-in(vi)    |                                                     |
    sdn_in =in-out(vi)=IN-OUT(vi)-lldp    |                                                     |
                                          |                                                     |
                                          |                                                     |
                                          +-------------------|eth1|------|eth2|----------------+

                                                            OUT=out+lldp
                                                            IN =in +lldp
                                                            sdn_out=out-in(vi)=OUT-lldp-IN(vi)
                                                            sdn_in =in-out(vi)=IN-lldp-OUT(vi)+lldp=IN-OUT(vi)

'''