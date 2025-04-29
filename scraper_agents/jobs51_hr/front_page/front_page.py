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


def get_front_page():
    try:

        image_path1 = os.path.join(
            project_root, "resources", "coords_images", "jobs51_coords_images", "1.png")
        image_path2 = os.path.join(
            project_root, "resources", "coords_images", "jobs51_coords_images", "search_job.png")
        image_path3 = os.path.join(
            project_root, "resources", "coords_images", "jobs51_coords_images", "search_btn.png")

        find_N_click(image_path1, min_sleep=0.6, max_sleep=1)
        find_N_click(image_path2, min_sleep=0.6, max_sleep=1)

        # Take screenshot of result
        screenshot_path = os.path.join(
            project_root, "resources", "debug_screenshots", "screenshot.png")
        pyautogui.screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")

    except Exception as e:
        logger.debug(f"Something went wrong in front page: {e}")
