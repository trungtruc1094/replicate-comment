from selenium import webdriver

def initialize_webdriver():
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"  # Ensure this matches your Chrome setup

    driver = webdriver.Chrome(options=options)
    return driver
