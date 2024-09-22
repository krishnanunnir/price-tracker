from pydantic import BaseModel, Field
from typing import Optional


class ProductInfo(BaseModel):
    name: str = Field(description="The full name of the product")
    price: float = Field(description="The current selling price of the product")
    unique_identifier: Optional[str] = Field(
        description="unique identifier to denote the proudct"
    )
    url: str = Field(description="url for the product")
