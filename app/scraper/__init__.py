from fake_useragent import UserAgent
from selenium.webdriver import Firefox, FirefoxProfile, FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType

from models.entry import Entry
from models.table import Tables

from logger import log
from . import ciw, jnc, kod, sea, yen


class Scraper(object):

    def __init__(self, proxy = '', headless = True):

        log.info('> Creating driver...')

        self.agent = UserAgent()
    
        options = FirefoxOptions()
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
        self._driver = Firefox(options = options)
        self._driver.maximize_window()
    
        log.info('> Driver successfully created!')


    def quit(self): self._driver.quit()


    def run(self, table: Tables = Tables.ALL) -> list[Entry]:

        entries: list[Entry] = []

        if table == Tables.ALL:
            for table in Tables:
                entries += self._scrape(table)

        else: entries += self._scrape(table)

        log.info(f'> Total: {len(entries)} entries')
        return entries


    # Scraper Commands
    
    def _scrape(self, target: Tables) -> list[Entry]:

        entries: list[Entry] = []

        match(target):
            case Tables.CIW:
                entries += ciw.scrape(self._driver)
            case Tables.JNC:
                entries += jnc.scrape(self._driver)
            case Tables.KOD:
                entries += kod.scrape(self._driver)
            case Tables.SEA:
                entries += sea.scrape(self._driver)
            case Tables.YEN:
                entries += yen.scrape(self._driver)

        return entries