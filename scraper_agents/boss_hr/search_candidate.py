import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.logger import logger


def search_candidate(driver, keyword="前端开发工程师·合肥"):
    try:
        logger.info("Beginning job search process")

        # Step 1: Make sure we're on the right page
        current_url = driver.current_url
        logger.info(f"Current page: {current_url}")

        wait = WebDriverWait(driver, 30)

        # Check for iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            logger.info(
                f"Found {len(iframes)} iframes on page. Trying to switch to them.")
            for i, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    logger.info(f"Switched to iframe {i}")
                    # Try to find the search input in this iframe
                    search_input = locate_search_input(driver, wait)
                    if search_input:
                        enter_search_text(driver, wait, search_input, keyword)
                        return
                    # Switch back to main content to try next iframe
                    driver.switch_to.default_content()
                except Exception as e:
                    logger.warning(f"Error switching to iframe {i}: {e}")
                    driver.switch_to.default_content()

        # If we found the input, enter the text
        enter_search_text(driver, wait, search_input, keyword)

    except Exception as e:
        logger.critical(f"Error in search process: {e}", exc_info=True)
        # Take a screenshot and save the page source for debugging
        try:
            driver.save_screenshot("logs/search_critical_error.png")
            with open("logs/page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info("Saved screenshot and page source for debugging")
        except:
            pass


def locate_search_input(driver, wait):
    """Try various strategies to locate the search input element"""
    logger.info("Attempting to locate search input element")

    # First wait for the page to be fully loaded and stable
    try:
        # Wait for key indicators that the page is fully loaded
        indicators = [
            (By.CSS_SELECTOR, ".loading-container[style*='display: none']"),
            (By.CSS_SELECTOR, ".search-container"),
            (By.CSS_SELECTOR, ".search-wrapper")
        ]

        for selector_type, selector in indicators:
            try:
                wait.until(EC.presence_of_element_located(
                    (selector_type, selector)))
                logger.debug(f"Found page load indicator: {selector}")
            except:
                pass
    except:
        pass

    # Use JavaScript to examine all input elements
    logger.debug("Using JavaScript to analyze all input elements")
    try:
        js_result = driver.execute_script("""
            const inputs = document.querySelectorAll('input');
            const details = [];
            inputs.forEach((input, i) => {
                details.push({
                    index: i,
                    type: input.type,
                    id: input.id,
                    name: input.name,
                    class: input.className,
                    placeholder: input.placeholder,
                    visible: input.offsetParent !== null,
                    value: input.value
                });
            });
            return details;
        """)
        logger.debug(f"Found {len(js_result)} input elements: {js_result}")

        # Try to identify the most likely search input
        search_inputs = []
        for input_detail in js_result:
            score = 0
            if input_detail.get('type') == 'text' or input_detail.get('type') == 'search':
                score += 2
            if 'search' in (input_detail.get('class') or '').lower():
                score += 3
            if 'search' in (input_detail.get('id') or '').lower():
                score += 2
            if '搜索' in (input_detail.get('placeholder') or ''):
                score += 3
            if input_detail.get('visible', False):
                score += 2

            if score > 0:
                search_inputs.append((score, input_detail.get('index')))

        if search_inputs:
            # Sort by score, highest first
            search_inputs.sort(reverse=True)
            best_index = search_inputs[0][1]
            logger.info(
                f"Best search input candidate has index {best_index} with score {search_inputs[0][0]}")

            # Try to get this element
            return driver.execute_script(f"return document.querySelectorAll('input')[{best_index}]")
    except Exception as e:
        logger.warning(f"JavaScript input analysis failed: {e}")

    # Try all the selectors
    selectors = [
        (By.CSS_SELECTOR, "input.search-input"),
        (By.CSS_SELECTOR, ".input-warp input"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.CSS_SELECTOR, "input[placeholder*='搜索']"),
        (By.XPATH, "//input[contains(@class, 'search')]"),
        (By.XPATH, "//input[contains(@placeholder, '搜索')]"),
        (By.XPATH, "//div[contains(@class, 'search')]/input"),
        (By.XPATH, "//div[contains(@class, 'input')]/input"),
        # This one matches exactly what you've shown in the screenshot
        (By.CSS_SELECTOR, "input[data-v-2dcdab82][type='text']")
    ]

    search_input = None
    for selector_type, selector in selectors:
        try:
            logger.debug(
                f"Trying to locate search input with {selector_type}: {selector}")
            search_input = wait.until(
                EC.presence_of_element_located((selector_type, selector)))
            if search_input:
                logger.info(
                    f"Found search input using {selector_type}: {selector}")
                return search_input
        except Exception as e:
            logger.debug(f"Selector {selector} failed: {e}")

    logger.error("Failed to locate search input element with all selectors")
    return None


def enter_search_text(driver, wait, search_input, keyword):
    """Enter text into the search input with multiple fallback strategies"""
    try:
        # Try to scroll the element into view first
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", search_input)
        logger.debug("Scrolled input element into view")

        # Try to clear existing input using multiple methods
        try:
            search_input.clear()
            logger.debug("Cleared input using .clear()")
        except:
            logger.debug("Standard clear failed, trying JavaScript clear")
            driver.execute_script("arguments[0].value = '';", search_input)

        # Focus the element
        driver.execute_script("arguments[0].focus();", search_input)
        logger.debug("Applied focus to input element")

        # Try multiple ways to enter text
        strategies = [
            # Strategy 1: Standard send_keys
            lambda: search_input.send_keys(keyword),

            # Strategy 2: Character-by-character input with delays
            lambda: send_keys_with_delay(search_input, keyword),

            # Strategy 3: JavaScript value assignment
            lambda: driver.execute_script(
                f"arguments[0].value = '{keyword}';", search_input),

            # Strategy 4: JavaScript + dispatchEvent
            lambda: driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, search_input, keyword)
        ]

        success = False
        for i, strategy in enumerate(strategies):
            try:
                logger.debug(f"Trying input strategy {i+1}")
                strategy()

                # Wait briefly to see if text was entered
                WebDriverWait(driver, 3).until(
                    lambda d: search_input.get_attribute('value') == keyword
                )
                logger.info(
                    f"Successfully entered search term using strategy {i+1}: {keyword}")
                success = True
                break
            except Exception as e:
                logger.warning(f"Strategy {i+1} failed: {e}")

        if not success:
            logger.error("All strategies failed to enter text")
            return False

        # Try to click the search button or press Enter key
        try:
            # First try finding search button using the exact data-v identifier from the screenshot
            search_button = None

            # Try with the exact selector from your screenshot
            try:
                search_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "i.icon-search[data-v-2dcdab82]")
                ))
                logger.info("Found search button with exact data-v attribute")
            except Exception:
                logger.debug(
                    "Could not find button with exact data-v attribute")

            # Try to find the button as a sibling of the input element
            if not search_button and search_input:
                try:
                    # Look for the button in the same container as the input
                    parent_div = driver.execute_script(
                        "return arguments[0].closest('.input-warp')", search_input)
                    if parent_div:
                        search_button = parent_div.find_element(
                            By.CSS_SELECTOR, "i.icon-search")
                        logger.info("Found search button as sibling to input")
                except Exception as e:
                    logger.debug(
                        f"Could not find button as input sibling: {e}")

            # Try finding any icon-search regardless of data-v attribute
            if not search_button:
                search_buttons = driver.find_elements(
                    By.CSS_SELECTOR, "i.icon-search")
                if search_buttons:
                    search_button = search_buttons[0]
                    logger.info(
                        "Found search button without specific data-v attribute")

            # Try JavaScript click if we found the button
            if search_button:
                try:
                    # First try a regular click
                    search_button.click()
                    logger.info("Clicked search button successfully")
                except Exception as e:
                    logger.warning(
                        f"Regular click failed: {e}, trying JavaScript click")
                    # If regular click fails, try with JavaScript
                    driver.execute_script(
                        "arguments[0].click();", search_button)
                    logger.info("Clicked search button with JavaScript")
            else:
                # If no button found, try pressing Enter
                logger.info("No search button found, sending Enter key")
                # Try both regular and JavaScript approaches
                try:
                    search_input.send_keys(Keys.ENTER)
                except Exception:
                    driver.execute_script("""
                        var event = new KeyboardEvent('keydown', {
                            'key': 'Enter',
                            'code': 'Enter',
                            'keyCode': 13,
                            'which': 13,
                            'bubbles': true
                        });
                        arguments[0].dispatchEvent(event);
                    """, search_input)

            # Wait for search results or page change
            time.sleep(30)  # Delay to allow search to initiate
            try:
                # Check if URL changed or search results appeared
                WebDriverWait(driver, 5).until(
                    lambda d: "search" in d.current_url.lower() or
                    len(d.find_elements(By.CSS_SELECTOR,
                        ".search-results, .result-list")) > 0
                )
            except:
                logger.warning(
                    "Couldn't confirm search initiated, proceeding anyway")

            logger.info("Search initiated")
            extract_candidate_information(driver)

            return True
        except Exception as e:
            logger.error(f"Error initiating search: {e}")
            return False

    except Exception as e:
        logger.error(f"Error interacting with search input: {e}")
        return False


