import string

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ._common import CSS, PTH, T_SLOW, error, wait_for, wait_many

from ...common.logger import log
from ...database.models.table import Tables
from ...database.models.entry import Entry, Media, Person


# region : Constants -----------------------------------------------------------------------------------------

TABLE = Tables.KOD
URL = 'https://kodansha.us/calendar?type=book'

# CSS Shortcuts
DATE = 'div.rc-daily-calendar-sticky span.rc-daily-calendar-day-text'
TAGS = 'div.product-desktop-rating-table-third-row-wrapper span.product-desktop-rating-table-tags-tag'
FORMATS = 'div.product-desktop-rating-table-second-row-wrapper > div.product-desktop-rating-table-second-row-inner-wrapper'
F_ROW = 'div.product-desktop-rating-table-title-value-wrapper'
TITLE = 'div.product-desktop-rating-table-title-wrapper'
VALUE = 'div.product-desktop-rating-table-value-wrapper'
TEXT = 'span.product-desktop-rating-table-title'

class Book(object):
    def __init__(self, url: str, date: str):
        self.url: str = url
        self.date: str = date

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def _getCredits(authors: str) -> list[Person]:
    authors = authors.replace('By ', '~').replace(', ', '~').replace(' and ', '~').strip()
    return [ Person(author, 'author') for author in authors.split('~') if author ]


def _getDate(date: str) -> str:
    strs = date.replace('on ', '').split(' ')
    return ' '.join(strs[1:])


def _getGenre(tag: str) -> str:
    return string.capwords(tag.lower())


def _getTitle(title: str) -> str:
    par = 0
    try: par = title.index(' (')
    except ValueError: par = len(title)
    return title[:par]


def _addMedia(elem: WebElement, date: str, media: list[Media]):

    rows = elem.find_elements(CSS, F_ROW)

    # Only add to MEDIA if DATES match
    if date == rows[0].find_element(CSS, f'{VALUE} > {TEXT}').text:

        isbn = rows[-1].find_element(CSS, f'{VALUE} > {TEXT}').text
        isbn = rows[-1].find_element(CSS, f'{VALUE} > {TEXT}').text

        format = rows[0].find_element(CSS, f'{TITLE} > {TEXT}').text
        format = format.replace(' Release:', '').lower()
        if format== 'e-book': format = 'digital'

        media.append(Media( format = format, isbn = isbn, price = ''))

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver, limit: int) -> list[Entry]:

    log.debug(f'> {TABLE}')

    # Load Book URLs & Retrieve all Release Days
    driver.get(URL)
    test = wait_for(driver, CSS, 'div.rc-calendar-item-wrapper')
    days = wait_many(driver, CSS, 'div.rc-daily-calendar-container')


    # Retreive all Book URLs from each Release Day
    books: list[Book] = []
    for day in days:
            
        try:

            children = day.find_elements(PTH, './div')
            date = _getDate(children[0].find_element(CSS, 'span.rc-daily-calendar-day-text').text)
            links: list[WebElement] = children[1].find_elements(CSS, 'div.rc-calendar-item-wrapper > a')

            for link in links:
                url = str(link.get_attribute('href'))
                if url: books.append(Book(url, date))

        except Exception as e: error(e)


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

            date = book.date

            try:

                driver.get(url)
                log.debug(f'>> {driver.current_url:.50s}')

                # Check if site leads to a 404 Error
                err = wait_for(driver, CSS, 'body > div > div > div > div.not-found')
                if err: return


                # Find TOP Element, if exists
                top = wait_for(driver, CSS, 'div.product-name-poster-wrapper')
                if not top: return

                # Section: Poster
                poster = top.find_element(CSS, 'div.product-poster-wrapper img')
                cover = str(poster.get_attribute('src'))

                # Section: Book Info
                info = top.find_element(CSS, 'div.name-author-wrapper-product')
                title = _getTitle(info.find_element(CSS, 'h2.product-title').text)
                blurb = info.find_element(CSS, 'p.series-desktop-header-info-description').text
                credits = _getCredits(info.find_element(CSS, 'span.series-desktop-header-info-author').text)


                # Find BOT Element, if exists
                bot = wait_for(driver, CSS, 'div.product-desktop-rating-wrapper > div > table > tbody')
                if not bot: return

                # Section: Tags
                tags = bot.find_elements(CSS, TAGS)
                genres = [ _getGenre(tag.text) for tag in tags ]

                # Section: Formats
                media: list[Media] = []
                formats = bot.find_elements(CSS, FORMATS)
                for format in formats: _addMedia(format, date, media)


                # Finalize Entry
                return Entry(
                    url = url,
                    date = date,
                    title = title,
                    cover = cover,
                    blurb = blurb,
                    genres = genres,
                    credits = credits,
                    media = media,
                    table = TABLE
                )

            except Exception as e:  error(e, url)