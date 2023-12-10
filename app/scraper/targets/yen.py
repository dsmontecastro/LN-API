import re

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from ._common import CSS, PTH, T_FAST, T_POLL, error, sleep, wait_for

from ...common.logger import log
from ...database.models.table import Tables
from ...database.models.entry import Entry, Media, Person


# region : Constants & Classes -------------------------------------------------------------------------------

TABLE = Tables.YEN
URL = 'https://yenpress.com/calendar'

# Selenium Shortcuts
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


# region : Helper Functions ----------------------------------------------------------------------------------

def _attr(elem: WebElement, attr: str = 'innerText') -> str:
    return elem.get_attribute(attr) or ''


def _getCredits(elems: list[WebElement]) -> list[Person]:
    
    credits: list[Person] = []

    for elem in elems:
        [ position, name ] = elem.text.split(': ')
        if position == 'Translated by': position = 'Translator'
        if name not in credits: credits.append(Person(name, position))
        
    return credits


def _getPrice(text: str) -> str:

    prices = text.split(' ')

    index = 0
    try: index = prices.index('US') - 1
    except ValueError: pass

    return prices[index]


def _getTitle(title: str) -> str:
    title = re.sub(r'\((.*?)\)', '', title)
    return title.replace('  ', ' ')

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver, limit: int) -> list[Entry]:

    log.debug(f'> {TABLE}')

    # Load Page & Root Elements
    driver.get(URL)
    body = driver.find_element(CSS, 'div.calendar-wrapper')
    heading = driver.find_element(CSS, 'div.releases-heading')
    calendar = body.find_element(CSS, 'div.calendar-slider')

    # Process the next <MONTHS> amount of months' Book Pages
    month = wait_for(calendar, CSS, ACTIVE)
    urls: set[str] = set()
    i = 0

    while i < MONTHS:

        # Scroll to MONTH button
        driver.execute_script('arguments[0].scrollIntoView();', heading)
        sleep(driver, T_POLL)

        # Click MONTH button, if exists
        if month: month.click()
        else: break

        # Scroll-Down to load all Pages
        driver.execute_script(SCROLL_DOWN)
        sleep(driver, T_FAST)


        # Get all Book Page URLs
        for page in driver.find_elements(CSS, 'div.releases-append > div.book-section > div > a'):

            # Check if FORMAT is some book (Novel/Audio)
            format = page.find_element(CSS, 'span.upper').text
            if (format.lower() == 'audio' or format.lower() == 'novels'):

                # Check if Book Page URL is valid
                url = _attr(page, 'href')
                if url:
                    urls.add(url)
                    i = MONTHS

        # Move to next month
        while True:

            try:

                # Find remaining Months excluding current/active
                months = calendar.find_elements(CSS, f'{ACTIVE} ~ div')

                if len(months) > 0: month = months[0]   # Go to next existing Month
                else: i = MONTHS                                    # Break Outer-Loop
                break                                               # Break Inner-Loop

            # Refresh stale HTML elements
            except StaleElementReferenceException:
                body = driver.find_element(CSS, 'div.calendar-wrapper')
                calendar = body.find_element(CSS, 'div.calendar-slider')
                heading = driver.find_element(CSS, 'div.releases-heading')
    
        i += 1


    # Process all Book Pages
    entries: list[Entry] = []
    for url in urls:
        entry = __process(driver, url)
        if entry: entries.append(entry)
        if len(entries) >= limit: break

    return entries


def __process(driver: WebDriver, url: str) -> Entry | None:

        try:

            driver.get(url)
            log.debug(f'>> {driver.current_url:.50s}')

            if not driver.title.lower().startswith('page not found'):

                sleep(driver, T_FAST)

                page = driver.find_element(CSS, 'div.books-page')
                info = page.find_element(CSS, 'section.book-cover > div.content-heading > div.book-info')
                heading = page.find_element(CSS, 'section.series-heading > div.wrapper-1595 > div.heading-content')

                # Heading Elements
                title = heading.find_element(CSS, 'h1.heading').text
                names = heading.find_elements(CSS, 'div.story-details > p')
                credits = _getCredits(names)

                # Detail Elements
                details = page.find_element(CSS, 'section.book-details')
                detail = details.find_element(CSS, 'div.detail.active')
                isbns = details.find_elements(PTH, '//span[text()="ISBN"]/following-sibling::p')

                # Detail: Date
                release = detail.find_element(PTH, '//span[text()="Release Date"]/following-sibling::p')
                date = _attr(release)

                # Detail: Genres
                tags = detail.find_elements(CSS, 'div.txt-hold > div.desktop-only > a')
                genres = [ _attr(tag) for tag in tags]

                # Info: Cover
                image = info.find_element(CSS, 'div.series-cover > div.book-cover-img > img')
                cover = _attr(image, 'src')

                # Info: Blurb
                blurbs = info.find_elements(CSS, 'div.content-heading-txt > *')
                blurb = '\n'.join([ blurb.text for blurb in blurbs ])

                # Info: Formats
                buy = info.find_element(CSS, 'div.buy-info')
                prices = buy.find_elements(CSS, 'div.deliver-info > p')
                formats = buy.find_elements(CSS, 'div.tabs > span')

                # Mixed: Media
                media: list[Media] = []
                for i in range(len(formats)):

                    try:
                        media.append(
                            Media(
                                isbn = _attr(isbns[i]),
                                format = _attr(formats[i]).lower(),
                                price = _getPrice(_attr(prices[i])),
                            )
                        )

                    except (IndexError, NoSuchElementException): continue


                return Entry(
                    url = url,
                    date = date,
                    title = _getTitle(title),
                    cover = cover,
                    blurb = blurb,
                    genres = genres,
                    credits = credits,
                    media = media,
                    table = TABLE
                )

        except Exception as e:  error(e, url)