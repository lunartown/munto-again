#!/usr/bin/env python3
"""소모임 웹 공개 목록을 커서 끝까지 순회해 SQLite에 저장한다.

개별 모임 상세 페이지는 요청하지 않는다. 목록 응답에 포함된 gid와 요약 필드만 저장한다.
"""

import argparse
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


HERE = Path(__file__).resolve().parent
DEFAULT_DB = HERE / "data" / "somoim-groups.sqlite3"
API_URL = "https://www.somoim.co.kr/api/groups/category"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS collection_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    loc TEXT NOT NULL,
    loc2 TEXT,
    category_id TEXT NOT NULL,
    query_limit INTEGER NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    record_count INTEGER NOT NULL DEFAULT 0,
    duplicate_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS groups (
    gid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description_excerpt TEXT NOT NULL DEFAULT '',
    category_id TEXT,
    category2_id TEXT,
    category22_id TEXT,
    keyword TEXT,
    raw_keyword TEXT,
    primary_keyword_id TEXT,
    loc TEXT,
    loc2 TEXT,
    loc1_name TEXT,
    loc2_name TEXT,
    age_level INTEGER,
    member_count INTEGER,
    image_timestamp INTEGER,
    group_type INTEGER,
    created_at TEXT,
    updated_at TEXT,
    open_event_count INTEGER,
    next_event_date INTEGER,
    next_event_time INTEGER,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS group_listings (
    run_id INTEGER NOT NULL,
    gid TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    position_in_page INTEGER NOT NULL,
    overall_position INTEGER NOT NULL,
    response_s_t INTEGER,
    response_ran INTEGER,
    response_aran INTEGER,
    PRIMARY KEY (run_id, gid),
    FOREIGN KEY (run_id) REFERENCES collection_runs(id),
    FOREIGN KEY (gid) REFERENCES groups(gid)
);

CREATE INDEX IF NOT EXISTS idx_groups_location ON groups(loc, loc2);
CREATE INDEX IF NOT EXISTS idx_groups_category ON groups(category_id, category2_id);
CREATE INDEX IF NOT EXISTS idx_groups_keyword ON groups(keyword);
CREATE INDEX IF NOT EXISTS idx_listings_run_position
    ON group_listings(run_id, overall_position);
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--loc", default="010000", help="1단계 지역 코드 (기본: 서울)")
    parser.add_argument("--loc2", default=None, help="2단계 지역 코드; 전체 수집 시 생략")
    parser.add_argument("--category", default="0", help="대분류 코드 (기본: 전체)")
    parser.add_argument("--limit", type=int, default=100, choices=range(1, 101))
    parser.add_argument("--delay", type=float, default=0.3)
    parser.add_argument("--max-pages", type=int, default=100)
    return parser.parse_args()


def connect(db_path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.executescript(SCHEMA)
    return connection


def insert_run(connection, args):
    cursor = connection.execute(
        """
        INSERT INTO collection_runs
            (started_at, status, loc, loc2, category_id, query_limit)
        VALUES (?, 'running', ?, ?, ?, ?)
        """,
        (utc_now(), args.loc, args.loc2, args.category, args.limit),
    )
    connection.commit()
    return cursor.lastrowid


def upsert_group(connection, group, observed_at):
    next_event = group.get("next_event") or {}
    gid = group.get("gid") or group.get("id")
    if not gid:
        raise ValueError("목록 레코드에 gid와 id가 모두 없습니다")

    connection.execute(
        """
        INSERT INTO groups (
            gid, name, description_excerpt, category_id, category2_id,
            category22_id, keyword, raw_keyword, primary_keyword_id,
            loc, loc2, loc1_name, loc2_name, age_level, member_count,
            image_timestamp, group_type, created_at, updated_at,
            open_event_count, next_event_date, next_event_time,
            first_seen_at, last_seen_at, raw_json
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?
        )
        ON CONFLICT(gid) DO UPDATE SET
            name = excluded.name,
            description_excerpt = excluded.description_excerpt,
            category_id = excluded.category_id,
            category2_id = excluded.category2_id,
            category22_id = excluded.category22_id,
            keyword = excluded.keyword,
            raw_keyword = excluded.raw_keyword,
            primary_keyword_id = excluded.primary_keyword_id,
            loc = excluded.loc,
            loc2 = excluded.loc2,
            loc1_name = excluded.loc1_name,
            loc2_name = excluded.loc2_name,
            age_level = excluded.age_level,
            member_count = excluded.member_count,
            image_timestamp = excluded.image_timestamp,
            group_type = excluded.group_type,
            created_at = excluded.created_at,
            updated_at = excluded.updated_at,
            open_event_count = excluded.open_event_count,
            next_event_date = excluded.next_event_date,
            next_event_time = excluded.next_event_time,
            last_seen_at = excluded.last_seen_at,
            raw_json = excluded.raw_json
        """,
        (
            gid,
            group.get("gn") or "",
            group.get("ge") or "",
            group.get("it"),
            group.get("it2"),
            group.get("it22"),
            group.get("keyword"),
            group.get("raw_keyword"),
            group.get("primary_keyword_id"),
            group.get("loc"),
            group.get("loc2"),
            group.get("loc1n"),
            group.get("loc2n"),
            group.get("al"),
            group.get("gmc"),
            group.get("im_t"),
            group.get("gt"),
            group.get("created"),
            group.get("updated"),
            group.get("open_event_count"),
            next_event.get("e_d"),
            next_event.get("e_t"),
            observed_at,
            observed_at,
            json.dumps(group, ensure_ascii=False, separators=(",", ":")),
        ),
    )
    return gid


def collect(connection, run_id, args):
    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 somoim-public-list-research/1.0",
        }
    )
    payload = {
        "loc": args.loc,
        "it": args.category,
        "wql": args.limit,
    }
    if args.loc2:
        payload["loc2"] = args.loc2

    seen = set()
    duplicate_count = 0
    data_page_count = 0

    for page_number in range(1, args.max_pages + 1):
        response = session.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        body = response.json()
        groups = body.get("l") or []
        observed_at = utc_now()

        if groups:
            data_page_count += 1

        with connection:
            for position, group in enumerate(groups, start=1):
                gid = upsert_group(connection, group, observed_at)
                if gid in seen:
                    duplicate_count += 1
                else:
                    seen.add(gid)
                connection.execute(
                    """
                    INSERT OR IGNORE INTO group_listings (
                        run_id, gid, page_number, position_in_page,
                        overall_position, response_s_t, response_ran, response_aran
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        gid,
                        page_number,
                        position,
                        (page_number - 1) * args.limit + position,
                        body.get("s_t"),
                        body.get("ran"),
                        body.get("aran"),
                    ),
                )

        print(
            f"page={page_number} rows={len(groups)} unique={len(seen)} "
            f"ran={body.get('ran')} eof={body.get('eof')}"
        )

        if body.get("eof") == "Y":
            return data_page_count, len(seen), duplicate_count
        if not groups:
            raise RuntimeError("빈 목록이 반환됐지만 eof가 Y가 아닙니다")

        payload.update(
            {
                "s_t": body.get("s_t"),
                "ran": body.get("ran"),
                "aran": body.get("aran"),
            }
        )
        time.sleep(max(args.delay, 0))

    raise RuntimeError(f"max-pages={args.max_pages} 안에 eof에 도달하지 못했습니다")


def main():
    args = parse_args()
    connection = connect(args.db)
    run_id = insert_run(connection, args)
    try:
        pages, records, duplicates = collect(connection, run_id, args)
    except Exception as error:
        connection.execute(
            """
            UPDATE collection_runs
            SET finished_at = ?, status = 'failed', error_message = ?
            WHERE id = ?
            """,
            (utc_now(), str(error), run_id),
        )
        connection.commit()
        raise
    else:
        connection.execute(
            """
            UPDATE collection_runs
            SET finished_at = ?, status = 'complete', page_count = ?,
                record_count = ?, duplicate_count = ?
            WHERE id = ?
            """,
            (utc_now(), pages, records, duplicates, run_id),
        )
        connection.commit()
        print(
            f"complete run_id={run_id} pages={pages} records={records} "
            f"duplicates={duplicates} db={args.db}"
        )
    finally:
        connection.close()


if __name__ == "__main__":
    main()
