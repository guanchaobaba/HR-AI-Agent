# Selenium browser helper functions
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC


def create_selenium_driver(url):
    """Create a new Chrome driver with given is_headless setting"""

    # Options for Chrome WebDriver
    # Note: You need to close the Chrome browser manually, because only one Chrome browser can use the profile at a time
    my_options = webdriver.ChromeOptions()
    profile_path = r"C:\Users\rasel\AppData\Local\Google\Chrome\User Data"
    profile_name = "Profile 1"  # Use "Profile N" if you have other accounts in Chrome
    my_options.add_argument(f"--user-data-dir={profile_path}")
    my_options.add_argument(f"--profile-directory={profile_name}")

    # Note: Don't write profile name after "...\Chrome\User Data", because it will make a new folder in that path.

    # Use Chrome WebDriver
    driver = webdriver.Chrome(
        options=my_options,
    )

    '''OPTIONAL:
    Download and use the JS code to avoid being detected by the website would block you
    https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js'''

    # load stealth.min.js from the same folder as this script
    stealth_path = os.path.join(os.path.dirname(__file__), 'stealth.min.js')
    if not os.path.exists(stealth_path):
        raise FileNotFoundError(f"stealth.min.js not found at {stealth_path}")
    with open(stealth_path, 'r', encoding='utf8') as f:
        js = f.read()

    # Execute the JavaScript code
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument", {'source': js})

    '''Vist the following two websites to test whether the browser is ok for anti-crawling
    1. https://bot.sannysoft.com/
    2. https://antcpt.com/score_detector/'''

    driver.get(url)

    sleep(10)

    return driver
