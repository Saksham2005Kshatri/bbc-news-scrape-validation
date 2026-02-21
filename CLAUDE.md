# BBC News Scraper - Project Guide

## Overview
Web scraper that extracts BBC Technology news articles (title, author, date, image URL, article ID, link) and writes them to a CSV file.

## Tech Stack
- Python 3.14+
- Playwright (async API) for browser automation
- `uv` for package management

## Project Structure
- `scraper.py` — Main scraper script, run with `python scraper.py <output_filename.csv>`
- `bbc_news.csv` — Scraped output data
- `pyproject.toml` / `uv.lock` — Dependency management

## Commands
- Install dependencies: `uv sync`
- Install Playwright browsers: `uv run playwright install chromium`
- Run scraper: `uv run python scraper.py bbc_news.csv`

## Conventions
- Use async/await with Playwright's async API
- Use `csv.DictWriter` for CSV operations
- Scraper targets `https://www.bbc.com/technology`
- Output CSV columns: title, author, date, image_url, article_id, link
