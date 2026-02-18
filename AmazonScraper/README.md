# AmazonScraper

Scrapes Amazon search result pages for a query and region, then stores product snapshots and price history.

## Features
- Multi-region Amazon domain support
- Cursor-like page traversal through result pagination
- Product de-duplication by ASIN
- SQLite storage for products and historical prices
- Timestamped text exports in `scrapes/`
- Desktop notification on completion (Windows)

## Requirements
- Python 3.9+
- Windows (notification and file-open behavior)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python amazon_scraper.py "wireless mouse" 3 us
```

Arguments:
- `query` (required): Search term
- `max_pages` (optional): Maximum pages to scan (default: `999`)
- `region` (optional): Region code (default: `in`)

## Output
- Text export: `scrapes/<Region>_<query>_<timestamp>.txt`
- SQLite database: `prices.db`
