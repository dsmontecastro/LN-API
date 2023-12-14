from enum import Enum
from typing import Callable

from selenium.webdriver.common.by import By as BY
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Waiter

from ...common.logger import log


# region : Constants -----------------------------------------------------------------------------------------

CSS = BY.CSS_SELECTOR
PTH = BY.XPATH

T_POLL = 5
T_FAST = 10
T_SLOW = 15

# endregion --------------------------------------------------------------------------------------------------


# region : Helper Functions ----------------------------------------------------------------------------------

def error(e: Exception, link: str = ''):
    log.exception(f'Error [{e.__class__.__name__}]: Failed to process item.')
    if link: log.exception(f'Link: {link}')

def code_isbn(isbn: str):

    if len(isbn) == 10:
        code = [
            isbn[0],
            isbn[1:3],
            isbn[3:9],
            isbn[9]
        ]
        isbn = '-'.join(code).upper()

    elif len(isbn) == 13:
        code = [
            isbn[0:3],
            isbn[3],
            isbn[4:9],
            isbn[9:12],
            isbn[12]
        ]
        isbn = '-'.join(code)
    
    return isbn


def sleep(elem: WebDriver | WebElement, time: int = T_POLL, func: Callable = lambda _: False):
    try: Waiter(elem, time, time).until(func)
    except TimeoutException: pass


def wait_for(elem: WebDriver | WebElement, mode: str, cmd: str, time: int = T_FAST) -> WebElement | None:
    try:

        if not __mode_is_valid(mode):
            log.exception('>> Mode Error!')
            raise ValueError

        waiter = Waiter(elem, time)
        result: WebElement = waiter.until(EC.visibility_of_element_located((mode, cmd)))

        return result

    except (ValueError, TimeoutException): return None


def wait_many(elem: WebDriver | WebElement, mode: str, cmd: str, time: int = T_FAST) -> list[WebElement]:
    try:

        if not __mode_is_valid(mode): raise ValueError

        waiter = Waiter(elem, time)
        return waiter.until(EC.visibility_of_all_elements_located((mode, cmd)))

    except (ValueError, TimeoutException): return []


def __mode_is_valid(mode: str): return mode == CSS or mode == PTH

# endregion --------------------------------------------------------------------------------------------------