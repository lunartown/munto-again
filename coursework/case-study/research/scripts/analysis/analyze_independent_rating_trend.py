#!/usr/bin/env python3
"""Summarize rating trends without reusing prior topic coding.

The collected Google Play history is not treated as a complete census of review
volume. Counts describe only the collected corpus; they must not be used as a
proxy for user growth, revenue, or total review activity.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = RESEARCH_ROOT / "data/reviews/google_play/raw/reviews_history.csv"
OUTPUT_DIR = RESEARCH_ROOT / "data/reviews/reanalysis/trends"
YEAR_PATH = OUTPUT_DIR / "google_play_rating_by_year.csv"
QUARTER_PATH = OUTPUT_DIR / "google_play_rating_by_quarter.csv"


def summarize(rows: list[dict[str, str]], key_fn) -> list[dict[str, object]]:
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        buckets[key_fn(row)].append(row)

    output = []
    for period in sorted(buckets):
        period_rows = buckets[period]
        ratings = [int(row["rating"]) for row in period_rows]
        low = sum(rating <= 3 for rating in ratings)
        high = sum(rating >= 4 for rating in ratings)
        output.append(
            {
                "period": period,
                "collected_review_count": len(ratings),
                "average_rating": round(sum(ratings) / len(ratings), 3),
                "one_star_count": ratings.count(1),
                "low_1_to_3_count": low,
                "low_1_to_3_share": round(low / len(ratings), 4),
                "high_4_to_5_count": high,
                "high_4_to_5_share": round(high / len(ratings), 4),
                "interpretation_limit": "collected_corpus_only_not_review_volume_or_growth",
            }
        )
    return output


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    def parsed(row: dict[str, str]) -> datetime:
        return datetime.fromisoformat(row["review_date_utc"])

    year_rows = summarize(rows, lambda row: str(parsed(row).year))
    quarter_rows = summarize(
        rows,
        lambda row: f'{parsed(row).year}-Q{((parsed(row).month - 1) // 3) + 1}',
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write(YEAR_PATH, year_rows)
    write(QUARTER_PATH, quarter_rows)
    print(f"reviews={len(rows)}")
    print(f"year_output={YEAR_PATH}")
    print(f"quarter_output={QUARTER_PATH}")


if __name__ == "__main__":
    main()
