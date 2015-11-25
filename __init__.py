import logging
import os
import config

log = logging.getLogger('oshi_monitoring')
log.setLevel(config.LOG_LEVEL)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(config.LOG_LEVEL)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)

# add the handlers to logger
log.addHandler(ch)

if config.ENABLE_FILE_LOGGING:
    fh_complete = logging.FileHandler(os.path.join(config.RRD_LOG_PATH, "complete.log"))
    fh_complete.setLevel(config.LOG_LEVEL)
    fh_complete.setFormatter(formatter)
    log.addHandler(fh_complete)

log.propagate = False
