# German RAM Price Scraper

A multi-site Python web scraper for collecting RAM product listings, specifications, and pricing data from major German e-commerce retailers. Designed for reliability at scale, with proxy support, structured storage, and a modular architecture that makes adding new retailers straightforward.

## Overview

This project automates the collection of RAM product data — names, specifications, and prices — across multiple German online stores, normalizing the results into a consistent format for downstream analysis (price tracking, market comparison, alerting, etc.).

## Supported Retailers

| Retailer  | Status |
|-----------|--------|
| Alternate |    Active |
| Caseking  |    Active |

## Features

- **Multi-site scraping** — unified interface across retailers with site-specific scrapers
- **Product discovery** — automated listing traversal and product URL extraction
- **Structured parsing** — extraction of product names, specifications, and metadata
- **Price normalization** — consistent price formatting and currency handling across sources
- **Flexible storage** — export to JSON/JSONL or persist directly to PostgreSQL
- **Proxy support** — built-in SOCKS5 proxy rotation for resilient, large-scale scraping
- **Configurable filtering** — customizable filters for targeted data collection

## Project Structure

```text
RAM_PARSING/
├── alternate/          # Alternate.de scraper module
│   ├── scraper.py       # Core scraping logic
│   └── urlbuilder.py    # Product/listing URL construction
├── caseking/            # Caseking.de scraper module
│   └── scraper.py       # Core scraping logic
├── Filters/             # Reusable filtering rules
├── data/                # Local output storage (JSON/JSONL)
├── config.py            # Global configuration (proxies, DB, constants)
├── database.py          # PostgreSQL connection and persistence layer
├── save.py              # Data export utilities (JSON/JSONL)
└── main.py              # Entry point — orchestrates scraping runs
```

## Requirements

- Python 3.10+
- PostgreSQL (optional, for database storage)
- SOCKS5 proxy credentials (optional, for proxy-based scraping)

## Installation

```bash
git clone <repository-url>
cd RAM_PARSING
pip install -r requirements.txt
```

## Configuration

Set up your scraping and storage preferences in `config.py`, including:

- Database connection parameters
- Proxy configuration
- Site-specific request settings

## Usage

```bash
python main.py
```

## Data Output

Scraped data can be persisted to:

- **JSON/JSONL files** in the `data/` directory
- **PostgreSQL database** via `database.py`

