import logging

# Disable Selenium-based Logging
logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


FILE = 'logs.log'
NAME = 'base_logger'
FRMT = '%(asctime)s : [%(levelname)s] : %(message)s'

logging.basicConfig(
    format = FRMT,
    # filemode = 'a',
    # filename = 'logs.txt',
    level = logging.DEBUG
)

log = logging.getLogger(NAME)

# console = logging.StreamHandler()
# log.addHandler(console)