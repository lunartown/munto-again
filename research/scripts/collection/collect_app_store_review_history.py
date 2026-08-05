#!/usr/bin/env python3
"""Collect the maximum public Korean App Store review history for Munto."""

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


APP_ID = "1535886772"
STORE_URL = f"https://apps.apple.com/kr/app/id{APP_ID}"
FEED_TEMPLATE = (
    "https://itunes.apple.com/kr/rss/customerreviews/"
    "page={page}/id={app_id}/sortby=mostrecent/json"
)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "research/data/reviews/app_store/raw/reviews_history.csv"
)
RAW_FIELDS = [
    "review_id",
    "rating",
    "review_date_utc",
    "review_text",
    "review_title",
    "app_version",
    "collected_date",
    "source_page",
    "source_url",
]


def fetch_page(page, app_id, timeout):
    url = FEED_TEMPLATE.format(page=page, app_id=app_id)
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response).get("feed", {}).get("entry", [])


def collect(app_id, max_pages, delay, timeout):
    collected_date = datetime.now(timezone.utc).date().isoformat()
    rows = []
    seen = set()

    for page in range(1, max_pages + 1):
        last_error = None
        for attempt in range(3):
            try:
                entries = fetch_page(page, app_id, timeout)
                break
            except Exception as error:
                last_error = error
                time.sleep(1 + attempt * 2)
        else:
            raise last_error

        page_count = 0
        for entry in entries:
            if "im:rating" not in entry:
                continue
            review_id = entry["id"]["label"]
            if review_id in seen:
                continue
            seen.add(review_id)
            rows.append(
                {
                    "review_id": review_id,
                    "rating": int(entry["im:rating"]["label"]),
                    "review_date_utc": entry["updated"]["label"],
                    "review_text": entry["content"]["label"].strip(),
                    "review_title": entry["title"]["label"].strip(),
                    "app_version": entry.get("im:version", {}).get("label", ""),
                    "collected_date": collected_date,
                    "source_page": page,
                    "source_url": STORE_URL,
                }
            )
            page_count += 1

        print(f"page={page} new_reviews={page_count} total={len(rows)}", flush=True)
        if page_count == 0:
            break
        if page < max_pages:
            time.sleep(delay)

    rows.sort(key=lambda row: row["review_date_utc"], reverse=True)
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default=APP_ID)
    parser.add_argument("--max-pages", type=int, default=10, choices=range(1, 11))
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = collect(args.app_id, args.max_pages, args.delay, args.timeout)
    write_csv(args.output, rows)
    oldest = rows[-1]["review_date_utc"] if rows else ""
    newest = rows[0]["review_date_utc"] if rows else ""
    print(
        f"saved={len(rows)} newest={newest} oldest={oldest} output={args.output}"
    )
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
