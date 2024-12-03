import os
import time
import logging

def rename_latest_pdf_file(download_path: str, ivrs_no: str) -> None:
    """
    Rename the latest downloaded PDF file using the IVRS number.

    Args:
        download_path (str): Directory path where files are downloaded.
        ivrs_no (str): IVRS number to be used for renaming the file.

    Raises:
        FileNotFoundError: If no PDF file is found in the download directory.
    """
    time.sleep(10)
    
    files = os.listdir(download_path)
    pdf_files = [f for f in files if f.endswith('.pdf')]
    
    if pdf_files:
        latest_file = max(pdf_files, key=lambda f: os.path.getctime(os.path.join(download_path, f)))
        old_filename = os.path.join(download_path, latest_file)
        new_filename = os.path.join(download_path, f"IVRS-{ivrs_no}.pdf")
        
        if os.path.exists(old_filename):
            if not os.path.exists(new_filename):
                os.rename(old_filename, new_filename)
                logging.info(f"Renamed file to: {new_filename}")
            else:
                logging.warning(f"File {new_filename} already exists. Attempting to rename with a new pattern.")
                counter = 1
                while os.path.exists(new_filename):
                    new_filename = os.path.join(download_path, f"IVRS-{ivrs_no}_{counter}.pdf")
                    counter += 1
                os.rename(old_filename, new_filename)
                logging.info(f"Renamed file to: {new_filename}")
        else:
            logging.error(f"Original file {old_filename} not found.")
            raise FileNotFoundError(f"Original file {old_filename} not found.")
    else:
        logging.error("No PDF file found in the download directory.")
        raise FileNotFoundError("No PDF file found in the download directory.")


