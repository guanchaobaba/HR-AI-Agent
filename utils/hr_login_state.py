import os
from datetime import datetime
import json
from selenium.webdriver.support.ui import WebDriverWait
from utils import wait_for_page_load
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .logger import logger

BASE_DIR = os.getcwd()


def validate_cookie_format(cookie):
    """Validate individual cookie format"""
    required_fields = ['name', 'value']
    for field in required_fields:
        if field not in cookie:
            logger.warning(f"Cookie validation failed: missing required field '{field}'")
            return False
    return True


def validate_cookies_file(cookies):
    """Validate the entire cookies file"""
    if not isinstance(cookies, list):
        logger.error("Cookies file must contain a list of cookie objects")
        return False
    
    if not cookies:
        logger.warning("Cookies file is empty")
        return False
    
    for cookie in cookies:
        if not validate_cookie_format(cookie):
            return False
    
    logger.debug(f"Successfully validated {len(cookies)} cookies")
    return True


def import_browser_cookies(driver, cookie_file=os.path.join(BASE_DIR, 'userSecret', 'browser_cookies.json')):
    """Import cookies from browser export with validation"""
    try:
        if not os.path.exists(cookie_file):
            logger.error(f"Cookie file {cookie_file} not found")
            return False

        with open(cookie_file, 'r', encoding='utf-8') as file:
            cookies = json.load(file)

        # Validate cookies format
        if not validate_cookies_file(cookies):
            logger.error("Invalid cookie format")
            return False

        # Load domain before adding cookies
        logger.debug("Loading domain before adding cookies")
        driver.get('https://www.zhipin.com')
        wait_for_page_load(driver)

        # Clear existing cookies
        logger.debug("Clearing existing cookies")
        driver.delete_all_cookies()

        success_count = 0
        for cookie in cookies:
            try:
                # Remove any problematic fields
                cookie_dict = {k: v for k, v in cookie.items() if k in
                               ['name', 'value', 'domain', 'path', 'secure', 'httpOnly', 'expiry']}
                
                driver.add_cookie(cookie_dict)
                success_count += 1
                logger.debug(f"Added cookie: {cookie.get('name')}")
            except Exception as e:
                logger.warning(f"Error adding cookie {cookie.get('name')}: {e}")

        logger.info(f"Successfully added {success_count}/{len(cookies)} cookies")
        driver.refresh()
        return success_count > 0

    except Exception as e:
        logger.error(f"Error importing cookies: {e}")
        return False


def verify_login(driver):
    """Verify if the login is successful with better checks"""
    try:
        # First check if we're redirected to login page
        logger.debug("Navigating to verification URL")
        driver.get('https://www.zhipin.com/web/chat/search')
        
        # Add explicit wait for page load
        driver.execute_script("return document.readyState") == "complete"
        wait = WebDriverWait(driver, 10)

        # Check for login indicators with descriptive names
        login_indicators = [
            ("Card List", By.CSS_SELECTOR, ".page-name"),
            ("Logout Button", By.CSS_SELECTOR, ".user-name"),
            ("Profile Card", By.CSS_SELECTOR, "[class*='.geek-info-card']")
        ]

        found_elements = []
        missing_elements = []

        for name, by, selector in login_indicators:
            try:
                element = wait.until(
                    EC.presence_of_element_located((by, selector)))
                if element.is_displayed():
                    found_elements.append(name)
                else:
                    missing_elements.append(f"{name} (hidden)")
            except:
                missing_elements.append(name)

        # Log status report
        if found_elements:
            logger.info("Found login indicator elements:")
            for element in found_elements:
                logger.info(f"  • {element}")

        if missing_elements:
            logger.warning("Missing login indicator elements:")
            for element in missing_elements:
                logger.warning(f"  • {element}")

        # Check if redirected to login page
        if 'login' in driver.current_url.lower():
            logger.warning("Redirected to login page - not logged in")
            return False

        # Consider login successful if at least one indicator is found
        is_logged_in = len(found_elements) > 0
        if is_logged_in:
            logger.info("Login verification successful")
        else:
            logger.warning("Login verification failed - no indicators found")
            
        return is_logged_in

    except Exception as e:
        logger.error(f"Login verification failed: {e}")
        return False