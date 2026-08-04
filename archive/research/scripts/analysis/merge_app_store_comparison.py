#!/usr/bin/env python3
"""Merge App Store cards and compare cluster recurrence across app stores."""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL = PROJECT_ROOT / "data/synthesis/qualitative_cards.csv"
GOOGLE = PROJECT_ROOT / "data/reviews/google_play/processed/review_cards_reviewed.csv"
APPLE = PROJECT_ROOT / "data/reviews/app_store/processed/review_cards_reviewed.csv"
CLUSTERS = PROJECT_ROOT / "data/synthesis/affinity_clusters.csv"
COMPARISON = PROJECT_ROOT / "data/reviews/app_store/outputs/comparison_summary.csv"
REPORT = PROJECT_ROOT / "docs/findings/app_store_comparison_report.md"

CLUSTER_TAGS = {
    "C01": {"숨은만남신호", "기대불일치", "탐색피로"},
    "C02": {"호스트상업화", "성비·조건"},
    "C03": {"안전·신뢰", "경험품질"},
    "C04": {"이탈행동", "대체서비스"},
    "C05": {"긍정·반례"},
}
STATUS = {
    "C01": ("재현", "소개팅 파티 인식과 취미 모임 탐색 곤란이 모두 확인됨"),
    "C02": ("부분 재현", "상업화 불만은 반복됐지만 성별 차등 모집은 이번 표본에서 독립 카드로 확인되지 않음"),
    "C03": ("재현", "운영 신뢰와 기능 실패가 여러 리뷰에서 반복됨"),
    "C04": ("재현", "탈퇴·삭제·사용 감소와 대체 플랫폼 고려가 확인됨"),
    "C05": ("재현", "취미 탐색과 관계 형성이 충족된 긍정 반례가 반복됨"),
}


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def review_key(card):
    return card["utterance_id"].split("-")[0]


def selected(cards, tags):
    return [card for card in cards if card["primary_tag"] in tags]


def main():
    canonical = read(CANONICAL)
    apple = read(APPLE)
    google = read(GOOGLE)
    fields = list(canonical[0])

    preserved = [row for row in canonical if row["source_id"] != "S006"]
    merged = preserved + apple
    assert len({row["card_id"] for row in merged}) == len(merged)
    write(CANONICAL, fields, merged)

    clusters = read(CLUSTERS)
    combined_reviews = google + apple
    positive_ids = [row["card_id"] for row in combined_reviews if row["primary_tag"] == "긍정·반례"][:5]
    for cluster in clusters:
        included = selected(combined_reviews, CLUSTER_TAGS[cluster["cluster_id"]])
        cluster["included_card_ids"] = "|".join(row["card_id"] for row in included)
        cluster["contradictory_card_ids"] = "" if cluster["cluster_id"] == "C05" else "|".join(positive_ids)
        cluster["supporting_card_count"] = str(len(included))
        cluster["source_type_count"] = "1"
        cluster["owner"] = "Codex AI 원문 검토; 사람 독립 검증 미실시"
        cluster["status"] = "cross_platform_reviewed"
    write(CLUSTERS, list(clusters[0]), clusters)

    rows = []
    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        tags = CLUSTER_TAGS[cluster_id]
        google_cards = selected(google, tags)
        apple_cards = selected(apple, tags)
        status, note = STATUS[cluster_id]
        rows.append({
            "cluster_id": cluster_id,
            "cluster_name": cluster["cluster_name"],
            "google_play_card_count": len(google_cards),
            "google_play_unique_review_count": len({review_key(row) for row in google_cards}),
            "app_store_card_count": len(apple_cards),
            "app_store_unique_review_count": len({review_key(row) for row in apple_cards}),
            "recurrence_status": status,
            "interpretation": note,
        })
    write(COMPARISON, list(rows[0]), rows)

    lines = [
        "# App Store 비교 표본 결과",
        "",
        "## 분석 범위",
        "",
        "- Apple 공개 리뷰 피드 원자료 50건",
        "- 최신순 1~3점 20건 + 4~5점 반례 10건",
        "- 30건 중 구체적 근거가 있는 27건에서 발화 카드 42장 생성",
        "- Google Play 표본과 빈도를 합산하지 않고 기존 클러스터의 재현 여부만 비교",
        "",
        "## 플랫폼 간 비교",
        "",
        "| 클러스터 | Google 리뷰 | App Store 리뷰 | 판정 |",
        "|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cluster_name']} | {row['google_play_unique_review_count']} | "
            f"{row['app_store_unique_review_count']} | {row['recurrence_status']} |"
        )
    lines += [
        "",
        "## 해석",
        "",
        "App Store에서도 소개팅 파티로의 변질 인식, 취미 모임 탐색 곤란, 호스트·플랫폼",
        "운영 불신, 탈퇴·사용 감소, 취미 목적 충족 반례가 모두 나타났다. 따라서 핵심 패턴이",
        "Google Play에만 존재한다고 보기는 어렵다. 다만 성별 차등 모집은 App Store 30건",
        "표본에서 독립적인 카드로 확인되지 않아 상업화 클러스터는 부분 재현으로 판정했다.",
        "",
        "## 비교 한계",
        "",
        "- Google Play 표본은 2025-10~2026-07, App Store 표본은 2024-09~2025-06으로 시기가 다름",
        "- 각 스토어의 리뷰 노출·작성자 구성·평점 문화가 달라 카드 수를 만족도 비율로 비교할 수 없음",
        "- App Store 공개 피드는 최신 50건만 확인되어 더 오래된 리뷰 전체를 대표하지 않음",
        "- 동일 AI가 두 플랫폼을 코딩했으므로 코더 간 독립 신뢰도는 확보되지 않음",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"canonical={len(merged)} apple_cards={len(apple)} comparison_clusters={len(rows)}")


if __name__ == "__main__":
    main()
