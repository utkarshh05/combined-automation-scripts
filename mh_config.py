#mh_config_module

import logging
import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from config import CHROMEDRIVER_PATH

# Initialize logging
def configure_logging() -> logging.Logger:
    """Configure logging settings."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def configure_chrome_options(download_path: str) -> webdriver.ChromeOptions:
    """
    Configure Chrome options for file download and print preview.

    Args:
        download_path (str): The path where downloaded files should be saved.

    Returns:
        webdriver.ChromeOptions: Configured Chrome options.
    """
    options = webdriver.ChromeOptions()
    profile = {
        "plugins.always_open_pdf_externally": True,
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "download.safebrowsing.enabled": True,
        "download.open_pdf_in_system_reader": False,
        "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local","account":""}],"selectedDestinationId":"Save as PDF","version":2}',  # Auto-select 'Save as PDF' in print preview
    }
    
    prefs = {
        'printing.default_directory': download_path,
        'savefile.default_directory': download_path,
        'download.default_directory': download_path,
    }

    options.add_experimental_option("prefs", {**profile, **prefs})
    options.add_argument("--kiosk-printing")  
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    return options

def launch_browser(download_path: str) -> webdriver.Chrome:
    """
    Initialize the WebDriver with configured Chrome options.

    Args:
        download_path (str): The path where downloaded files should be saved.

    Returns:
        webdriver.Chrome: The initialized WebDriver instance.

    Raises:
        Exception: If there is an error initializing the WebDriver.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    options = configure_chrome_options(download_path)
    service = Service(CHROMEDRIVER_PATH)
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
    except WebDriverException as e:
        logger.error(f"Failed to initialize driver: {e}")
        raise
    return driver
