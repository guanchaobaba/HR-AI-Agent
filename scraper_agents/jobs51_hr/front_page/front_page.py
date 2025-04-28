import pyautogui
import os
import time
import json
import hashlib
import random
from helpers.lookup_caching import get_image_id, load_cache, save_cache
from helpers.mouse_movements import human_click
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
            pos = pyautogui.locateCenterOnScreen(image_path, confidence=0.6)
            if not pos:
                raise RuntimeError(f"Couldn't find {image_path} on screen!")

            x, y = int(pos[0]), int(pos[1])
            cache[img_id] = [x, y]
            cache_updated = True
            logger.info(
                f"Found & cached {os.path.basename(image_path)} at: {x},{y}")

        # Use human-like mouse movement and click
        human_click(x, y)

        # Variable sleep time that can be controlled by parameters
        time.sleep(random.uniform(min_sleep, max_sleep))

        if cache_updated:
            save_cache(cache, cache_path)
            logger.info(f"Cache updated with new coordinates")

        return True

    except Exception as e:
        logger.error(f"Error in find_N_click: {str(e)}")
        return False


def get_front_page():
    try:

        image_path1 = os.path.join(
            project_root, "resources", "coords_images", "1.png")
        image_path2 = os.path.join(
            project_root, "resources", "coords_images", "2.png")

        find_N_click(image_path1, min_sleep=1, max_sleep=2)
        find_N_click(image_path2, 0.5, 1)

        # Take screenshot of result
        screenshot_path = os.path.join(
            project_root, "resources", "screenshot.png")
        pyautogui.screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")

    except Exception as e:
        logger.debug(f"Something went wrong in front page: {e}")
