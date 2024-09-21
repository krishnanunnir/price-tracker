from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def get_urls():
    response = supabase.table("Product").select("*").execute()
    products = response.data
    urls = [product["url"] for product in products if "url" in product]
    return urls


def get_products():
    response = supabase.table("Product").select("*").execute()
    products = response.data
    return products
