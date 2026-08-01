#!/usr/bin/env python3
"""Build reproducible review statistics and a cross-evidence matrix.

The reviewed datasets use one row per utterance card. This script reports both
card counts and deduplicated source-review counts so card splitting is not
mistaken for independent respondents.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
GOOGLE_CARDS = (
    RESEARCH_ROOT
    / "data/reviews/google_play/processed/review_cards_reviewed.csv"
)
APP_STORE_CARDS = (
    RESEARCH_ROOT
    / "data/reviews/app_store/processed/review_cards_reviewed.csv"
)
CLUSTERS = RESEARCH_ROOT / "data/synthesis/affinity_clusters.csv"
CLUSTER_OUTPUT = (
    RESEARCH_ROOT / "data/synthesis/review_cluster_statistics.csv"
)
EVIDENCE_OUTPUT = (
    RESEARCH_ROOT / "data/synthesis/evidence_triangulation.csv"
)


# Only cards whose original text directly describes the interview condition are
# counted here. Broader thematic similarity is marked as indirect in the output.
DIRECT_CARD_IDS = {
    "A": set(),
    "B": {"AS013"},
    "C": {"GP009", "GP016", "GP022", "GP047", "GP065", "AS040"},
    "D": set(),
    "E": {"GP088", "GP094", "GP095"},
    "F": {
        "GP003",
        "GP006",
        "GP012",
        "GP023",
        "GP028",
        "GP032",
        "GP037",
        "GP041",
        "GP045",
        "GP053",
        "GP054",
        "GP057",
        "GP069",
        "GP072",
        "GP079",
        "GP082",
        "GP087",
        "AS016",
        "AS017",
        "AS018",
        "AS019",
        "AS023",
        "AS031",
        "AS032",
        "AS033",
        "AS034",
        "AS035",
        "AS038",
    },
}


CONDITION_META = {
    "A": {
        "name": "참여 전 실제 목적·조건 예측",
        "cluster_ids": {"C01"},
        "support": "strong",
        "interpretation": (
            "소개팅·술모임 노출, 취미 공급 부족과 필터 실패가 참여 전 선택을 "
            "어렵게 한다는 리뷰가 양 플랫폼에서 반복됨"
        ),
    },
    "B": {
        "name": "반복 가능한 상호작용 포맷",
        "cluster_ids": set(),
        "support": "weak",
        "interpretation": (
            "현장 진행 실패 한 사례 외에는 리뷰가 진행 포맷을 구체적으로 설명하지 않아 "
            "인터뷰 기반 메커니즘 가설로 유지"
        ),
    },
    "C": {
        "name": "호스트 역량 의존·운영 지원 부족",
        "cluster_ids": set(),
        "support": "weak",
        "interpretation": (
            "호스트 책임 전가·제재·수수료·정산 사례는 있으나 호스트 소진과 모임 지속의 "
            "관계를 직접 말한 리뷰는 적어 핵심 문제 단독 근거로 부족"
        ),
    },
    "D": {
        "name": "위험 판단·퇴출·사건 대응 부족",
        "cluster_ids": {"C03"},
        "support": "strong",
        "interpretation": (
            "취소·환불·신원·신고·지원 대응과 앱 오류가 한 클러스터에 함께 나타남. "
            "그중 안전·신뢰 태그는 별도로 집계"
        ),
    },
    "E": {
        "name": "반복 참여·작은 기여",
        "cluster_ids": set(),
        "support": "weak",
        "interpretation": (
            "반복 이용을 직접 말한 긍정 리뷰가 일부 있으나 참석 확정·후기 기여가 "
            "소속감을 만든다는 관계는 인터뷰에서만 확인"
        ),
    },
    "F": {
        "name": "앱 완성도·내부 운영 도구",
        "cluster_ids": set(),
        "support": "strong",
        "interpretation": (
            "로그인·채팅·알림·결제·필터·프로필 등 기본 과업 실패가 양 플랫폼에서 반복됨"
        ),
    },
    "G": {
        "name": "비용·모집 방식의 공정성",
        "cluster_ids": {"C02"},
        "support": "strong",
        "interpretation": (
            "인터뷰 여섯 그룹에 없던 리뷰 고유 패턴. 비용 명세·성별 차등·외부 결제와 "
            "호스트 상업화가 참가자 진정성 불신으로 연결됨"
        ),
    },
    "R": {
        "name": "삭제·탈퇴·외부 이동 결과",
        "cluster_ids": {"C04"},
        "support": "strong",
        "interpretation": (
            "평가를 넘어 삭제·탈퇴·비사용·대체 서비스 이동을 직접 표현한 결과 카드"
        ),
    },
    "P": {
        "name": "취미·관계 가치가 작동한 반례",
        "cluster_ids": {"C05"},
        "support": "strong",
        "interpretation": (
            "조건이 맞을 때 다양한 취미와 긍정적 관계가 충족된 사례도 양 플랫폼에서 반복됨"
        ),
    },
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def review_id(row: dict[str, str]) -> str:
    source_review_id = row["utterance_id"].rsplit("-", 1)[0]
    return f'{row["platform"]}::{source_review_id}'


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = read_rows(GOOGLE_CARDS) + read_rows(APP_STORE_CARDS)
    cards_by_id = {row["card_id"]: row for row in cards}
    cluster_rows = read_rows(CLUSTERS)
    cluster_card_ids = {
        row["cluster_id"]: set(row["included_card_ids"].split("|"))
        for row in cluster_rows
    }

    statistics = []
    for row in cluster_rows:
        selected = [
            cards_by_id[card_id]
            for card_id in cluster_card_ids[row["cluster_id"]]
        ]
        unique_reviews = {review_id(card) for card in selected}
        platform_counts = Counter(
            cards_by_id[next(
                card_id
                for card_id in cluster_card_ids[row["cluster_id"]]
                if review_id(cards_by_id[card_id]) == unique_review
            )]["platform"]
            for unique_review in unique_reviews
        )
        low_rating_reviews = {
            review_id(card)
            for card in selected
            if card["rating"] and int(card["rating"]) <= 3
        }
        statistics.append(
            {
                "cluster_id": row["cluster_id"],
                "cluster_name": row["cluster_name"],
                "card_count": len(selected),
                "unique_review_count": len(unique_reviews),
                "google_play_unique_reviews": platform_counts["Google Play"],
                "app_store_unique_reviews": platform_counts["Apple App Store"],
                "low_rating_unique_reviews": len(low_rating_reviews),
                "counting_note": "클러스터 간 동일 리뷰 중복 가능",
            }
        )

    write_rows(
        CLUSTER_OUTPUT,
        [
            "cluster_id",
            "cluster_name",
            "card_count",
            "unique_review_count",
            "google_play_unique_reviews",
            "app_store_unique_reviews",
            "low_rating_unique_reviews",
            "counting_note",
        ],
        statistics,
    )

    evidence_rows = []
    for condition_id, meta in CONDITION_META.items():
        ids = set(DIRECT_CARD_IDS.get(condition_id, set()))
        for cluster_id in meta["cluster_ids"]:
            ids.update(cluster_card_ids[cluster_id])

        # D uses the broad C03 cluster for context but its direct count is limited
        # to cards whose primary tag is safety/trust.
        if condition_id == "D":
            ids = {
                row["card_id"]
                for row in cards
                if row["primary_tag"] == "안전·신뢰"
            }

        selected = [cards_by_id[card_id] for card_id in ids]
        unique_reviews = {review_id(card) for card in selected}
        unique_by_platform = Counter(
            unique_review.split("::", 1)[0]
            for unique_review in unique_reviews
        )
        evidence_rows.append(
            {
                "condition_id": condition_id,
                "condition_name": meta["name"],
                "direct_card_count": len(selected),
                "direct_unique_review_count": len(unique_reviews),
                "google_play_unique_reviews": unique_by_platform["Google Play"],
                "app_store_unique_reviews": unique_by_platform["Apple App Store"],
                "review_support": meta["support"],
                "interpretation": meta["interpretation"],
            }
        )

    write_rows(
        EVIDENCE_OUTPUT,
        [
            "condition_id",
            "condition_name",
            "direct_card_count",
            "direct_unique_review_count",
            "google_play_unique_reviews",
            "app_store_unique_reviews",
            "review_support",
            "interpretation",
        ],
        evidence_rows,
    )

    print(
        f"review cards={len(cards)}, "
        f"unique reviews={len({review_id(card) for card in cards})}"
    )
    print(f"wrote {CLUSTER_OUTPUT}")
    print(f"wrote {EVIDENCE_OUTPUT}")


if __name__ == "__main__":
    main()
