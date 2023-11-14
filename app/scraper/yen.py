import re

from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Waiter
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

from models.entry import Entry, Media
from models.table import Tables

from ..logger import log


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


# region : Helper Functions ----------------------------------------------------------------------------------

def _attr(elem: WebElement, attr: str = 'innerText') -> str:
    return elem.get_attribute(attr) or ''

def _getCredits(elems: list[WebElement]) -> list[str]:
    
    credits = []

    for elem in elems:
        name = elem.text
        if name not in credits: credits.append(name)
        
    return credits

def _getTitle(title: str) -> str:
    title = re.sub(r'\((.*?)\)', '', title)
    return title.replace('  ', ' ')

def _getPrice(text: str) -> str:

    prices = text.split(' ')

    index = 0
    try: index = prices.index('US') - 1
    except ValueError: pass

    return prices[index]

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver, limit: int) -> list[Entry]:

    # Load Page
    driver.get(URL)
    body = driver.find_element(CSS, 'div.calendar-wrapper')
    calendar = body.find_element(CSS, 'div.calendar-slider')
    heading = driver.find_element(CSS, 'div.releases-heading')

    def sleep(time = WAIT):
        try: Waiter(driver, time, time).until(lambda _: False)
        except TimeoutException: pass


    # Process the next <MONTHS> months' Book Pages
    month: WebElement = Waiter(calendar, WAIT, POLL).until(
        EC.visibility_of_element_located((CSS, ACTIVE))
    )


    i = 0
    urls: set[str] = set()
    while i < MONTHS:

        try:

            # Scroll-To and Click MONTH button
            driver.execute_script('arguments[0].scrollIntoView();', heading)
            sleep(5)
            month.click()

            # Scroll-Down to load all Pages
            driver.execute_script(SCROLL_DOWN)
            sleep(10)

            # Get all Book Page URLs
            for page in driver.find_elements(CSS, 'div.releases-append > div.book-section > div > a'):

                # Check if FORMAT is some book (Novel/Audio)
                format = page.find_element(CSS, 'span.upper').text
                if format.lower() == 'audio' or format.lower() == 'novels':

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

                    if len(months) > 0: month = months[0]   # Get next existing Month
                    else: i = MONTHS                        # Break Outer-Loop
                    break                                   # Break Inner-Loop

                # Refresh stale HTML elements
                except StaleElementReferenceException:
                    body = driver.find_element(CSS, 'div.calendar-wrapper')
                    calendar = body.find_element(CSS, 'div.calendar-slider')
                    heading = driver.find_element(CSS, 'div.releases-heading')
        
            i += 1

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')


    # Process all Book Pages
    entries: list[Entry] = []
    for url in list(urls)[:3]:

        try:

            driver.get(url)

            if not driver.title.lower().startswith('page not found'):

                sleep(10)

                print(f'@{driver.current_url}')
                page = driver.find_element(CSS, 'div.books-page')
                info = page.find_element(CSS, 'section.book-cover > div.content-heading > div.book-info')
                heading = page.find_element(CSS, 'section.series-heading > div.wrapper-1595 > div.heading-content')

                # Heading Elements
                title = heading.find_element(CSS, 'h1.heading').text
                names = heading.find_elements(CSS, 'div.story-details > p > span')
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


                entries.append(
                    Entry(
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
                )

        except Exception as e:
            log.exception('Error: Failed to process item.')
            log.exception(f'Message: {e}')


    return entries