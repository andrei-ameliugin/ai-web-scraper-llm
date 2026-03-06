import re

from bs4 import BeautifulSoup

from schemas import ProductData

RATING_MAP = {
    "One": "One",
    "Two": "Two",
    "Three": "Three",
    "Four": "Four",
    "Five": "Five",
}


def extract_with_css(html: str) -> ProductData:
    """Extract product data from HTML using CSS selectors.

    Returns a ProductData instance with None for any field that cannot
    be located in the page markup.
    """
    soup = BeautifulSoup(html, "lxml")

    # Title — the main <h1> tag
    title_tag = soup.select_one("h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Price — e.g. "£51.77"
    price_tag = soup.select_one(".price_color")
    price = price_tag.get_text(strip=True) if price_tag else None

    # Availability — e.g. "In stock (22 available)" → "In stock"
    availability = None
    avail_tag = soup.select_one(".availability")
    if avail_tag:
        raw = avail_tag.get_text(strip=True)
        match = re.match(r"(In stock|Out of stock)", raw, re.IGNORECASE)
        availability = match.group(1) if match else raw

    # Rating — derived from the class name on <p class="star-rating Three">
    rating = None
    rating_tag = soup.select_one("p.star-rating")
    if rating_tag:
        classes = rating_tag.get("class", [])
        for cls in classes:
            if cls in RATING_MAP:
                rating = RATING_MAP[cls]
                break

    return ProductData(
        title=title,
        price=price,
        availability=availability,
        rating=rating,
        extraction_method="css",
    )
