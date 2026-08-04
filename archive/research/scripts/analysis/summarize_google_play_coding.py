#!/usr/bin/env python3
"""Summarize AI-coded Google Play cards and propose—not finalize—clusters."""

import csv
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_ROOT = PROJECT_ROOT / "data/reviews/google_play"
CARDS_PATH = REVIEW_ROOT / "interim/review_cards_ai.csv"
TAG_PATH = REVIEW_ROOT / "outputs/tag_summary.csv"
CLUSTER_PATH = REVIEW_ROOT / "interim/affinity_candidates.csv"
SUMMARY_PATH = REVIEW_ROOT / "interim/coding_summary.md"
VALIDATION_PATH = REVIEW_ROOT / "validation/ai_validation_sample_20.csv"


CLUSTERS = [
    {
        "cluster_id": "AI-C1",
        "cluster_name": "취미 모임이 소개팅·술모임 사이에서 보이지 않음",
        "tags": {"숨은만남신호", "기대불일치", "탐색피로"},
        "pattern_summary": "소개팅·술·파티 상품의 노출과 지역 선택지 부족이 겹치며 취미 중심 모임을 찾기 어렵다는 발화가 나타남.",
        "need_statement": "취미 목적 사용자는 목록 탐색 단계에서 모임의 실제 목적과 활동 비중을 빠르게 구별할 수 있어야 한다. 원하는 활동을 찾기 전에 소개팅·술모임을 반복해서 걸러내야 하기 때문이다.",
        "design_implication": "목적·활동 강도 필터와 추천 기준 설명을 검토할 후보. 해결책 확정 전 인터뷰로 판단 신호를 확인해야 함.",
    },
    {
        "cluster_id": "AI-C2",
        "cluster_name": "수익화 구조가 호스트와 참가자 구성을 왜곡한다고 느낌",
        "tags": {"호스트상업화", "성비·조건"},
        "pattern_summary": "수고비·수수료·개인계좌 결제·성별 차등 초대·인기 연출이 공정성과 진정성을 훼손한다는 발화가 나타남.",
        "need_statement": "참여자는 결제 전에 비용의 구성과 참가자 모집 방식을 신뢰할 수 있어야 한다. 숨은 비용이나 인위적인 성비·인기 신호가 참여 판단을 흐리기 때문이다.",
        "design_implication": "비용 명세, 모집 방식 표시, 호스트 운영 이력의 검증 가능성을 탐색할 후보.",
    },
    {
        "cluster_id": "AI-C3",
        "cluster_name": "문제 발생 후 보호받지 못해 플랫폼 신뢰가 무너짐",
        "tags": {"안전·신뢰", "경험품질"},
        "pattern_summary": "당일 취소·환불·신원·고객센터 대응과 앱 오류가 연결되며 시간과 비용을 회복하기 어렵다는 발화가 많음.",
        "need_statement": "사용자는 취소·분쟁·기능 오류가 생겼을 때 책임 주체와 해결 경로를 예측할 수 있어야 한다. 현재는 손실과 증명 부담이 참여자에게 남는다고 느끼기 때문이다.",
        "design_implication": "환불 책임 기준과 신고·지원 상태 가시화를 별도 문제 영역으로 검토.",
    },
    {
        "cluster_id": "AI-C4",
        "cluster_name": "반복된 불일치 뒤 삭제하거나 외부 관계로 이동함",
        "tags": {"이탈행동", "대체서비스"},
        "pattern_summary": "불편을 평가하는 데서 끝나지 않고 앱 삭제·탈퇴·재이용 중단 또는 다른 서비스·외부 관계 이동으로 이어진 사례가 확인됨.",
        "need_statement": "취미 목적 사용자는 실패 경험 이후에도 더 적합한 모임을 다시 찾을 이유가 필요하다. 그렇지 않으면 이미 만난 사람이나 다른 서비스로 이동하기 때문이다.",
        "design_implication": "이탈 직전의 마지막 실패 경험과 대체 서비스 선택 이유를 인터뷰에서 우선 확인.",
    },
    {
        "cluster_id": "AI-C5",
        "cluster_name": "관심사와 운영 정보가 맞으면 취미 목적이 실제로 충족됨",
        "tags": {"긍정·반례"},
        "pattern_summary": "다양한 주제, 맞는 관심사, 후기·매너 정보, 참여 형식의 선택 폭이 긍정 경험과 관계 형성을 만든 반례가 존재함.",
        "need_statement": "취미 목적 사용자는 자신의 관심사·일정·안전 기대에 맞는 모임을 확신하고 선택할 수 있어야 한다. 조건이 맞을 때는 낯선 사람과도 취미 경험이 충분히 가치 있기 때문이다.",
        "design_implication": "부정 패턴만으로 결론 내리지 말고 만족 사례의 선택 기준을 인터뷰 질문에 포함.",
    },
]


def review_key(card):
    return card["utterance_id"].split("-")[0]


