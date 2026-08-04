#!/usr/bin/env python3
"""Compare the preserved interview affinity with newly rebuilt review analyses.

Counts remain source-specific. The script does not add review counts together
across platforms and does not turn repeated evidence into a final problem
definition.
"""

from __future__ import annotations

import csv
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
CURRENT_PATH = RESEARCH_ROOT / "data/reviews/reanalysis/current/affinity_second_pass_cards.csv"
APP_PATH = RESEARCH_ROOT / "data/reviews/reanalysis/app_store/app_store_50_independent_coding.csv"
OUTPUT_DIR = RESEARCH_ROOT / "data/synthesis/reanalysis"
OUTPUT_PATH = OUTPUT_DIR / "source_triangulation_matrix.csv"


INTERVIEW_GROUPS = {
    "A": {
        "name": "참여 전 실제 목적·방식·조건을 예측하기 어렵다",
        "cards": 6,
        "participants": 4,
        "google_groups": ["C07", "C08", "C11", "C12", "C14", "C15", "C16"],
        "app_groups": ["C07", "C08", "C11", "C12", "C14", "C15", "C16"],
        "relation": "direct_repetition",
    },
    "B": {
        "name": "반복 가능한 상호작용 포맷이 경험을 좌우한다",
        "cards": 6,
        "participants": 3,
        "google_groups": ["V01", "V02", "V03"],
        "app_groups": ["V01", "V02", "V03"],
        "relation": "interview_led_review_outcomes_are_indirect",
    },
    "C": {
        "name": "모임 품질·지속이 호스트 역량에 의존하지만 지원은 부족하다",
        "cards": 7,
        "participants": 3,
        "google_groups": ["H01", "C03", "C06", "C07"],
        "app_groups": ["H01", "C06", "C07"],
        "relation": "interview_led_partial_review_repetition",
    },
    "D": {
        "name": "위험 판단·퇴출·사건 대응 체계가 부족하다",
        "cards": 4,
        "participants": 3,
        "google_groups": ["C06", "C07", "C08"],
        "app_groups": ["C06", "C07", "C08"],
        "relation": "direct_repetition",
    },
    "E": {
        "name": "반복 참여와 작은 기여 구조가 관계·소속감을 만든다",
        "cards": 3,
        "participants": 1,
        "google_groups": ["V04", "R01"],
        "app_groups": ["R01"],
        "relation": "single_interview_with_limited_review_support",
    },
    "F": {
        "name": "앱 완성도와 내부 운영 도구 부족이 신뢰·잔존을 낮춘다",
        "cards": 3,
        "participants": 2,
        "google_groups": ["C01", "C02", "R02"],
        "app_groups": ["C01", "C02", "R02"],
        "relation": "direct_repetition",
    },
}


def current_review_sets() -> dict[str, set[str]]:
    sets: dict[str, set[str]] = {}
    with CURRENT_PATH.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            sets.setdefault(row["affinity_group"], set()).add(row["corpus_id"])
    return sets


def app_review_sets() -> dict[str, set[str]]:
    sets: dict[str, set[str]] = {}
    with APP_PATH.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            for tag in filter(None, row["theme_ids"].split("|")):
                sets.setdefault(tag, set()).add(row["sample_id"])
    return sets


def union_count(sets: dict[str, set[str]], groups: list[str]) -> int:
    combined: set[str] = set()
    for group in groups:
        combined.update(sets.get(group, set()))
    return len(combined)


def main() -> None:
    current_sets = current_review_sets()
    app_sets = app_review_sets()
    rows = []
    for group_id, group in INTERVIEW_GROUPS.items():
        rows.append(
            {
                "interview_group": group_id,
                "interview_group_name": group["name"],
                "interview_card_count": group["cards"],
                "interview_participant_count": group["participants"],
                "google_play_current_group_ids": "|".join(group["google_groups"]),
                "google_play_current_unique_reviews": union_count(
                    current_sets, group["google_groups"]
                ),
                "google_play_current_denominator": 119,
                "app_store_group_ids": "|".join(group["app_groups"]),
                "app_store_unique_reviews": union_count(app_sets, group["app_groups"]),
                "app_store_denominator": 50,
                "cross_source_relation": group["relation"],
                "decision_status": "evidence_comparison_only_not_final_problem",
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"output={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
