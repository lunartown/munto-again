#!/usr/bin/env python3
"""과거 다음카페 검색 후보에서 공개 원문만 복구한다.

검색 미리보기는 URL 후보를 찾는 용도로만 사용한다. 모바일 원문이 HTTP 200을
반환하고 ``#article`` 본문이 실제로 존재하는 글만 full-post 파일에 기록한다.
권한 제한·삭제·본문 미확보 글은 unavailable 파일에 URL과 실패 사유만 남긴다.
"""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FULL_POSTS = DATA / "daum-full-posts.jsonl"
UNAVAILABLE = DATA / "daum-unavailable.jsonl"
SOURCE_REVISION = "756e30d"
SOURCE_PATH = "tools/somoim-scraper/data/records.jsonl"
TIMEOUT = 20
DELAY = 0.5
EXACT_APP = re.compile(r"소모임\s*(?:앱|어플|애플리케이션)", re.I)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def load_snapshot() -> list[dict]:
    result = subprocess.run(
        ["git", "show", f"{SOURCE_REVISION}:{SOURCE_PATH}"],
        cwd=HERE,
        check=True,
        capture_output=True,
        text=True,
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def candidate_rows() -> list[dict]:
    rows = []
    seen = set()
    for row in load_snapshot():
        if row.get("site") != "daum" or row.get("url") in seen:
            continue
        preview = "\n".join(str(row.get(key, "")) for key in ("title", "body"))
        if not EXACT_APP.search(preview):
            continue
        seen.add(row["url"])
        rows.append(row)
    return rows


def mobile_url(url: str) -> str:
    parsed = urlparse(url)
    return f"https://m.cafe.daum.net{parsed.path}"


def text_of(node) -> str:
    if not node:
        return ""
    text = node.get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def meta(soup: BeautifulSoup, prop: str) -> str:
    node = soup.find("meta", property=prop)
    return (node.get("content", "") if node else "").strip()


def classify_restriction(soup: BeautifulSoup, status: int) -> str:
    page_text = soup.get_text(" ", strip=True)
    if "운영자 이상 읽기 가능" in page_text:
        return "operator_only"
    if "카페 가입 후" in page_text or "회원만 읽" in page_text:
        return "members_only"
    if "해당 게시글이 삭제" in page_text or "존재하지 않" in page_text:
        return "deleted"
    if status == 403:
        return "restricted"
    if status == 404:
        return "not_found"
    return "body_unavailable"


def extract_date(soup: BeautifulSoup) -> str:
    info = text_of(soup.select_one(".txt_info"))
    match = re.search(r"작성시간\s*([^\n|]+)", info)
    return match.group(1).strip() if match else ""


def fetch(session: requests.Session, candidate: dict) -> tuple[str, dict]:
    source_url = candidate["url"]
    url = mobile_url(source_url)
    try:
        response = session.get(url, timeout=TIMEOUT)
    except requests.RequestException as error:
        return "retry", {
            "site": "daum",
            "url": source_url,
            "access": "request_error",
            "error": type(error).__name__,
        }

    soup = BeautifulSoup(response.text, "lxml")
    article = soup.select_one("#article")
    body = text_of(article)
    title = meta(soup, "og:title")
    if response.status_code == 200 and article and len(body) >= 20 and title:
        return "ok", {
            "title": title,
            "body": body,
            "comments": [],
            "date": extract_date(soup) or candidate.get("date", ""),
            "source_kind": "full_post",
            "cafe": meta(soup, "og:article:author") or candidate.get("cafe", ""),
            "access": "public",
            "site": "daum",
            "url": source_url,
            "score": candidate.get("score", 0),
            "query": candidate.get("query", ""),
        }

    return "unavailable", {
        "site": "daum",
        "url": source_url,
        "title": candidate.get("title", ""),
        "access": classify_restriction(soup, response.status_code),
        "http_status": response.status_code,
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=DELAY)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    candidates = candidate_rows()
    if args.limit:
        candidates = candidates[: args.limit]

    session = requests.Session()
    session.headers.update(HEADERS)
    full_posts = []
    unavailable = []
    retries = []

    for index, candidate in enumerate(candidates, 1):
        state, row = fetch(session, candidate)
        if state == "ok":
            full_posts.append(row)
        elif state == "retry":
            retries.append(candidate)
        else:
            unavailable.append(row)
        if index % 25 == 0 or index == len(candidates):
            print(
                f"{index}/{len(candidates)} 공개 {len(full_posts)} / "
                f"미확보 {len(unavailable)} / 재시도 {len(retries)}",
                flush=True,
            )
        time.sleep(args.delay)

    for candidate in retries:
        time.sleep(max(args.delay, 1.0))
        state, row = fetch(session, candidate)
        if state == "ok":
            full_posts.append(row)
        else:
            if state == "retry":
                row = {
                    "site": "daum",
                    "url": candidate["url"],
                    "title": candidate.get("title", ""),
                    "access": "request_error_after_retry",
                }
            unavailable.append(row)

    DATA.mkdir(parents=True, exist_ok=True)
    write_jsonl(FULL_POSTS, full_posts)
    write_jsonl(UNAVAILABLE, unavailable)
    print(
        f"완료: 후보 {len(candidates)} / 공개 원문 {len(full_posts)} / "
        f"미확보 {len(unavailable)}"
    )


if __name__ == "__main__":
    main()
