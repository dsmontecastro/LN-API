from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver

from models.entry import Entry, Media


# region : Constants -----------------------------------------------------------------------------------------

URL = 'https://crossinfworld.com/Calendar.html'
CSS = BY.CSS_SELECTOR

CREDITS = ['h4', 'h5', 'h6']
DIGITALS = ['digital', 'audiobook', 'ebook']

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def td(header: str) -> str:
    return f'td[data-table-header="{header}"]'

def getCredit(name: str) -> str:
    credits = [ i.capitalize() for i in name.split(' ') ]
    return ' '.join(credits[1:])

def getPrice(text: str, format: str = 'digital') -> str:

    prices = text.replace('&', ' ').split(' ')[1:]

    i = 0
    try: i = prices.index('Digital')
    except(ValueError): pass

    price: str = ''
    if i > 0 and format.lower() not in DIGITALS:
        del prices[i:i+3]
        i = 0

    return prices[1]

# endregion --------------------------------------------------------------------------------------------------



def scrape(driver: WebDriver) -> list[Entry]:

    print(f'Extracting from {URL}...')

    entries: list[Entry] = []

    driver.get(URL)
    driver.find_element(CSS, 'option[value="100"]').click()

    for item in driver.find_elements(CSS, 'tbody > *'):

        # Calendar Page
        head = item.find_element(CSS, 'td > a')
        href = head.get_attribute('href') or ''

        if href:

            # From Calendar Page
            title = head.text
            date = item.find_element(CSS, td('Date')).text
            isbn = item.find_element(CSS, td('ISBN')).text
            format = item.find_element(CSS, td('Format')).text
            genres = item.find_element(CSS, td('Genre')).text.split(', ')


            # Go to Book Page
            driver.get(href)
            info = driver.find_element(CSS, 'div.col-sm-4')
            about = driver.find_element(CSS, 'div.col-sm-6')
            image = driver.find_element(CSS, 'img.img-responsive.pull-left')

            
            cover = image.get_attribute('src') or ''
        
            blurb: str = ''
            for p in about.find_elements(CSS, 'p'): blurb += p.text + '\n'

            credits = [ getCredit(about.find_element(CSS, i).text) for i in CREDITS ]

            prices = info.find_elements(CSS, 'p')[-1].text.splitlines()[-1]
            price = getPrice(prices)

    
            entries.append(
                Entry(
                    url = href,
                    date = date,
                    title = title,
                    cover = cover,
                    blurb = blurb,
                    genres = genres,
                    credits = credits,
                    media = [ Media(format, isbn, price) ],
                )
            )

            # Back to Calendar
            driver.back()


    return entries