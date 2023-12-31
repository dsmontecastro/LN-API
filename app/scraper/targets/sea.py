from enum import Enum

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from ._common import CSS, T_SLOW, error, sleep, wait_for

from ...common.logger import log
from ...database.models.table import Tables
from ...database.models.entry import Entry, Media, Person


# region : Constants -----------------------------------------------------------------------------------------

TABLE = Tables.SEA
URL = 'https://webcache.googleusercontent.com/search?q=cache:'  # Bypasses the actual site's CloudFlare

class MODE(Enum):
    DIGITAL = 'https://sevenseasentertainment.com/digital/'
    PHYSICAL = 'https://sevenseasentertainment.com/release-dates/'

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def __getCrew(par: str) -> list[Person]:

    people: list[Person] = []

    if par:
        items = par.split('\n')

        for item in items:
            [ position, name ] = item.split(': ')
            people.append(Person(name, position))

    return people


def __getTitle(title: str, format: str) -> str:
    return title.replace(f' ({format})', '')


def __getMedia(par: str, format: str) -> Media:

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

    log.debug(f'> {TABLE}')

    entries: list[Entry] = []
    limit //= 2

    try: entries += __preprocess(driver, limit, MODE.DIGITAL)
    except TimeoutException:
        log.exception('Error: SEA.DIGITAL has failed.')

    try: entries += __preprocess(driver, limit, MODE.PHYSICAL)
    except TimeoutException:
        log.exception('Error: SEA.PHYSICAL has failed.')

    return entries


def __preprocess(driver: WebDriver, limit: int, mode: MODE) -> list[Entry]:

    # Load Page
    driver.get(URL + mode.value)
    main = driver.find_element(CSS, 'table#releasedates > tbody')


    # Entry Pre-processing
    books: list[Entry] = []
    items: list[WebElement] = main.find_elements(CSS, 'tr#volumes')
    for item in items:

        try:

            cols = item.find_elements(CSS, 'td')
            format = cols[2].text

            series = cols[1].find_element(CSS, 'a')
            url = series.get_attribute('href')

            # Check if URL exists and Format is a Light/Novel
            if url and 'novel' in format.lower():
                books.append(
                    Entry(
                        url = url,
                        date = cols[0].text,
                        title = __getTitle(series.text, format),
                        table = TABLE
                    )
                )

        except Exception as e: error(e)
 

    # Throttle to avoid Google's Bot-Detection
    sleep(driver, T_SLOW)


    medium = mode.name.lower()
    entries: list[Entry] = []
    for book in books:
        entry = __process(driver, medium, book)
        if entry: entries.append(entry)
        if len(entries) >= limit: break
        sleep(driver, T_SLOW)

    return entries


def __process(driver: WebDriver, medium: str, entry: Entry) -> Entry | None:

        url = entry.url

        if url: # Check if URL exists

            try:

                # Go to Book Page
                driver.get(URL + url)
                log.debug(f'>> {driver.current_url:.50s}')

                # Check if Book Page leads to a 404
                err = wait_for(driver, CSS, 'body > a')
                if err: return


                # Primary Sections
                page = driver.find_element(CSS, 'div.container > div#content > div')
                cover = page.find_element(CSS, 'div#volume-cover > img')
                meta = page.find_elements(CSS, 'div#volume-meta > p')
                metas = len(meta)

                # Info: Media
                media = __getMedia(meta[0].text, medium)

                # Meta: Blurb
                blurb = ''
                if metas > 4: blurb = f'{meta[4].text}\n'
                if metas > 5:
                    for m in meta[5:]:
                        blurb += '\n' + m.text

                # Meta: Credits
                credits: list[Person] = []
                authors = meta[0].find_elements(CSS, 'span')
                credits = [ Person(author.text, 'Story/Art') for author in authors ]
                credits += __getCrew(meta[1].text)

                # Finalize Entry
                entry.blurb = blurb
                entry.cover = cover.get_attribute('src') or ''
                entry.credits = credits
                entry.media = [ media ]

                return entry

            except Exception as e:  error(e, url)