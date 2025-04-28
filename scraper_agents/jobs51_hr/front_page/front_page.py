import pyautogui
import os
import time
from utils.logger import logger

def get_front_page():
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        
        image_paths = [
            os.path.join(project_root, "resources", "coords_images", "1.png"),
            os.path.join(project_root, "resources", "coords_images", "2.png")
        ]
        for img in image_paths:
            print(f"Searching for {img}…")
            pos = pyautogui.locateCenterOnScreen(img, confidence=0.8)
            if not pos:
                raise RuntimeError(f"Couldn't find {img} on screen!")
            x, y = pos
            print(f"For this img: {img} Found at coord: {x},{y}")
            pyautogui.moveTo(x, y, duration=0.6)
            pyautogui.click()
            time.sleep(5)

        # 6) Final screenshot
        out_path = os.path.join(os.path.dirname(__file__), "screenshot.png")
        pyautogui.screenshot(out_path)
        print(f"✅ Done - screenshot saved to {out_path}")
        return True

    except Exception as e:
        logger.debug("Something went wrong in front page", e)
        return False