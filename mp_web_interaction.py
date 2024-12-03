from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

# Web Interaction Helpers

def wait_for_page_load(driver: webdriver.Chrome, timeout: int = 30) -> None:
    """
    Wait for the page to load by checking the readiness of the document.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
        timeout (int): Maximum time to wait for the page to load.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException:
        logging.error("Page did not load within the timeout period.")
        raise

def locate_element(driver: webdriver.Chrome, by: By, value: str, timeout: int = 30) -> WebElement:
    """
    Find an element with a timeout.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
        by (By): Locator strategy.
        value (str): Locator value.
        timeout (int): Timeout in seconds.
    
    Returns:
        WebElement: Located WebElement instance.
    
    Raises:
        TimeoutException: If element is not found within the timeout period.
    """
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def click_on_element(driver: webdriver.Chrome, by: By, value: str, timeout: int = 30) -> None:
    """
    Click an element after scrolling it into view.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
        by (By): Locator strategy.
        value (str): Locator value.
        timeout (int): Timeout in seconds.
    """
    element = locate_element(driver, by, value, timeout)
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
    except TimeoutException as e:
        logging.error(f"Element located by {by} and value {value} could not be clicked: {e}")
        raise
    except NoSuchElementException as e:
        logging.error(f"Element located by {by} and value {value} not found: {e}")
        raise
