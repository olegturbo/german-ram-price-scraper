# German RAM Price Scraper

A multi-site Python web scraper for collecting RAM product listings, specifications, and pricing data from major German e-commerce retailers. Designed for reliability at scale, with proxy support, structured storage, and a modular architecture that makes adding new retailers straightforward.

## Overview

This project automates the collection of RAM product data — names, specifications, and prices — across multiple German online stores, normalizing the results into a consistent format for downstream analysis (price tracking, market comparison, alerting, etc.).

## Supported Retailers

| Retailer    | Status |
| ----------- | ------ |
| Alternate   | Active |
| Caseking    | Active |
| Mindfactory | Active |

## Features

* **Multi-site scraping** — unified interface across retailers with site-specific scrapers
* **Product discovery** — automated listing traversal and product URL extraction
* **Structured parsing** — extraction of product names, specifications, and metadata
* **Price normalization** — consistent price formatting and currency handling across sources
* **Flexible storage** — export to JSON/JSONL or persist directly to PostgreSQL
* **State persistence** — track scraping progress with state files (`last_link.txt`, `completed.txt`)
* **Secure configuration** — environment variable support (`.env`) for database credentials and settings
* **Proxy support** — built-in SOCKS5 proxy support for resilient scraping
* **Configurable filtering** — customizable filters for targeted data collection

## Project Structure

```text
RAM_PARSING/
├── alternate/          # Alternate.de scraper module
├── caseking/           # Caseking.de scraper module
├── mindfactory/        # Mindfactory.de scraper module
├── filters/            # Reusable filtering rules
├── data/               # Local output storage (JSON/JSONL)
├── .env.example        # Template for environment variables
├── .gitignore          # Excludes sensitive files (.env, venv)
├── completed.txt       # Log for completed items/links
├── last_link.txt       # State file for resuming interrupted runs
├── config.py           # Global configuration (proxies, constants)
├── database.py         # PostgreSQL connection & persistence layer
├── save.py             # Data export utilities (JSON/JSONL)
└── main.py             # Entry point — orchestrates scraping runs
```

## Requirements

* Python 3.10+
* PostgreSQL (optional, for database storage)
* SOCKS5 proxy credentials (optional, for proxy-based scraping)

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd RAM_PARSING
```

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory based on `.env.example`:

```bash
cp .env.example .env
```

Configure environment variables in `.env` or system environment:

```env
PORT=5432
DATABASE=scraper_db
DB_USER=olegturbo
PASSWORD=your_secure_password
```

Adjust non-sensitive settings such as proxies and request timeouts in `config.py`.

## Usage

Run the main orchestrator script:

```bash
python main.py
```

## Data Output

* **JSON/JSONL files** in the `data/` directory
* **PostgreSQL database** via `database.py`, using credentials loaded from environment variables
