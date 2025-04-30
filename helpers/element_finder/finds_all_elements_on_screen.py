import cv2
import numpy as np
import pyautogui
import os
from PIL import ImageGrab
from utils.logger import logger


def find_element_on_screen(template_path, region=None, threshold=0.7):
    """
    Find element on screen using template matching with OpenCV.

    Args:
        template_path: Path to the template image
        region: (x, y, width, height) region to search in, or None for entire screen
        threshold: Matching threshold (0-1), higher is more strict

    Returns:
        (x, y, w, h) of the match, or None if not found
    """
    try:
        # Take screenshot
        if region:
            screenshot = np.array(ImageGrab.grab(bbox=region))
        else:
            screenshot = np.array(ImageGrab.grab())

        # Convert to grayscale
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Load template and convert to grayscale
        template = cv2.imread(template_path, 0)
        if template is None:
            raise FileNotFoundError(
                f"Template image not found: {template_path}")

        # Template dimensions
        w, h = template.shape[::-1]

        # Perform template matching
        result = cv2.matchTemplate(
            screenshot_gray, template, cv2.TM_CCOEFF_NORMED)

        # Find positions where match exceeds threshold
        locations = np.where(result >= threshold)

        # If no matches found
        if len(locations[0]) == 0:
            logger.info(
                f"No matches found for template: {os.path.basename(template_path)}")
            return None

        # Get the best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        x, y = max_loc

        if region:
            # Adjust coordinates to account for region offset
            x += region[0]
            y += region[1]

        logger.info(
            f"Found element {os.path.basename(template_path)} at ({x}, {y}) with confidence {max_val:.2f}")
        return (x, y, w, h)

    except Exception as e:
        logger.error(f"Error finding element on screen: {e}")
        return None


def find_all_elements_on_screen(template_path, region=None, threshold=0.7):
    """
    Find all matching elements on screen using template matching with OpenCV.

    Args:
        template_path: Path to the template image
        region: (x, y, width, height) region to search in, or None for entire screen
        threshold: Matching threshold (0-1), higher is more strict

    Returns:
        List of (x, y, w, h) tuples for each match, or empty list if none found
    """
    try:
        # Take screenshot
        if region:
            screenshot = np.array(ImageGrab.grab(bbox=region))
        else:
            screenshot = np.array(ImageGrab.grab())

        # Convert to grayscale
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Load template and convert to grayscale
        template = cv2.imread(template_path, 0)
        if template is None:
            raise FileNotFoundError(
                f"Template image not found: {template_path}")

        # Template dimensions
        w, h = template.shape[::-1]

        # Perform template matching
        result = cv2.matchTemplate(
            screenshot_gray, template, cv2.TM_CCOEFF_NORMED)

        # Find positions where match exceeds threshold
        locations = np.where(result >= threshold)
        matches = []

        for pt in zip(*locations[::-1]):  # Reverse for (x, y)
            x, y = pt

            # Check if this match overlaps with existing ones
            is_duplicate = False
            for mx, my, _, _ in matches:
                if abs(mx - x) < w//2 and abs(my - y) < h//2:
                    is_duplicate = True
                    break

            if not is_duplicate:
                if region:
                    # Adjust coordinates to account for region offset
                    matches.append((x + region[0], y + region[1], w, h))
                else:
                    matches.append((x, y, w, h))

        logger.info(
            f"Found {len(matches)} elements matching {os.path.basename(template_path)}")
        return matches

    except Exception as e:
        logger.error(f"Error finding elements on screen: {e}")
        return []
