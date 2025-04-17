# Entry point to run the spider
from utils.browser import create_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.hr_login_state import import_browser_cookies, verify_login
from utils.logger import logger


def search_jobs(driver, keyword="前端开发工程师·合肥"):
    try:
        logger.info("Beginning job search process")

        # Step 1: Wait for any loading toast to disappear
        wait = WebDriverWait(driver, 15)

        try:
            wait.until(EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".toast[style*='display: none']"))
            )
            logger.info("Toast loading indicator has disappeared")
        except Exception as e:
            logger.warning(f"Timeout or error waiting for toast to disappear: {e}")

        # Step 2: Ensure the page has fully rendered (dynamic content)
        try:
            logger.debug("Waiting for dynamic content to render...")
            search_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[contains(@class, 'search-input')]")))
            logger.info("Dynamic content is fully loaded")
        except Exception as e:
            logger.error(f"Error waiting for dynamic content to render: {e}")
            return

        # Step 3: Clear the search input and enter the keyword
        try:
            search_input.clear()
            search_input.send_keys(keyword)
            logger.info(f"Entered search term: {keyword}")
        except Exception as e:
            logger.error(f"Error interacting with search input: {e}")
            return

        # Step 4: Wait briefly for autocomplete suggestions to appear
        driver.implicitly_wait(2)

        # Step 5: Click the search button
        try:
            search_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//i[@class='icon-search']")))
            search_button.click()
            logger.info("Search button clicked")
        except Exception as e:
            logger.error(f"Error interacting with search button: {e}")
            return

        # Step 6: Wait for the results to be loaded
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'job-list-box')]")))
            logger.info("Search results loaded")
        except Exception as e:
            logger.error(f"Error waiting for search results to load: {e}")
            return

        # Step 7: Verify each <li> element text is loaded
        try:
            logger.debug("Verifying job list items...")
            job_list_items = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".card-list .geek-info-card")))
            
            logger.info(f"Found {len(job_list_items)} job listings")
            
            for index, item in enumerate(job_list_items):
                try:
                    text_content = item.text.strip()
                    if text_content:
                        logger.debug(f"Job item {index + 1} loaded: {text_content[:50]}...")
                    else:
                        logger.warning(f"Job item {index + 1} has no text content")
                except Exception as e:
                    logger.error(f"Error processing job item {index + 1}: {e}")
        except Exception as e:
            logger.error(f"Error verifying job list items: {e}")

    except Exception as e:
        logger.critical(f"Error in search page: {e}")
        logger.debug("Page source: " + driver.page_source[:1000] + "...")  # Log only first part for debugging


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
                # Continue with your search functionality
                try:
                    search_jobs(driver)
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
        logger.critical(f"Critical error: {e}", exc_info=True)  # Include full traceback
        return False
    finally:
        if driver:
            logger.info("Closing browser")
            driver.quit()


if __name__ == "__main__":
    main()