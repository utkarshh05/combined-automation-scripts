import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, UnexpectedAlertPresentException
)
from mh_automation.mh_captcha_handler import refresh_captcha, solve_captcha_and_login
from mh_automation.mh_error_handler import handle_login_errors, restart_script_for_mh_website
from mh_automation.mh_config import configure_logging
from config import LOGIN_URL_MH

# Initialize logging
logger = configure_logging()

def select_language(driver: webdriver.Chrome, language: str = "English") -> None:
    """
    Selects the language on the website.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        language (str): Language to select. Defaults to "English".
    """
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'topnav_hreflanguage'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//a[text()='{language}']"))
    ).click()

def navigate_to_login_page(driver: webdriver.Chrome) -> None:
    """
    Navigates to the login page of the website.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
    """
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
    ).click()
    time.sleep(2)

def enter_login_details(driver: webdriver.Chrome, username: str, password: str) -> None:
    """
    Enters the login details (username and password).

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        username (str): Username for login.
        password (str): Password for login.
    """
    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'loginId'))
        )
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'password'))
        )
        username_input.clear()
        password_input.clear()
        username_input.send_keys(username)
        password_input.send_keys(password)
        logger.info("Entered login details.")
    except NoSuchElementException as e:
        logger.error(f"Login input fields not found: {e}")
        raise

def perform_login(driver: webdriver.Chrome, username: str, password: str) -> None:
    """
    Perform login operation on the website with retry logic for CAPTCHA failures,
    handling unexpected alerts and other exceptions efficiently.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        username (str): Username for login.
        password (str): Password for login.
    """
    from main_program import main_mh_website

    driver.get(LOGIN_URL_MH)
    
    try:
        select_language(driver, 'English')
        navigate_to_login_page(driver)
        time.sleep(2)

        max_captcha_attempts = 10
        captcha_attempts = 0

        while captcha_attempts < max_captcha_attempts:
            try:
                if captcha_attempts == 0:
                    enter_login_details(driver, username, password)
                
                captcha_value = solve_captcha_and_login(driver)

                if not captcha_value:
                    logger.error("CAPTCHA value is empty. Refreshing CAPTCHA...")
                    refresh_captcha(driver)
                    captcha_attempts += 1
                    continue

                logger.info(f"CAPTCHA entered: {captcha_value}")

                if handle_login_errors(driver):
                    break
                else:
                    logger.info("Login failed due to CAPTCHA. Retrying...")
                    captcha_attempts += 1
                    refresh_captcha(driver)
                    
            except UnexpectedAlertPresentException:
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    logger.warning("Unexpected alert handled.")
                except Exception as alert_exception:
                    logger.error(f"Error handling alert: {alert_exception}")
                captcha_attempts += 1

            except NoSuchElementException as e:
                logger.warning(f"Login elements not found: {e}. Retrying...")
                captcha_attempts += 1
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error during CAPTCHA handling: {e}")
                driver.refresh()
                time.sleep(5)
                captcha_attempts += 1

        if captcha_attempts >= max_captcha_attempts:
            logger.error("Max CAPTCHA attempts exceeded. Restarting script...")
            restart_script_for_mh_website()

    except Exception as e:
        logger.error(f"Unexpected error during login process: {e}")
        restart_script_for_mh_website()





