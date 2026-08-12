#!/usr/bin/env python3
"""Split yearly review stats into review-event periods and normal periods."""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUTS = {
    "Google Play": PROJECT_ROOT / "archive/research/data/reviews/google_play/raw/reviews_history.csv",
    "App Store": PROJECT_ROOT / "research/data/reviews/app_store/raw/reviews_history.csv",
}
OUTPUT = PROJECT_ROOT / "research/data/reviews/summaries/review_event_period_comparison.csv"
FIELDS = [
    "platform",
    "year",
    "period_type",
    "review_count",
    "average_rating",
    "low_rating_share",
]

# 사용자가 확인한 리뷰 이벤트 운영 기간(참여 조건은 회차마다 다를 수 있음)
EVENT_WINDOWS = [
    ("2022-11-11", "2022-12-04"),
    ("2022-12-19", "2023-01-25"),
    ("2025-11-27", "2025-12-03"),
    ("2025-12-05", "2025-12-11"),
    ("2026-04-10", "2026-04-16"),
    ("2026-04-22", "2026-04-28"),
]


def in_event_window(date):
    return any(start <= date <= end for start, end in EVENT_WINDOWS)


def load_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            (row["review_date_utc"][:10], int(row["rating"]))
            for row in csv.DictReader(handle)
        ]


def summarize(ratings):
    if not ratings:
        return 0, None, None
    count = len(ratings)
    average = sum(ratings) / count
    low_share = sum(1 for r in ratings if r <= 3) / count
    return count, average, low_share


def build_rows(platform, path):
    records = load_rows(path)
    years = sorted({date[:4] for date, _ in records})
    output = []
    for year in years:
        normal = [r for date, r in records if date[:4] == year and not in_event_window(date)]
        event = [r for date, r in records if date[:4] == year and in_event_window(date)]
        for period_type, ratings in (("평시", normal), ("이벤트", event)):
            count, average, low_share = summarize(ratings)
            output.append(
                {
                    "platform": platform,
                    "year": year,
                    "period_type": period_type,
                    "review_count": count,
                    "average_rating": round(average, 2) if average is not None else "",
                    "low_rating_share": round(low_share, 4) if low_share is not None else "",
                }
            )
    return output


def main():
    rows = [row for platform, path in INPUTS.items() for row in build_rows(platform, path)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved={len(rows)} output={OUTPUT}")


if __name__ == "__main__":
    main()
