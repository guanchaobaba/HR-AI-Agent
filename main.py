# main.py
from browsers.seleniumbase_browser import create_sbase_driver
from utils.logger import logger


def main():
    driver = None
    try:
        driver = create_sbase_driver(
            url="https://www.liepin.com",
            user_data_dir=r"C:\Users\rasel\AppData\Local\Google\Chrome\User Data",
            profile_dir="Profile 1",
            headless=False,
            use_uc=False,
        )
        # … do your scraping here …

        # Now I need to start here code from JS inject with coords mouse movement

        # If you want to pause for debugging, e.g.:
        input("Press Enter to close the browser…")

    except Exception as e:
        logger.exception(f"Main code something went wrong! {e}")

    finally:
        if not driver:
            driver.quit()


if __name__ == "__main__":
    main()