def main():
    with CARDS_PATH.open(encoding="utf-8-sig", newline="") as handle:
        cards = list(csv.DictReader(handle))

    by_tag = defaultdict(list)
    for card in cards:
        by_tag[card["primary_tag"]].append(card)

    tag_rows = []
    for tag, rows in sorted(by_tag.items(), key=lambda item: (-len(item[1]), item[0])):
        rating_groups = Counter("low_1_3" if int(row["rating"]) <= 3 else "high_4_5" for row in rows)
        tag_rows.append({
            "primary_tag": tag,
            "card_count": len(rows),
            "unique_review_count": len({review_key(row) for row in rows}),
            "low_rating_review_count": rating_groups["low_1_3"],
            "high_rating_review_count": rating_groups["high_4_5"],
            "interpretation_note": "카드 빈도는 전체 사용자 비율이 아니라 최신순 목적표본 안의 발화 수임",
        })
    with TAG_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = list(tag_rows[0])
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(tag_rows)

    positive_ids = [row["card_id"] for row in by_tag.get("긍정·반례", [])][:5]
    cluster_rows = []
    for cluster in CLUSTERS:
        included = [row for row in cards if row["primary_tag"] in cluster["tags"]]
        contradictory = [] if cluster["cluster_id"] == "AI-C5" else positive_ids
        cluster_rows.append({
            "cluster_id": cluster["cluster_id"],
            "cluster_name": cluster["cluster_name"],
            "included_card_ids": "|".join(row["card_id"] for row in included),
            "pattern_summary": cluster["pattern_summary"],
            "need_statement": cluster["need_statement"],
            "contradictory_card_ids": "|".join(contradictory),
            "supporting_card_count": len(included),
            "supporting_review_count": len({review_key(row) for row in included}),
            "confidence": "medium" if len({review_key(row) for row in included}) >= 5 else "low",
            "design_implication": cluster["design_implication"],
            "owner": "연구자 검증 필요",
            "status": "ai_proposed",
        })
    with CLUSTER_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = list(cluster_rows[0])
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(cluster_rows)

    # Deterministic stratified sample: two cards per primary tag. This is a
    # review worksheet, not a claim that the 20 cards are statistically random.
    validation_rows = []
    for tag in sorted(by_tag):
        for row in by_tag[tag][:2]:
            validation_rows.append({
                "card_id": row["card_id"],
                "review_date": row["event_or_publish_date"],
                "rating": row["rating"],
                "verbatim_excerpt": row["verbatim_excerpt"],
                "ai_primary_tag": row["primary_tag"],
                "ai_secondary_tag": row["secondary_tag"],
                "ai_evidence_strength": row["evidence_strength"],
                "researcher_primary_tag": "",
                "researcher_decision": "",
                "split_or_merge_action": "",
                "reallocation_rationale": "",
                "verification_status": "pending",
            })
    assert len(validation_rows) == 20
    with VALIDATION_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = list(validation_rows[0])
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(validation_rows)

    included_reviews = len({review_key(row) for row in cards})
    low_cards = sum(int(row["rating"]) <= 3 for row in cards)
    lines = [
        "# Google Play 리뷰 AI 1차 코딩 요약",
        "",
        "## 처리 결과",
        "",
        f"- 표본 리뷰: 65건",
        f"- 구체적 근거가 있어 포함된 리뷰: {included_reviews}건",
        f"- 생성된 발화 카드: {len(cards)}장 (1~3점 {low_cards}장, 4~5점 {len(cards)-low_cards}장)",
        "- 상태: AI 1차 코딩(`coded`). 연구자 검증 전이므로 `verified`가 아님",
        "",
        "## 1차 태그 분포",
        "",
        "| 태그 | 카드 | 고유 리뷰 | 1~3점 | 4~5점 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in tag_rows:
        lines.append(
            f"| {row['primary_tag']} | {row['card_count']} | {row['unique_review_count']} | "
            f"{row['low_rating_review_count']} | {row['high_rating_review_count']} |"
        )
    lines += [
        "",
        "카드 수는 서로 독립적인 사용자 수가 아니다. 한 리뷰에서 여러 문제를 분리했기 때문에",
        "빈도는 방향을 찾는 용도로만 사용하고 사용자 비율로 해석하지 않는다.",
        "",
        "## AI가 제안한 클러스터",
        "",
    ]
    for row in cluster_rows:
        lines.append(
            f"- **{row['cluster_name']}** — {row['supporting_review_count']}개 리뷰, "
            f"{row['supporting_card_count']}장. {row['pattern_summary']}"
        )
    lines += [
        "",
        "## 연구자 검증 체크리스트",
        "",
        "1. `숨은만남신호` 7장을 원문과 대조해 단순 소개팅 기능 불만과 서비스 정체성 변화 발화를 분리한다.",
        "2. `탐색피로`에서 지역 공급 부족과 추천 노출 편향을 서로 다른 하위 클러스터로 재배치한다.",
        "3. `호스트상업화`에서 정상적인 유료 운영 불만과 기만적 운영 신호를 구분한다.",
        "4. `긍정·반례`를 삭제하지 말고 취미 목적 충족 조건을 별도 인터뷰 질문으로 만든다.",
        "5. 4~5점 표본은 반례 탐색용 15건뿐이므로 부정·긍정 카드 수를 만족도 비율로 비교하지 않는다.",
    ]
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"tags={len(tag_rows)} clusters={len(cluster_rows)} validation={len(validation_rows)} summary={SUMMARY_PATH.name}")


if __name__ == "__main__":
    main()
