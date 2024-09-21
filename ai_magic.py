from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class ProductInfo(BaseModel):
    name: str = Field(description="The full name of the product")
    price: float = Field(description="The current selling price of the product")
    unique_identifier: Optional[str] = Field(
        description="unique identifier to denote the proudct"
    )
    url: str = Field(description="url for the product")


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
