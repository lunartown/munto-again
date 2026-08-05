#!/usr/bin/env python3
"""Collect public Munto socialing list snapshots into raw JSON and SQLite.

The default is one page so an accidental invocation does not crawl the whole
catalog. Use ``--max-pages 0`` to follow ``hasMore`` until the endpoint ends.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://api.munto.kr/api/web/v1/socialing/section"
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "socialing"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch_page(offset: int, limit: int, timeout: int) -> dict:
    query = urlencode({"type": "recent", "offset": offset, "limit": limit})
    request = Request(
        f"{API_URL}?{query}",
        headers={
            "Accept": "application/json",
            "Origin": "https://www.munto.kr",
            "Referer": "https://www.munto.kr/",
            "User-Agent": "munto-research-socialing-collector/1.0",
            "X-User-Locale": "ko",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS crawl_runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            requested_limit INTEGER NOT NULL,
            page_count INTEGER NOT NULL DEFAULT 0,
            item_count INTEGER NOT NULL DEFAULT 0,
            success INTEGER NOT NULL DEFAULT 0,
            error TEXT
        );
        CREATE TABLE IF NOT EXISTS socialing_snapshots (
            run_id TEXT NOT NULL REFERENCES crawl_runs(run_id),
            observed_at TEXT NOT NULL,
            offset INTEGER NOT NULL,
            list_rank INTEGER NOT NULL,
            socialing_id INTEGER NOT NULL,
            status TEXT,
            name TEXT,
            category_id INTEGER,
            category_name TEXT,
            socialing_type TEXT,
            created_at TEXT,
            start_date TEXT,
            location TEXT,
            price INTEGER,
            maximum_person INTEGER,
            minimum_person INTEGER,
            avail_count INTEGER,
            request_count INTEGER,
            participant_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,
            club_id INTEGER,
            content_hash TEXT NOT NULL,
            raw_json TEXT NOT NULL,
            PRIMARY KEY (run_id, socialing_id)
        );
        CREATE INDEX IF NOT EXISTS idx_snapshots_socialing_time
            ON socialing_snapshots(socialing_id, observed_at);
        """
    )


def as_int(value):
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def save_page(connection, run_id: str, observed_at: str, offset: int, items: list[dict]) -> None:
    rows = []
    for rank, item in enumerate(items, start=offset + 1):
        raw = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        category = item.get("categoryTag") or {}
        participants = item.get("participants") or []
        rows.append(
            (
                run_id, observed_at, offset, rank, as_int(item.get("id")), item.get("status"),
                item.get("name"), as_int(item.get("categoryId")), category.get("name"),
                item.get("type"), item.get("createdAt"), item.get("startDate"), item.get("location"),
                as_int(item.get("price")), as_int(item.get("maximumPerson")),
                as_int(item.get("minimumPerson")), as_int(item.get("availCount")),
                as_int(item.get("requestCount")), len(participants), as_int(item.get("likeCount")),
                as_int(item.get("commentCount")), as_int(item.get("clubId")),
                hashlib.sha256(raw.encode()).hexdigest(), raw,
            )
        )
    connection.executemany(
        """INSERT OR REPLACE INTO socialing_snapshots
        (run_id, observed_at, offset, list_rank, socialing_id, status, name,
         category_id, category_name, socialing_type, created_at, start_date,
         location, price, maximum_person, minimum_person, avail_count,
         request_count, participant_count, like_count, comment_count, club_id,
         content_hash, raw_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )


def collect(args) -> int:
    data_dir = Path(args.data_dir)
    raw_dir = data_dir / "raw" / datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    raw_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "socialing.sqlite"
    run_id, started_at = str(uuid.uuid4()), utc_now()
    with sqlite3.connect(db_path) as connection:
        init_db(connection)
        connection.execute(
            "INSERT INTO crawl_runs(run_id, started_at, requested_limit) VALUES (?,?,?)",
            (run_id, started_at, args.limit),
        )
        offset = args.offset
        pages = items_total = 0
        try:
            while args.max_pages == 0 or pages < args.max_pages:
                payload = fetch_page(offset, args.limit, args.timeout)
                items = payload.get("socialings") or []
                observed_at = utc_now()
                raw_path = raw_dir / f"offset_{offset:05d}.json.gz"
                with gzip.open(raw_path, "wt", encoding="utf-8") as raw_file:
                    json.dump(payload, raw_file, ensure_ascii=False, indent=2)
                save_page(connection, run_id, observed_at, offset, items)
                pages += 1
                items_total += len(items)
                if not payload.get("hasMore") or not items:
                    break
                offset += args.limit
                if args.delay:
                    time.sleep(args.delay)
            connection.execute(
                "UPDATE crawl_runs SET completed_at=?, page_count=?, item_count=?, success=1 WHERE run_id=?",
                (utc_now(), pages, items_total, run_id),
            )
            connection.commit()
        except Exception as error:
            connection.execute(
                "UPDATE crawl_runs SET completed_at=?, page_count=?, item_count=?, error=? WHERE run_id=?",
                (utc_now(), pages, items_total, repr(error), run_id),
            )
            connection.commit()
            raise
    print(f"run_id={run_id} pages={pages} items={items_total} db={db_path} raw={raw_dir}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max-pages", type=int, default=1, help="0 means until hasMore is false")
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--timeout", type=int, default=30)
    return collect(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
