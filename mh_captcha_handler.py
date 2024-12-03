import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import pytesseract
from config import CAPTCHA_IMAGE_PATH
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, UnexpectedAlertPresentException, StaleElementReferenceException
)
from mh_automation.mh_config import configure_logging
from mh_automation.mh_error_handler import handle_login_errors, restart_login_process

# Initialize logging
logger = configure_logging()
    
def solve_captcha(driver: webdriver.Chrome) -> str:
    """
    Solve CAPTCHA by extracting the text from the CAPTCHA image.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        str: Extracted CAPTCHA value.
    """
    try:
        captcha_image = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'divCaptcha'))
        )
        captcha_image.screenshot(CAPTCHA_IMAGE_PATH)
        
        captcha_image = Image.open(CAPTCHA_IMAGE_PATH)
        captcha_value = pytesseract.image_to_string(Image.open(CAPTCHA_IMAGE_PATH)).strip()

        if not captcha_value:
            raise ValueError("Extracted CAPTCHA value is empty.")
        
        logger.info(f"Extracted CAPTCHA value: {captcha_value}")
        return captcha_value
    
    except Exception as e:
        logger.error(f"Failed to extract CAPTCHA value: {e}")
        refresh_captcha(driver)
        return ""  # Return an empty string to indicate failure

def refresh_captcha(driver: webdriver.Chrome) -> None:
    """
    Refreshes the CAPTCHA by clicking the refresh button.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    try:
        refresh_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'btnCaptchaRefLogin'))
        )
        refresh_button.click()
        logger.info("Successfully refreshed CAPTCHA.")
        time.sleep(2)

    except (TimeoutException, StaleElementReferenceException) as e:
        logger.error(f"Failed to refresh CAPTCHA: {str(e)}")
        raise


def enter_captcha(driver: webdriver.Chrome) -> None:
    """
    Enters the CAPTCHA value into the input field.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    try:
        captcha_value = solve_captcha(driver)
        if not captcha_value:
            logger.error("CAPTCHA value is empty. Skipping entry.")
            return

        captcha_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'txtInput'))
        )
        captcha_input.clear()
        captcha_input.send_keys(captcha_value)
        logger.info(f"CAPTCHA entered: {captcha_value}")
    except NoSuchElementException:
        logger.warning("CAPTCHA input field not found.")
        raise
    except Exception as e:
        logger.error(f"Error entering CAPTCHA: {e}")
        raise

def solve_captcha_and_login(driver: webdriver.Chrome) -> bool:
    """
    Handles CAPTCHA entry and attempts to log in.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    max_captcha_attempts = 10
    captcha_attempts = 0

    while captcha_attempts < max_captcha_attempts:
        try:
            enter_captcha(driver)
            driver.find_element(By.ID, 'loginButton').click()
            time.sleep(5)

            if handle_login_errors(driver):
                logger.info("Login successful.")
                return True

            logger.info("Login failed. Retrying CAPTCHA...")
            captcha_attempts += 1
        except NoSuchElementException as e:
            logger.warning(f"Login elements not found: {e}. Retrying...")
            captcha_attempts += 1
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error during CAPTCHA handling: {e}")
            restart_login_process(driver)
            captcha_attempts += 1

    logger.error("Max CAPTCHA attempts exceeded.")
    return False