def send_keys_with_delay(element, text, delay=0.09):
    """Send keys character by character with slight delay"""
    for char in text:
        element.send_keys(char)
        time.sleep(delay)


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

                # Basic candidate info (name)
                try:
                    candidate_name = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[1]/span[1]').text
                    candidate_data["candidate_name"] = candidate_name
                except Exception as e:
                    logger.debug(
                        f"Could not extract basic info for candidate {index+1}: {e}")

                # Education
                try:
                    education = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[2]/span[3]').text
                    candidate_data["education"] = education
                except Exception as e:
                    logger.debug(
                        f"Could not extract education for candidate {index+1}: {e}")

                # Current location
                try:
                    current_location = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[2]/ul[1]/li/span[2]').text
                    candidate_data["current_location"] = current_location
                except Exception as e:
                    logger.debug(
                        f"Could not extract current position for candidate {index+1}: {e}")

                # Age
                try:
                    age = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[2]/span[1]').text
                    candidate_data["age"] = age
                except Exception as e:
                    logger.debug(
                        f"Could not extract age for candidate {index+1}: {e}")

                # Age
                try:
                    degree_duration = candidate.find_element(
                        By.XPATH, './/div[2]/div/div[2]/div/div[1]/div[2]/span[2]').text
                    candidate_data["degree_duration"] = degree_duration
                except Exception as e:
                    logger.debug(
                        f"Could not extract degree_duration for candidate {index+1}: {e}")

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
