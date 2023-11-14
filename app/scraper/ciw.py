from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from models.entry import Entry, Media
from models.table import Tables

from ..logger import log


# region : Constants -----------------------------------------------------------------------------------------

TABLE = Tables.CIW
URL = 'https://crossinfworld.com/Calendar.html'
CSS = BY.CSS_SELECTOR

# CSS Shortcuts
WAIT = 10
DIGITALS = ['digital', 'audiobook', 'ebook']

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def _td(header: str) -> str:
    return f'td[data-table-header="{header}"]'

def _getCredit(name: str) -> str:
    credits = [ i.capitalize() for i in name.split(' ') ]
    return ' '.join(credits[1:])

def _getPrice(text: str, format: str = 'digital') -> str:

    prices = text.replace('&', ' ').split(' ')[1:]

    i = 0
    try: i = prices.index('Digital')
    except(ValueError): pass

    if i > 0 and format.lower() not in DIGITALS:
        del prices[i:i+3]
        i = 0

    return prices[1]

# endregion --------------------------------------------------------------------------------------------------


def scrape(driver: WebDriver) -> list[Entry]:

    # Load & Expand Calendar
    driver.get(URL)
    driver.find_element(CSS, 'option[value="100"]').click()


    # Process all Calendar Items into Books
    books: list[Entry] = []
    items: list[WebElement] = driver.find_elements(CSS, 'tbody > *')
    for item in items:

        try:

            # Calendar Page
            head = item.find_element(CSS, 'td > a')
            url = head.get_attribute('href') or ''

            if url: # If URL for Book Page is valid
        
                isbn = item.find_element(CSS, _td('ISBN')).text
                format = item.find_element(CSS, _td('Format')).text

                # Get following from Calendar Page
                books.append(
                    Entry(
                        table = TABLE,
                        url = url,
                        title = head.text,
                        date = item.find_element(CSS, _td('Date')).text,
                        genres = item.find_element(CSS, _td('Genre')).text.split(', '),
                        media = [ Media(format, isbn, '') ],
                    )
                )

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')


    # Process all found Books into Entries
    entries: list[Entry] = []
    for book in books:

        try:

            # Go to Book Page
            driver.get(book.url)

            info = driver.find_element(CSS, 'div.col-sm-4')
            about = driver.find_element(CSS, 'div.col-sm-6')
            image = driver.find_element(CSS, 'img.img-responsive.pull-left')

            # Info: Price
            prices = info.find_elements(CSS, 'p')[-1].text.splitlines()[-1]
            price = _getPrice(prices, book.media[0].format)

            # About: Blurb
            blurb: str = ''
            for p in about.find_elements(CSS, 'p'): blurb += p.text + '\n'

            # About: Credits
            headings = about.find_elements(CSS, ':not(p)')
            credits = [ _getCredit(heading.text) for heading in headings ]

            # Image: Cover
            cover = image.get_attribute('src') or ''


            # Finalize Entry
            book.blurb = blurb
            book.cover = cover
            book.credits = credits
            book.media[0].price = price
            entries.append(book)

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')


    return entries