# Log config
import logging

BASE_PATH = "/home/user/workspace/OSHI-monitoring/"

RRD_LOG_PATH = BASE_PATH+"logs/"
TRAFFIC_MONITOR_LOG_PATH = BASE_PATH+"logs/"
LOG_LEVEL = logging.ERROR

# RRD config
RRD_STEP = "300"
RRD_STORE_PATH = BASE_PATH+"rrd/"  # /home/user/workspace/OSHI-Monitoring/rrd/
RRD_DATA_SOURCE_TYPE = "GAUGE"
RRD_DATA_SOURCE_HEARTBEAT = "600"

# Traffic monitor config
PORT_BYTES_STATS_PATH = BASE_PATH+"port_stats/bytes_stats"
PORT_PACKETS_STATS_PATH = BASE_PATH+"port_stats/packets_stats"
REQUEST_INTERVAL = 1  # Stats request time interval. MUST BE 1
DELTA_WINDOW = 20  # RATE WINDOWS
LLDP_NOISE_BYTE_S = 19
LLDP_NOISE_PACK_S = 0.365
