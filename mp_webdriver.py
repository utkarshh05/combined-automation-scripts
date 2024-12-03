import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from config import CHROMEDRIVER_PATH

# WebDriver Initialization


def configure_chrome_download_preferences(download_path: str) -> Options:
    """
    Configure Chrome options for downloading files.
    
    Args:
        download_path (str): Directory path where files will be downloaded.
    
    Returns:
        Options: Configured ChromeOptions instance.
    """
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")

    return chrome_options

def initialize_chrome_driver(download_path: str) -> webdriver.Chrome:
    """
    Initialize the Chrome WebDriver with specified options.
    
    Args:
        download_path (str): Directory path where files will be downloaded.
    
    Returns:
        webdriver.Chrome: Configured WebDriver instance.
    """
    chrome_options = configure_chrome_download_preferences(download_path)
    service = Service(CHROMEDRIVER_PATH)
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize Chrome driver: {e}")
        raise


