import time
import logging
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.delays import simulate_typing, human_like_delay, rate_limiting_pause

def extract_index_from_xpath(xpath):
    """Extract the numerical index from the comment's XPath."""
    match = re.search(r'div\[(\d+)\]/div/div\[2\]/span\[2\]', xpath)
    if match:
        return int(match.group(1))
    return None

def fetch_all_comments(driver, source_tab_handle):
    """Fetch all comments from the livestream tab (source tab) and assign an ID based on their position."""
    driver.switch_to.window(source_tab_handle)
    time.sleep(1)
    logging.info(f"Switched to source tab with URL: {driver.current_url}")

    comments_xpath = '//*[@id="default-activity-chat"]/div/div/div[2]/span[2]'
    comments_elements = driver.find_elements(By.XPATH, comments_xpath)
    
    if not comments_elements:
        logging.warning("No comment elements found using the provided XPath.")
    else:
        logging.info(f"Found {len(comments_elements)} comment elements.")

    comments = []
    for index, element in enumerate(comments_elements, start=2):
        comment_text = element.text.strip()
        logging.info(f"Processing comment at index {index}: '{comment_text}'")
        
        if comment_text:
            comment_id = f"comment_{index}"
            comments.append((comment_id, comment_text))
            logging.info(f"Comment added with ID: {comment_id} - Text: {comment_text}")
        else:
            logging.warning(f"Comment at index {index} is empty or only contains whitespace.")

    logging.info(f"Total comments fetched: {len(comments)}")
    return comments


def send_unsent_comments(driver, recipient_tab_handle, comments_list, sensitive_words):
    """Send comments based on the logic: send one, skip two, ensuring no sensitive words."""
    logging.info(f"Unsent comments dict: {comments_list}")
    unsent_found = False
    comment_counter = 0
    logging.info(f"Starting to send comments. Total comments to process: {len(comments_list)}")
    
    for comment in comments_list:
        unique_id = comment['unique_id']
        text = comment['text']
        sent_status = comment['sent']  # If you're tracking the 'sent' status
        logging.info(f"Evaluating comment ID: {unique_id} - Text: {text} - Status: {sent_status}")
        
        if comment_counter == 0 and filter_sensitive_words(text, sensitive_words):
            paste_comment(driver, recipient_tab_handle, text)
            logging.info(f"Sent comment ID: {unique_id} - Text: {text}")
            unsent_found = True
            comment_counter = 1
        
        elif comment_counter == 3:
            if filter_sensitive_words(text, sensitive_words):
                paste_comment(driver, recipient_tab_handle, text)
                logging.info(f"Sent comment ID: {unique_id} - Text: {text}")
                unsent_found = True
            comment_counter = 1
        
        else:
            logging.info(f"Skipping comment ID: {unique_id} - Text: {text}")
            comment_counter += 1

    if not unsent_found:
        logging.info("No unsent comments found, or all comments contained sensitive words. Returning to the source tab to listen for new comments.")

def paste_comment(driver, recipient_tab_handle, comment):
    """Paste the latest comment into the recipient tab."""
    driver.switch_to.window(recipient_tab_handle)
    time.sleep(1)
    logging.info(f"Current tab URL: {driver.current_url}")

    input_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[1]/div/div/div[1]/div[2]/div[2]/div/textarea'))
    )
    
    simulate_typing(input_box, comment)
    input_box.send_keys(u'\ue007')
    logging.info(f"Comment '{comment}' pasted.")
    human_like_delay(5, 15)
    rate_limiting_pause()

def filter_sensitive_words(comment, sensitive_words):
    """Filter out sensitive words from the comment."""
    for word in sensitive_words:
        if word in comment.lower():
            logging.info(f"Comment contains sensitive word '{word}'. Skipping or altering comment.")
            return False
    return True
