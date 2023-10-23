import string

from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from models.entry import Entry, Media
from models.table import Tables


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


def scrape(driver: WebDriver) -> list[Entry]:

    print(f'Extracting from {URL}...')

    driver.get(URL)
    body = driver.find_element(CSS, 'div.f1owoso1')
    button = body.find_elements(CSS, 'div.f1bj9jk4')[-1]


    # Load in all Items
    while True:
        try: button.click()
        except WebDriverException: break


    # Retrieve all Items
    books: list[Book] = []
    for book in body.find_elements(CSS, 'div.fhkbwa > a'):

        url = book.get_attribute('href')
        volume = book.find_element(CSS, 'div.f6nfde4 > div > span.fpcytuh').text
        format = book.find_element(CSS, 'div.f1qz2g98 > div > div.f1mwi361 > div.text').text

        # Create Item only if URL is valid and Format is not 'partial'
        if url and 'part' not in format.lower():
            books.append(Book(url, format, volume))


    # Process all Items
    entries: list[Entry] = []
    for book in books:

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

    return entries