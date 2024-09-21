import logging
import os
import time
import subprocess

import requests
import schedule
from dotenv import load_dotenv

from ai_magic import get_response
from fetch_url import fetch_page_content_for_urls
from supabse import get_products

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="error.log",
)
logger = logging.getLogger(__name__)


def get_data(urls: str):
    logger.info(f"Fetching data for {len(urls)} URLs")
    contents = fetch_page_content_for_urls(urls)
    logger.info(f"Retrieved content for {len(contents)} URLs")
    result = []
    for i, content in enumerate(contents):
        logger.info(f"Processing content {i+1}/{len(contents)}")
        result.append(get_response(content))
    logger.info(f"Processed {len(result)} items")
    return result


def send_telegram_message(text):
    logger.info("Sending Telegram message")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text, "parse_mode": "markdown"}
    response = requests.get(url, params=params)
    logger.info(f"Telegram API response: {response.status_code}")
    return response.json()


def handle_url():
    products = get_products()
    urls = [product["url"] for product in products if "url" in product]
    url_map = {
        product["url"]: product["target_price"]
        for product in products
        if "url" and "target_price" in product
    }
    logger.info(f"Handling {len(urls)} URLs")
    results = get_data(urls)
    for i, x in enumerate(results):
        logger.info(f"Sending message for item {i+1}/{len(results)}")
        if url_map.get(x.url, None) is None or url_map[x.url] > x.price:
            message = f" [{x.name}]({x.url}) {x.price}"
            send_telegram_message(message)
    logger.info("Finished handling URLs")


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


schedule.every(5).minutes.do(handle_url)

git_hash, commit_message = get_git_info()
logger.info(f"Current Git hash: {git_hash}")
logger.info(f"Latest commit message: {commit_message}")
logger.info("Starting main loop")
while True:
    schedule.run_pending()
    time.sleep(1)
