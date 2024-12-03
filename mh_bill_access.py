#mh_access_bill_module

import logging
import time
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from mh_automation.mh_config import configure_logging
from mh_automation.mh_file_manager import handle_file_download, fetch_consumer_details
from config import DOWNLOAD_PATH_2

# Initialize logging
logger = configure_logging()

# Accessing and downloading the bill module
    
def get_view_bill_button(driver: webdriver.Chrome) -> WebElement:
    """
    Locate and return the 'View Bill' button element.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        WebElement: The 'View Bill' button element.
    """
    try:
        view_bill_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'grdCustList_ctl02_viewHTMLBill'))
        )
        logging.info("Located 'View Bill' button.")
        return view_bill_button
    except Exception as e:
        logging.error(f"Failed to locate 'View Bill' button: {e}")
        raise


def click_view_bill_button(driver: webdriver.Chrome) -> None:
    """
    Click the 'View Bill' button.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    view_bill_button = get_view_bill_button(driver)
    try:
        view_bill_button.click()
        logging.info("Clicked on 'View Bill' button.")
    except Exception as e:
        logging.error(f"Failed to click 'View Bill' button: {e}")
        raise


def switch_to_new_window(driver: webdriver.Chrome) -> None:
    """
    Switch to the latest opened window.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    driver.switch_to.window(driver.window_handles[-1])
    logging.info("Switched to new window.")


def click_view_printable_version(driver: webdriver.Chrome) -> None:
    """
    Click the 'View Printable Version' link.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'View Printable Version')]"))
    ).click()
    logging.info("Clicked on 'View Printable Version' link.")


def click_print_download_button(driver: webdriver.Chrome) -> None:
    """
    Click the 'Print / Download' button.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    print_download_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Print / Download')]"))
    )
    print_download_button.click()
    logging.info("Clicked on 'Print / Download' button.")


def access_and_download_bill(driver: webdriver.Chrome) -> Tuple[str, str]:
    """
    Access the bill and initiate the download process.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        Tuple[str, str]: Consumer name and number.
    """
    try:
        click_view_bill_button(driver)
        switch_to_new_window(driver)

        consumer_name, consumer_number = fetch_consumer_details(driver)

        if not consumer_name or not consumer_number:
            logging.error("Consumer details not found. Cannot proceed with file renaming.")
            return "", ""
        
        click_view_printable_version(driver)
        switch_to_new_window(driver)
        click_print_download_button(driver)
        
        time.sleep(5)
        
        handle_file_download(driver, DOWNLOAD_PATH_2, consumer_name, consumer_number)
        return consumer_name, consumer_number

    except TimeoutException as e:
        logging.error(f"Timeout occurred: {e}")
        page_source = driver.page_source
        with open("debug_page_source.html", "w") as file:
            file.write(page_source)
        logging.error("Page source saved to debug_page_source.html.")
        raise
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

