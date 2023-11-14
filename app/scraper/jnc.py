import string

from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException

from models.entry import Entry, Media
from models.table import Tables

from ..logger import log


# region : Constants & Classes -------------------------------------------------------------------------------

TABLE = Tables.JNC
URL = 'https://j-novel.club/calendar?type=novel'
CSS = BY.CSS_SELECTOR

class Book(object):

    def __init__(self, url = '', format = '', volume = ''):
        self.url: str = url
        self.format: str = format
        self.volume: str = volume
    
    def __str__(self):
        return f'{self.volume}:  @{self.url} [{self.format}]'

# endregion --------------------------------------------------------------------------------------------------


def scrape(driver: WebDriver, limit: int) -> list[Entry]:

    # Load Page
    driver.get(URL)
    body = driver.find_element(CSS, 'div.f1owoso1')
    button = body.find_elements(CSS, 'div.f1bj9jk4')[-1]


    # Load in all Items
    while True:
        try: button.click()
        except WebDriverException: break


    # Retrieve all Items
    books: list[Book] = []
    items: list[WebElement] = body.find_elements(CSS, 'div.fhkbwa > a')
    for item in items:

        try: 

            url = item.get_attribute('href')
            volume = item.find_element(CSS, 'div.f6nfde4 > div > span.fpcytuh').text
            format = item.find_element(CSS, 'div.f1qz2g98 > div > div.f1mwi361 > div.text').text

            # Create Item only if:
            # > URL is valid
            # > Format is not 'partial'
            # > Books List has not hit the limit

            if url and 'part' not in format.lower() and len(books) < limit:
                books.append(Book(url, format, volume))

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')


    # Process all Items
    entries: list[Entry] = []
    for book in books:

        try:

            format = book.format
            url = book.url
            driver.get(url)

            # Check if Book Page exists
            if not driver.current_url.endswith('404'):

                # Primary Sections
                title = driver.find_element(CSS, 'div.fl45o3o > h1').text + f' {book.volume}'
                main = driver.find_element(CSS, 'div.f1vdb00x.novel > div > div.f1k2es0r')
                side = driver.find_elements(CSS, 'div.fcoxyrb > div.aside-buttons')

                # Main Elements
                date = main.find_element(CSS, f'div.f1ijq7jq > div.color-{format.lower()} > div.text').text
                cover = main.find_element(CSS, 'div.fz7z7g5 > img').get_attribute('src') or ''
                blurb = main.find_element(CSS, 'p').text

                # Side: Credits
                credits: list[str] = []
                for aside in side[:-1]:
                    credit = aside.find_element(CSS, 'a > div > div.text').text
                    credits.append(credit)

                # Side: Genres
                genres: list[str] = []
                for tag in side[-1].find_elements(CSS, 'a')[1:]:
                    genre = tag.find_element(CSS, 'div > div.text').text
                    genres.append(string.capwords(genre))


                # Finalize Entry
                entries.append(
                    Entry(
                        url = url,
                        date = date,
                        title = title,
                        cover = cover,
                        blurb = blurb,
                        genres = genres,
                        credits = credits,
                        media = [ Media(format, '', '') ],
                        table = TABLE
                    )
                )

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')

    return entries