#!/usr/bin/env python3
"""Collect Google Play reviews newest-first until the 2021 launch period."""

import argparse
import time
from pathlib import Path

from collect_google_play_reviews import RAW_FIELDS, rpc_page, write_csv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default="kr.munto.app")
    parser.add_argument("--until-date", default="2021-01-01")
    parser.add_argument("--max-reviews", type=int, default=6000)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--output", type=Path,
                        default=PROJECT_ROOT / "data/reviews/google_play/raw/reviews_history.csv")
    args = parser.parse_args()

    rows = []
    seen = set()
    token = None
    page_number = 0
    reached_target = False
    while len(rows) < args.max_reviews:
        page_number += 1
        last_error = None
        for attempt in range(3):
            try:
                page, next_token = rpc_page(
                    args.app_id, "ko", "kr", min(40, args.max_reviews - len(rows)), token, 2
                )
                break
            except IndexError:
                # The undocumented endpoint returns an empty positional payload
                # instead of a conventional end token after the oldest review.
                page, next_token = [], None
                break
            except Exception as error:  # transient HTTP/RPC errors
                last_error = error
                time.sleep(1 + attempt * 2)
        else:
            raise last_error

        if not page:
            token = next_token
            break
        for review in page:
            if review["review_id"] not in seen:
                seen.add(review["review_id"])
                rows.append(review)
        oldest = min(review["review_date_utc"] for review in page)[:10]
        if page_number == 1 or page_number % 10 == 0:
            print(f"page={page_number} reviews={len(rows)} oldest={oldest}", flush=True)
            write_csv(rows, args.output, RAW_FIELDS)
        if oldest <= args.until_date:
            reached_target = True
            break
        token = next_token
        if not token:
            break
        time.sleep(args.delay)

    rows.sort(key=lambda row: row["review_date_utc"], reverse=True)
    write_csv(rows, args.output, RAW_FIELDS)
    oldest = rows[-1]["review_date_utc"][:10] if rows else ""
    print(f"saved={len(rows)} oldest={oldest} reached_target={reached_target}")
    return 0 if rows and (reached_target or not token) else 1


if __name__ == "__main__":
    raise SystemExit(main())
