
from scraper_agents.liepin_hr.candidates_message.candidates_message import get_candidates_conversations
from utils.logger import logger


def run_scraper_liepin(sb):
    try:
        get_candidates_conversations(sb)

    except Exception as e:
        logger.warning(f"Error in Liepin functions: {e}")
