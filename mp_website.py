import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from mp_automation.mp_web_interaction import wait_for_page_load, locate_element, click_on_element
from mp_automation.mp_file_operations import rename_latest_pdf_file
from config import LOGIN_URL_MP, DOWNLOAD_PATH_1


def navigate_to_mp_website(driver: webdriver.Chrome) -> None:
    """
    Navigate to the website and perform initial setup.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
    """
    driver.get(LOGIN_URL_MP)
    wait_for_page_load(driver)
    logging.info("Navigated to M.P. Pashchim Kshetra Vidyut Vitaran Co. Ltd. website.")

def input_ivrs_number(driver: webdriver.Chrome, ivrs_no: str) -> None:
    """
    Input IVRS number into the form.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
        ivrs_no (str): IVRS number to be entered.
    """
    try:
        ivrs_input = locate_element(driver, By.XPATH, "//input[contains(@class, 'form-control')]")
        ivrs_input.clear()
        ivrs_input.send_keys(ivrs_no)
        logging.info(f"Entered IVRS number: {ivrs_no}")
    except Exception as e:
        logging.error(f"Error entering IVRS number {ivrs_no}: {e}")
        raise

def submit_form(driver: webdriver.Chrome, ivrs_no: str) -> None:
    """
    Submit the form to view the bill.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
        ivrs_no (str): IVRS number used for logging.
    """
    click_on_element(driver, By.XPATH, "//input[contains(@class, 'btn-warning')]")
    time.sleep(5)
    logging.info("Login submitted for IVRS number: %s", ivrs_no)

def click_full_bill_button(driver: webdriver.Chrome) -> None:
    """
    Click the "Full Bill" button.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
    """
    click_on_element(driver, By.XPATH, "//button[contains(text(), 'View Full Bill (English)')]")
    time.sleep(5)

def handle_post_download(ivrs_no: str) -> None:
    """
    Handle post-download steps such as renaming the file.
    
    Args:
        ivrs_no (str): IVRS number used for renaming the file.
    """
    rename_latest_pdf_file(DOWNLOAD_PATH_1, ivrs_no)
    logging.info(f"Bill downloaded and renamed for IVRS number: {ivrs_no}")

def download_bill_for_ivrs(driver: webdriver.Chrome, ivrs_no: str) -> None:
    """
    Download the bill for the provided IVRS number.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
        ivrs_no (str): IVRS number for which the bill is to be downloaded.
    """
    navigate_to_mp_website(driver)
    input_ivrs_number(driver, ivrs_no)
    submit_form(driver, ivrs_no)
    click_full_bill_button(driver)  
    handle_post_download(ivrs_no)

