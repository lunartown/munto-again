#!/usr/bin/env python3
"""Independently code the 50 collected App Store reviews at review level.

This source is older (2024-04 to 2025-06) and remains separate from the current
Google Play affinity. Tags are used only for later corroboration/contradiction.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = RESEARCH_ROOT / "data/reviews/reanalysis/samples/app_store_all_50.csv"
OUTPUT_DIR = RESEARCH_ROOT / "data/reviews/reanalysis/app_store"
CODED_PATH = OUTPUT_DIR / "app_store_50_independent_coding.csv"
SUMMARY_PATH = OUTPUT_DIR / "app_store_50_theme_summary.csv"


THEMES = {
    "C01": "앱 오류·기능 실패",
    "C02": "앱 사용 편의와 정보 표현",
    "C04": "환불 기준과 비용 책임",
    "C05": "문의·문제 해결",
    "C06": "규칙 집행과 제재",
    "C07": "호스트·참여자·정보 신뢰",
    "C08": "참여 전 판단 단서",
    "C09": "가격·수수료 대비 가치",
    "C10": "수익 구조와 상업화 인식",
    "C11": "연애·파티 목적 경험",
    "C12": "특정 목적 과다 노출",
    "C13": "원치 않는 접근·알림",
    "C14": "필터·검색·발견",
    "C15": "지역별 공급·장소",
    "C16": "모임 선택 폭",
    "V01": "함께하는 취미 활동 가치",
    "V02": "새로운 시도·취향 발견",
    "V03": "잘 맞는 사람·관계 가치",
    "H01": "호스트 개설·운영 조건",
    "R01": "재참여·지속 이용",
    "R02": "이용 중단·외부 이동",
}


TAGS = {
    "ASR001": ["H01"],
    "ASR002": ["C06", "R02"],
    "ASR003": ["C12", "C09", "C07", "C16", "R02"],
    "ASR004": ["C04"],
    "ASR005": ["C14", "C16", "R02"],
    "ASR006": ["C07"],
    "ASR007": ["C15"],
    "ASR008": ["C05", "C07", "C08", "R02"],
    "ASR009": ["C01", "R02"],
    "ASR010": ["C01"],
    "ASR011": ["C01"],
    "ASR012": ["C02", "V03"],
    "ASR013": ["C01", "V01", "V03"],
    "ASR014": [],
    "ASR015": ["V03"],
    "ASR016": ["C01"],
    "ASR017": ["C02", "C08"],
    "ASR018": ["C06", "C08", "C09", "C10", "R02"],
    "ASR019": ["C09", "V01"],
    "ASR020": ["C01"],
    "ASR021": ["C06"],
    "ASR022": ["C07"],
    "ASR023": ["C07", "C10", "C16", "R02"],
    "ASR024": ["C02"],
    "ASR025": ["C01", "C05", "H01"],
    "ASR026": ["C07", "C11"],
    "ASR027": ["C14"],
    "ASR028": ["C01"],
    "ASR029": ["V01"],
    "ASR030": ["C01"],
    "ASR031": ["C10"],
    "ASR032": ["C07"],
    "ASR033": ["C14", "C16", "V01"],
    "ASR034": ["C14", "V03"],
    "ASR035": ["C01", "R02"],
    "ASR036": ["C13"],
    "ASR037": ["C13"],
    "ASR038": ["C01", "C13", "R02"],
    "ASR039": ["V02"],
    "ASR040": ["C01"],
    "ASR041": ["V01", "V03"],
    "ASR042": ["C02", "R02"],
    "ASR043": ["C06", "H01"],
    "ASR044": ["V03"],
    "ASR045": ["C01", "C05"],
    "ASR046": ["C07", "C11", "R01"],
    "ASR047": ["C09", "C10", "C11", "C16"],
    "ASR048": ["C06"],
    "ASR049": ["C01"],
    "ASR050": ["C15"],
}


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    coded = []
    counts: Counter[str] = Counter()
    low_counts: Counter[str] = Counter()
    high_counts: Counter[str] = Counter()
    for row in rows:
        tags = TAGS[row["sample_id"]]
        for tag in tags:
            counts[tag] += 1
            if int(row["rating"]) <= 3:
                low_counts[tag] += 1
            else:
                high_counts[tag] += 1
        coded.append(
            {
                "sample_id": row["sample_id"],
                "review_date_utc": row["review_date_utc"],
                "rating": row["rating"],
                "review_title": row["review_title"],
                "review_text": row["review_text"],
                "theme_ids": "|".join(tags),
                "theme_names": "|".join(THEMES[tag] for tag in tags),
                "coding_status": "independent_review_level_second_pass",
                "source_scope": "app_store_2024_04_to_2025_06_only",
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CODED_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(coded[0].keys()))
        writer.writeheader()
        writer.writerows(coded)

    summary = [
        {
            "theme_id": theme_id,
            "theme_name": theme_name,
            "unique_review_count": counts[theme_id],
            "share_of_50": round(counts[theme_id] / 50, 4),
            "low_rating_reviews": low_counts[theme_id],
            "high_rating_reviews": high_counts[theme_id],
            "comparison_status": "separate_source_not_yet_triangulated",
        }
        for theme_id, theme_name in THEMES.items()
    ]
    with SUMMARY_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    print(f"reviews={len(rows)}")
    print(f"coded_output={CODED_PATH}")
    print(f"summary_output={SUMMARY_PATH}")


if __name__ == "__main__":
    main()
