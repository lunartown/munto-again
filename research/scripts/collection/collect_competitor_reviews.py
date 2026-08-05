#!/usr/bin/env python3
"""Collect Korean Google Play and App Store review histories for competitor apps."""

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RPC_URL = "https://play.google.com/_/PlayStoreUi/data/batchexecute"
APPLE_TEMPLATE = "https://itunes.apple.com/kr/rss/customerreviews/page={page}/id={app_id}/sortby={sort_key}/json"
GOOGLE_FIELDS = ["review_id", "rating", "review_date_utc", "review_text", "thumbs_up", "app_version", "collected_date", "source_url"]
APPLE_FIELDS = ["review_id", "rating", "review_date_utc", "review_text", "review_title", "app_version", "collected_date", "source_sort", "source_page", "source_url"]


def google_page(app_id: str, token: Optional[str]) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    inner = [None, None, [2, 2, [40, None, token]], [app_id, 7]]
    envelope = [[["UsvDTd", json.dumps(inner, separators=(",", ":"), ensure_ascii=False), None, "generic"]]]
    body = urlencode({"f.req": json.dumps(envelope, separators=(",", ":"), ensure_ascii=False)}).encode()
    url = f"{RPC_URL}?rpcids=UsvDTd&hl=ko&gl=kr"
    request = Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8", "User-Agent": "MuntoResearchReviewCollector/1.0"})
    with urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8")
    outer = json.loads(raw.split("\n", 2)[2])
    payload = json.loads(outer[0][2])
    items, token_block = payload[0], payload[1]
    collected = datetime.now(timezone.utc).date().isoformat()
    rows = []
    for item in items:
        if not isinstance(item, list) or len(item) < 7 or not item[4]:
            continue
        timestamp = datetime.fromtimestamp(item[5][0], tz=timezone.utc).isoformat(timespec="seconds")
        rows.append({"review_id": item[0], "rating": int(item[2]), "review_date_utc": timestamp, "review_text": str(item[4]).strip(), "thumbs_up": int(item[6] or 0), "app_version": item[10] if len(item) > 10 and isinstance(item[10], str) else "", "collected_date": collected, "source_url": f"https://play.google.com/store/apps/details?hl=ko&id={app_id}"})
    next_token = token_block[1] if isinstance(token_block, list) and len(token_block) > 1 else None
    return rows, next_token


def collect_google(app_id: str, until_date: str, max_reviews: int, delay: float) -> List[Dict[str, Any]]:
    rows, seen, token = [], set(), None
    while len(rows) < max_reviews:
        page, next_token = google_page(app_id, token)
        if not page:
            break
        for row in page:
            if row["review_id"] not in seen:
                seen.add(row["review_id"])
                rows.append(row)
        oldest = min(row["review_date_utc"][:10] for row in page)
        print(f"google app={app_id} reviews={len(rows)} oldest={oldest}", flush=True)
        token = next_token
        if oldest <= until_date or not token:
            break
        time.sleep(delay)
    rows.sort(key=lambda row: row["review_date_utc"], reverse=True)
    return rows


def apple_page(app_id: str, page: int, sort_key: str) -> List[Dict[str, Any]]:
    url = APPLE_TEMPLATE.format(page=page, app_id=app_id, sort_key=sort_key)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.load(response).get("feed", {}).get("entry", [])


def collect_apple(app_id: str, max_pages: int, delay: float) -> List[Dict[str, Any]]:
    rows, seen = [], set()
    collected = datetime.now(timezone.utc).date().isoformat()
    for sort_key in ("mostrecent", "mosthelpful"):
        for page in range(1, max_pages + 1):
            entries = apple_page(app_id, page, sort_key)
            new_count = 0
            for entry in entries:
                if "im:rating" not in entry:
                    continue
                review_id = entry["id"]["label"]
                if review_id in seen:
                    continue
                seen.add(review_id)
                rows.append({"review_id": review_id, "rating": int(entry["im:rating"]["label"]), "review_date_utc": datetime.fromisoformat(entry["updated"]["label"]).astimezone(timezone.utc).isoformat(), "review_text": entry["content"]["label"].strip(), "review_title": entry["title"]["label"].strip(), "app_version": entry.get("im:version", {}).get("label", ""), "collected_date": collected, "source_sort": sort_key, "source_page": page, "source_url": f"https://apps.apple.com/kr/app/id{app_id}"})
                new_count += 1
            print(f"apple app={app_id} sort={sort_key} page={page} new_reviews={new_count} total={len(rows)}", flush=True)
            if new_count == 0:
                break
            if page < max_pages:
                time.sleep(delay)
    rows.sort(key=lambda row: row["review_date_utc"], reverse=True)
    return rows


def write_csv(path: Path, fields: List[str], rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--google-app-id", required=True)
    parser.add_argument("--apple-app-id", required=True)
    parser.add_argument("--until-date", default="2021-01-01")
    parser.add_argument("--google-max-reviews", type=int, default=6000)
    parser.add_argument("--apple-max-pages", type=int, default=10)
    parser.add_argument("--delay", type=float, default=0.25)
    args = parser.parse_args()
    root = PROJECT_ROOT / "research/data/reviews" / args.slug
    google = collect_google(args.google_app_id, args.until_date, args.google_max_reviews, args.delay)
    apple = collect_apple(args.apple_app_id, args.apple_max_pages, args.delay)
    write_csv(root / "google_play/raw/reviews_history.csv", GOOGLE_FIELDS, google)
    write_csv(root / "app_store/raw/reviews_history.csv", APPLE_FIELDS, apple)
    print(f"saved slug={args.slug} google_play={len(google)} app_store={len(apple)} root={root}")
    return 0 if google and apple else 1


if __name__ == "__main__":
    raise SystemExit(main())
