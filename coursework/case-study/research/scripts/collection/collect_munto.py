#!/usr/bin/env python3
"""Collect a privacy-minimized snapshot of public Munto socialing listings.

Only meeting-level fields needed for the research coding sheet are retained.
Participant profiles, host names, images, precise addresses, and chat URLs are
intentionally discarded.
"""

import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "https://api.munto.kr/api/web/v1"
USER_AGENT = "MuntoResearchSnapshot/1.0 (non-commercial research)"

# Direct romantic-intent terms are deliberately conservative. Broad words such
# as '인연' and '설렘' are not enough on their own, per the coding book.
C_DIRECT_PATTERNS = [
    r"소개팅", r"로테이션\s*미팅", r"쪽지\s*미팅", r"미팅\s*파티",
    r"이상형\s*매칭", r"커플\s*매칭", r"남녀\s*매칭", r"썸\s*매칭",
    r"솔로\s*파티", r"싱글\s*파티", r"연애\s*상대", r"결혼\s*상대",
]
SEX_RATIO_PATTERNS = [
    r"남(?:자|성)?\s*\d+\s*[:대/]\s*여(?:자|성)?\s*\d+",
    r"\d+\s*[:대]\s*\d+\s*(?:성비|남녀|미팅|만남)",
    r"성비\s*(?:균형|조절|맞춤|매칭)",
]
OPPOSITE_SEX_CONDITION_PATTERNS = [
    r"(?:남성|남자).{0,30}(?:키|직업|연봉|대기업|전문직)",
    r"(?:여성|여자).{0,30}(?:키|직업|외모|나이)",
    r"이성.{0,20}(?:조건|선호|어필)",
]
B_PATTERNS = [
    r"친목", r"친해져", r"뒤풀이", r"뒷풀이", r"네트워킹",
    r"2차", r"3차", r"n차", r"N차", r"사교",
]
AGE_PATTERNS = [
    r"(?:만\s*)?(\d{2})\s*(?:세|살)?\s*[~\-–]\s*(?:만\s*)?(\d{2})\s*(?:세|살)",
    r"(\d{2})\s*[~\-–]\s*(\d{2})\s*(?:년생)",
]


CSV_FIELDS = [
    "id", "수집일시_UTC", "플랫폼", "목록유형", "목록순번", "상세URL",
    "카테고리ID", "카테고리", "세부카테고리", "제목", "설명",
    "태그", "참가비", "정원", "현재참가자수", "지역", "시작일시_UTC",
    "모집방식", "소셜링종류", "클럽ID", "반복모임키",
    "남성정원", "여성정원", "성비명시", "성비판정근거",
    "최소연령", "최대연령", "연령제한", "연령판정근거",
    "활동구체성", "규칙기반_예비분류", "예비판정근거", "예비확신도",
    "최종분류", "최종판정근거", "코더", "검토상태",
]


def fetch_json(path: str, params: Optional[Dict[str, Any]] = None,
               retries: int = 3) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=20) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            if attempt == retries - 1:
                raise RuntimeError(f"Request failed after {retries} attempts: {url}: {error}")
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def first_match(patterns: Iterable[str], text: str) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0).replace("\n", " ")[:80]
    return None


