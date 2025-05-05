from seleniumbase import SB
from time import sleep
import atexit
from utils.logger import logger


class SBDriverManager:
    """
    A robust manager class for SeleniumBase CDP driver that handles initialization,
    cleanup, and provides methods for interacting with the browser.
    """

    def __init__(self):
        self.driver = None
        self.sb_generator = None
        self._register_cleanup()

    def _register_cleanup(self):
        """Register cleanup method with atexit to ensure browser is closed properly"""
        atexit.register(self.cleanup)

    def create_driver(self, url=None, detach=False):
        """
        Creates a SeleniumBase driver with CDP mode activated using the context manager pattern
        that works in your test.py file.

        Args:
            url: The URL to navigate to
            detach: Whether to detach the browser from the driver process
                    (if True, browser will stay open when the script ends)

        Returns:
            The SeleniumBase driver with CDP mode activated
        """
        try:
            # Create SB with the same parameters that work in test.py
            self.sb_generator = SB(
                browser="chrome",
                uc=True,
                uc_cdp_events=True,
                uc_subprocess=True,
                # It take by default existing profile which create by UC Mode
                user_data_dir=r"C:\Users\rasel\AppData\Local\Google\Chrome\User Data",
                binary_location=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                xvfb=False,
                maximize=True,
                uc_cdp=True,
                headless=False,
                test=True,
                ad_block=False,
                chromium_arg="--timezone=Asia/Shanghai",
                locale_code="cn"
            )

            # Get the actual driver from the context manager
            self.driver = self.sb_generator.__enter__()

            # Store the detach preference for use in cleanup
            self.driver._custom_detach = detach

            # Activate CDP mode with the URL if provided
            if url:
                self.driver.activate_cdp_mode(
                    url, tzone="Asia/Shanghai", geoloc=(31.2304, 121.4737))
                sleep(1)

            logger.info(f"Browser successfully initialized with CDP mode")
            logger.info(f"Page title: {self.driver.get_title()}")

            return self.driver

        except Exception as e:
            logger.error(f"Failed to create SeleniumBase CDP driver: {e}")
            self.cleanup()
            raise

    def cleanup(self):
        """Clean up resources when done"""
        if self.driver:
            try:
                # Check our custom detach attribute
                if not getattr(self.driver, "_custom_detach", False):
                    logger.info("Closing browser...")
                    # Use the context manager's exit method for proper cleanup
                    if self.sb_generator:
                        self.sb_generator.__exit__(None, None, None)
                else:
                    logger.info("Browser detached - will stay open")
            except Exception as e:
                logger.warning(f"Error during driver cleanup: {e}")
            finally:
                self.driver = None
                self.sb_generator = None


# Global instance for easy import
sb_manager = SBDriverManager()


def create_sbase_driver(url=None, detach=False):
    """
    Creates a SeleniumBase driver with CDP mode activated.

    Args:
        url: The URL to navigate to
        detach: Whether to detach the browser from the driver process

    Returns:
        The SeleniumBase driver with CDP mode activated
    """
    return sb_manager.create_driver(url, detach)
