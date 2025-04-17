# Selenium browser helper functions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from typing import Optional
from .logger import logger


def create_driver(is_headless=False):
    """Create a new Chrome driver with given is_headless setting"""
    options = Options()
    if is_headless:
        options.add_argument("--is_headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-web-security")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    try:
        driver = webdriver.Chrome(options=options)
        logger.debug("Chrome driver created successfully")
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        raise

    if not is_headless:
        driver.maximize_window()
        logger.debug("Browser window maximized")

    return driver


def wait_for_page_load(driver, timeout=30):
    """Wait for page to load completely"""
    try:
        logger.debug(f"Waiting for page to load (timeout: {timeout}s)")
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script(
                'return document.readyState') == 'complete'
        )
        logger.debug("Page loaded successfully")
    except Exception as e:
        logger.warning(f"Timeout waiting for page to load: {e}")
        raise


def wait_for_element(
    driver,
    xpath: str,
    timeout: int = 30,
    check_text: bool = True,
    wait_type: str = "presence"
) -> Optional[object]:
    """
    Wait for an element to be present or clickable
    
    Args:
        driver: Selenium WebDriver instance
        xpath: XPath of the element to wait for
        timeout: Maximum time to wait in seconds
        check_text: Whether to check if the element has text
        wait_type: Type of wait - "presence" or "clickable"
        
    Returns:
        WebElement if found, None otherwise
    """
    logger.debug(f"Waiting for element: {xpath} (type: {wait_type}, timeout: {timeout}s)")
    try:
        if wait_type == "clickable":
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        else:  # default to presence
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        
        if check_text:
            text = element.text.strip()
            if text:
                logger.debug(f"Element found with text: {text[:30]}...")
            else:
                logger.debug("Element found but has no text")
        else:
            logger.debug("Element found")
            
        return element
    except Exception as e:
        logger.warning(f"Failed to find element {xpath}: {e}")
        return None