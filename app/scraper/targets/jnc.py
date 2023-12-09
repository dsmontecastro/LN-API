import string

from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException

from ...common.logger import log
from ...database.models.table import Tables
from ...database.models.entry import Entry, Media, Person


# region : Constants & Classes -------------------------------------------------------------------------------

TABLE = Tables.JNC
URL = 'https://j-novel.club/calendar?type=novel'
CSS = BY.CSS_SELECTOR
PTH = BY.XPATH


class Book(object):

    def __init__(self, url = '', format = '', volume = ''):
        self.url: str = url
        self.format: str = format
        self.volume: str = volume
    
    def __str__(self):
        return f'{self.volume}:  @{self.url} [{self.format}]'


def __error__(e: Exception, link: str = ''):
    log.exception(f'Error [{e.__class__.__name__}]: Failed to process item.')
    if link: log.exception(f'Link: {link}')

# endregion --------------------------------------------------------------------------------------------------


def scrape(driver: WebDriver, limit: int) -> list[Entry]:

    log.debug(f'> {TABLE}')

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
            # > URL is a valid string
            # > Format is 'complete' (not 'partial')

            if url and 'part' not in format.lower():
                books.append(Book(url, format, volume))

        except Exception as e: __error__(e)


    # Process all Books into Entries
    entries: list[Entry] = []
    for book in books:
        entry = __process(driver, book)
        if entry: entries.append(entry)
        if len(entries) >= limit: break

    return entries


def __process(driver: WebDriver, book: Book) -> Entry | None:
        
        url = book.url

        if url:

            format = book.format

            try:

                driver.get(url)
                log.debug(f'>> {driver.current_url:.50s}')

                # Check if Book Page exists
                if not driver.current_url.endswith('404'):

                    # Primary Sections
                    title = driver.find_element(CSS, 'div.fl45o3o > h1').text + f' {book.volume}'
                    main = driver.find_element(CSS, 'div.f1vdb00x.novel > div > div.f1k2es0r')
                    side = driver.find_element(CSS, 'div.fcoxyrb')

                    # Main Elements
                    date = main.find_element(CSS, f'div.f1ijq7jq > div.color-{format.lower()} > div.text').text
                    cover = main.find_element(CSS, 'div.fz7z7g5 > img').get_attribute('src') or ''
                    blurb = main.find_element(CSS, 'p').text

                    # Side: Genres
                    genres: list[str] = []
                    tags = side.find_elements(CSS, 'div.aside-buttons')[-1]
                    for tag in tags.find_elements(CSS, 'a'):
                        genre = tag.find_element(CSS, 'div > div.text').text
                        genres.append(string.capwords(genre))

                    # Side: Credits
                    credits: list[Person] = []
                    people = side.find_elements(CSS, 'div.f3gc1kc')[:-1]
                    for person in people:
                
                        position: str = person.find_element(CSS, 'div > h3').text
                        credit = person

                        while True:
                            
                            credit = credit.find_element(PTH, 'following-sibling::div')
                            cls = credit.get_attribute('class')

                            if cls == 'aside-buttons':
                                name = credit.find_element(CSS, 'a > div > div.text').text
                                credits.append(Person(name, position))

                            else: break


                    # Finalize Entry
                    return Entry(
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

            except Exception as e:  __error__(e, url)