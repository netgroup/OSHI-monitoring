import logging
import os
import config

version = '1.0.0.dev1'

log = logging.getLogger('oshi_monitoring')
log.setLevel(config.LOG_LEVEL)
ch = logging.StreamHandler()
ch.setLevel(config.LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
log.addHandler(ch)

if config.ENABLE_FILE_LOGGING:
    fh_complete = logging.FileHandler(os.path.join(config.RRD_LOG_PATH, "complete.log"))
    fh_complete.setLevel(config.LOG_LEVEL)
    fh_complete.setFormatter(formatter)
    log.addHandler(fh_complete)

log.propagate = False
