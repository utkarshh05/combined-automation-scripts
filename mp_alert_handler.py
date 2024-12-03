import os
import logging
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mp_automation.mp_database import create_database_engine, retrieve_ivrs_numbers

def handle_unexpected_alert(driver: webdriver.Chrome) -> bool:
    """
    Handle unexpected alerts and determine if a restart is needed.
    
    Args:
        driver (webdriver.Chrome): WebDriver instance.
    
    Returns:
        bool: True if no unexpected alert was detected, False otherwise.
    """
    try:
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()
        logging.error(f"Unexpected alert encountered: {alert_text}")

        if "Invalid IVRS" in alert_text:
            logging.info("Handling Invalid IVRS alert")
        else:
            logging.info("Unexpected alert detected. Restarting the script.")
        driver.quit()
        restart_script_for_mp_website()
        return False

    except TimeoutException:
        logging.info("No unexpected alert detected.")
        return True
    except Exception as e:
        logging.error(f"Error while handling unexpected alert: {e}")
        driver.quit()
        restart_script_for_mp_website()
        return False

def terminate_chrome_browser_instances() -> None:
    """
    Terminate all open Chrome browser instances.
    """
    logging.info("Terminating all Chrome browser instances.")
    try:
        os.system("pkill chrome")
    except Exception as e:
        logging.error(f"Failed to terminate Chrome browser instances: {e}")

def restart_script_for_mp_website() -> None:
    """
    Restart the automation script for the M.P. Pashchim Kshetra Vidyut Vitaran Co. Ltd. website.
    """
    from main_program import main_mp_website

    logging.info("Restarting script for M.P. Pashchim Kshetra Vidyut Vitaran Co. Ltd. website...")
    terminate_chrome_browser_instances()
    # Restart the script by invoking the main function
    try:
        main_mp_website()
    except Exception as e:
        logging.error(f"Failed to restart the script: {e}")
        sys.exit(1)

