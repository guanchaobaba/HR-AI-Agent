from time import sleep
from browsers.seleniumbase_browser import create_sbase_driver, sb_manager
from scraper_agents.liepin_hr.scraper_liepin import run_scraper_liepin
from utils.logger import logger


def main():
    sb = None
    try:
        # Create the driver with detach=True to keep browser open when script ends
        sb = create_sbase_driver(
            url="https://lpt.liepin.com/chat/im",
            # url="https://www.randymajors.org/what-time-zone-am-i-in",
            # url="https://pixelscan.net/fingerprint-check",
            detach=True  # This will keep the browser open when the script ends
        )

        # Now you can use CDP commands (the activate_cdp_mode was already called in create_driver)
        run_scraper_liepin(sb)

        # Wait for user input before closing (optional)
        input("Press Enter to continue...")

    except Exception as e:
        logger.exception(f"Main code something went wrong! {e}")

    finally:
        # If detach=True, the browser will stay open even after the script ends
        # To explicitly close it, uncomment the next line
        # sb_manager.cleanup()
        pass


if __name__ == "__main__":
    main()
