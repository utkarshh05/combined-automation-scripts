#mh_error_handling_module

import logging
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from mh_automation.mh_config import configure_logging
from mp_automation.mp_alert_handler import terminate_chrome_browser_instances

# Initialize logging
logger = configure_logging()

def handle_login_errors(driver: webdriver.Chrome) -> bool:
    """
    Handle login errors by checking for specific alert messages.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        bool: True if login was successful, False otherwise.
    """
    try:
        alert = WebDriverWait(driver, 5).until(
            EC.alert_is_present()
        )
        alert_text = alert.text
        if "Invalid CAPTCHA" in alert_text or "Enter CAPTCHA First" in alert_text:
            logger.error(f"CAPTCHA error: {alert_text}")
            alert.accept()
            return False
        elif "Please enter Login Name" in alert_text or "Please enter Password" in alert_text:
            logger.error(f"Login error: {alert_text}")
            alert.accept()
            return False
        else:
            logger.error(f"Unexpected alert: {alert_text}")
            alert.accept()
            return False
    except TimeoutException:
        return True
    except Exception as e:
        logger.error(f"Error handling alert: {e}")
        return False

def check_login_error(driver: webdriver.Chrome) -> bool:
    """
    Check for login error message on the website and return True if an error is found.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.

    Returns:
        bool: True if login error is detected, False otherwise.
    """
    try:
        error_message_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'error-message') and contains(text(), 'An error occurred during the login process, please try again')]"))
        )
        if error_message_element:
            logger.error("Login error detected on the website.")
            return True
    except TimeoutException:
        return False
    return False

def restart_login_process(driver: webdriver.Chrome) -> None:
    """
    Refreshes the CAPTCHA and preserves login details to prevent unnecessary restarts.
    
    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    logger.warning("Refreshing CAPTCHA and retrying...")
    
    # Save the current state of the login fields if necessary
    try:
        username_field = driver.find_element(By.ID, "username_field_id")
        password_field = driver.find_element(By.ID, "password_field_id")
        username = username_field.get_attribute("value")
        password = password_field.get_attribute("value")
    except NoSuchElementException:
        username = ""
        password = ""

    # Click the CAPTCHA refresh button
    try:
        captcha_refresh_button = driver.find_element(By.ID, "btnCaptchaRefLogin")
        captcha_refresh_button.click()
        logger.info("CAPTCHA refreshed.")
        time.sleep(3)  # Wait for CAPTCHA to refresh
    except NoSuchElementException:
        logger.error("CAPTCHA refresh button not found.")
    
    # Re-enter saved login details if they were found
    if username and password:
        try:
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            logger.info("Re-entered login details.")
        except NoSuchElementException as e:
            logger.error(f"Error re-entering login details: {e}")
    
    # Capture the new CAPTCHA image if necessary
    try:
        captcha_image = driver.find_element(By.ID, "captcha_image_id")
        captcha_image.screenshot('captcha.png')
        logger.info("CAPTCHA image saved.")
    except NoSuchElementException:
        logger.error("CAPTCHA image not found.")

def manage_unexpected_alerts(driver: webdriver.Chrome) -> None:
    """
    Handle expected and unexpected alerts by restarting the script if necessary.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.accept()
        logger.info("Unexpected alert handled.")
        restart_script_for_mh_website()
    except TimeoutException:
        logger.error("No unexpected alert detected.")


def restart_script_for_mh_website() -> None:
    """
    Restart the automation script for Website 2.
    """
    from main_program import main_mh_website

    logger.info("Restarting Maharashtra Website script...")
    terminate_chrome_browser_instances()
    # Restart the script by invoking the main function
    try:
        main_mh_website()
    except Exception as e:
        logging.error(f"Failed to restart the script: {e}")
        sys.exit(1)
