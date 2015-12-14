# Log config
import logging

BASE_PATH = "/home/user/workspace/OSHI-monitoring/"

# Logging configuration
RRD_LOG_PATH = BASE_PATH + "logs/"
TRAFFIC_MONITOR_LOG_PATH = BASE_PATH + "logs/"
LOG_LEVEL = logging.INFO
ENABLE_FILE_LOGGING = False

# OUTPUT Levels
NO_OUTPUT = 'NO_OUTPUT'
SUMMARY_OUTPUT = 'SUMMARY_OUTPUT'  # How many RRDs where updated since the last update
DETAILED_OUTPUT = 'DETAILED_OUTPUT'  # Detailed output about RRD updates (current values for each variable)
OUTPUT_LEVEL = SUMMARY_OUTPUT

# Traffic monitor config
REQUEST_INTERVAL = 1
LLDP_NOISE_BYTE_S = 19
LLDP_NOISE_PACK_S = 0.365

# RRD config
RRD_STEP = 30
RRD_STORE_PATH = BASE_PATH + "rrd/"
RRD_DATA_SOURCE_TYPE = "GAUGE"
RRD_DATA_SOURCE_HEARTBEAT = "60"
