import logging
import os
import subprocess
import time

import requests
import schedule
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from supabase import Client, create_client
from webdriver_manager.firefox import GeckoDriverManager

from type import ProductInfo

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="error.log",
)
logger = logging.getLogger(__name__)

load_dotenv()
client = OpenAI()


class ProductDTO:
    # Initialize Supabase client
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    @classmethod
    def get_products(cls):
        response = cls.supabase.table("Product").select("*").execute()
        products = response.data
        return products

    @classmethod
    def update_target_price(cls, product_id: int, new_target_price: float):
        try:
            response = (
                cls.supabase.table("Product")
                .update({"target_price": new_target_price})
                .eq("id", product_id)
                .execute()
            )
            if response.data:
                logger.info(
                    f"Successfully updated target price for product {product_id}"
                )
                return True
            else:
                logger.warning(f"No product found with id {product_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating target price: {str(e)}")
            return False


class Webscraper:
    def __init__(self):
        self.driver = self._setup_driver()

    def fetch(self, url):
        try:
            self.driver.get(url)
            elements = self._get_page_elements(url)
            content_parts = []
            for tag, by_content in elements:
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((by_content, tag))
                    )
                    content_parts.append(element.text)
                except Exception as e:
                    logging.error(f"Error extracting content from {tag}: {str(e)}")

            return "\n".join(content_parts)
        except Exception as e:
            logging.error(f"An error occurred while fetching {url}: {str(e)}")
            return None

    def quit(self):
        if self.driver:
            self.driver.quit()

    def _setup_driver(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")

        geckodriver_path = os.getenv("GECKODRIVER_PATH")

        if geckodriver_path:
            service = FirefoxService(executable_path=geckodriver_path)
        else:
            service = FirefoxService(GeckoDriverManager().install())

        return webdriver.Firefox(service=service, options=firefox_options)

    def _get_page_elements(self, url):
        if "amazon" in url:
            return [("apex_desktop", By.ID), ("title_feature_div", By.ID)]
        elif "flipkart" in url:
            return [("C7fEHH", By.CLASS_NAME)]
        else:
            return [("body", By.TAG_NAME)]


class AI:
    def get_response(content):
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful data extractor and extracts useful data about Products from content",
                },
                {
                    "role": "user",
                    "content": f"Find details about the product {content}",
                },
            ],
            response_format=ProductInfo,
        )

        return completion.choices[0].message.parsed


class TelegramMessenger:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, text):
        logger.info("Sending Telegram message")
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {"chat_id": self.chat_id, "text": text, "parse_mode": "markdown"}
        response = requests.get(url, params=params)
        logger.info(f"Telegram API response: {response.status_code}")
        return response.json()


def get_git_info():
    try:
        # Get the current commit hash
        hash_command = ["git", "rev-parse", "HEAD"]
        git_hash = subprocess.check_output(hash_command).decode("ascii").strip()

        # Get the latest commit message
        message_command = ["git", "log", "-1", "--pretty=%B"]
        commit_message = (
            subprocess.check_output(message_command).decode("ascii").strip()
        )

        return git_hash, commit_message
    except subprocess.CalledProcessError:
        return "Git info unavailable", "Git info unavailable"


def main():
    products = ProductDTO.get_products()

    scraper = Webscraper()
    try:
        for product in products:
            content = scraper.fetch(product["url"])
            if content:
                product_info = AI.get_response(content)
                message = f"Test: [{product_info.name}]({product['url']}) {product_info.price}"
                TelegramMessenger().send_message(message)

                # Update the target price in the database
                ProductDTO.update_target_price(product["id"], product_info.price)
    finally:
        scraper.quit()


schedule.every(10).minutes.do(main)

git_hash, commit_message = get_git_info()
logger.info(f"Current Git hash: {git_hash}")
logger.info(f"Latest commit message: {commit_message}")
logger.info("Program initiaated")
while True:
    schedule.run_pending()
    time.sleep(1)
