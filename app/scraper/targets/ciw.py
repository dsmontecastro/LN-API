from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ._common import CSS, error

from ...common.logger import log
from ...common.isbn import to_isbn
from ...database.models.table import Tables
from ...database.models.entry import Entry, Media, Person


# region : Constants -----------------------------------------------------------------------------------------

TABLE = Tables.CIW
URL = 'https://crossinfworld.com/Calendar.html'

DIGITALS = ['digital', 'audiobook', 'ebook']

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def __td(header: str) -> str:
    return f'td[data-table-header="{header}"]'


def __getCredit(name: str) -> Person:

    strings = [ i.capitalize() for i in name.split(' ') ]

    position = strings[0]
    if position.lower() == 'by': position = 'Author'

    name = ' '.join(strings[1:])

    return Person(name, position)


def __getPrice(text: str, format: str = 'digital') -> str:

    prices = text.replace('&', ' ').split(' ')[1:]

    i = 0
    try: i = prices.index('Digital')
    except(ValueError): pass

    if i > 0 and format.lower() not in DIGITALS:
        del prices[i:i+3]
        i = 0

    return prices[1]

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver, limit: int) -> list[Entry]:

    log.debug(f'> {TABLE}')

    # Load & Expand Calendar
    driver.get(URL)
    driver.find_element(CSS, 'option[value="100"]').click()

    # Process all Calendar Items into Books
    books: list[Entry] = []
    items: list[WebElement] = driver.find_elements(CSS, 'tbody > *')
    for item in items[:limit]:

        try:

            # Calendar Page
            head = item.find_element(CSS, 'td > a')
            url = str(head.get_attribute('href'))

            if url: # If URL for Book Page is valid
        
                format = item.find_element(CSS, __td('Format')).text.lower()
                isbn = item.find_element(CSS, __td('ISBN')).text
                isbn = to_isbn(isbn)

                if 'audio' in format: format = 'audio'
                if 'print' in format: format = 'physical'

                # Get following from Calendar Page
                books.append(
                    Entry(
                        table = TABLE,
                        url = url,
                        title = head.text,
                        date = item.find_element(CSS, __td('Date')).text,
                        genres = item.find_element(CSS, __td('Genre')).text.split(', '),
                        media = [ Media(format, isbn, '') ],
                    )
                )

        except Exception as e: error(e)


    # Process all Books into Entries
    entries: list[Entry] = []
    for book in books:
        entry = __process(driver, book)
        if entry: entries.append(entry)
        if len(entries) >= limit: break
    
    return entries


def __process(driver: WebDriver, entry: Entry) -> Entry | None:
        
        url = entry.url

        if url:

            try:

                # Go to Book Page
                driver.get(url)
                log.debug(f'>> {driver.current_url:.50s}')

                # Primary Sections
                info = driver.find_element(CSS, 'div.col-sm-4')
                about = driver.find_element(CSS, 'div.col-sm-6')
                image = driver.find_element(CSS, 'img.img-responsive.pull-left')

                # Info: Price
                prices = info.find_elements(CSS, 'p')[-1].text.splitlines()[-1]
                price = __getPrice(prices, entry.media[0].format)

                # About: Blurb
                blurb: str = ''
                for p in about.find_elements(CSS, 'p'): blurb += p.text + '\n'

                # About: Credits
                headings = about.find_elements(CSS, ':not(p):not(strong)')
                credits = [ __getCredit(heading.text) for heading in headings ]

                # Image: Cover
                cover = str(image.get_attribute('src'))

                # Finalize Entry
                entry.blurb = blurb
                entry.cover = cover
                entry.credits = credits
                entry.media[0].set_price(price)
            
                return entry

            except Exception as e: error(e)