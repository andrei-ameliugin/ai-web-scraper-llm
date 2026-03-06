from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl


class ExtractionMode(str, Enum):
    css = "css"
    llm = "llm"
    auto = "auto"


class ExtractionRequest(BaseModel):
    url: HttpUrl
    mode: ExtractionMode = ExtractionMode.auto


class ProductData(BaseModel):
    title: Optional[str] = None
    price: Optional[str] = None
    availability: Optional[str] = None
    rating: Optional[str] = None
    extraction_method: Optional[str] = None

    def has_all_fields(self) -> bool:
        """Check whether all product fields are populated."""
        return all([self.title, self.price, self.availability, self.rating])
