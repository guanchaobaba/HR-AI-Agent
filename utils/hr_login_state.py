import os
import json
from selenium.webdriver.support.ui import WebDriverWait
from utils import wait_for_page_load
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .logger import logger
import time
from selenium.webdriver.common.action_chains import ActionChains

BASE_DIR = os.getcwd()


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
                logger.warning(
                    f"Error adding cookie {cookie.get('name')}: {e}")

        logger.info(
            f"Successfully added {success_count}/{len(cookies)} cookies")
        driver.refresh()
        return success_count > 0

    except Exception as e:
        logger.error(f"Error importing cookies: {e}")
        return False


def verify_login(driver):
    """Verify if the login is successful with better checks"""
    try:
        logger.debug("Starting login verification process")

        # Wait for page to be fully loaded first
        wait = WebDriverWait(driver, 10)

        # Look for the "我要招聘" (I want to recruit) link and click it like a human
        recruit_link_xpaths = [
            "//*[@id='header']/div[1]/div[4]/div/span/a[1]",  # Provided xpath
            # Using the ka attribute
            "//a[@ka='header-boss']",
            # Using the title attribute
            "//a[contains(@title, '我要招聘')]",
            # Using the link text
            "//a[contains(text(), '我要招聘')]"
        ]

        # Try each xpath until we find the element
        clicked = False
        for xpath in recruit_link_xpaths:
            try:
                logger.debug(f"Looking for recruit link with xpath: {xpath}")
                recruit_link = wait.until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )

                # Scroll to the element to ensure it's visible
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", recruit_link)

                # Add a small delay to mimic human behavior

                time.sleep(0.5)

                # Use ActionChains for more human-like click behavior
                actions = ActionChains(driver)
                # Move to the element and pause briefly before clicking
                actions.move_to_element(recruit_link)
                actions.pause(0.2)  # Brief pause when hovering
                actions.click()
                actions.perform()
                logger.info("Successfully clicked on '我要招聘' link")
                clicked = True
                break
            except Exception as e:
                logger.debug(f"Could not click using xpath {xpath}: {e}")

        if not clicked:
            logger.warning(
                "Could not find or click the recruitment link, falling back to direct URL")

        # Check for and close any popups that might appear
        handle_popups(driver)

        # Check for login indicators with descriptive names
        login_indicators = [
            ("Card List", By.CSS_SELECTOR, ".page-name"),
            ("Logout Button", By.CSS_SELECTOR, ".user-name"),
            ("Profile Card", By.CSS_SELECTOR, "[class*='.geek-info-card']"),
            # Additional indicators that might be present in the recruitment page
            ("Chat Section", By.CSS_SELECTOR, ".chat-container"),
            ("Recruitment Dashboard", By.CSS_SELECTOR, ".boss-dashboard")
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

        # Rest of your function remains the same...
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


def handle_popups(driver):
    """Handle any popups that appear after login in a human-like manner"""
    try:
        # Set a short wait time for popups
        popup_wait = WebDriverWait(driver, 2)

        # Common close button patterns
        close_button_selectors = [
            (By.CSS_SELECTOR, ".icon-close"),
            # X icons
            (By.XPATH, "//i[contains(@class, 'close')]")
        ]

        # Look for popup elements
        popup_found = False
        logger.debug("Checking for popups after login")

        # First check if any popup/modal/dialog exists
        popup_containers = [
            (By.CSS_SELECTOR, ".dialog-container"),
            (By.CSS_SELECTOR, ".popup-container"),
            (By.CSS_SELECTOR, ".modal-container"),
            (By.CSS_SELECTOR, ".overlay"),
            (By.XPATH,
             "//div[contains(@class, 'dialog') or contains(@class, 'popup') or contains(@class, 'modal')]")
        ]

        for by, selector in popup_containers:
            try:
                popup = popup_wait.until(
                    EC.presence_of_element_located((by, selector)))
                if popup.is_displayed():
                    popup_found = True
                    logger.info("Popup detected after login")
                    break
            except:
                continue

        # If no popup found, return
        if not popup_found:
            logger.debug("No popups detected after login")
            return

        # Try to close the popup
        for by, selector in close_button_selectors:
            try:
                close_button = popup_wait.until(
                    EC.element_to_be_clickable((by, selector)))

                # Scroll to button if needed
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", close_button)

                time.sleep(0.3)

                # Use ActionChains for more human-like interaction
                actions = ActionChains(driver)
                # Move to the button with slight randomness to mimic human movement
                actions.move_to_element_with_offset(
                    close_button, 2, 1)  # Slight offset
                actions.pause(0.3)  # Brief pause before clicking
                actions.click()
                actions.perform()
                logger.info(
                    f"Successfully closed popup using selector: {selector}")

                # Add a small delay to let the popup close animation finish
                time.sleep(0.5)
                return
            except Exception as e:
                logger.debug(
                    f"Could not close popup with selector {selector}: {e}")

        # If we get here, we found a popup but couldn't close it
        logger.warning("Found popup but couldn't find a close button")

        # Try to click outside the popup as a last resort
        try:
            # Using ActionChains to click in the top-left corner of the page
            actions = ActionChains(driver)
            # Move to a position likely outside the popup (top-left)
            actions.move_by_offset(10, 10)
            actions.pause(0.2)  # Slight pause
            actions.click()
            actions.perform()
            logger.info("Attempted to close popup by clicking outside")
        except:
            logger.warning("Could not close popup by clicking outside")

    except Exception as e:
        logger.error(f"Error handling popups: {e}")


def validate_cookie_format(cookie):
    """Validate individual cookie format"""
    required_fields = ['name', 'value']
    for field in required_fields:
        if field not in cookie:
            logger.warning(
                f"Cookie validation failed: missing required field '{field}'")
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
