#!/usr/bin/env python3
"""Build fresh review-analysis samples from raw sources only.

This script intentionally does not read any existing coded cards, clusters, or
findings. Google Play is sampled by period and rating band. All available App
Store reviews are copied into a separate analysis set.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
GOOGLE_RAW = RESEARCH_ROOT / "data/reviews/google_play/raw/reviews_history.csv"
APP_STORE_RAW = RESEARCH_ROOT / "data/reviews/app_store/raw/reviews_raw.csv"
OUTPUT_DIR = RESEARCH_ROOT / "data/reviews/reanalysis/samples"
GOOGLE_OUTPUT = OUTPUT_DIR / "google_play_stratified_180.csv"
APP_STORE_OUTPUT = OUTPUT_DIR / "app_store_all_50.csv"

PERIOD_ORDER = ("early", "middle", "recent")
RATING_BAND_ORDER = ("low", "high")
SAMPLE_SIZE_PER_STRATUM = 30
SAMPLE_SEED = "munto-review-reanalysis-v1"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def rating_band(rating: str) -> str:
    return "low" if int(rating) <= 3 else "high"


def stable_order_key(review_id: str) -> str:
    value = f"{SAMPLE_SEED}:{review_id}".encode()
    return hashlib.sha256(value).hexdigest()


def base_output_row(
    row: dict[str, str],
    *,
    sample_id: str,
    platform: str,
) -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "platform": platform,
        "review_id": row["review_id"],
        "review_date_utc": row["review_date_utc"],
        "period_bucket": row["period_bucket"],
        "rating": row["rating"],
        "rating_band": rating_band(row["rating"]),
        "review_title": row.get("review_title", ""),
        "review_text": row["review_text"],
        "source_url": row["source_url"],
        "inclusion_status": "",
        "exclusion_reason": "",
        "meaning_unit_count": "",
        "card_count": "",
        "researcher_note": "",
    }


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_google_sample() -> list[dict[str, str]]:
    raw_rows = [
        row
        for row in read_rows(GOOGLE_RAW)
        if row["review_text"].strip()
    ]
    selected: list[dict[str, str]] = []

    for period in PERIOD_ORDER:
        for band in RATING_BAND_ORDER:
            stratum = [
                row
                for row in raw_rows
                if row["period_bucket"] == period
                and rating_band(row["rating"]) == band
            ]
            if len(stratum) < SAMPLE_SIZE_PER_STRATUM:
                raise ValueError(
                    f"Not enough rows for {period}/{band}: {len(stratum)}"
                )
            stratum.sort(key=lambda row: stable_order_key(row["review_id"]))
            selected.extend(stratum[:SAMPLE_SIZE_PER_STRATUM])

    output = []
    for index, row in enumerate(selected, start=1):
        output.append(
            base_output_row(
                row,
                sample_id=f"GPR{index:03d}",
                platform="Google Play",
            )
        )
    return output


def build_app_store_set() -> list[dict[str, str]]:
    raw_rows = [
        row
        for row in read_rows(APP_STORE_RAW)
        if row["review_text"].strip() or row.get("review_title", "").strip()
    ]
    raw_rows.sort(
        key=lambda row: (row["review_date_utc"], row["review_id"]),
        reverse=True,
    )

    output = []
    for index, row in enumerate(raw_rows, start=1):
        output.append(
            base_output_row(
                row,
                sample_id=f"ASR{index:03d}",
                platform="Apple App Store",
            )
        )
    return output


def main() -> None:
    google_rows = build_google_sample()
    app_store_rows = build_app_store_set()
    write_rows(GOOGLE_OUTPUT, google_rows)
    write_rows(APP_STORE_OUTPUT, app_store_rows)

    google_counts = Counter(
        (row["period_bucket"], row["rating_band"])
        for row in google_rows
    )
    app_store_counts = Counter(row["rating_band"] for row in app_store_rows)

    print(f"Google Play sample: {len(google_rows)}")
    for key in (
        (period, band)
        for period in PERIOD_ORDER
        for band in RATING_BAND_ORDER
    ):
        print(f"  {key[0]}/{key[1]}: {google_counts[key]}")
    print(f"App Store set: {len(app_store_rows)}")
    for band in RATING_BAND_ORDER:
        print(f"  {band}: {app_store_counts[band]}")
    print(f"Wrote {GOOGLE_OUTPUT}")
    print(f"Wrote {APP_STORE_OUTPUT}")


if __name__ == "__main__":
    main()
