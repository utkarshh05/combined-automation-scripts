import logging
from mp_automation.mp_database import create_database_engine, retrieve_ivrs_numbers
from mp_automation.mp_webdriver import initialize_chrome_driver
from mp_automation.mp_web_interaction import wait_for_page_load, locate_element, click_on_element
from mp_automation.mp_website import download_bill_for_ivrs
from mp_automation.mp_file_operations import rename_latest_pdf_file
from mp_automation.mp_alert_handler import handle_unexpected_alert, restart_script_for_mp_website, terminate_chrome_browser_instances
from mh_automation.mh_config import configure_logging, launch_browser
from mh_automation.mh_database import setup_maharashtra_db_connection, get_credentials_by_id
from mh_automation.mh_captcha_handler import refresh_captcha, solve_captcha, enter_captcha, solve_captcha_and_login
from mh_automation.mh_login import select_language, navigate_to_login_page, enter_login_details, perform_login
from mh_automation.mh_bill_access import get_view_bill_button, click_view_bill_button, switch_to_new_window, click_view_printable_version, click_print_download_button, access_and_download_bill
from mh_automation.mh_file_manager import wait_for_download_to_complete, handle_file_download, fetch_consumer_details, rename_file
from mh_automation.mh_error_handler import handle_login_errors, check_login_error, restart_login_process, manage_unexpected_alerts, restart_script_for_mh_website
from config import CHROMEDRIVER_PATH, DOWNLOAD_PATH_1, DOWNLOAD_PATH_2, LOGIN_URL_MP, LOGIN_URL_MH, DATABASE_URL

# Initialize logging
logger = configure_logging()

def main_mp_website() -> None:
    """
    Main function to download bills for all IVRS numbers.
    """
    logging.info("Starting Madhya Pradesh Website Automation Script.")

    try:
        engine = create_database_engine(DATABASE_URL)
        # Retrieve all IVRS numbers from the database
        ivrs_numbers = retrieve_ivrs_numbers(engine)
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        return

    try:
        driver = initialize_chrome_driver(DOWNLOAD_PATH_1)
    except Exception as e:
        logging.error(f"Failed to initialize Chrome driver: {e}")
        return

    for ivrs_no in ivrs_numbers:
        try:
            download_bill_for_ivrs(driver, ivrs_no)
            logging.info("Process completed successfully for IVRS number: %s", ivrs_no)

            if not handle_unexpected_alert(driver):
                restart_script_for_mp_website()
                break
        except Exception as e:
            logging.error(f"Error in processing IVRS number {ivrs_no}: {e}")
            restart_script_for_mp_website()
            break
    # Attempt to quit the driver after processing all IVRS numbers
    try:
        driver.quit()
    except Exception as e:
        logging.error(f"Failed to quit driver: {e}")

    logging.info("All IVRS bills processed successfully.")
    logging.info("Ending Madhya Pradesh Website Automation Script.")

def main_mh_website():
    """
    Automate tasks for the Maharashtra State Electricity Distribution Co. Ltd. website.

    This function:
    1. Sets up the database and retrieves login credentials.
    2. Initializes the WebDriver.
    3. Performs login using the retrieved credentials.
    4. Accesses and downloads the bill.
    5. Handles any exceptions and alerts that occur during the process.
    """
    logging.info("Starting Maharashtra Website Automation Script.")
    driver = None
    session = None
    success = False

    try:
        # Setup the database and create a session
        Session, mh_table = setup_maharashtra_db_connection()
        session = Session()

        # Retrieve all IDs from the database
        ids = [record.id for record in session.query(mh_table).all()]

        for id in ids:
            credentials = get_credentials_by_id(session, mh_table, id)
            if credentials:
                driver = launch_browser(DOWNLOAD_PATH_2)

                username = credentials.get('login_name')
                password = credentials.get('password')

                if not username or not password:
                    logging.error(f"Missing username or password for record ID {id}. Skipping.")
                    continue

                try:
                    perform_login(driver, username, password)
                    access_and_download_bill(driver)
                    logging.info(f"Successfully processed record ID {id}.")
                    
                except Exception as e:
                    logging.error(f"An error occurred with record ID {id}: {e}")
                    handle_login_errors(driver)
                    driver.refresh()
                    
                finally:
                    if driver:
                        try:
                            driver.quit()
                            logging.info(f"Browser closed for record ID {id}.")
                        except Exception as quit_error:
                            logging.error(f"Error closing the browser for record ID {id}: {quit_error}")
                    driver = None

            else:
                logging.error(f"Invalid record format: {credentials}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        if driver:
            manage_unexpected_alerts(driver)

    finally:
        if session:
            session.close()

    logging.info("Ending Maharashtra Website Automation Script.")


if __name__ == "__main__":

##    try:
##        logging.info("Starting automation scripts for both websites.")
##        main_mp_website()
##    except Exception as e:
##        logging.error(f"Script encountered an error: {e}. Restarting the script...")
##        restart_script_for_mp_website()
    
    try:
        main_mh_website()
    except Exception as e:
        logging.error(f"Script encountered an error: {e}. Restarting the script for Maharashtra Website...")
        restart_script_for_mh_website()
    
    logging.info("Ending automation scripts for both websites.")

