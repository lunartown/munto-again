#!/usr/bin/env python3
"""Apply the Sprint 1 coding book to a collected Munto CSV.

This is an auditable AI/rule-assisted first pass. It does not claim to replace
the researcher's human validation. Rows are explicitly marked accordingly.
"""

import argparse
import csv
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts/collection"))

from collect_munto import CSV_FIELDS, normalize_title


# Cases missed by the conservative collector but supported by explicit signals
# in titles/descriptions. Keeping them in a visible override table makes changes
# traceable instead of burying judgment in an opaque model call.
C_OVERRIDES = {
    "664555": "상세 설명의 솔로 파티 표현",
    "664554": "상세 설명의 솔로 파티 표현",
    "664553": "상세 설명의 솔로 파티 표현",
    "664556": "상세 설명의 솔로 파티 표현",
    "664557": "상세 설명의 솔로 파티 표현",
    "663427": "훈남 환영 조건과 활동 없는 파티",
    "664623": "외모·비주얼 조건과 인연 중심 파티",
    "664598": "훈남 급구와 매치 표현",
    "665781": "상세 설명의 남녀 성비 운영",
    "664755": "비주얼 파티",
    "664385": "남성 급구 조건",
    "665756": "상세 설명의 썸 중심 파티",
    "665708": "여성 우선 승인과 와인 미팅",
    "664181": "비주얼·직업/외모 조건 파티",
    "664254": "남녀 정원 명시",
    "663904": "로테이션 파티",
    "664079": "여성 다수·남성 급구와 썸 표현",
    "664255": "동일 포맷의 남녀 균형 운영",
}

HIGH_ACTIVITY = [
    r"만들기", r"배워", r"강습", r"클래스", r"스터디", r"세미나",
    r"봉사", r"번역", r"스피치", r"드로잉", r"페인팅", r"글쓰기",
    r"토론", r"목공", r"조향", r"홈페이지\s*제작", r"샐러드\s*팩토리",
    r"책\s*쓰", r"연기", r"재테크", r"투자\s*시황", r"커리어", r"베이킹",
]
MEDIUM_ACTIVITY = [
    r"독서", r"영화", r"전시", r"사진", r"보드게임", r"크라임씬",
    r"머더", r"홀덤", r"여행", r"캠핑", r"수영", r"서핑", r"골프",
    r"야구", r"댄스", r"회화", r"언어\s*교환", r"투어", r"드라이브",
    r"요리", r"베이킹", r"사케", r"와인", r"위스키", r"향수",
    r"상담", r"대화\s*모임", r"플레이리스트", r"뮤직",
]
CONCRETE_TITLE = HIGH_ACTIVITY + MEDIUM_ACTIVITY + [
    r"타르트", r"케이크", r"쿠키", r"휘낭시에", r"에그타르트",
    r"바베큐", r"전어", r"한치", r"중식", r"동파육", r"프리다이빙",
    r"빠지", r"물놀이", r"책으로", r"『.+』", r"<.+>", r"해금",
]


def match(patterns: Iterable[str], text: str) -> str:
    for pattern in patterns:
        found = re.search(pattern, text, flags=re.IGNORECASE)
        if found:
            return found.group(0)
    return ""


def activity_specificity(row: Dict[str, str]) -> Tuple[str, str]:
    text = f"{row['제목']} {row['세부카테고리']}"
    evidence = match(HIGH_ACTIVITY, text)
    if evidence:
        return "상", evidence
    evidence = match(MEDIUM_ACTIVITY, text)
    if evidence:
        return "중", evidence
    return "하", "구체 활동보다 분위기·만남 중심"


def classify(row: Dict[str, str]) -> Tuple[str, str, str]:
    row_id = row["id"]
    specificity, activity_evidence = activity_specificity(row)
    preliminary = row["규칙기반_예비분류"]
    if preliminary == "C":
        return "C", row["예비판정근거"], specificity
    if row_id in C_OVERRIDES:
        return "C", C_OVERRIDES[row_id], specificity
    if preliminary == "B":
        return "B", row["예비판정근거"], specificity

    title = row["제목"]
    title_and_tag = f"{title} {row['세부카테고리']}"
    concrete = match(CONCRETE_TITLE, title_and_tag)
    high_concrete = match(HIGH_ACTIVITY, title_and_tag)
    # A concrete activity takes precedence over the platform's broad 'party'
    # category (e.g. a baking session listed under Food Party).
    if row["카테고리"] == "파티" and not high_concrete:
        return "B", "활동보다 대화·친목·파티 중심", "하"
    if concrete:
        return "A", f"구체 활동: {concrete}", specificity
    if row["카테고리"] in {"파티", "동네·또래"}:
        return "B", "활동보다 대화·친목·파티 중심", "하"
    if row["세부카테고리"] in {"대화", "또래친구", "취향친구"}:
        return "B", "관계 형성 중심의 대화 모임", "하"
    # Remaining non-party rows have a named interest/category but sparse titles.
    # Conservatively keep them at A with medium/low specificity, per the coding
    # book's rule to choose the lower contamination class when ambiguous.
    return "A", f"관심사 활동: {row['세부카테고리'] or row['카테고리']}", specificity


