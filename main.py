# Entry point to run the spider

from automation.pyautogui_browser import py_auto_gui_browser
from scraper_agents.jobs51_hr.scraper_51jobs import run_scraper_51jobs
from utils.logger import logger






def main():
    try:
        py_auto_gui_browser()

        run_scraper_51jobs()
    except Exception as e:
        logger.error("Main code something went wrong!")




if __name__ == "__main__":
    main()
