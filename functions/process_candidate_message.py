from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.logger import logger


def process_candidate_message(driver, wait_time=30):
    """
    Process candidate messages by selecting and clicking all child elements
    in the candidate message container to open chat windows

    Args:
        driver: Selenium WebDriver instance
        wait_time: Maximum time to wait for elements in seconds

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Starting to process candidate messages")

        # Define parent xpath for the message container
        parent_xpath = '//*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]'

        # Wait for the parent element to be present
        wait = WebDriverWait(driver, wait_time)
        parent_element = wait.until(
            EC.presence_of_element_located((By.XPATH, parent_xpath))
        )

        logger.info("Found parent message container")

        # Find all child elements (typically these would be message items/cards)
        # Using a more general selector to find clickable children
        child_elements = parent_element.find_elements(By.XPATH, './div')

        if not child_elements:
            logger.warning("No message items found in the container")

            # Try alternative selectors if the standard one doesn't work
            alternative_selectors = [
                # Common class pattern for list items
                './div[contains(@class, "item")]',
                './/div[contains(@class, "chat")]',  # Chat items
                './*',  # Any direct children
                './/div[contains(@class, "message")]'  # Message items
            ]

            for selector in alternative_selectors:
                child_elements = parent_element.find_elements(
                    By.XPATH, selector)
                if child_elements:
                    logger.info(
                        f"Found {len(child_elements)} message items using selector: {selector}")
                    break

            # If still no elements found
            if not child_elements:
                # Save page source for debugging
                with open("logs/message_elements_not_found.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                driver.save_screenshot("logs/message_container.png")
                logger.error(
                    "Could not identify any message items. Saved page source for debugging.")
                return False

        total_messages = len(child_elements)
        logger.info(
            f"Found {total_messages} candidate message items to process")

        # Process each message item
        for index, message_item in enumerate(child_elements):
            if index < 1:
                try:
                    logger.info(
                        f"Processing message {index + 1} of {total_messages}")

                    # Scroll the element into view
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", message_item)
                    time.sleep(0.5)  # Small delay after scrolling

                    # Take screenshot before clicking (for debugging)
                    if index == 0:  # Only for first item to avoid too many screenshots
                        driver.save_screenshot(
                            f"logs/before_click_message_{index}.png")

                    # Try clicking the element
                    try:
                        message_item.click()
                        logger.info(f"Clicked message item {index + 1}")
                    except Exception as e:
                        logger.warning(
                            f"Direct click failed on message {index + 1}: {e}")
                        # Try JavaScript click as fallback
                        try:
                            driver.execute_script(
                                "arguments[0].click();", message_item)
                            logger.info(
                                f"Clicked message {index + 1} using JavaScript")
                        except Exception as js_error:
                            logger.error(
                                f"JavaScript click also failed on message {index + 1}: {js_error}")
                            continue

                    # Wait for the chat to load
                    time.sleep(2)  # Give the chat some time to load

                    # Check if chat opened successfully
                    try:
                        # Look for common chat window elements
                        chat_indicators = [
                            "//div[contains(@class, 'chat-window')]",
                            "//div[contains(@class, 'message-container')]",
                            "//textarea[contains(@placeholder, '发送')]",
                            "//div[contains(@class, 'chat-header')]"
                        ]

                        chat_opened = False
                        for indicator in chat_indicators:
                            try:
                                if driver.find_elements(By.XPATH, indicator):
                                    chat_opened = True
                                    break
                            except:
                                pass

                        if chat_opened:
                            logger.info(
                                f"Chat window {index + 1} opened successfully")

                            # Process chat content here if needed
                            # Example: Extract messages, send a response, etc.

                            # Close chat or go back to message list
                            back_buttons = driver.find_elements(
                                By.XPATH, "//i[contains(@class, 'back')] | //button[contains(@class, 'back')]")
                            if back_buttons:
                                back_buttons[0].click()
                                logger.info("Returned to message list")
                                time.sleep(1)  # Wait for transition
                            else:
                                logger.debug(
                                    "No back button found, continuing to next message")
                        else:
                            logger.warning(
                                f"Could not verify if chat {index + 1} opened properly")

                    except Exception as chat_error:
                        logger.error(
                            f"Error processing chat window {index + 1}: {chat_error}")

                except Exception as e:
                    logger.error(
                        f"Error processing message item {index + 1}: {e}")
                    continue
            break

        logger.info(
            f"Completed processing all {total_messages} candidate messages")
        return True

    except Exception as e:
        logger.error(f"Error in process_candidate_message: {e}", exc_info=True)
        # Take a screenshot for debugging
        try:
            driver.save_screenshot("logs/process_messages_error.png")
            logger.info("Saved error screenshot")
        except:
            pass
        return False


def extract_chat_messages(driver):
    """
    Extract message content from an open chat window

    Args:
        driver: Selenium WebDriver instance

    Returns:
        list: List of message dictionaries with sender and content
    """
    try:
        # Wait for messages to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.XPATH,
             "//div[contains(@class, 'message-item')] | //div[contains(@class, 'chat-message')]")
        ))

        # Find all message elements
        message_elements = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'message-item')] | //div[contains(@class, 'chat-message')]"
        )

        messages = []
        for msg in message_elements:
            try:
                # Try to determine if message is from self or other party
                sender_type = "unknown"
                if "self" in msg.get_attribute("class") or "right" in msg.get_attribute("class"):
                    sender_type = "self"
                else:
                    sender_type = "candidate"

                # Extract message content
                content = msg.text.strip()

                if content:
                    messages.append({
                        "sender": sender_type,
                        "content": content,
                        "timestamp": None  # Could extract timestamp if available
                    })

            except Exception as e:
                logger.debug(f"Error extracting a message: {e}")
                continue

        logger.info(f"Extracted {len(messages)} messages from chat")
        return messages

    except Exception as e:
        logger.error(f"Error extracting chat messages: {e}")
        return []
