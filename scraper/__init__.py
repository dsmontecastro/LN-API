import json

from fake_useragent import UserAgent
from selenium.webdriver import Firefox, FirefoxProfile, FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType

from models.entry import Entry
from models.targets import Target
from . import ciw, jnc, kod, sea


class Scraper(object):

    def __init__(self, proxy = '', headless = True):

        self.agent = UserAgent()

        print('Creating driver...')
    
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
    
        print('Driver successfully created!')

    def quit(self): self._driver.quit()

    def test(self, target: Target):
        entries = self._scrape(target)
        self.save(entries)

    def save(self, entries: list[Entry]):

        jsons = [entry.json() for entry in entries]

        with open('test.json', 'w') as f:
            json.dump(jsons, f)


    def run(self, target: Target = Target.ALL):

        entries: list[Entry] = []

        if target == Target.ALL:
            entries += self._scrapeAll()

        else: entries += self._scrape(target)

        print(f'Total: {len(entries)} entries')
        self.save(entries)


    # Scraper Commands
    
    def _scrape(self, target: Target) -> list[Entry]:

        entries: list[Entry] = []

        match(target):
            case Target.CIW:
                entries += ciw.scrape(self._driver)
            case Target.JNC:
                entries += jnc.scrape(self._driver)
            case Target.KOD:
                entries += kod.scrape(self._driver)
            case Target.SEA:
                entries += sea.scrape(self._driver)

        return entries

    
    def _scrapeAll(self) -> list[Entry]:

        entries: list[Entry] = []

        entries += ciw.scrape(self._driver)
        entries += jnc.scrape(self._driver)
        entries += kod.scrape(self._driver)
        entries += sea.scrape(self._driver)

        return entries