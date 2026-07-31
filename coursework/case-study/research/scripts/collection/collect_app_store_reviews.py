#!/usr/bin/env python3
"""Collect a privacy-minimized Korean App Store review comparison sample."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


APP_ID = "1535886772"
STORE_URL = f"https://apps.apple.com/kr/app/id{APP_ID}"
FEED_TEMPLATE = "https://itunes.apple.com/kr/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data/reviews/app_store/raw/reviews_raw.csv"
SAMPLE_PATH = PROJECT_ROOT / "data/reviews/app_store/samples/review_sample_30.csv"
RAW_FIELDS = [
    "review_id", "rating", "review_date_utc", "review_text", "review_title",
    "app_version", "collected_date", "period_bucket", "source_url",
]
SAMPLE_FIELDS = RAW_FIELDS + ["sample_group", "selection_order"]


def period_bucket(date_text):
    year = int(date_text[:4])
    if year <= 2022:
        return "early"
    if year <= 2024:
        return "middle"
    return "recent"


def fetch_page(page):
    url = FEED_TEMPLATE.format(page=page, app_id=APP_ID)
    # Apple returns an empty legacy feed for some non-browser user agents.
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.load(response).get("feed", {}).get("entry", [])


def collect():
    collected_date = datetime.now(timezone.utc).date().isoformat()
    rows = []
    seen = set()
    # The legacy Apple RSS feed can expose populated results on a non-first
    # page, so check the documented page range and deduplicate by review ID.
    for page in range(1, 11):
        for entry in fetch_page(page):
            if "im:rating" not in entry:
                continue
            review_id = entry["id"]["label"]
            if review_id in seen:
                continue
            seen.add(review_id)
            date_text = entry["updated"]["label"]
            rows.append({
                "review_id": review_id,
                "rating": int(entry["im:rating"]["label"]),
                "review_date_utc": date_text,
                "review_text": entry["content"]["label"].strip(),
                "review_title": entry["title"]["label"].strip(),
                "app_version": entry.get("im:version", {}).get("label", ""),
                "collected_date": collected_date,
                "period_bucket": period_bucket(date_text),
                "source_url": STORE_URL,
            })
    rows.sort(key=lambda row: row["review_date_utc"], reverse=True)
    return rows


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sample(rows):
    low = [dict(row, sample_group="1-3점", selection_order=i + 1)
           for i, row in enumerate(row for row in rows if row["rating"] <= 3)][:20]
    high = [dict(row, sample_group="4-5점_반례", selection_order=i + 1)
            for i, row in enumerate(row for row in rows if row["rating"] >= 4)][:10]
    return low + high


def main():
    rows = collect()
    selected = sample(rows)
    write_csv(RAW_PATH, RAW_FIELDS, rows)
    write_csv(SAMPLE_PATH, SAMPLE_FIELDS, selected)
    low = sum(row["rating"] <= 3 for row in selected)
    high = sum(row["rating"] >= 4 for row in selected)
    print(f"raw={len(rows)} sample={len(selected)} low={low} high={high}")
    return 0 if low == 20 and high == 10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
