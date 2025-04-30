import time
import pyperclip  # Add this import at the top
import pyautogui
import os
from helpers.element_finder.finds_all_elements_on_screen import find_all_elements_on_screen
from helpers.lookup_caching import get_image_id, load_cache, save_cache
from helpers.mouse_movements import human_click
from helpers.sleeping_time import random_sleep
from utils.logger import logger
# 1) find project root & cache file
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../../"))
cache_path = os.path.join(
    project_root, "cache_database", "leipin_cache_database.json")


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


def process_conversations():
    """Process each conversation in the list by finding all matching conversation items."""
    try:
        # Define the conversation list region (adjust these values)
        # Format is (left, top, right, bottom)
        conversation_list_region = (10, 150, 350, 650)

        # Template for conversation items (create a small template of the common part)
        conversation_item_template = os.path.join(
            project_root, "resources", "coords_images", "leipin_coords_images", "conversation_item_template.png")

        # Find all conversation items in the region
        conversation_items = find_all_elements_on_screen(
            conversation_item_template,
            region=conversation_list_region,
            threshold=0.7
        )

        logger.info(f"Found {len(conversation_items)} conversation items")

        # Sort conversation items from top to bottom
        # Sort by y-coordinate
        conversation_items.sort(key=lambda item: item[1])

        # Process each conversation
        # Limit to first 5
        for i, (x, y, w, h) in enumerate(conversation_items[:5]):
            # Click on the conversation (use center of the item)
            center_x = x + w//2
            center_y = y + h//2
            human_click(center_x, center_y, speed_factor=1.5)

            logger.info(
                f"Clicked conversation {i+1} at ({center_x}, {center_y})")

            # Wait for conversation to load
            random_sleep(1.0, 2.0)

            # Process this conversation (read messages, etc.)
            process_single_conversation()

            # Find and click back button to return to conversation list
            back_button = os.path.join(
                project_root, "resources", "coords_images", "leipin_coords_images", "back_button.png")
            find_N_click(back_button, min_sleep=0.5, max_sleep=1.0)

            # Wait for conversation list to reload
            random_sleep(1.0, 1.5)

        return True

    except Exception as e:
        logger.error(f"Error processing conversations: {e}")
        return False


def process_single_conversation():
    """Process a single open conversation."""
    try:
        # Take screenshot of the conversation
        screenshot_path = os.path.join(
            project_root, "resources", "debug_screenshots",
            f"conversation_{int(time.time())}.png")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        pyautogui.screenshot(screenshot_path)

        # Read message content
        # (You can implement OCR here if needed)

        # Scroll through conversation history
        # scroll_down_gradually(
        #     num_scrolls=3, scroll_amount=-100, delay_between=0.3)

        # Additional processing as needed

        return True
    except Exception as e:
        logger.error(f"Error processing conversation: {e}")
        return False


def get_candidates_conversations():
    try:
        # Navigate to messages section
        messages_tab = os.path.join(
            project_root, "resources", "coords_images", "leipin_coords_images", "messages_tab.png")
        find_N_click(messages_tab, min_sleep=0.5, max_sleep=1.0)

        # Wait for messages to load
        random_sleep(1.5, 2.5)

        # Process the conversation list
        process_conversations()

        # Take a final screenshot
        screenshot_path = os.path.join(
            project_root, "resources", "debug_screenshots", "conversations_processed.png")
        pyautogui.screenshot(screenshot_path)
        logger.info(
            f"Conversations processing complete. Screenshot saved to {screenshot_path}")

    except Exception as e:
        logger.error(
            f"Something went wrong in get_candidates_conversations: {e}")
