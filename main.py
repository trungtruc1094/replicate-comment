import logging_config  # Import the logging configuration
from utils.browser import initialize_webdriver
from utils.tab_management import identify_tabs
from utils.comment_processing import fetch_all_comments, send_unsent_comments
from utils.database import initialize_database, store_comments, get_unsent_comments, mark_comment_as_sent, close_database, delete_database
from utils.delays import human_like_delay
import logging
import config

def main():
    # Step 1: Initialize WebDriver
    logging.info("Initializing WebDriver...")
    driver = initialize_webdriver()

    # Step 2: Identify the source and recipient tabs by their URLs
    source_tab_handle, recipient_tab_handle = identify_tabs(driver)
    if not source_tab_handle or not recipient_tab_handle:
        return

    # Initialize the SQLite database
    conn = initialize_database()
    sensitive_words_list = config.SENSITIVE_WORDS_LIST
    
    try:
        while True:
            # Step 3: Fetch all comments from the source tab
            current_comments = fetch_all_comments(driver, source_tab_handle)
            
            # Step 4: Store new comments in the database
            logging.info(f"Current comments: {current_comments}")
            store_comments(conn, current_comments)
            
            # Step 5: Retrieve and send unsent comments
            unsent_comments = get_unsent_comments(conn)
            logging.info(f"Unsent comments: {unsent_comments}")
            send_unsent_comments(driver, recipient_tab_handle, [{'unique_id': unique_id, 'text': text, 'sent': False} for unique_id, text in unsent_comments], sensitive_words_list)
            
            # Mark comments as sent after they are processed
            for comment in unsent_comments:
                mark_comment_as_sent(conn, comment[1])
            
            # Step 6: Return to the source tab for new comments
            driver.switch_to.window(source_tab_handle)
            human_like_delay(1, 3)  # Delay after switching tabs
            logging.info(f"Returned to the source tab to listen for new comments. Current tab URL: {driver.current_url}")

            # Step 7: Wait for a short period before checking again
            logging.info("Waiting for a short period before checking for new comments again.")
            human_like_delay(5, 10)  # Adjust delay as necessary
            
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    
    finally:
        # Step 8: Close the SQLite database and browser
        close_database(conn)
        delete_database()
        logging.info("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()
