import logging
from selenium.webdriver.remote.remote_connection import LOGGER

# Disable Selenium-based Logging
logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


NAME = 'base_logger'
FORMAT = '[%(levelname)s] : %(message)s'

logging.basicConfig(format = FORMAT, level = logging.DEBUG)
log = logging.getLogger(NAME)