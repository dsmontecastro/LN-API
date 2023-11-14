import logging

BASE = 'base_logger'
LEVEL = logging.DEBUG

logging.basicConfig(level = LEVEL)
log = logging.getLogger(BASE)