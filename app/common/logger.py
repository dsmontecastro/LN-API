import logging
from selenium.webdriver.remote.remote_connection import LOGGER

LOGGER.setLevel(logging.ERROR)  # Disable Selenium-based Logging
# logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.ERROR)


NAME = 'base_logger'
FORMAT = '[%(levelname)s] : %(message)s'

logging.basicConfig(format = FORMAT, level = logging.DEBUG)
log = logging.getLogger(NAME)