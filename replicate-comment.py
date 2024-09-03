import time
import logging
import random
import platform
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

def fetch_all_comments(driver):
    """Fetch all comments from the livestream tab (first tab)."""
    driver.switch_to.window(driver.window_handles[0])  # Switch to the first tab (livestream)
    logging.info("Switched to the livestream tab to fetch comments.")
    
    # Generalized XPath pattern to match all comment elements
    comments_xpath = '//*[@id="default-activity-chat"]/div/div/div[2]/span[2]'
    
    # Find all elements that match the XPath
    comments_elements = driver.find_elements(By.XPATH, comments_xpath)
    
    comments = []
    for element in comments_elements:
        comments.append({
            'text': element.text,
            'sent': False  # Initially mark each comment as unsent
        })
    
    logging.info(f"Fetched {len(comments)} comments.")
    return comments

def send_unsent_comments(driver, comments_list):
    """Send all unsent comments to the recipient tab."""
    for comment in comments_list:
        if not comment['sent']:
            paste_comment(driver, comment['text'])
            comment['sent'] = True  # Mark comment as sent
            logging.info(f"Comment sent and marked as sent: {comment['text']}")

def paste_comment(driver, comment):
    """Paste the latest comment into the second tab."""
    driver.switch_to.window(driver.window_handles[1])  # Switch to the second tab (sending comments)
    logging.info("Switched to the second tab to paste the comment.")

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
    
    comments_list = []
    
    try:
        while True:
            # Step 2: Fetch all comments from the livestream tab
            current_comments = fetch_all_comments(driver)
            
            # Step 3: Update the comments_list with new comments
            for comment in current_comments:
                if comment not in comments_list:
                    comments_list.append(comment)
            
            # Step 4: Send all unsent comments
            send_unsent_comments(driver, comments_list)
            
            # Step 5: Wait for a short period before checking again
            human_like_delay(5, 10)  # Adjust delay as necessary
            
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    
    finally:
        # Step 6: Close the browser
        logging.info("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()