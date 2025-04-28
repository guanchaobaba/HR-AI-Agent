from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json
import hashlib
import os
from datetime import datetime
from utils.logger import logger
from scraper_agents.boss_hr.random_sleep import random_delay
from scraper_agents.boss_hr.candidate_db import CandidateDatabase
from pathlib import Path
from selenium.webdriver.common.action_chains import ActionChains
import requests


def process_candidate_message(driver, wait_time=30, auto_reply=True, max_candidates=5):
    """
    Process candidate messages by selecting and clicking them to open chat windows
    and optionally send automatic messages requesting resumes

    Args:
        driver: Selenium WebDriver instance
        wait_time: Maximum time to wait for elements in seconds
        auto_reply: Whether to automatically send messages to candidates
        max_candidates: Maximum number of candidates to process in one run

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Starting to process candidate messages")

        # Initialize the database
        db = CandidateDatabase()

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

        # Store results of processing
        processed_results = []

        # Process each message item, limited by max_candidates
        for index, message_item in enumerate(child_elements):
            if index >= max_candidates:
                logger.info(
                    f"Reached maximum candidates to process ({max_candidates})")
                break

            try:
                logger.info(
                    f"Processing message {index + 1} of {total_messages}")

                # Extract candidate info from preview before clicking
                candidate_info = extract_candidate_info_from_preview(
                    message_item)

                # Generate a unique ID for this candidate
                candidate_name = candidate_info.get('name', 'Unknown')
                candidate_id = generate_candidate_id(
                    candidate_name, message_item)

                # Add or update candidate in database
                db.add_or_update_candidate(candidate_id, candidate_name, source="chat",
                                           extra_info={"preview_text": candidate_info.get('preview')})

                # Scroll the element into view
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", message_item)
                random_delay(1, 5)

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
                random_delay(1, 4)

                # Check if chat opened successfully
                chat_opened = is_chat_window_open(driver)

                if chat_opened:
                    logger.info(
                        f"Chat window for {candidate_name} opened successfully")

                    # Extract messages from chat
                    messages = extract_chat_messages(driver)
                    check_if_resume_found = check_and_download_resume(
                        driver, candidate_id)

                    # Record messages in the database
                    if messages:
                        for msg in messages:
                            db.record_message(
                                candidate_id,
                                "inbound" if msg["sender"] == "candidate" else "outbound",
                                msg["content"],
                                has_resume=check_if_resume_found
                            )

                    # Get candidate record to check status
                    candidate = db.get_candidate_by_id(candidate_id)

                    # Check if candidate has sent a resume
                    has_resume = candidate.get("resume_received", False)

                    # Re-check messages for resume if database says no resume
                    if not has_resume:
                        for msg in messages:
                            if msg["sender"] == "candidate" and check_if_resume_found:
                                has_resume = True
                                # Update database
                                db.update_candidate_status(
                                    candidate_id, "resume_received")
                                break

                    # Only send message if:
                    # 1. Candidate is new (no messages sent yet)
                    if not check_if_resume_found:

                        # Send initial resume request
                        logger.debug("Send initial resume request ... ")
                        resume_request_success = send_resume_request(
                            driver, candidate_name)
                        if resume_request_success:
                            db.record_message(
                                candidate_id,
                                "outbound",
                                f"您好{candidate_name}，感谢您的关注。请问您方便发一份最新的简历过来吗？",
                                has_resume=False
                            )

                    # Record results
                    processed_results.append({
                        'candidate_id': candidate_id,
                        'name': candidate_name,
                        'has_resume': has_resume,
                        'message_count': len(messages),
                        'status': candidate.get('status', 'unknown')
                    })

                    # Go back to another candidate chat
                    back_buttons = driver.find_elements(
                        By.XPATH, "//i[contains(@class, 'back')] | //button[contains(@class, 'back')]")
                    if back_buttons:
                        back_buttons[0].click()
                        logger.info("Returned to message list")
                        random_delay(1, 5)
                    else:
                        logger.debug(
                            "No back button found, continuing to next message")
                else:
                    logger.warning(
                        f"Could not verify if chat for {candidate_name} opened properly")

            except Exception as e:
                logger.error(
                    f"Error processing message item {index + 1}: {e}")
                continue

        # Generate report after processing
        report = db.generate_report()
        logger.info(
            f"Generated report with {len(processed_results)} processed candidates")

        return processed_results

    except Exception as e:
        logger.error(f"Error in process_candidate_message: {e}", exc_info=True)
        # Take a screenshot for debugging
        try:
            driver.save_screenshot("logs/process_messages_error.png")
            logger.info("Saved error screenshot")
        except:
            pass
        return False


def extract_candidate_info_from_preview(message_item):
    """
    Extract candidate name and preview text from message list item

    Args:
        message_item: WebElement representing a message in the list

    Returns:
        dict: Dictionary with candidate info
    """
    info = {'name': None, 'preview': None}

    try:
        # Try to find candidate name (usually in a heading or first line)
        name_elements = message_item.find_elements(
            By.XPATH, ".//h4 | .//div[contains(@class, 'name')] | .//span[contains(@class, 'name')]")
        if name_elements:
            info['name'] = name_elements[0].text.strip()

        # Try to find message preview
        preview_elements = message_item.find_elements(
            By.XPATH, ".//p | .//div[contains(@class, 'preview')] | .//span[contains(@class, 'content')]")
        if preview_elements:
            info['preview'] = preview_elements[0].text.strip()

        if info['name']:
            logger.debug(f"Extracted candidate name: {info['name']}")
    except Exception as e:
        logger.debug(f"Error extracting candidate preview info: {e}")

    return info


def is_chat_window_open(driver):
    """Check if a chat window is currently open"""
    chat_indicators = [
        "//div[contains(@class, 'conversation-main')]",
        "//div[contains(@class, 'base-info-content')]",
        "//div[contains(@class, 'chat-message-list is-to-top')]"
    ]

    for indicator in chat_indicators:
        try:
            if driver.find_elements(By.XPATH, indicator):
                return True
        except:
            pass

    return False


def send_resume_request(driver, candidate_name):
    """
    Send a message requesting a resume to the candidate

    Args:
        driver: Selenium WebDriver instance
        candidate_name: Name of the candidate

    Returns:
        bool: True if message sent successfully, False otherwise
    """

    # First try to check if there's a resume attachment button
    try:
        # Look for the resume attachment button with the exact CSS class structure from HTML
        first_btn = driver.find_element(
            By.CSS_SELECTOR, "div.btn.resume-btn-file")

        if first_btn:
            logger.info("Found resume attachment button")

        # Click using ActionChains for more human-like behavior
        actions = ActionChains(driver)
        actions.move_to_element(first_btn)
        actions.pause(0.2)
        actions.click()
        actions.perform()

        logger.debug("Clicked resume attachment button")
        random_delay(0.5, 1.2)

        # Now look for the confirmation button with the exact class
        confirm_btn = driver.find_element(
            By.CSS_SELECTOR, "button.boss-btn-primary")

        if confirm_btn:
            # Use ActionChains again for human-like click
            actions = ActionChains(driver)
            actions.move_to_element(confirm_btn)
            actions.pause(0.1)
            actions.click()
            actions.perform()

            logger.debug("Clicked confirmation button for resume template")
            random_delay(0.7, 1.5)
        else:
            logger.debug("Confirmation button not found or not displayed")
    except Exception as e:
        # If any error occurs, just continue with normal sending
        logger.debug(f"No resume attachment process available: {e}")


def generate_candidate_id(name, element):
    """
    Generate a unique ID for a candidate based on their name and element

    Args:
        name: Candidate name
        element: WebElement representing the candidate's message item

    Returns:
        str: Unique ID
    """
    # Get a unique attribute from the element if possible
    try:
        element_id = element.get_attribute('id') or ''
        element_class = element.get_attribute('class') or ''
        element_text = element.text or ''
    except:
        element_id = ''
        element_class = ''
        element_text = ''

    # Create a unique string and hash it
    unique_str = f"{name}_{element_id}_{element_class}_{element_text}"
    hashed = hashlib.md5(unique_str.encode()).hexdigest()

    return hashed[:16]  # Use first 16 characters of hash


def extract_chat_messages(driver):
    """
    Extract message content from an open chat window using the specific HTML structure

    Args:
        driver: Selenium WebDriver instance

    Returns:
        list: List of message dictionaries with sender and content
    """
    try:
        # Wait for the chat container to load
        wait = WebDriverWait(driver, 10)
        chat_container_xpath = "//*[@id='container']/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]"

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, chat_container_xpath)))
        except Exception as e:
            logger.warning(f"Chat container not found: {e}")
            return []

        messages = []

        # 1. Find candidate messages (item-friend)
        candidate_messages = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'item-friend')]")

        # 2. Find HR messages (item-myself)
        hr_messages = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'item-myself')]")

        # Process candidate messages
        for msg in candidate_messages:
            try:
                # Extract the text from the span element inside the .text div
                text_element = msg.find_element(
                    By.XPATH, ".//div[@class='text']/span | .//div[@class='text']")
                content = text_element.text.strip()

                # Check for attachments
                attachment_elements = msg.find_elements(
                    By.XPATH, ".//h3[contains(@class, 'message-card-top-title')] | .//div[contains(@class, 'message-card-top-content')]")
                if attachment_elements:
                    file_name = attachment_elements[0].text.strip()
                    if file_name:
                        content += f" [附件: {file_name}]"
                    else:
                        content += " [附件]"

                if content:
                    messages.append({
                        "sender": "candidate",
                        "content": content,
                        "timestamp": None  # Could extract timestamp if available
                    })
            except Exception as e:
                logger.debug(f"Error extracting candidate message: {e}")
                continue

        # Process HR messages
        for msg in hr_messages:
            try:
                # Extract the text - note the status element that might be present
                text_container = msg.find_element(
                    By.XPATH, ".//div[contains(@class, 'text')]")

                # Check for delivery status
                status_text = ""
                status_elements = text_container.find_elements(
                    By.XPATH, ".//i[contains(@class, 'status')]")
                if status_elements:
                    status_text = status_elements[0].text.strip()
                    logger.debug(f"Message status: {status_text}")

                # Get the main message text
                span_element = text_container.find_element(By.XPATH, "./span")
                content = span_element.text.strip()

                if content:
                    messages.append({
                        "sender": "self",
                        "content": content,
                        "timestamp": None,
                        "status": status_text  # Add delivery status information
                    })
            except Exception as e:
                logger.debug(f"Error extracting HR message: {e}")
                continue

        # Sort messages to ensure they're in chronological order
        # (We're assuming the DOM structure already presents them in the correct order)

        logger.info(f"Extracted {len(messages)} messages from chat " +
                    f"({len(candidate_messages)} from candidate, {len(hr_messages)} from HR)")

        return messages

    except Exception as e:
        logger.error(f"Error extracting chat messages: {e}")
        # Capture screenshot for debugging
        try:
            screenshot_path = "logs/chat_extraction_error.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"Error screenshot saved to: {screenshot_path}")
        except:
            pass
        return []


def check_and_download_resume(driver, candidate_id):
    """
    Check for resume attachments, click to preview them, and download if available

    Args:
        driver: Selenium WebDriver instance
        candidate_id: Candidate ID to use for filename

    Returns:
        bool: True if resume was found and downloaded, False otherwise
    """
    try:
        logger.info("Checking for resume preview buttons in chat")

        # Look for "点击预览附件简历" (Click to preview attachment resume) buttons
        resume_preview_buttons = driver.find_elements(
            By.XPATH, "//span[contains(@class, 'card-btn') and contains(text(), '点击预览')]")

        if not resume_preview_buttons:
            logger.debug("No resume attachment buttons found in chat")
            return False

        logger.info(
            f"Found {len(resume_preview_buttons)} resume attachment buttons")

        # Try to click each resume preview button
        for i, preview_button in enumerate(resume_preview_buttons):
            try:
                # Scroll to the button to make it visible
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", preview_button)

                # Add a small delay to mimic human behavior
                random_delay(0.5, 1.5)

                # Click the preview button
                logger.info(f"Clicking resume preview button {i+1}")
                preview_button.click()

                # Wait for preview dialog to appear
                wait = WebDriverWait(driver, 10)

                # Dialog selector
                dialog_xpath = "//div[contains(@id, 'boss-dynamic-dialog')]"

                try:
                    # First wait for the dialog to appear
                    dialog = wait.until(
                        EC.presence_of_element_located((By.XPATH, dialog_xpath)))

                    # Take a screenshot of the preview dialog for debugging
                    screenshot_path = f"logs/resume_preview_{candidate_id}.png"
                    driver.save_screenshot(screenshot_path)

                    # --- APPROACH 1: Try finding by SVG parent element ---
                    download_button = None
                    try:
                        # Look for spans containing SVG elements
                        svg_spans = driver.find_elements(
                            By.CSS_SELECTOR, f"{dialog_xpath.replace('//div', 'div')} span svg")

                        for span in svg_spans:
                            # Check parent span element
                            parent = span.find_element(By.XPATH, "./..")
                            # If it looks like a download button or we can't tell for sure
                            download_button = parent
                            logger.info(
                                "Found download button via SVG approach")
                            break
                    except Exception as svg_err:
                        logger.debug(f"SVG approach failed: {svg_err}")

                    # --- APPROACH 2: Try using JavaScript to find by attribute ---
                    if not download_button:
                        try:
                            # Use JavaScript to find elements with download icon
                            js_script = """
                                var dialog = document.querySelector('div[id*="boss-dynamic-dialog"]');
                                if (!dialog) return null;
                                
                                // Look for download icon by various means
                                var downloadBtn = dialog.querySelector('[class*="download"]') || 
                                                dialog.querySelector('span svg') ||
                                                dialog.querySelector('span [xlink\\:href*="download"]');
                                                
                                return downloadBtn ? downloadBtn.closest('span') || downloadBtn : null;
                            """
                            download_element = driver.execute_script(js_script)
                            if download_element:
                                download_button = download_element
                                logger.info(
                                    "Found download button via JavaScript")
                        except Exception as js_err:
                            logger.debug(
                                f"JavaScript approach failed: {js_err}")

                    # --- APPROACH 3: Try any clickable element in dialog ---
                    if not download_button:
                        try:
                            # Look for any button or clickable span in dialog
                            buttons = driver.find_elements(
                                By.XPATH, f"{dialog_xpath}//button | {dialog_xpath}//span[contains(@class, 'btn')]")

                            # Choose right-most button (often download)
                            if buttons:
                                for btn in buttons:
                                    if btn.is_displayed() and "close" not in btn.get_attribute("class").lower():
                                        download_button = btn
                                        logger.info(
                                            "Found potential download button via buttons search")
                                        break
                        except Exception as btn_err:
                            logger.debug(
                                f"Button search approach failed: {btn_err}")

                    # If we found a download button, click it
                    if download_button:
                        # Scroll to and click the download button
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", download_button)
                        random_delay(0.5, 1)

                        # Click the download button
                        logger.info("Clicking download button for resume")
                        download_button.click()

                        # Wait for download to start
                        random_delay(1, 3)

                        # Find close button for the preview dialog and close it
                        close_buttons = driver.find_elements(
                            By.XPATH, f"{dialog_xpath}//i[contains(@class, 'close')]")
                        if close_buttons:
                            close_buttons[0].click()
                            logger.info("Closed resume preview dialog")
                            random_delay(0.5, 1)

                        logger.info(
                            f"Successfully downloaded resume for candidate {candidate_id}")
                        return True
                    else:
                        logger.warning(
                            "Could not find download button in dialog")

                except Exception as e:
                    logger.warning(f"Error handling download button: {e}")

                # Try to close the dialog if it's still open
                try:
                    close_buttons = driver.find_elements(
                        By.XPATH, "//div[contains(@class, 'boss-popup__close')] | //i[contains(@class, 'icon-close')]")
                    if close_buttons:
                        close_buttons[0].click()
                        logger.info("Closed resume preview dialog")
                except Exception as close_err:
                    logger.debug(f"Error closing dialog: {close_err}")

            except Exception as e:
                logger.warning(f"Failed to preview resume {i+1}: {e}")

        return False

    except Exception as e:
        logger.error(f"Error checking for resume attachments: {e}")
        return False
