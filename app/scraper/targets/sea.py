from enum import Enum

from selenium.webdriver.common.by import By as BY
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Waiter

from ...common.logger import log
from ...database.models.table import Tables
from ...database.models.entry import Entry, Media, Person


# region : Constants -----------------------------------------------------------------------------------------

TABLE = Tables.SEA
URL = 'https://webcache.googleusercontent.com/search?q=cache:'  # Bypasses the actual site's CloudFlare
CSS = BY.CSS_SELECTOR
T_SLOW = 15
T_FAST = 5

class MODE(Enum):
    DIGITAL = 'https://sevenseasentertainment.com/digital/'
    PHYSICAL = 'https://sevenseasentertainment.com/release-dates/'

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def _getCrew(par: str) -> list[Person]:

    people: list[Person] = []
    items = par.split('\n')

    for item in items:
        [ position, name ] = item.split(': ')
        people.append(Person(name, position))

    return people


def _getTitle(title: str, format: str) -> str:
    return title.replace(f' ({format})', '')


def _getMedia(par: str, format: str) -> Media:

    info = par.replace('\n', ': ').split(': ')

    price_index = info.index('Price') + 1
    isbn_index = info.index('ISBN') + 1
    
    return Media(
        format = format,
        isbn = info[isbn_index],
        price = info[price_index]
    )

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver, limit: int) -> list[Entry]:

    entries: list[Entry] = []

    try: entries += _scrape(driver, limit, MODE.DIGITAL)
    except TimeoutException:
        log.exception('Error: SEA.DIGITAL has failed.')

    try: entries += _scrape(driver, limit, MODE.PHYSICAL)
    except TimeoutException:
        log.exception('Error: SEA.PHYSICAL has failed.')

    return entries


def _scrape(driver: WebDriver, limit: int, mode: MODE) -> list[Entry]:

    # Load Page
    driver.get(URL + mode.value)
    medium = mode.name.lower()

    # Load all Entries
    main = driver.find_element(CSS, 'table#releasedates > tbody')

    # Entry Pre-processing
    entries: list[Entry] = []
    items: list[WebElement] = main.find_elements(CSS, 'tr#volumes')
    for item in items[:limit]:

        try:

            cols = item.find_elements(CSS, 'td')
            format = cols[2].text

            series = cols[1].find_element(CSS, 'a')
            url = series.get_attribute('href')

            # Check if URL exists and Format is Light/Novel
            if url and 'novel' in format.lower():
                entries.append(
                    Entry(
                        url = url,
                        date = cols[0].text,
                        title = _getTitle(series.text, format),
                        table = TABLE
                    )
                )

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')
 

    # Throttle to avoid Google's Bot-Detection
    driver.implicitly_wait(T_SLOW)


    # Entry Completion
    final: list[Entry] = []
    for entry in entries:

        try:

            url = entry.url

            if url: # Check if URL exists

                # Go to Book Page
                driver.get(URL + url)

                # Check if Book Page leads to a 404
                try: Waiter(driver, timeout = T_FAST).until(
                    EC.visibility_of_element_located((CSS, 'body > a'))
                )

                # Proceed if Book Page is valid
                except TimeoutException:

                    page = driver.find_element(CSS, 'div.container > div#content > div')
                    meta = page.find_elements(CSS, 'div#volume-meta > p')
                    cover = page.find_element(CSS, 'div#volume-cover > img')

                    # Info: Media
                    media = _getMedia(meta[0].text, medium)

                    # Meta: Blurb
                    blurb = f'{meta[4].text}\n'
                    for m in meta[5:]: blurb += m.text

                    # Meta: Credits
                    credits: list[Person] = []
                    authors = meta[0].find_elements(CSS, 'span')
                    credits = [ Person(author.text, 'Story/Art') for author in authors ]
                    credits += _getCrew(meta[1].text)

                    # Finalize Entry
                    entry.blurb = blurb
                    entry.cover = cover.get_attribute('src') or ''
                    entry.credits = credits
                    entry.media = [ media ]

                    final.append(entry)
                
            driver.implicitly_wait(T_SLOW)

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')

    return final