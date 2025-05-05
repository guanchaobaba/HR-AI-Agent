import random
import pyperclip  # Add this import at the top
import pyautogui
from pyautogui import easeInOutCubic
import os
from helpers.lookup_caching import get_image_id, load_cache, save_cache
from helpers.mouse_movements import human_click
from helpers.sleeping_time import random_sleep
from utils.logger import logger
# 1) find project root & cache file
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../../"))
cache_path = os.path.join(
    project_root, "cache_database", "liepin_cache_database.json")


def get_single_candidate(sb):
    try:

        # ─── 1) Wait and Grab the contact element ──────────────────────────────────
        contacts = sb.cdp.wait_for_element_visible(
            ".im-ui-contact-info", timeout=20)

        contacts = sb.cdp.find_all(".im-ui-contact-info")

        logger.warning(f"Total contacts expected {len(contacts)}")

        if not len(contacts):
            logger.error("No contacts found!")
            return None, None

        # el = contacts[0]

        for el in contacts:
            # Access direct properties
            logger.info(f"Candidate Element text: {el.text}")

            # ─── 2) Scroll into view ──────────────────────────────────────────────
            sb.sleep(1)

            el.scroll_into_view()
            sb.cdp.maximize()
            sb.sleep(1)
            el.gui_click(timeframe=0.5)
            sb.sleep(1)

    except Exception as e:
        logger.error(f"Error running JS script: {e}")


def get_candidates_conversations(sb):
    try:
        # First try to run the JS script to count candidates
        get_single_candidate(sb)

        # Take screenshot of result
        screenshot_path = os.path.join(
            project_root, "resources", "debug_screenshots", "screenshot.png")
        pyautogui.screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")

    except Exception as e:
        logger.error(f"Something went wrong in front page: {e}")
