# AI Web Scraper API

An AI-powered web scraping API that extracts structured product data from web pages using a hybrid extraction architecture — traditional CSS selector parsing with an LLM fallback.

## Architecture

```
POST /extract-url
        │
        ▼
   Fetch HTML (httpx)
        │
        ▼
   ┌─────────────────────┐
   │  Extraction Mode?   │
   └──┬──────┬───────┬───┘
      │      │       │
     css    llm    auto
      │      │       │
      ▼      ▼       ▼
   CSS     LLM    CSS first
 Parsing  (GPT)  → fallback
                   to LLM
```

## Extraction Modes

| Mode   | Behavior |
|--------|----------|
| `css`  | Parse HTML with BeautifulSoup using CSS selectors |
| `llm`  | Send page text to OpenAI and extract fields via LLM |
| `auto` | Try CSS first; if any fields are missing, fallback to LLM |

## Extracted Fields

- `title` — Book title
- `price` — Price with currency symbol
- `availability` — Stock status
- `rating` — Star rating as a word (One–Five)
- `extraction_method` — Which method produced the result (`css` or `llm`)

## Prerequisites

- **Python 3.10+**

## Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ai-web-scraper-llm.git
cd ai-web-scraper-llm

# Create and activate local virtual environment
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

> The `.venv/` directory is listed in `.gitignore` and will not be committed.

To deactivate the virtual environment when you're done:

```bash
deactivate
```

## Usage

### Start the server

```bash
uvicorn main:app --reload
```

The API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Example requests

**CSS extraction:**
```bash
curl -X POST http://localhost:8000/extract-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", "mode": "css"}'
```

**LLM extraction:**
```bash
curl -X POST http://localhost:8000/extract-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html", "mode": "llm"}'
```

**Auto mode (default):**
```bash
curl -X POST http://localhost:8000/extract-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"}'
```

### Example response

```json
{
  "title": "A Light in the Attic",
  "price": "£51.77",
  "availability": "In stock",
  "rating": "Three",
  "extraction_method": "css"
}
```

## Project Structure

```
├── main.py              # FastAPI app & endpoint orchestration
├── scraper.py           # Async page fetching with httpx
├── css_extractor.py     # BeautifulSoup CSS selector extraction
├── llm_extractor.py     # OpenAI-based LLM extraction
├── schemas.py           # Pydantic models (request/response)
├── config.py            # App settings via pydantic-settings
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── README.md
```

## Tech Stack

- **Python** — async throughout
- **FastAPI** — web framework
- **httpx** — async HTTP client
- **BeautifulSoup4** + **lxml** — HTML parsing
- **OpenAI API** — LLM extraction
- **Pydantic** — data validation & settings

## License

MIT
