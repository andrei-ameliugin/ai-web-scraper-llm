import json
import logging

import httpx
from bs4 import BeautifulSoup

from config import settings
from schemas import ProductData

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a strict data extraction engine.\n"
    "Extract product fields from the provided web page text.\n\n"
    "Return ONLY valid JSON with exactly these keys:\n"
    "title\n"
    "price\n"
    "availability\n"
    "rating\n\n"
    "Extraction rules:\n"
    "- Copy values exactly as they appear in the text.\n"
    "- Do NOT summarize or modify values.\n"
    "- If availability contains additional text like '(22 available)', return only 'In stock'.\n"
    "- The rating is a word such as: One, Two, Three, Four, Five.\n"
    "- If the rating appears in text like 'star-rating Three', extract 'Three'.\n"
    "- If a field cannot be determined, return null.\n\n"
    "Return ONLY JSON. No explanations."
)


def _html_to_text(html: str) -> str:
    """Strip HTML tags and return clean visible text."""
    soup = BeautifulSoup(html, "lxml")
    # Remove script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def _parse_response_text(body: dict) -> str:
    """Extract the output text from a Responses API response body.

    Expected structure:
        {"output": [{"type": "message", "content": [{"type": "output_text", "text": "..."}]}]}

    Raises:
        ValueError: if the expected structure is not found.
    """
    for item in body.get("output", []):
        if item.get("type") == "message":
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    return block["text"]
    raise ValueError("No output_text found in Responses API response")


async def extract_with_llm(html: str) -> ProductData:
    """Extract product data by sending page text to an LLM.

    Uses the OpenAI Responses API with JSON mode for reliable
    structured output.

    Raises:
        RuntimeError: if the OpenAI API call fails or returns invalid data.
    """
    page_text = _html_to_text(html)

    payload = {
        "model": settings.openai_model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Extract product data from this page:\n\n{page_text}",
            },
        ],
        "text": {
            "format": {"type": "json_object"},
        },
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                settings.openai_api_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "OpenAI API error %s: %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise RuntimeError(
                f"OpenAI API returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("OpenAI API request failed: %s", exc)
            raise RuntimeError(f"OpenAI API request failed: {exc}") from exc

    body = response.json()
    raw = _parse_response_text(body)
    logger.info("LLM raw response: %s", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned invalid JSON: %s", raw)
        raise RuntimeError("LLM returned invalid JSON") from exc

    return ProductData(
        title=data.get("title"),
        price=data.get("price"),
        availability=data.get("availability"),
        rating=data.get("rating"),
        extraction_method="llm",
    )
