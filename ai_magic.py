from openai import OpenAI
from dotenv import load_dotenv
from type import ProductInfo

# Load environment variables from .env file
load_dotenv()


client = OpenAI()


def get_response(product):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful data extractor and extracts useful data about Products from content",
            },
            {"role": "user", "content": f"Find details about the product {product}"},
        ],
        response_format=ProductInfo,
    )

    return completion.choices[0].message.parsed
