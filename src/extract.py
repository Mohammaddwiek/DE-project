"""
Step 2 - Extraction.

Downloads every country from the REST Countries API (v5) and saves the
response exactly as received to data/raw/countries_raw.json.

Why v5: the old v3.1 API was shut down and now only returns a
"This API version has been deprecated" error (checked on 2026-11-09).

How it works:
  1. Read the API key from the .env file (never hard-coded, never committed).
  2. The free plan returns at most 100 countries per request, so we ask
     page by page (offset 0, 100, 200, ...) until the API says there is no more.
  3. Save all countries into one JSON file, plus a small metadata file
     with the download date and the country count.

Run from the project folder:
    python src/extract.py           # downloads only if the raw file does not exist yet
    python src/extract.py --force   # downloads again and overwrites the raw file
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# --- Settings ---------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "countries_raw.json"
METADATA_FILE = PROJECT_ROOT / "data" / "raw" / "extraction_metadata.json"

API_URL = "https://api.restcountries.com/countries/v5"
PAGE_LIMIT = 100                         # maximum allowed on the free plan
OMITTED_FIELDS = "names.translations"    # country name in ~25 languages; not needed
REQUEST_TIMEOUT = 30                     # seconds to wait before giving up on a request
PAUSE_BETWEEN_REQUESTS = 1               # seconds; stays far below the 20 requests / 10 s rate limit


def get_api_key():
    """Read the key from .env. Stop with a clear message if it is missing."""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("RESTCOUNTRIES_API_KEY")
    if not api_key or api_key == "your-key-here":
        sys.exit("ERROR: RESTCOUNTRIES_API_KEY not found. Copy .env.example to .env and add your key.")
    return api_key


def fetch_page(api_key, offset):
    """Request one page of up to PAGE_LIMIT countries, starting at `offset`."""
    response = requests.get(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        params={
            "limit": PAGE_LIMIT,
            "offset": offset,
            "response_fields_omit": OMITTED_FIELDS,
        },
        timeout=REQUEST_TIMEOUT,
    )
    body = response.json()

    # The API reports problems as {"errors": [{"message": ...}]}
    if response.status_code != 200 or "errors" in body:
        sys.exit(f"ERROR: HTTP {response.status_code} at offset {offset}: {body.get('errors')}")
    # The demo key returns fake sample data; make sure we got the real dataset
    if "_demo" in body["data"]:
        sys.exit("ERROR: the API returned demo data. Check that .env contains your real key.")

    return body["data"]


def extract_all(api_key):
    """Loop over all pages and return (list of countries, number of requests made)."""
    countries = []
    offset = 0
    requests_made = 0

    while True:
        page = fetch_page(api_key, offset)
        requests_made += 1
        countries.extend(page["objects"])
        meta = page["meta"]
        print(f"  request {requests_made}: offset {offset}, got {meta['count']} countries "
              f"({len(countries)} of {meta['total']} so far)")

        if not meta["more"]:
            break
        offset += PAGE_LIMIT
        time.sleep(PAUSE_BETWEEN_REQUESTS)

    # Sanity check: did we receive as many countries as the API says exist?
    if len(countries) != meta["total"]:
        sys.exit(f"ERROR: expected {meta['total']} countries but received {len(countries)}.")

    return countries, requests_made


def main():
    parser = argparse.ArgumentParser(description="Download all countries from the REST Countries API.")
    parser.add_argument("--force", action="store_true", help="download again even if the raw file exists")
    args = parser.parse_args()

    # Download once, then always work from the saved file
    if RAW_FILE.exists() and not args.force:
        print(f"Raw file already exists: {RAW_FILE.relative_to(PROJECT_ROOT)}")
        print("Skipping download. Use --force to download again.")
        return

    api_key = get_api_key()
    print(f"Downloading countries from {API_URL} ...")
    countries, requests_made = extract_all(api_key)

    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii=False keeps names like "Côte d'Ivoire" readable instead of ô
        json.dump(countries, f, ensure_ascii=False, indent=2)

    metadata = {
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": API_URL,
        "api_version": "v5",
        "country_count": len(countries),
        "requests_made": requests_made,
        "page_limit": PAGE_LIMIT,
        "fields_omitted": OMITTED_FIELDS,
    }
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved {len(countries)} countries to {RAW_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Saved metadata to {METADATA_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
