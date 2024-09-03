import time
import random
import logging

def human_like_delay(min_seconds=5, max_seconds=15):
    """Introduce a longer random delay to simulate human-like actions."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def rate_limiting_pause():
    """Introduce random pauses to simulate breaks in user activity."""
    if random.random() < 0.2:
        pause_duration = random.uniform(30, 90)
        logging.info(f"Taking a break for {pause_duration:.2f} seconds to avoid detection.")
        time.sleep(pause_duration)

def simulate_typing(element, text):
    """Simulate typing each character with a random delay."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))
