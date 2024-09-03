import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the WebDriver by attaching to an existing Chrome session
def initialize_webdriver():
    options = webdriver.ChromeOptions()
    
    # Specify the debugger address to attach to an existing Chrome session
    options.debugger_address = "127.0.0.1:9222"  # Ensure this matches your Chrome setup

    driver = webdriver.Chrome(options=options)
    return driver

def simulate_typing(element, text):
    """Simulate typing each character with a random delay."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))  # Random delay between each keystroke

def human_like_delay(min_seconds=1, max_seconds=3):
    """Introduce a random delay to simulate human-like actions."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def identify_tabs(driver):
    """Identify the source and recipient tabs by checking for specific text in their URLs."""
    source_tab_handle = None
    recipient_tab_handle = None

    # Iterate over all open window handles
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        time.sleep(1)  # Delay to ensure the page loads properly
        current_url = driver.current_url.lower()  # Convert URL to lowercase for case-insensitive comparison
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

def fetch_all_comments(driver, source_tab_handle):
    """Fetch all comments from the livestream tab (source tab)."""
    driver.switch_to.window(source_tab_handle)  # Switch to the source tab (livestream)
    time.sleep(1)  # Delay after switching tabs
    logging.info(f"Current tab URL: {driver.current_url}")  # Show current tab URL
    
    # Generalized XPath pattern to match all comment elements
    comments_xpath = '//*[@id="default-activity-chat"]/div/div/div[2]/span[2]'
    
    # Find all elements that match the XPath
    comments_elements = driver.find_elements(By.XPATH, comments_xpath)
    
    # Print out the text of each element found
    for idx, element in enumerate(comments_elements):
        logging.info(f"Comment element {idx}: {element.text}")

    if not comments_elements:
        logging.warning("No comments found with the given XPath.")

    comments = []
    for element in comments_elements:
        comment_text = element.text.strip()
        if comment_text:  # Ensure the comment has some text
            comments.append(comment_text)  # Collect the text of each comment
    
    return comments

def update_comments_list(comments_list, new_comments, last_comment):
    """Update the comments_list with new comments, ensuring no duplicates, starting from the last comment."""
    start_collecting = last_comment is None  # Start collecting if there is no last_comment
    
    for new_comment in new_comments:
        if start_collecting:
            comments_list.append({
                'text': new_comment,
                'sent': False
            })
            logging.info(f"Added new comment to list: {new_comment}")
        elif new_comment == last_comment:
            start_collecting = True  # Start collecting new comments after the last known comment

def send_unsent_comments(driver, recipient_tab_handle, comments_list):
    """Send all unsent comments to the recipient tab."""
    unsent_found = False
    for comment in comments_list:
        if not comment['sent']:
            paste_comment(driver, recipient_tab_handle, comment['text'])
            comment['sent'] = True  # Mark comment as sent
            logging.info(f"Comment sent and marked as sent: {comment['text']}")
            unsent_found = True
    
    if not unsent_found:
        logging.info("No unsent comments found. Returning to the source tab to listen for new comments.")

def paste_comment(driver, recipient_tab_handle, comment):
    """Paste the latest comment into the recipient tab."""
    driver.switch_to.window(recipient_tab_handle)  # Switch to the recipient tab
    time.sleep(1)  # Delay after switching tabs
    logging.info(f"Current tab URL: {driver.current_url}")  # Show current tab URL

    # Find the input element where you want to paste the comment
    input_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[1]/div/div/div[1]/div[2]/div[2]/div/textarea'))  # Replace with your actual selector
    )
    
    simulate_typing(input_box, comment)
    input_box.send_keys(u'\ue007')  # Unicode for Enter key to submit the comment
    logging.info(f"Comment '{comment}' pasted.")
    human_like_delay(1, 2)

# Main function
def main():
    # Step 1: Initialize WebDriver
    logging.info("Initializing WebDriver...")
    driver = initialize_webdriver()

    # Step 2: Identify the source and recipient tabs by their URLs
    source_tab_handle, recipient_tab_handle = identify_tabs(driver)
    if not source_tab_handle or not recipient_tab_handle:
        return

    comments_list = []
    
    # Step 3: Fetch the initial comments and identify the last comment
    initial_comments = fetch_all_comments(driver, source_tab_handle)
    last_comment = initial_comments[-1] if initial_comments else None
    logging.info(f"Last existing comment: {last_comment}")
    
    try:
        while True:
            # Step 4: Fetch all comments from the source tab starting after the last known comment
            current_comments = fetch_all_comments(driver, source_tab_handle)
            
            # Step 5: Update the comments_list with new comments
            update_comments_list(comments_list, current_comments, last_comment)
            
            # Update last_comment to the last one in the current fetch
            if current_comments:
                last_comment = current_comments[-1]
            
            # Step 6: Send all unsent comments
            send_unsent_comments(driver, recipient_tab_handle, comments_list)
            
            # Step 7: Return to the source tab for new comments
            driver.switch_to.window(source_tab_handle)
            time.sleep(1)  # Delay after switching tabs
            logging.info(f"Returned to the source tab to listen for new comments. Current tab URL: {driver.current_url}")

            # Step 8: Wait for a short period before checking again
            human_like_delay(5, 10)  # Adjust delay as necessary
            
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    
    finally:
        # Step 9: Close the browser
        logging.info("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()
