#!/usr/bin/env python3
"""Build the current-review corpus and a balanced screening pilot.

Only the raw Google Play review history is read. Existing coded reviews,
clusters, and findings are intentionally excluded.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = RESEARCH_ROOT / "data/reviews/google_play/raw/reviews_history.csv"
OUTPUT_DIR = RESEARCH_ROOT / "data/reviews/reanalysis/current"
CORPUS_PATH = OUTPUT_DIR / "google_play_current_12m_120.csv"
PILOT_PATH = OUTPUT_DIR / "screening_pilot_20.csv"
SCREENING_PATH = OUTPUT_DIR / "screening_decisions_120.csv"

START = datetime.fromisoformat("2025-07-30T00:00:00+00:00")
END = datetime.fromisoformat("2026-07-30T23:59:59+00:00")
BURST_MONTH = "2026-04"
PILOT_PER_COHORT = 10
ORDER_SEED = "munto-current-review-screening-v1"

EXCLUDED_REVIEWS = {
    "CUR049": (
        "평가 대상·가치·불편·행동·결과가 드러나지 않는 "
        "일반 긍정 표현('좋습니다ㅎㅎ')"
    ),
}
EVENT_DECLARED_REVIEWS = {"CUR085", "CUR091"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def stable_key(review_id: str) -> str:
    value = f"{ORDER_SEED}:{review_id}".encode()
    return hashlib.sha256(value).hexdigest()


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    raw_rows = read_rows(RAW_PATH)
    current_rows = [
        row
        for row in raw_rows
        if START <= datetime.fromisoformat(row["review_date_utc"]) <= END
    ]
    current_rows.sort(
        key=lambda row: (row["review_date_utc"], row["review_id"]),
        reverse=True,
    )

    corpus = []
    for index, row in enumerate(current_rows, start=1):
        corpus.append(
            {
                "corpus_id": f"CUR{index:03d}",
                "review_id": row["review_id"],
                "review_date_utc": row["review_date_utc"],
                "month": row["review_date_utc"][:7],
                "cohort": (
                    "april_2026_burst"
                    if row["review_date_utc"].startswith(BURST_MONTH)
                    else "other_recent_months"
                ),
                "rating": row["rating"],
                "review_text": row["review_text"],
                "thumbs_up": row["thumbs_up"],
                "app_version": row["app_version"],
                "source_url": row["source_url"],
            }
        )

    pilot = []
    for cohort in ("april_2026_burst", "other_recent_months"):
        cohort_rows = [row for row in corpus if row["cohort"] == cohort]
        cohort_rows.sort(key=lambda row: stable_key(row["review_id"]))
        for row in cohort_rows[:PILOT_PER_COHORT]:
            pilot.append(
                {
                    **row,
                    "inclusion_status": "",
                    "exclusion_reason": "",
                    "screening_note": "",
                }
            )

    screening = []
    for row in corpus:
        flags = []
        if row["cohort"] == "april_2026_burst":
            flags.append("april_2026_burst")
        if row["corpus_id"] in EVENT_DECLARED_REVIEWS:
            flags.append("event_declared")

        excluded_reason = EXCLUDED_REVIEWS.get(row["corpus_id"], "")
        screening.append(
            {
                "corpus_id": row["corpus_id"],
                "review_id": row["review_id"],
                "cohort": row["cohort"],
                "rating": row["rating"],
                "inclusion_status": (
                    "exclude" if excluded_reason else "include"
                ),
                "special_flag": "|".join(flags),
                "exclusion_reason": excluded_reason,
                "screening_note": (
                    "근거 구체성은 의미 단위 카드별로 판정"
                    if not excluded_reason
                    else "별점·시계열 통계에는 유지"
                ),
            }
        )

    write_rows(CORPUS_PATH, corpus)
    write_rows(PILOT_PATH, pilot)
    write_rows(SCREENING_PATH, screening)

    counts = Counter(row["cohort"] for row in corpus)
    print(f"Current corpus: {len(corpus)}")
    for cohort in ("april_2026_burst", "other_recent_months"):
        print(f"  {cohort}: {counts[cohort]}")
    print(f"Screening pilot: {len(pilot)}")
    print(
        "Screening decisions: "
        f"{sum(row['inclusion_status'] == 'include' for row in screening)} "
        "include, "
        f"{sum(row['inclusion_status'] == 'exclude' for row in screening)} "
        "exclude"
    )
    print(f"Wrote {CORPUS_PATH}")
    print(f"Wrote {PILOT_PATH}")
    print(f"Wrote {SCREENING_PATH}")


if __name__ == "__main__":
    main()
