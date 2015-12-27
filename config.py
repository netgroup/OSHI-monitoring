# Log config
import logging
import os

version = '1.0.0'

BASE_PATH = "/home/user/workspace/OSHI-monitoring/"

# Logging configuration
RRD_LOG_PATH = BASE_PATH + "logs/"
TRAFFIC_MONITOR_LOG_PATH = BASE_PATH + "logs/"
LOG_LEVEL = logging.DEBUG
ENABLE_FILE_LOGGING = True

log = logging.getLogger('oshi_monitoring')
log.setLevel(LOG_LEVEL)
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
log.addHandler(ch)

if ENABLE_FILE_LOGGING:
    log_file_path = os.path.join(RRD_LOG_PATH, "OSHI-monitoring.log")
    fh_complete = logging.FileHandler(log_file_path)
    fh_complete.setLevel(LOG_LEVEL)
    fh_complete.setFormatter(formatter)
    log.addHandler(fh_complete)
    log.info("Enabled logging on file in %s", log_file_path)

log.propagate = False

# OUTPUT Levels
NO_OUTPUT = 'NO_OUTPUT'
SUMMARY_OUTPUT = 'SUMMARY_OUTPUT'  # How many RRDs where updated since the last update
DETAILED_OUTPUT = 'DETAILED_OUTPUT'  # Detailed output about RRD updates (current values for each variable)
OUTPUT_LEVEL = DETAILED_OUTPUT

# Traffic monitor config
REQUEST_INTERVAL = 1
LLDP_NOISE_BYTE_S = 19
LLDP_NOISE_PACK_S = 0.365

# RRD config
RRD_STEP = 30
RRD_STORE_PATH = BASE_PATH + "rrd/"
RRD_DATA_SOURCE_TYPE = "GAUGE"
RRD_DATA_SOURCE_HEARTBEAT = "60"
