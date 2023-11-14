import logging

BASE = 'base_logger'
LEVEL = logging.INFO
FORMAT = '[%(levelname)s] : %(message)s'

logging.basicConfig(format = FORMAT, level = LEVEL)
log = logging.getLogger(BASE)