def write_rows(rows: List[Dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: List[Dict[str, str]], output: Path) -> None:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["카테고리"]].append(row)
    fields = ["카테고리", "전체", "A", "B", "C", "C비율", "고유포맷", "고유포맷_C", "고유포맷_C비율"]
    summary = []
    for category, items in sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        counts = Counter(item["최종분류"] for item in items)
        formats = defaultdict(list)
        for item in items:
            formats[item["반복모임키"]].append(item["최종분류"])
        format_classes = ["C" if "C" in classes else "B" if "B" in classes else "A" for classes in formats.values()]
        format_counts = Counter(format_classes)
        summary.append({
            "카테고리": category, "전체": len(items), "A": counts["A"], "B": counts["B"], "C": counts["C"],
            "C비율": counts["C"] / len(items), "고유포맷": len(formats), "고유포맷_C": format_counts["C"],
            "고유포맷_C비율": format_counts["C"] / len(formats),
        })
    total_counts = Counter(row["최종분류"] for row in rows)
    all_formats = defaultdict(list)
    for row in rows:
        all_formats[row["반복모임키"]].append(row["최종분류"])
    all_format_classes = ["C" if "C" in classes else "B" if "B" in classes else "A" for classes in all_formats.values()]
    all_format_counts = Counter(all_format_classes)
    summary.append({
        "카테고리": "전체", "전체": len(rows), "A": total_counts["A"], "B": total_counts["B"], "C": total_counts["C"],
        "C비율": total_counts["C"] / len(rows), "고유포맷": len(all_formats), "고유포맷_C": all_format_counts["C"],
        "고유포맷_C비율": all_format_counts["C"] / len(all_formats),
    })
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)


def make_validation_sample(rows: List[Dict[str, str]], output: Path) -> None:
    """Create a blinded, stratified 20-row sample for independent coding."""
    rng = random.Random(20260730)
    allocation = {"A": 7, "B": 6, "C": 7}
    sampled = []
    for label, count in allocation.items():
        pool = [row for row in rows if row["최종분류"] == label]
        sampled.extend(rng.sample(pool, count))
    rng.shuffle(sampled)
    fields = [
        "id", "카테고리", "세부카테고리", "제목", "설명", "태그", "참가비",
        "정원", "성비명시", "연령제한", "활동구체성_검증자", "검증자분류",
        "검증근거", "검증자", "검증완료",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sampled:
            writer.writerow({key: row.get(key, "") for key in fields})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=PROJECT_ROOT / "data/listings/raw/munto_socialings.csv")
    parser.add_argument("--output", type=Path,
                        default=PROJECT_ROOT / "data/listings/processed/munto_socialings_coded.csv")
    parser.add_argument("--summary", type=Path,
                        default=PROJECT_ROOT / "data/listings/processed/munto_category_summary.csv")
    parser.add_argument("--validation-sample", type=Path,
                        default=PROJECT_ROOT / "data/listings/validation/munto_validation_sample_20.csv")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        club_id = row.get("클럽ID", "")
        normalized = normalize_title(row["제목"])
        row["반복모임키"] = f"club:{club_id}|title:{normalized}" if club_id else f"title:{normalized}"
        final_class, evidence, specificity = classify(row)
        row["활동구체성"] = specificity
        row["최종분류"] = final_class
        row["최종판정근거"] = evidence
        row["코더"] = "Codex AI 1차"
        row["검토상태"] = "AI 1차완료·사용자검증필요"
    write_rows(rows, args.output)
    summarize(rows, args.summary)
    make_validation_sample(rows, args.validation_sample)
    print(f"coded {len(rows)} rows -> {args.output}")
    print(f"summary -> {args.summary}")
    print(f"blinded validation sample -> {args.validation_sample}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
