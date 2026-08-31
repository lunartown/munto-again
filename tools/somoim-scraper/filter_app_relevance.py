#!/usr/bin/env python3
"""검토가 끝난 URL만 소모임 앱 관련 코퍼스로 분리한다.

자동 키워드 분류 결과를 최종 데이터로 쓰지 않는다. 원본 4,767건의 제목과
본문/검색 미리보기를 검토한 뒤, 앱 탐색·가입·참석·운영·탈퇴·평가·질문이
글의 실질적인 맥락인 URL만 아래 allowlist에 기록했다.
"""

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "records.jsonl"
KEPT = HERE / "data" / "records.app-relevant.jsonl"
NOISE = HERE / "data" / "records.noise.jsonl"
AUDIT = HERE / "data" / "records.app-review.csv"

# 검토 당시 원본을 고정한다. 원본이 바뀌면 allowlist도 다시 검토해야 한다.
SOURCE_SHA256 = "cfddf690fcdf445698366e96a837f75513f2407e2d84ec791d808ef780603f5c"

# 직접 사용/참석/운영 후기가 글의 중심인 자료
EXPERIENCE_INDEXES = {
    15, 17, 18, 22, 41, 43, 49, 75, 177, 200, 228, 302,
    339, 340, 342, 343, 344, 346, 347, 349, 352, 358,
    394, 395, 399, 432, 473,
    2241, 2381, 2415, 2916, 3129,
    3928, 3929, 3930, 3931, 3932, 3934, 3938, 3939, 3940, 3945, 3949,
}

# 앱에서 모임을 탐색하거나 가입 전후 판단을 묻는 자료
QUESTION_INDEXES = {
    74, 79, 93, 319, 345, 348, 353,
    388, 390, 391, 393, 398, 404, 406, 410, 411, 415, 417,
    435, 436, 439, 444, 451, 452, 456, 458, 459, 467,
    1164,
    3088, 3611, 3638, 3680, 3689,
    3933, 3936, 3941,
}

# 사용 후 앱/모임 구조를 직접 평가한 자료
EVALUATION_INDEXES = {344, 3939, 3940}

REVIEWED_INDEXES = EXPERIENCE_INDEXES | QUESTION_INDEXES | EVALUATION_INDEXES


def compact(text):
    return re.sub(r"[^가-힣a-z0-9]+", "", text.lower())


def duplicate_key(row):
    """동일 제목으로 재게시된 글은 본문 미리보기 위치가 달라도 한 건으로 본다."""
    title = compact(row.get("title", ""))
    if len(title) >= 12:
        return (title,)
    return title, compact(row.get("body", ""))[:180]


def keep_reason(index):
    if index in EVALUATION_INDEXES:
        return "K03_REVIEWED_APP_EVALUATION"
    if index in EXPERIENCE_INDEXES:
        return "K01_REVIEWED_APP_EXPERIENCE"
    return "K02_REVIEWED_APP_QUESTION"


def main():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise SystemExit(
            "원본 records.jsonl이 검토 당시와 달라졌습니다. "
            "allowlist를 재검토한 뒤 SOURCE_SHA256을 갱신하세요."
        )

    rows = [json.loads(line) for line in SOURCE.open(encoding="utf-8")]
    missing = sorted(REVIEWED_INDEXES - set(range(len(rows))))
    if missing:
        raise SystemExit(f"원본에 없는 검토 인덱스: {missing}")

    results = []
    seen_kept = {}
    for index, row in enumerate(rows):
        if index in REVIEWED_INDEXES:
            decision = "keep"
            reason = keep_reason(index)
            key = duplicate_key(row)
            if key in seen_kept:
                decision = "noise"
                reason = f"R02_DUPLICATE_OF_{seen_kept[key]}"
            else:
                seen_kept[key] = index
        else:
            decision = "noise"
            reason = "R01_REVIEWED_NOT_ABOUT_SOMOIM_APP"
        results.append((index, decision, reason, row))

    with KEPT.open("w", encoding="utf-8") as kept, NOISE.open("w", encoding="utf-8") as noise:
        for _, decision, reason, row in results:
            enriched = dict(row, app_relevance=decision, review_reason=reason)
            target = kept if decision == "keep" else noise
            target.write(json.dumps(enriched, ensure_ascii=False) + "\n")

    with AUDIT.open("w", encoding="utf-8", newline="") as audit:
        writer = csv.writer(audit)
        writer.writerow(["index", "decision", "reason", "site", "source_kind", "title", "url"])
        for index, decision, reason, row in results:
            writer.writerow([
                index,
                decision,
                reason,
                row.get("site", ""),
                row.get("source_kind", "legacy"),
                row.get("title", ""),
                row.get("url", ""),
            ])

    counts = Counter(decision for _, decision, _, _ in results)
    reasons = Counter(reason for _, _, reason, _ in results)
    print(f"원본 {len(rows)} → 앱 관련 {counts['keep']} / 노이즈 {counts['noise']}")
    for reason, count in sorted(reasons.items()):
        print(f"  {reason}: {count}")
    print(f"감사 파일: {AUDIT}")


if __name__ == "__main__":
    main()
