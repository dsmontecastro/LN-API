from fake_useragent import UserAgent
from selenium.webdriver import Firefox, FirefoxProfile, FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType

from ..common.logger import log
from ..database.models.entry import Entry
from ..database.models.table import Tables

from .targets import ciw, jnc, kod, sea, yen


log_level = 'TRACE'

class Scraper(object):

    def __init__(self, proxy = '', headless = True):

        log.info('> Creating driver...')

        self.agent = UserAgent()
    
        options = FirefoxOptions()
        options.add_argument(log_level)
        if headless: options.add_argument('--headless')

        profile = FirefoxProfile()
        profile.set_preference('useAutomationExtension', False)
        profile.set_preference('webdriver.log.file', 'log.txt')
        profile.set_preference('general.useragent.override', self.agent.firefox)

        if proxy: options.proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            "socksVersion": 5,
            "socksProxy": proxy,
            'httpProxy': proxy,
            'sslProxy': proxy,
            'noProxy':''
        })

        options.profile = profile
        self._driver = Firefox(options)
        self._driver.maximize_window()
    
        log.info('> Driver successfully created!')


    def quit(self): self._driver.quit()


    def run(self, table: Tables = Tables.ALL, limit: int = 0) -> list[Entry]:

        entries: list[Entry] = []

        if table == Tables.ALL:
            for table in Tables:
                entries += self.__scrape(table, limit)

        else: entries += self.__scrape(table, limit)

        log.info(f'> Total: {len(entries)} entries')
        return entries


    # Scraper Commands
    
    def __scrape(self, target: Tables, limit: int) -> list[Entry]:

        entries: list[Entry] = []

        match(target):
            case Tables.CIW:
                entries += ciw.scrape(self._driver, limit)
            case Tables.JNC:
                entries += jnc.scrape(self._driver, limit)
            case Tables.KOD:
                entries += kod.scrape(self._driver, limit)
            case Tables.SEA:
                entries += sea.scrape(self._driver, limit)
            case Tables.YEN:
                entries += yen.scrape(self._driver, limit)

        return entries