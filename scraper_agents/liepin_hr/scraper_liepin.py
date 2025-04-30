
from scraper_agents.liepin_hr.candidates_message.candidates_message import get_candidates_conversations
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import logger


def run_scraper_leipin(driver):
    try:
        # get_candidates_conversations(driver)
        # 1) Go to the IM page

        # driver.get("https://www.liepin.com/chat/im")

        # 2) Wait until at least one contact info block is present
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".im-ui-contact-info"))
        )

        # 3) Execute your JS to get bounding‐rects
        positions = driver.execute_script("""
        return Array.from(document.querySelectorAll('.im-ui-contact-info'))
            .map(el => {
            const r = el.getBoundingClientRect();
            return { x: r.left, y: r.top, w: r.width, h: r.height };
            });
        """)

        logger.info(f"Found {len(positions)} contacts:")
        for pos in positions:
            logger.info(pos)
    except Exception as e:
        logger.warning(f"Error in Leipin functions {e}")
