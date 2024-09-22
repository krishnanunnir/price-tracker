import os
import logging
from typing import List
from supabase import create_client, Client
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders import AmazonProductSpider, FlipkartProductSpider
from dotenv import load_dotenv
import schedule
import time

load_dotenv()


logger = logging.getLogger(__name__)


class ProductDTO:
    # Initialize Supabase client
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    @classmethod
    def get_products(cls) -> List[dict]:
        response = cls.supabase.table("Product").select("*").execute()
        products = response.data
        return products

    @classmethod
    def get_urls(cls) -> List[str]:
        response = cls.supabase.table("Product").select("url").execute()
        urls = [product["url"] for product in response.data]
        return urls


def run_spiders():
    urls = ProductDTO.get_urls()
    amazon_urls = [url for url in urls if "amazon" in url.lower()]
    flipkart_urls = [url for url in urls if "flipkart" in url.lower()]

    process = CrawlerProcess(get_project_settings())
    process.crawl(AmazonProductSpider, urls=amazon_urls)
    process.crawl(FlipkartProductSpider, urls=flipkart_urls)
    process.start()


schedule.every(5).minutes.do(run_spiders)


while True:
    schedule.run_pending()
    time.sleep(1)
