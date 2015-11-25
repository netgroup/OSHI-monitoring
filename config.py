# Log config
import logging

BASE_PATH = "/home/user/workspace/OSHI-monitoring/"

# Logging configuration
RRD_LOG_PATH = BASE_PATH + "logs/"
TRAFFIC_MONITOR_LOG_PATH = BASE_PATH + "logs/"
LOG_LEVEL = logging.INFO
ENABLE_FILE_LOGGING = False

# Traffic monitor config
REQUEST_INTERVAL = 1
LLDP_NOISE_BYTE_S = 19
LLDP_NOISE_PACK_S = 0.365

# RRD config
RRD_STEP = 30
RRD_STORE_PATH = BASE_PATH + "rrd/"
RRD_DATA_SOURCE_TYPE = "GAUGE"
RRD_DATA_SOURCE_HEARTBEAT = "60"