def normalize_title(title: str) -> str:
    """Create a review aid for repeated sessions, not an analytical truth."""
    value = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", title)
    value = re.sub(r"\b\d{1,4}\s*(?:회|차|기)\b", " ", value)
    value = re.sub(r"\d{1,2}\s*[~\-–]\s*\d{1,2}", " ", value)
    value = re.sub(r"[0-9\W_]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip().lower()[:80]


def infer_age(detail: Dict[str, Any], title: str, text: str) -> Tuple[str, str, str]:
    min_age, max_age = detail.get("minAge"), detail.get("maxAge")
    if min_age is not None or max_age is not None:
        label = f"{min_age or ''}~{max_age or ''}세"
        return "Y", label, "API minAge/maxAge"
    for pattern in AGE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return "Y", f"{match.group(1)}~{match.group(2)}", match.group(0)
    # Birth-year shorthand such as 90-02 is only accepted in the title. This
    # prevents times (15~20), prices, and event dates from becoming age limits.
    birth_year = re.search(r"(?<!\d)([7-9]\d)\s*[~\-–]\s*([0-1]\d|[7-9]\d)(?!\d)", title)
    if birth_year:
        return "Y", f"{birth_year.group(1)}~{birth_year.group(2)}년생 추정", birth_year.group(0)
    restricted_wording = re.search(
        r"(?:20대|30대|40대).{0,8}(?:만|위주|중심|까지|초반|중반|후반)|"
        r"(?:나이|연령)\s*(?:제한|조건)(?!\s*(?:없|무))|\d{2}\s*년생",
        text,
    )
    no_limit = re.search(
        r"(?:나이|연령).{0,10}(?:제한.{0,4}(?:없|두지\s*않)|무관)",
        text,
    )
    if restricted_wording and not no_limit:
        evidence = restricted_wording.group(0)
        return "Y", "원문 확인", evidence
    return "N", "없음", ""


def infer_ratio(detail: Dict[str, Any], text: str) -> Tuple[str, str]:
    male_max = int(detail.get("maleMaximumCount") or 0)
    female_max = int(detail.get("femaleMaximumCount") or 0)
    if male_max > 0 or female_max > 0:
        return "Y", f"API 성별정원 남{male_max}/여{female_max}"
    evidence = first_match(SEX_RATIO_PATTERNS, text)
    return ("Y", evidence) if evidence else ("N", "")


def preliminary_code(text: str, ratio_explicit: str) -> Tuple[str, str, str]:
    evidence = first_match(C_DIRECT_PATTERNS, text)
    if evidence:
        return "C", f"직접표현: {evidence}", "상"
    if ratio_explicit == "Y":
        return "C", "성비 정원/조절 명시", "상"
    evidence = first_match(OPPOSITE_SEX_CONDITION_PATTERNS, text)
    if evidence:
        return "C", f"이성조건: {evidence}", "상"
    evidence = first_match(B_PATTERNS, text)
    if evidence:
        return "B", f"사교표현: {evidence}", "중"
    # The A/B boundary depends on activity specificity and should be reviewed by
    # a human. Marking it A here would falsely imply that judgment was made.
    return "미판정", "A/B 판정은 활동구체성 수기 검토 필요", "하"


def make_row(item: Dict[str, Any], detail: Dict[str, Any], collected_at: str,
             list_type: str, rank: int) -> Dict[str, Any]:
    title = str(detail.get("name") or item.get("name") or "")
    description = str(detail.get("introduce") or "").strip()
    tags = detail.get("tags") or item.get("tags") or []
    combined = "\n".join([title, " ".join(map(str, tags)), description,
                           str(detail.get("recruitQuestion") or "")])
    ratio, ratio_evidence = infer_ratio(detail, combined)
    age_yn, age_label, age_evidence = infer_age(detail, title, combined)
    preliminary, coding_evidence, confidence = preliminary_code(combined, ratio)
    category = detail.get("category") or {}
    category_tag = detail.get("categoryTag") or item.get("categoryTag") or {}
    club = detail.get("club") or {}
    club_id = club.get("id") or item.get("clubId") or ""
    normalized = normalize_title(title)
    repeat_key = f"club:{club_id}|title:{normalized}" if club_id else f"title:{normalized}"
    capacity = int(detail.get("maximumPerson") or item.get("maximumPerson") or 0)
    available = int(detail.get("availCount") or item.get("availCount") or 0)
    return {
        "id": detail.get("id") or item.get("id"),
        "수집일시_UTC": collected_at,
        "플랫폼": "문토",
        "목록유형": list_type,
        "목록순번": rank,
        "상세URL": f"https://www.munto.kr/detail-socialing?id={detail.get('id') or item.get('id')}",
        "카테고리ID": category.get("id") or item.get("categoryId") or "",
        "카테고리": category.get("name") or "",
        "세부카테고리": category_tag.get("name") or "",
        "제목": title,
        "설명": description,
        "태그": " | ".join(map(str, tags)),
        "참가비": detail.get("price") if detail.get("price") is not None else item.get("price", ""),
        "정원": capacity,
        "현재참가자수": max(0, capacity - available),
        "지역": detail.get("location") or item.get("location") or "",
        "시작일시_UTC": detail.get("startDate") or item.get("startDate") or "",
        "모집방식": detail.get("recruitType") or item.get("recruitType") or "",
        "소셜링종류": detail.get("socialingKind") or item.get("socialingKind") or "",
        "클럽ID": club_id,
        "반복모임키": repeat_key,
        "남성정원": detail.get("maleMaximumCount") or 0,
        "여성정원": detail.get("femaleMaximumCount") or 0,
        "성비명시": ratio,
        "성비판정근거": ratio_evidence,
        "최소연령": detail.get("minAge") if detail.get("minAge") is not None else "",
        "최대연령": detail.get("maxAge") if detail.get("maxAge") is not None else "",
        "연령제한": age_yn,
        "연령판정근거": age_evidence or age_label,
        "활동구체성": "",
        "규칙기반_예비분류": preliminary,
        "예비판정근거": coding_evidence,
        "예비확신도": confidence,
        "최종분류": "",
        "최종판정근거": "",
        "코더": "",
        "검토상태": "미검토",
    }


def collect(count: int, page_size: int, list_type: str, delay: float) -> List[Dict[str, Any]]:
    collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    items: List[Dict[str, Any]] = []
    seen = set()
    offset = 0
    while len(items) < count:
        page = fetch_json("/socialing/section", {"type": list_type, "offset": offset, "limit": page_size})
        page_items = page.get("socialings") or []
        if not page_items:
            break
        for item in page_items:
            item_id = item.get("id")
            if item_id and item_id not in seen:
                seen.add(item_id)
                items.append(item)
                if len(items) >= count:
                    break
        if not page.get("hasMore", False):
            break
        offset += page_size
        time.sleep(delay)

    rows = []
    total = len(items)
    for index, item in enumerate(items, start=1):
        try:
            detail = fetch_json(f"/socialing/{item['id']}")
        except RuntimeError as error:
            print(f"warning: skipping {item.get('id')}: {error}", file=sys.stderr)
            continue
        rows.append(make_row(item, detail, collected_at, list_type, index))
        if index == 1 or index % 20 == 0 or index == total:
            print(f"details: {index}/{total}", file=sys.stderr)
        time.sleep(delay)
    return rows


def write_csv(rows: List[Dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=200, help="number of listings (default: 200)")
    parser.add_argument("--page-size", type=int, default=20, help="section API page size (default: 20)")
    parser.add_argument("--type", default="default", dest="list_type", help="section type (default: default)")
    parser.add_argument("--delay", type=float, default=0.2, help="seconds between requests (default: 0.2)")
    parser.add_argument("--output", type=Path,
                        default=PROJECT_ROOT / "data/listings/raw/munto_socialings.csv")
    args = parser.parse_args()
    if args.count < 1 or args.page_size < 1 or args.delay < 0:
        parser.error("count/page-size must be positive and delay must be non-negative")
    rows = collect(args.count, args.page_size, args.list_type, args.delay)
    write_csv(rows, args.output)
    print(f"saved {len(rows)} rows to {args.output}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
