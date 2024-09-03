import logging
import time

def identify_tabs(driver):
    """Identify the source and recipient tabs by checking for specific text in their URLs."""
    source_tab_handle = None
    recipient_tab_handle = None

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        time.sleep(1)
        current_url = driver.current_url.lower()
        logging.info(f"Checking tab with URL: {current_url}")

        if "tevi" in current_url:
            source_tab_handle = handle
            logging.info("Identified source tab (contains 'tevi' in URL).")
        elif "bigo" in current_url:
            recipient_tab_handle = handle
            logging.info("Identified recipient tab (contains 'bigo' in URL).")
    
    if not source_tab_handle:
        logging.error("Failed to identify the source tab. Please check the URLs.")
    if not recipient_tab_handle:
        logging.error("Failed to identify the recipient tab. Please check the URLs.")
    
    return source_tab_handle, recipient_tab_handle
