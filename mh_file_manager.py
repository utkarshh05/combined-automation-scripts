#mh_file_management_module

import logging
import os
import time
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, NoAlertPresentException, UnexpectedAlertPresentException
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from mh_automation.mh_config import configure_logging

# Initialize logging
logger = configure_logging()

def wait_for_download_to_complete(download_path: str, timeout: int = 120) -> str:
    """
    Wait for the download to complete by checking if the file is present in the download directory.

    Args:
        download_path (str): The path where files are downloaded.
        timeout (int): The maximum time to wait for the download to complete.

    Returns:
        str: The path to the downloaded file.
    """
    start_time = time.time()
    while True:
        files = os.listdir(download_path)
        pdf_files = [f for f in files if f.endswith('.pdf') and not f.endswith('.pdf.part')]
        if pdf_files:
            latest_file = max(pdf_files, key=lambda f: os.path.getctime(os.path.join(download_path, f)))
            return os.path.join(download_path, latest_file)
        
        if time.time() - start_time > timeout:
            raise TimeoutError("Download did not complete within the specified timeout.")
        
        time.sleep(1)


def handle_file_download(driver: webdriver.Chrome, download_path: str, consumer_name: str, consumer_number: str) -> None:
    """
    Handles the file download process by ensuring the file is saved and renamed directly.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance used for automation.
        download_path (str): The path where files are to be downloaded.
        consumer_name (str): The name of the consumer used for renaming the downloaded file.
        consumer_number (str): The number of the consumer used for renaming the downloaded file.

    Raises:
        Exception: If any error occurs during the file download or renaming process.
    """
    try:
        # Wait for the download to complete and get the file path
        downloaded_file_path = wait_for_download_to_complete(download_path)
        
        # Rename the file with consumer details
        new_filename = f"{consumer_name}_{consumer_number}.pdf"
        new_file_path = os.path.join(download_path, new_filename)
        os.rename(downloaded_file_path, new_file_path)
        logging.info(f"File successfully downloaded and renamed to {new_file_path}")

    except Exception as e:
        logging.error(f"Error in file download: {e}")
        raise

    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        logging.info("Browser closed and switched back to the first window.")


def fetch_consumer_details(driver: webdriver.Chrome) -> Tuple[str, str]:
    """
    Fetch the consumer name and number from the page.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        Tuple[str, str]: Consumer name and number.
    """
    try:
        consumer_number_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//td[@class='tdLabel' and contains(text(), 'Consumer No.')]/following-sibling::td"))
        )
        consumer_number = consumer_number_element.text.strip()
        
        consumer_name_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//td[@class='tdLabel' and contains(text(), 'Consumer Name')]/following-sibling::td"))
        )
        consumer_name = consumer_name_element.text.strip()

        logging.info(f"Consumer Name: {consumer_name}, Consumer Number: {consumer_number}")
        return consumer_name, consumer_number

    except TimeoutException:
        logging.error("Timeout: Consumer details not found.")
        return "", ""
    except Exception as e:
        logging.error(f"An error occurred while fetching consumer details: {e}")
        return "", ""


def rename_file(source_path: str, consumer_name: str, consumer_number: str) -> None:
    """
    Rename the downloaded file.

    Args:
        source_path (str): The path where the file is initially downloaded.
        consumer_name (str): The name of the consumer used for renaming the downloaded file.
        consumer_number (str): The number of the consumer used for renaming the downloaded file.
    
    Raises:
        FileNotFoundError: If no PDF file is found or if the file to be renamed does not exist.
    """
    timeout = 60
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        files = os.listdir(source_path)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        
        if pdf_files:
            latest_file = max(pdf_files, key=lambda f: os.path.getctime(os.path.join(source_path, f)))
            old_filename = os.path.join(source_path, latest_file)
            new_filename = os.path.join(source_path, f"{consumer_name}_{consumer_number}.pdf")
            
            if os.path.exists(old_filename):
                if not os.path.exists(new_filename):
                    os.rename(old_filename, new_filename)
                    logging.info(f"File renamed to: {new_filename}")
                else:
                    logging.warning(f"File {new_filename} already exists. Attempting to rename with a new pattern.")
                    # Handle file naming conflict
                    counter = 1
                    while os.path.exists(new_filename):
                        new_filename = os.path.join(source_path, f"{consumer_name}_{consumer_number}_{counter}.pdf")
                        counter += 1
                    os.rename(old_filename, new_filename)
                    logging.info(f"File renamed to: {new_filename}")
                return
            
        time.sleep(1)

    logging.error("No PDF file found in the source directory within the timeout period.")
    raise FileNotFoundError("No PDF file found in the source directory within the timeout period.")


