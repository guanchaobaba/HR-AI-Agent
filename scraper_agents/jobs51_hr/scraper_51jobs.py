
from scraper_agents.jobs51_hr.front_page.front_page import get_front_page
from utils.logger import logger


def run_scraper_51jobs():
    try:
        get_front_page()
    except Exception as e:
        logger.warning(f"Error in 51jobs functions {e}")
