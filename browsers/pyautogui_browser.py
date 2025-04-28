
import subprocess
import ctypes
import pyautogui
import time

from utils.logger import logger


def py_auto_gui_browser(get_URL='https://www.51job.com/'):
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        # 2) Chrome executable for Linux Server
        # chrome_path = r"/usr/bin/google-chrome"
        # 2) Chrome executable path for Windows
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        # change the URL when working on different website
        # 3) Launch Chrome at 1920×1080, 100% scale, at your URL
        subprocess.Popen([
            chrome_path,
            '--window-size=1920,1080',
            '--window-position=0,0',
            '--force-device-scale-factor=1',
            get_URL
        ])
        logger.info(
            f"⏳ Launched Chrome Display Screen size (should be 1920x1080): {pyautogui.size()}")
        time.sleep(1)

    except Exception as e:
        logger.debug("Browser opening error", e)
