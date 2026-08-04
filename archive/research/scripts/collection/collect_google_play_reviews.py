#!/usr/bin/env python3
"""Collect a privacy-minimized public Google Play review sample.

Google does not publish a general read API for public reviews. This script uses
the same unauthenticated batchexecute review RPC as the public store page. The
RPC is undocumented and may change. Author names, profile IDs/images, and
developer replies are deliberately discarded.
"""

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RPC_URL = "https://play.google.com/_/PlayStoreUi/data/batchexecute"
STORE_URL = "https://play.google.com/store/apps/details?hl=ko&id=kr.munto.app"
RAW_FIELDS = [
    "review_id", "rating", "review_date_utc", "review_text", "thumbs_up",
    "app_version", "collected_date", "period_bucket", "source_url",
]
SAMPLE_FIELDS = RAW_FIELDS + ["sample_group", "selection_order"]


def period_bucket(iso_date: str) -> str:
    year = int(iso_date[:4])
    if year <= 2022:
        return "early"
    if year <= 2024:
        return "middle"
    return "recent"


def rpc_page(app_id: str, language: str, country: str, count: int,
             token: Optional[str], sort_order: int = 2) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    # sort: 1=helpfulness, 2=newest, 3=rating (Google's positional schema)
    inner = [None, None, [2, sort_order, [count, None, token]], [app_id, 7]]
    envelope = [[["UsvDTd", json.dumps(inner, separators=(",", ":"), ensure_ascii=False), None, "generic"]]]
    body = urlencode({"f.req": json.dumps(envelope, separators=(",", ":"), ensure_ascii=False)}).encode()
    url = f"{RPC_URL}?rpcids=UsvDTd&hl={language}&gl={country}"
    request = Request(url, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "User-Agent": "MuntoResearchReviewCollector/1.0",
    })
    with urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8")
    outer = json.loads(raw.split("\n", 2)[2])
    payload = json.loads(outer[0][2])
    items, token_block = payload[0], payload[1]
    collected = datetime.now(timezone.utc).date().isoformat()
    reviews = []
    for item in items:
        if not isinstance(item, list) or len(item) < 7 or not item[4]:
            continue
        timestamp = datetime.fromtimestamp(item[5][0], tz=timezone.utc).isoformat(timespec="seconds")
        version = item[10] if len(item) > 10 and isinstance(item[10], str) else ""
        reviews.append({
            "review_id": item[0],
            "rating": int(item[2]),
            "review_date_utc": timestamp,
            "review_text": str(item[4]).strip(),
            "thumbs_up": int(item[6] or 0),
            "app_version": version,
            "collected_date": collected,
            "period_bucket": period_bucket(timestamp),
            "source_url": STORE_URL,
        })
    next_token = token_block[1] if isinstance(token_block, list) and len(token_block) > 1 else None
    return reviews, next_token


def collect(app_id: str, max_reviews: int, delay: float) -> List[Dict[str, Any]]:
    all_reviews: List[Dict[str, Any]] = []
    seen = set()
    token = None
    while len(all_reviews) < max_reviews:
        page, token = rpc_page(app_id, "ko", "kr", min(40, max_reviews - len(all_reviews)), token)
        if not page:
            break
        for review in page:
            if review["review_id"] not in seen:
                seen.add(review["review_id"])
                all_reviews.append(review)
        low = sum(review["rating"] <= 3 for review in all_reviews)
        high = sum(review["rating"] >= 4 for review in all_reviews)
        print(f"collected={len(all_reviews)} low(1-3)={low} high(4-5)={high}")
        if low >= 50 and high >= 15:
            break
        if not token:
            break
        time.sleep(delay)
    return all_reviews


def write_csv(rows: List[Dict[str, Any]], path: Path, fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sample_reviews(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Newest-sort order is preserved. This avoids selecting only reviews whose
    # wording matches the research hypothesis.
    low = [dict(row, sample_group="1-3점", selection_order=i + 1)
           for i, row in enumerate(review for review in rows if review["rating"] <= 3)][:50]
    high = [dict(row, sample_group="4-5점_반례", selection_order=i + 1)
            for i, row in enumerate(review for review in rows if review["rating"] >= 4)][:15]
    return low + high


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default="kr.munto.app")
    parser.add_argument("--max-reviews", type=int, default=400)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--raw-output", type=Path,
                        default=PROJECT_ROOT / "data/reviews/google_play/raw/reviews_recent_120.csv")
    parser.add_argument("--sample-output", type=Path,
                        default=PROJECT_ROOT / "data/reviews/google_play/samples/review_sample_65.csv")
    args = parser.parse_args()
    rows = collect(args.app_id, args.max_reviews, args.delay)
    sample = sample_reviews(rows)
    write_csv(rows, args.raw_output, RAW_FIELDS)
    write_csv(sample, args.sample_output, SAMPLE_FIELDS)
    print(f"saved raw={len(rows)} sample={len(sample)}")
    return 0 if len([row for row in sample if row["rating"] <= 3]) >= 50 else 1


if __name__ == "__main__":
    raise SystemExit(main())
