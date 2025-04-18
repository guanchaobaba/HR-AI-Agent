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
        # First check if we're redirected to login page
        logger.debug("Navigating to verification URL")
        driver.get('https://www.zhipin.com/web/chat/index')

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


def extract_candidate_information(driver):
    """
    Extract and log candidate information from search results

    This function extracts key details about candidates from the search results
    using specific XPath selectors, and logs the information.
    """
    logger.info("Extracting candidate information from search results")

    try:
        # Wait for candidate list to be present
        wait = WebDriverWait(driver, 30)
        candidate_container = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="is-gray-batch-chat"]/div[1]')
        ))

        # Find all candidate items (list items)
        candidate_items = candidate_container.find_elements(By.XPATH, './li')

        if not candidate_items:
            logger.warning("No candidate items found in the search results")
            return

        logger.info(
            f"Found {len(candidate_items)} candidates in search results")

        # Extract information for each candidate
        for index, candidate in enumerate(candidate_items):
            try:
                # Extract name, job title, experience, etc.
                candidate_data = {}

                # Basic candidate info (name, position)
                try:
                    basic_info = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[1]/span[1]').text
                    candidate_data["basic_info"] = basic_info
                except Exception as e:
                    logger.debug(
                        f"Could not extract basic info for candidate {index+1}: {e}")

                # Experience
                try:
                    experience = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[2]/span[3]').text
                    candidate_data["experience"] = experience
                except Exception as e:
                    logger.debug(
                        f"Could not extract experience for candidate {index+1}: {e}")

                # Current position
                try:
                    current_position = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[2]/ul[1]/li/span[2]').text
                    candidate_data["current_position"] = current_position
                except Exception as e:
                    logger.debug(
                        f"Could not extract current position for candidate {index+1}: {e}")

                # Education
                try:
                    education = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[2]/span[1]').text
                    candidate_data["education"] = education
                except Exception as e:
                    logger.debug(
                        f"Could not extract education for candidate {index+1}: {e}")

                # Age
                try:
                    age = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[2]/span[2]').text
                    candidate_data["age"] = age
                except Exception as e:
                    logger.debug(
                        f"Could not extract age for candidate {index+1}: {e}")

                # Log the complete candidate information
                logger.info(f"Candidate {index+1} Information:")
                for key, value in candidate_data.items():
                    logger.info(
                        f"  • {key.replace('_', ' ').title()}: {value}")
                logger.info("---")

            except Exception as e:
                logger.error(
                    f"Error extracting information for candidate {index+1}: {e}")

        return True

    except Exception as e:
        logger.error(f"Error extracting candidate information: {e}")
        # Take a screenshot for debugging
        try:
            screenshot_path = "logs/candidate_extraction_error.png"
            driver.save_screenshot(screenshot_path)
            logger.error(f"Screenshot saved to {screenshot_path}")
        except:
            pass
        return False
