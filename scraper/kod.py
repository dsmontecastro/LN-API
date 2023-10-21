from selenium.webdriver.common.by import By as BY
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Waiter

from models.entry import Entry, Media


# region : Constants -----------------------------------------------------------------------------------------

URL = 'https://kodansha.us/calendar?type=book'
CSS = BY.CSS_SELECTOR

# CSS Shortcuts
TAGS = 'div.product-desktop-rating-table-third-row-wrapper span.product-desktop-rating-table-tags-tag'
FORMATS = 'div.product-desktop-rating-table-second-row-wrapper > div.product-desktop-rating-table-second-row-inner-wrapper'
F_ROW = 'div.product-desktop-rating-table-title-value-wrapper'
TITLE = 'div.product-desktop-rating-table-title-wrapper'
VALUE = 'div.product-desktop-rating-table-value-wrapper'
TEXT = 'span.product-desktop-rating-table-title'

# class Item(object):
#     def __init__(self, url = '', date = ''):
#         self.url: str = url
#         self.date: str = date

#     def __str__(self):
#         return f'{self.url}:  @{self.date}'

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def getCredits(authors: str) -> list[str]:
    authors = authors.replace('By ', '~').replace(', ', '~').replace(' and ', '~').strip()
    return [ author for author in authors.split('~') if author ]

def getDate(elem: WebElement) -> str:
    return elem.find_element(CSS, f'{F_ROW} > {VALUE} > {TEXT}').text

def getMedia(elem: WebElement) -> Media:

    rows = elem.find_elements(CSS, F_ROW)

    isbn = rows[-1].find_element(CSS, f'{VALUE} > {TEXT}').text

    format = rows[0].find_element(CSS, f'{TITLE} > {TEXT}').text
    format = format.replace(' Release:', '').lower()
    if format== 'e-book': format = 'digital'

    return Media( format = format, isbn = isbn, price = '')

def getTitle(title: str) -> str:
    par = 0
    try: par = title.index(' (')
    except ValueError: par = len(title)
    return title[:par]

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver) -> list[Entry]:

    print(f'Extracting from {URL}...')
    entries: list[Entry] = []


    # Retrieve all Items
    driver.get(URL)
    err = Waiter(driver, timeout = 5)
    wait = Waiter(driver, timeout = 30)
    items: list[WebElement] = wait.until(
        EC.visibility_of_all_elements_located((CSS, 'div.rc-calendar-item-wrapper'))
    )


    # Retreive all Book URLs
    urls: list[str] = []
    for item in items:
        a = item.find_element(CSS, 'a')
        url = a.get_attribute('href')
        if url: urls.append(url)


    # Process all Book URLs
    entries: list[Entry] = []
    for url in urls:

        # Go to Book Page
        driver.get(url)
        print(f'@{driver.current_url}')

        # Check for 404 elements
        isValid = False
        try: err.until(EC.visibility_of_all_elements_located((CSS, 'div.not-found')))
        except TimeoutException: isValid = True

        # Check if Book Page is not a 404
        if isValid:

            top: WebElement = wait.until(
                EC.visibility_of_element_located((CSS, 'div.product-name-poster-wrapper'))
            )
            bot: WebElement = wait.until(
                EC.visibility_of_element_located((CSS, 'div.product-desktop-rating-wrapper > div > table > tbody'))
            )


            # Top Elements: Poster
            poster = top.find_element(CSS, 'div.product-poster-wrapper img')
            cover = poster.get_attribute('src') or ''

            # Top Elements: Book Info
            info = top.find_element(CSS, 'div.name-author-wrapper-product')
            title = getTitle(info.find_element(CSS, 'h2.product-title').text)
            blurb = info.find_element(CSS, 'p.series-desktop-header-info-description').text
            credits = getCredits(info.find_element(CSS, 'span.series-desktop-header-info-author').text)


            # Bot Elements: Tags
            tags = bot.find_elements(CSS, TAGS)
            genres = [ tag.text for tag in tags ]

            # Bot Elements: Format
            formats = bot.find_elements(CSS, FORMATS)
            media = [ getMedia(format) for format in formats ]
            date = getDate(formats[0])


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
                    media = media,
                )
            )


    return entries