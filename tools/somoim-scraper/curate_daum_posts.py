#!/usr/bin/env python3
"""전수 검토한 다음카페 공개 원문을 정성 코퍼스에 반영한다."""

import csv
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FULL_POSTS = DATA / "daum-full-posts.jsonl"
RECORDS = DATA / "records.jsonl"
REVIEW = DATA / "daum-app-review.csv"
EXPECTED_COUNT = 124

# 1-based row numbers in daum-full-posts.jsonl. Every row was read before this
# allowlist was fixed. The list is deliberately explicit so an automatic score
# cannot silently change the corpus.
INCLUDE = {2, 3, 7, 14, 49, 103, 108, 123, 124}
DUPLICATE_REPOST = {1, 121, 122}
APPLICATION_FORM = {
    35, 37, 39, 41, 42, 45, 46, 47, 48,
    *range(50, 61), *range(62, 99), 100, *range(113, 117),
}
RECRUITMENT_OR_NOTICE = {
    4, 6, 8, 9, 10, 11, 12, 21, 22, 23, 24, 26, 27, 28, 29, 30,
    32, 33, 34, 36, 40, 43, 44, 61, 99, 101, 102, 104, 105, 107,
    109, 110, 111, 112, 117, 119,
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def normalize_date(value: str) -> str:
    match = re.search(r"(20\d{2}|\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})", value or "")
    if not match:
        return ""
    year, month, day = match.groups()
    if len(year) == 2:
        year = "20" + year
    return f"{year}-{int(month):02d}-{int(day):02d}"


def decision(index: int) -> tuple[str, str]:
    if index in INCLUDE:
        return "include", "소모임 앱 탐색·가입·참석·평가 경험이 원문의 실질적 맥락"
    if index in DUPLICATE_REPOST:
        return "exclude", "동일 본문 재게시물; 가장 이른 공개 원문 1건만 유지"
    if index in APPLICATION_FORM:
        return "exclude", "카페 준회원 가입 신청 양식; 앱은 가입 경로 선택지로만 등장"
    if index in RECRUITMENT_OR_NOTICE:
        return "exclude", "회원 모집·홍보·운영 공지 또는 활동 보고"
    return "exclude", "앱이 주변적으로만 언급되거나 일반 동호회·다른 주제가 본문 중심"


def main() -> None:
    daum_rows = read_jsonl(FULL_POSTS)
    if len(daum_rows) != EXPECTED_COUNT:
        raise SystemExit(
            f"다음 원문 수가 바뀌었습니다: 예상 {EXPECTED_COUNT}, 실제 {len(daum_rows)}"
        )

    reviewed = []
    kept = []
    for index, row in enumerate(daum_rows, 1):
        verdict, reason = decision(index)
        reviewed.append({
            "row": index,
            "verdict": verdict,
            "reason": reason,
            "date": normalize_date(str(row.get("date", ""))),
            "title": row.get("title", ""),
            "url": row.get("url", ""),
        })
        if verdict == "include":
            item = dict(row)
            item["date"] = normalize_date(str(item.get("date", "")))
            item["source_kind"] = "full_post"
            item["access"] = "ok"
            item["retrieved_at"] = "2026-08-31"
            kept.append(item)

    with REVIEW.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["row", "verdict", "reason", "date", "title", "url"]
        )
        writer.writeheader()
        writer.writerows(reviewed)

    current = [row for row in read_jsonl(RECORDS) if row.get("site") != "daum"]
    current.extend(kept)
    temp = RECORDS.with_suffix(".jsonl.tmp")
    temp.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in current),
        encoding="utf-8",
    )
    temp.replace(RECORDS)
    print(f"다음카페 공개 원문 {len(daum_rows)}건 검토 → 포함 {len(kept)} / 제외 {len(daum_rows)-len(kept)}")
    print(f"통합 코퍼스 {len(current)}건")


if __name__ == "__main__":
    main()
