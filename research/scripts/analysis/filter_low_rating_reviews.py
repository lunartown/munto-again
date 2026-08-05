#!/usr/bin/env python3
"""Filter 1-3 star reviews written from 2024 through 2026."""

import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUTS = {
    "Google Play": PROJECT_ROOT / "archive/research/data/reviews/google_play/raw/reviews_history.csv",
    "App Store": PROJECT_ROOT / "research/data/reviews/app_store/raw/reviews_history.csv",
}
OUTPUT = PROJECT_ROOT / "research/data/reviews/filtered/low_rating_2024_2026.csv"
FIELDS = [
    "platform",
    "review_id",
    "rating",
    "review_date_utc",
    "review_year",
    "review_text",
    "review_title",
    "thumbs_up",
    "app_version",
    "collected_date",
    "source_sort",
    "source_page",
    "source_url",
]


def filter_rows(platform, path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        selected = []
        for row in rows:
            date = datetime.fromisoformat(row["review_date_utc"].replace("Z", "+00:00"))
            if 2024 <= date.year <= 2026 and int(row["rating"]) <= 3:
                selected.append(
                    {
                        "platform": platform,
                        "review_id": row.get("review_id", ""),
                        "rating": row.get("rating", ""),
                        "review_date_utc": row.get("review_date_utc", ""),
                        "review_year": date.year,
                        "review_text": row.get("review_text", ""),
                        "review_title": row.get("review_title", ""),
                        "thumbs_up": row.get("thumbs_up", ""),
                        "app_version": row.get("app_version", ""),
                        "collected_date": row.get("collected_date", ""),
                        "source_sort": row.get("source_sort", ""),
                        "source_page": row.get("source_page", ""),
                        "source_url": row.get("source_url", ""),
                    }
                )
    return selected


def main():
    selected = [row for platform, path in INPUTS.items() for row in filter_rows(platform, path)]
    selected.sort(key=lambda row: (row["platform"], row["review_date_utc"], row["review_id"]), reverse=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(selected)
    print(f"saved={len(selected)} output={OUTPUT}")
    for platform in INPUTS:
        print(f"{platform}={sum(row['platform'] == platform for row in selected)}")


if __name__ == "__main__":
    main()
