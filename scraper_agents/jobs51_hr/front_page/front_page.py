import random
import pyperclip  # Add this import at the top
import pyautogui
import os
from helpers.lookup_caching import get_image_id, load_cache, save_cache
from helpers.mouse_movements import human_click
from helpers.sleeping_time import random_sleep
from utils.logger import logger
# 1) find project root & cache file
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../../"))
cache_path = os.path.join(
    project_root, "cache_database", "jobs51_cache_database.json")


def find_N_click(image_path, min_sleep=0.5, max_sleep=3.0):
    """Find image on screen, click it with human-like movement, and cache the coordinates."""
    try:
        cache = load_cache(cache_path)
        cache_updated = False
        img_id = get_image_id(image_path)

        if img_id in cache:
            x, y = cache[img_id]
            logger.info(
                f"Using cached coords for {os.path.basename(image_path)}: {x},{y}")
        else:
            print("New image coords", image_path)
            pos = pyautogui.locateCenterOnScreen(image_path, confidence=0.6)
            print("New image coords", pos)
            if not pos:
                raise RuntimeError(f"Couldn't find {image_path} on screen!")

            x, y = pos
            cache[img_id] = [x, y]
            cache_updated = True
            logger.info(
                f"Found & cached {os.path.basename(image_path)} at: {x},{y}")

        # Use human-like mouse movement and click
        # normal speed of mouse 1, faster move 3, slow move 0.5
        human_click(x, y, speed_factor=2)

        # Variable sleep time that can be controlled by parameters
        random_sleep(min_sleep, max_sleep)

        if cache_updated:
            save_cache(cache, cache_path)
            logger.info(f"Cache updated with new coordinates")

        return True

    except Exception as e:
        logger.error(f"Error in find_N_click: {e}")
        return False


def human_typewrite(text, min_interval=0.05, max_interval=0.2):
    """
    Type text with human-like randomized timing between keystrokes.
    Handles non-ASCII characters like Chinese through clipboard.

    Args:
        text: The text to type
        min_interval: Minimum delay between keystrokes
        max_interval: Maximum delay between keystrokes
    """
    # For pure ASCII strings, use character-by-character typing
    if all(ord(c) < 128 for c in text):
        for char in text:
            pyautogui.typewrite(char)
            random_sleep(min_interval, max_interval)
    else:
        # For non-ASCII (like Chinese), use clipboard
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        random_sleep(min_interval, max_interval)


def scroll_down_gradually(num_scrolls=5, scroll_amount=-100, delay_between=0.5, variation=0.2):
    """
    Scroll down gradually with human-like behavior.

    Args:
        num_scrolls: Number of scroll actions to perform
        scroll_amount: Amount to scroll each time (negative is down)
        delay_between: Base delay between scrolls in seconds
        variation: Random variation to add to delay (fraction of delay_between)
    """
    try:
        logger.info(f"Starting to scroll down ({num_scrolls} scrolls)")

        for i in range(num_scrolls):
            # Add some randomness to the scroll amount to seem more human-like
            actual_amount = scroll_amount + \
                int(scroll_amount * random.uniform(-0.2, 0.2))
            pyautogui.scroll(actual_amount)

            # Log the scroll action
            logger.info(
                f"Scrolled down {actual_amount} (scroll {i+1}/{num_scrolls})")

            # Don't wait after the last scroll
            if i < num_scrolls - 1:
                # Add some randomness to the wait time
                actual_delay = delay_between + \
                    random.uniform(-delay_between*variation,
                                   delay_between*variation)
                random_sleep(actual_delay, actual_delay + 0.1)

        return True
    except Exception as e:
        logger.error(f"Error while scrolling: {e}")
        return False


def get_front_page(driver):
    try:

        talent_menu = os.path.join(
            project_root, "resources", "coords_images", "jobs51_coords_images", "talent_search_menu.png")
        search_field_image = os.path.join(
            project_root, "resources", "coords_images", "jobs51_coords_images", "talent_search_field.png")
        talent_search_btn = os.path.join(
            project_root, "resources", "coords_images", "jobs51_coords_images", "talent_search_btn.png")

        find_N_click(talent_menu, min_sleep=0.2, max_sleep=0.6)
        if find_N_click(search_field_image, min_sleep=0.6, max_sleep=1):
            human_typewrite("java开发人员", 0.01, 0.2)
            find_N_click(talent_search_btn, min_sleep=0.1, max_sleep=0.5)

        random_sleep(2.0, 3.0)
        # Start scrolling down gradually with human-like behavior
        scroll_down_gradually(num_scrolls=5, delay_between=0.5)

        # Take screenshot of result
        screenshot_path = os.path.join(
            project_root, "resources", "debug_screenshots", "screenshot.png")
        pyautogui.screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")

    except Exception as e:
        logger.error(f"Something went wrong in front page: {e}")
