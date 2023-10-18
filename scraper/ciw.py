from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from models.entry import Entry


URL = 'https://crossinfworld.com/Calendar.html'
CSS = BY.CSS_SELECTOR
    

def td(header: str) -> str:
    return f'td[data-table-header="{header}"]'


def extract(driver: WebDriver) -> list[Entry]:

    print(f'Extracting from {URL}...')
    entries: list[Entry] = []

    driver.get(URL)
    driver.find_element(CSS, 'option[value="100"]').click()

    for item in driver.find_elements(CSS, 'tbody > *'):

        # Calendar Page
        head = item.find_element(CSS, 'td > a')
        href = head.get_attribute('href') or ''

        entry = Entry(

            url = href,
            title = head.text,

            date = item.find_element(CSS, td('Date')).text,
            isbn = item.find_element(CSS, td('ISBN')).text,
            medium = item.find_element(CSS, td('Format')).text,
            genres = item.find_element(CSS, td('Genre')).text.split(', ')

        )

        if href:

            driver.get(href)

            cover = driver.find_element(CSS, 'img.img-responsive.pull-left')

            story = driver.find_element(CSS, 'div.col-sm-6')
            blurb = story.find_element(CSS, 'p > strong').text
    
            for p in story.find_elements(CSS, 'p'):
                blurb += p.text + '\n'

            entry.image = cover.get_attribute('src') or ''
            entry.blurb = blurb
            
            driver.back()

        entries.append(entry)

    return entries