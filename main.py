import logging

from fastapi import FastAPI, HTTPException

from schemas import ExtractionMode, ExtractionRequest, ProductData
from scraper import fetch_page
from css_extractor import extract_with_css
from llm_extractor import extract_with_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Web Scraper API",
    description=(
        "Extract structured product data from web pages using CSS selectors, "
        "LLM-based extraction, or a hybrid auto mode."
    ),
    version="1.0.0",
)


@app.post("/extract-url", response_model=ProductData)
async def extract_url(request: ExtractionRequest) -> ProductData:
    """Extract product data from a given URL.

    Supports three extraction modes:
    - **css**: Traditional HTML parsing with BeautifulSoup.
    - **llm**: AI-powered extraction via OpenAI.
    - **auto**: CSS first, with LLM fallback if fields are missing.
    """
    url = str(request.url)
    logger.info("Extraction request: url=%s mode=%s", url, request.mode)

    # Step 1: Fetch the page
    html = await fetch_page(url)

    # Step 2: Extract based on mode
    if request.mode == ExtractionMode.css:
        result = extract_with_css(html)
        if not result.has_all_fields():
            logger.warning("CSS extraction returned incomplete data for %s", url)
        return result

    if request.mode == ExtractionMode.llm:
        try:
            return await extract_with_llm(html)
        except Exception as exc:
            logger.error("LLM extraction failed: %s", exc)
            raise HTTPException(
                status_code=500,
                detail=f"LLM extraction failed: {exc}",
            )

    # mode == auto: CSS first, fallback to LLM
    result = extract_with_css(html)
    if result.has_all_fields():
        logger.info("Auto mode: CSS extraction succeeded for %s", url)
        return result

    logger.info("Auto mode: CSS incomplete, falling back to LLM for %s", url)
    try:
        return await extract_with_llm(html)
    except Exception as exc:
        logger.error("LLM fallback failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"LLM fallback extraction failed: {exc}",
        )
