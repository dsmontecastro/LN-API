import time
from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Waiter
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

from models.entry import Entry, Media
from models.table import Tables


# region : Constants & Classes -------------------------------------------------------------------------------

TABLE = Tables.YEN
URL = 'https://yenpress.com/calendar'
CSS = BY.CSS_SELECTOR
PTH = BY.XPATH

# Selenium Shortcuts
POLL = 5
WAIT = 10
MONTHS = 3
SCROLL_UP = 'window.scrollTo(0,0)'
SCROLL_DOWN = 'window.scrollTo(0,document.body.scrollHeight)'

# CSS Shortcuts
ACTIVE = 'div.calendar-slider > div.swiper-wrapper > div.calendar-dates.active'

class Book(object):

    def __init__(self, url = '', format = '', volume = ''):
        self.url: str = url
        self.format: str = format
        self.volume: str = volume
    
    def __str__(self):
        return f'{self.volume}:  @{self.url} [{self.format}]'

# endregion --------------------------------------------------------------------------------------------------


def scrape(driver: WebDriver) -> list[Entry]:

    print(f'Extracting from {URL}...')

    driver.get(URL)
    body = driver.find_element(CSS, 'div.calendar-wrapper')
    calendar = body.find_element(CSS, 'div.calendar-slider')
    heading = driver.find_element(CSS, 'div.releases-heading')

    def sleep(time = WAIT):
        try: Waiter(driver, time, time).until(lambda _: False)
        except TimeoutException: pass


    # Process the next <MONTHS> months' Book Pages
    i = 0
    urls: list[str] = []
    month = calendar.find_element(CSS, ACTIVE)
    while i < MONTHS:

        # Scroll-To and Click MONTH button
        driver.execute_script('arguments[0].scrollIntoView();', heading)
        sleep(3)
        month.click()

        # Scroll-Down to load all Pages
        driver.execute_script(SCROLL_DOWN)
        sleep(3)

        # Get all Book Page URLs
        for page in driver.find_elements(CSS, 'div.releases-append > div.book-section > div > a'):

            # Check if FORMAT is some book (Novel/Audio)
            format = page.find_element(CSS, 'span.upper').text
            if format.lower() == 'audio' or format.lower() == 'novels':

                # Check if Book Page URL is valid
                url = page.get_attribute('href') or ''
                if url: urls.append(url)

        # Error Handling
        while True:

            # Move to next month
            try: month = month.find_element(PTH, 'following-sibling::div[1]')

            # Refresh stale HTML elements
            except StaleElementReferenceException:
                body = driver.find_element(CSS, 'div.calendar-wrapper')
                calendar = body.find_element(CSS, 'div.calendar-slider')
                heading = driver.find_element(CSS, 'div.releases-heading')
                month = calendar.find_element(CSS, ACTIVE)

            # Break loop on last month
            except NoSuchElementException: break

        i += 1


    # Process all Book Pages
    entries: list[Entry] = []
    for url in urls:

        driver.get(url)

        if not driver.title.lower().startswith('page not found'):
            print(f'@{driver.current_url}')


    return entries