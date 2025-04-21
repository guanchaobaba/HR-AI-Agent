# Entry point to run the spider

from functions.process_candidate_message import process_candidate_message
from utils.browser import create_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.logger import logger
from utils.hr_login_state import import_browser_cookies, verify_login


def main():
    driver = None
    try:
        logger.info("Starting AI resume scoring application")
        driver = create_driver(is_headless=False)
        driver.maximize_window()

        logger.info("Importing cookies...")
        if import_browser_cookies(driver):
            logger.info("Cookies imported, verifying login...")

            if verify_login(driver):
                logger.info("Successfully logged in")
                try:
                    # Continue with your search functionality
                    # search_candidate(driver)
                    process_candidate_message(driver, max_candidates=1)
                except Exception as e:
                    logger.error(f"Error in search page: {e}")

                return True
            else:
                logger.warning("Login failed - checking cookies")
                logger.info("Redirecting to manual login page...")
                driver.get(
                    'https://www.zhipin.com/web/user/?intent=1&ka=header-boss')
                return False
        else:
            logger.error("Cookie import failed")
            return False

    except Exception as e:
        # Include full traceback
        logger.critical(f"Critical error: {e}", exc_info=True)
        return False
    finally:
        if driver:
            logger.info("Closing browser")
            driver.quit()


if __name__ == "__main__":
    main()
