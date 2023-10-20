import json

from selenium.webdriver import Firefox, FirefoxOptions
from models.targets import Target
from models.entry import Entry

# Individual Scrapers
from . import ciw


class Scraper(object):

    def __init__(self):
        options = FirefoxOptions()
        options.add_argument('--headless')
        self._driver = Firefox(options = options)

    def quit(self): self._driver.quit()

    def test(self, target: Target):
        entries = self._scrape(target)
        self.save(entries)

    def save(self, entries: list[Entry]):

        jsons = [entry.json() for entry in entries]

        with open('data.json', 'w') as f:
            json.dump(jsons, f)


    def run(self, target: Target = Target.ALL):

        entries: list[Entry] = []

        if target == Target.ALL:
            entries += self._scrapeAll()

        else: entries += self._scrape(target)
    
        self.save(entries)


    # Scraper Commands
    
    def _scrape(self, target: Target) -> list[Entry]:

        entries: list[Entry] = []

        match(target):
            case Target.CIW:
                entries += ciw.scrape(self._driver)

        return entries

    
    def _scrapeAll(self) -> list[Entry]:

        entries: list[Entry] = []

        entries += ciw.scrape(self._driver)

        return entries