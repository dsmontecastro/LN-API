from enum import Enum

from selenium.webdriver.common.by import By as BY
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
# from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Waiter

from models.entry import Entry, Media


# region : Constants -----------------------------------------------------------------------------------------

URL = 'https://webcache.googleusercontent.com/search?q=cache:'  # Bypasses the actual site's CloudFlare
CSS = BY.CSS_SELECTOR
T_SLOW = 15
T_FAST = 5

class MODE(Enum):
    DIGITAL = 'https://sevenseasentertainment.com/digital/'
    PHYSICAL = 'https://sevenseasentertainment.com/release-dates/'

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def _getTitle(title: str, format: str) -> str:
    return title.replace(f' ({format})', '')

def _getMedia(info: list[str], format: str) -> Media:

    price_index = info.index('Price') + 1
    isbn_index = info.index('ISBN') + 1
    
    return Media(
        format = format,
        isbn = info[isbn_index],
        price = info[price_index]
    )

def _parsePar(info: str) -> list[str]:
    return info.replace('\n', ': ').split(': ')

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver) -> list[Entry]:

    entries: list[Entry] = []

    try: entries += _scrape(driver, MODE.DIGITAL)
    except TimeoutException:
        print('Error: SEA.DIGITAL has failed.')

    try: entries += _scrape(driver, MODE.PHYSICAL)
    except TimeoutException:
        print('Error: SEA.PHYSICAL has failed.')

    print(f'Total: {len(entries)}')
    return entries


def _scrape(driver: WebDriver, mode: MODE) -> list[Entry]:


    driver.get(URL + mode.value)
    medium = mode.name.lower()
    print(f'Extracting from {driver.current_url} ({medium})...')


    # Load all Entries
    main = driver.find_element(CSS, 'table#releasedates > tbody')

    # Entry Pre-processing
    entries: list[Entry] = []
    for item in main.find_elements(CSS, 'tr#volumes'):

        cols = item.find_elements(CSS, 'td')
        format = cols[2].text

        series = cols[1].find_element(CSS, 'a')
        url = series.get_attribute('href')

        # Check if URL exists and Format is Light/Novel
        if url and 'novel' in format.lower():
            entries.append(
                Entry(
                    url = url,
                    date = cols[0].text,
                    title = _getTitle(series.text, format),
                )
            )
 

    # Throttle to avoid Google's Bot-Detection
    driver.implicitly_wait(T_SLOW)


    # Entry Completion
    final: list[Entry] = []
    for entry in entries:
        
        url = entry.url
        date = entry.date
        print(f'{date}: {url}')

        if url: # Check if URL exists

            # Go to Book Page
            driver.get(URL + url)

            # Check if Book Page leads to a 404
            try: Waiter(driver, timeout = T_FAST).until(
                EC.visibility_of_element_located((CSS, 'body > a'))
            )

            # Proceed if Book Page is valid
            except TimeoutException:

                page = driver.find_element(CSS, 'div.container > div#content > div')
                cover = page.find_element(CSS, 'div#volume-cover > img')
                metas = page.find_element(CSS, 'div#volume-meta')

                # Meta Elements
                pars = metas.find_elements(CSS, 'p')
                creators = metas.find_elements(CSS, 'span.creator')

                # Info: Media
                info = _parsePar(pars[0].text)
                media = _getMedia(info, medium)

                # Crew: Credits
                crew = _parsePar(pars[1].text)
                credits = [ creator.text for creator in creators ]
                credits += [ crew[i] for i in range(len(crew)) if i % 2 == 1 ]


                # Finalize Entry
                entry.blurb = f'{pars[4].text}\n{pars[5].text}'
                entry.cover = cover.get_attribute('src') or ''
                entry.credits = credits
                entry.media = [ media ]

                final.append(entry)
            
        driver.implicitly_wait(T_SLOW)

    return final