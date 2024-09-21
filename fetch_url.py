import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_page_content_for_urls(urls):
    contents = []
    driver = setup_driver()

    try:
        for url in urls:
            driver.get(url)
            elements = get_page_elements(url)
            content_parts = []
            for tag, by_content in elements:
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((by_content, tag))
                    )
                    content_parts.append(element.text)
                except Exception as e:
                    logging.error(f"Error extracting content from {tag}: {str(e)}")

            content = f"url: {url}\n" + "\n".join(content_parts)
            contents.append(content)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

    return contents


def setup_driver():
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")

    geckodriver_path = os.getenv("GECKODRIVER_PATH")

    if geckodriver_path:
        service = FirefoxService(executable_path=geckodriver_path)
    else:
        service = FirefoxService(GeckoDriverManager().install())

    return webdriver.Firefox(service=service, options=firefox_options)


def get_page_elements(url):
    if "amazon" in url:
        return [("apex_desktop", By.ID), ("title_feature_div", By.ID)]
    elif "flipkart" in url:
        return [("C7fEHH", By.CLASS_NAME)]
    else:
        return [("body", By.TAG_NAME)]
