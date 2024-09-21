import logging
import os
import time
from typing import List

import requests
import schedule
from dotenv import load_dotenv

from ai_magic import get_response
from fetch_url import fetch_page_content_for_urls
from supabse import get_urls

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # This handler will log to the console
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


def handle_url(urls: List[str]):
    logger.info(f"Handling {len(urls)} URLs")
    results = get_data(urls)
    for i, x in enumerate(results):
        logger.info(f"Sending message for item {i+1}/{len(results)}")
        message = f" [{x.name}]({x.url}) {x.price}"
        send_telegram_message(message)
    logger.info("Finished handling URLs")


def main():
    logger.info("Starting main function")
    urls = get_urls()
    logger.info(f"Retrieved {len(urls)} URLs")
    handle_url(urls=urls)
    logger.info("Completed main function")


schedule.every(1).minutes.do(main)

logger.info("Starting main loop")
while True:
    schedule.run_pending()
    time.sleep(1)
