import scrapy
import time
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


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


class AmazonProductSpider(scrapy.Spider):
    name = "amazon_product_spider"

    def __init__(self, urls=[], *args, **kwargs):
        super(AmazonProductSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls
        self.telegram_messenger = TelegramMessenger()

    def parse(self, response):
        title = response.css("#productTitle::text").get().strip()
        price_whole = response.css(".a-price-whole::text").get()
        price = f"{price_whole}" if price_whole else None
        time.sleep(2)  # 2-second delay between requests
        message = f"Amazon: [{title}]({response.url}) - Price: {price}"
        self.telegram_messenger.send_message(message)


class FlipkartProductSpider(scrapy.Spider):
    name = "flipkart_product_spider"

    def __init__(self, urls=[], *args, **kwargs):
        super(FlipkartProductSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls
        self.telegram_messenger = TelegramMessenger()

    def parse(self, response):
        title = response.css(".VU-ZEz::text").get().strip()
        price = response.css(".Nx9bqj.CxhGGd::text").get()

        if price:
            price = price.replace("₹", "").replace(",", "").strip()
        # Add a delay to avoid overwhelming the server

        time.sleep(2)  # 2-second delay between requests
        message = f"Flipkart\n[{title}]({response.url}) \n Price: {price}"
        self.telegram_messenger.send_message(message)
