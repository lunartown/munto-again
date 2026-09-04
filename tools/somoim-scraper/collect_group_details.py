#!/usr/bin/env python3
"""선택한 소모임 공개 상세 페이지의 소개와 정모 정보를 SQLite에 저장한다."""

import argparse
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


HERE = Path(__file__).resolve().parent
DEFAULT_DB = HERE / "data" / "somoim-groups.sqlite3"
DETAIL_URL = "https://www.somoim.co.kr/{gid}"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS group_details (
    gid TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    image_url TEXT NOT NULL,
    source_url TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    FOREIGN KEY (gid) REFERENCES groups(gid)
);

CREATE TABLE IF NOT EXISTS group_events (
    eid TEXT PRIMARY KEY,
    gid TEXT NOT NULL,
    name TEXT NOT NULL,
    event_date INTEGER,
    event_time INTEGER,
    location TEXT,
    cost TEXT,
    max_members INTEGER,
    current_members INTEGER,
    image_url TEXT,
    collected_at TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    FOREIGN KEY (gid) REFERENCES groups(gid)
);

CREATE INDEX IF NOT EXISTS idx_group_events_gid_date
ON group_events(gid, event_date, event_time);
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("gids", nargs="+", help="수집할 모임 gid")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--inspect", action="store_true")
    return parser.parse_args()


def extract_group_info(html):
    chunks = []
    soup = BeautifulSoup(html, "html.parser")
    prefix = "self.__next_f.push("
    for script in soup.find_all("script"):
        text = script.string or script.get_text()
        if not text.startswith(prefix) or not text.endswith(")"):
            continue
        record = json.loads(text[len(prefix) : -1])
        if record[0] == 1 and isinstance(record[1], str):
            chunks.append(record[1])

    payload = "".join(chunks)
    marker = '"groupInfoData":'
    start = payload.find(marker)
    if start < 0:
        raise ValueError("groupInfoData를 찾지 못했습니다")
    value_start = start + len(marker)
    info, _ = json.JSONDecoder().raw_decode(payload[value_start:])
    return info


def event_list(info):
    for key, value in info.items():
        if isinstance(value, list) and value and isinstance(value[0], dict) and "eid" in value[0]:
            return value
    return []


def save_detail(connection, gid, info, collected_at):
    group = info["group"]
    events = event_list(info)
    image_url = group.get("groupImgUrl") or f"https://d228e474i2d5yf.cloudfront.net/{gid}.png"
    detail_raw = {
        "group": {
            key: group.get(key)
            for key in ("gid", "gn", "ge", "loc1n", "loc2n", "gmc", "im_t")
        },
        "events": [
            {
                key: event.get(key)
                for key in ("eid", "en", "e_d", "e_t", "el", "ee", "emm", "enum", "imgUrl")
            }
            for event in events
        ],
    }
    connection.execute(
        """
        INSERT INTO group_details (gid, description, image_url, source_url, collected_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(gid) DO UPDATE SET
            description = excluded.description,
            image_url = excluded.image_url,
            source_url = excluded.source_url,
            collected_at = excluded.collected_at,
            raw_json = excluded.raw_json
        """,
        (
            gid,
            group.get("ge") or "",
            image_url,
            DETAIL_URL.format(gid=gid),
            collected_at,
            json.dumps(detail_raw, ensure_ascii=False, separators=(",", ":")),
        ),
    )
    connection.execute("DELETE FROM group_events WHERE gid = ?", (gid,))
    for event in events:
        connection.execute(
            """
            INSERT INTO group_events (
                eid, gid, name, event_date, event_time, location, cost,
                max_members, current_members, image_url, collected_at, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["eid"],
                gid,
                event.get("en") or "",
                event.get("e_d"),
                event.get("e_t"),
                event.get("el"),
                event.get("ee"),
                event.get("emm"),
                len(event.get("jms") or []),
                event.get("imgUrl"),
                collected_at,
                json.dumps(
                    {key: event.get(key) for key in ("eid", "en", "e_d", "e_t", "el", "ee", "emm", "enum", "imgUrl")},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            ),
        )
    return len(events)


def main():
    args = parse_args()
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 somoim-public-detail-research/1.0"})
    connection = sqlite3.connect(args.db)
    connection.executescript(SCHEMA)
    try:
        for index, gid in enumerate(args.gids):
            response = session.get(DETAIL_URL.format(gid=gid), timeout=30)
            response.raise_for_status()
            info = extract_group_info(response.text)
            if args.inspect:
                print(json.dumps({"gid": gid, "keys": list(info), "group_keys": list(info["group"])}, ensure_ascii=False))
                continue
            collected_at = utc_now()
            with connection:
                count = save_detail(connection, gid, info, collected_at)
            print(f"gid={gid} events={count}")
            if index + 1 < len(args.gids):
                time.sleep(max(args.delay, 0))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
