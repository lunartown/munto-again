#!/usr/bin/env python3
"""Apply a documented second-pass review and merge Google Play cards.

This is an AI-assisted second review, not an independent human coder check.
The script preserves non-Google-Play cards in qualitative_cards.csv, replaces
the two early S001 seed cards, and keeps card IDs stable for auditability.
"""

import csv
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_ROOT = PROJECT_ROOT / "data/reviews/google_play"
AI_CARDS = REVIEW_ROOT / "interim/review_cards_ai.csv"
VALIDATION = REVIEW_ROOT / "validation/ai_validation_sample_20.csv"
REVIEWED = REVIEW_ROOT / "processed/review_cards_reviewed.csv"
CANONICAL = PROJECT_ROOT / "data/synthesis/qualitative_cards.csv"
CLUSTERS = PROJECT_ROOT / "data/synthesis/affinity_clusters.csv"
REPORT = PROJECT_ROOT / "docs/findings/google_play_review_validation_report.md"


DECISIONS = {
    "GP003": ("agree", "경험품질", "", "알림 지연과 중복 노출은 구체적인 기능 경험 문제다."),
    "GP006": ("agree", "경험품질", "", "업데이트 후 모임 채팅 불가라는 구체적 이용 실패가 있다."),
    "GP019": ("agree", "긍정·반례", "", "불편을 인정하면서도 다양한 활동 경험의 가치를 명시한 반례다."),
    "GP027": ("agree", "긍정·반례", "", "파티 외 모임은 좋았다고 구분해 평가한 제한적 반례다."),
    "GP026": ("exclude", "", "remove", "참여 회피 권고만 있고 구체적 기대 불일치 근거는 같은 리뷰의 다른 카드에 이미 담겼다."),
    "GP060": ("exclude", "", "remove", "파티 리뷰의 도입 문장으로 독립적인 상황·판단 증거가 부족하다."),
    "GP013": ("agree", "대체서비스", "", "넷플연가를 명시해 운영자 이동 대안을 구체적으로 제시했다."),
    "GP073": ("agree", "대체서비스", "", "기존 참여자가 플랫폼 밖 관계로 이동한다고 명시했다."),
    "GP021": ("agree", "성비·조건", "", "여성 무료 초대와 남성 비용 부담이라는 성별 차등 구조가 구체적이다."),
    "GP025": ("agree", "성비·조건", "", "섭외 여성 비중과 무료 참여를 수치와 함께 주장했다."),
    "GP014": ("agree", "숨은만남신호", "", "로테이션 소개팅과 파티가 주로 노출된다는 직접 신호가 있다."),
    "GP020": ("agree", "숨은만남신호", "", "다양한 모임이 사라지고 소개팅만 남았다는 시간축 비교가 있다."),
    "GP001": ("agree", "안전·신뢰", "", "승인·연락·환불 책임을 확인할 수 없는 상태가 신뢰 문제로 연결된다."),
    "GP002": ("agree", "안전·신뢰", "", "다섯 차례 신청과 반복 취소라는 구체적 경험이 있다."),
    "GP024": ("exclude", "", "remove", "다른 사람에게 가지 말라고 권한 것으로 작성자 자신의 이탈 행동 증거는 아니다."),
    "GP029": ("agree", "이탈행동", "", "문제 누적 뒤 앱을 삭제했다고 명시했다."),
    "GP010": ("agree", "탐색피로", "", "지역 선택지 부재를 짧게 보고했으며 증거 강도는 낮게 유지한다."),
    "GP015": ("agree", "탐색피로", "", "추천 노출 밖의 모임을 찾기 어렵다는 탐색 비용이 직접 서술됐다."),
    "GP007": ("agree", "호스트상업화", "", "2차 비용의 개인계좌 수납을 반복 관찰하고 신고한 구체적 사례다."),
    "GP011": ("change", "경험품질", "merge_into_GP012", "핵심은 캔디 결제 자체보다 결제 후 콘텐츠가 열리지 않는 기능 실패이며 GP012와 같은 발화다."),
}

EXTRA_REMOVE = {"GP064", "GP080"}

CLUSTER_DEFS = [
    ("C01", "취미 모임이 소개팅·술모임 사이에서 보이지 않음",
     {"숨은만남신호", "기대불일치", "탐색피로"},
     "소개팅·술·파티 노출과 지역 공급 부족이 서로 다른 경로로 취미 모임 발견을 어렵게 한다.",
     "취미 목적 사용자는 탐색 단계에서 모임의 실제 목적과 활동 비중을 빠르게 구별할 수 있어야 한다. 원하는 활동을 찾기 전에 부적합한 모임을 반복해서 걸러내야 하기 때문이다.",
     "목적·활동 강도 표시와 추천 기준 설명을 검토하되, 지역 공급 부족은 별도 하위 문제로 유지한다."),
    ("C02", "수익화와 모집 방식이 참가자 진정성을 의심하게 함",
     {"호스트상업화", "성비·조건"},
     "수고비·수수료·외부 결제·성별 차등 초대·인기 연출이 비용 공정성과 참가자 진정성에 대한 불신을 만든다.",
     "참여자는 결제 전에 비용 구성과 참가자 모집 방식을 신뢰할 수 있어야 한다. 숨은 비용과 인위적인 성비·인기 신호가 참여 판단을 흐리기 때문이다.",
     "비용 명세, 모집 방식, 호스트 운영 이력의 검증 가능성을 탐색한다."),
    ("C03", "문제 발생 후 보호받지 못해 플랫폼 신뢰가 무너짐",
     {"안전·신뢰", "경험품질"},
     "당일 취소·환불·신원·지원 대응과 앱 오류가 시간·비용 손실을 회복하기 어려운 경험으로 연결된다.",
     "사용자는 취소·분쟁·기능 오류가 생겼을 때 책임 주체와 해결 경로를 예측할 수 있어야 한다. 현재는 손실과 증명 부담이 참여자에게 남는다고 느끼기 때문이다.",
     "환불 책임 기준과 신고·지원 상태 가시화를 별도 문제 영역으로 검토한다."),
    ("C04", "반복된 불일치 뒤 삭제하거나 외부 관계로 이동함",
     {"이탈행동", "대체서비스"},
     "불만 평가를 넘어 앱 삭제·탈퇴·재이용 중단 또는 다른 서비스·외부 관계 이동으로 이어진 사례가 있다.",
     "취미 목적 사용자는 실패 경험 이후에도 더 적합한 모임을 다시 찾을 이유가 필요하다. 그렇지 않으면 이미 만난 사람이나 다른 서비스로 이동하기 때문이다.",
     "이탈 직전의 마지막 실패 경험과 대체 서비스 선택 이유를 인터뷰에서 확인한다."),
    ("C05", "조건이 맞으면 취미 목적과 관계 형성이 함께 충족됨",
     {"긍정·반례"},
     "다양한 주제, 맞는 관심사, 후기·매너 정보와 참여 형식 선택 폭이 취미 만족과 긍정적 관계를 만든 반례가 있다.",
     "취미 목적 사용자는 관심사·일정·안전 기대에 맞는 모임을 확신하고 선택할 수 있어야 한다. 조건이 맞으면 낯선 사람과의 취미 경험도 충분한 가치가 있기 때문이다.",
     "만족 사례의 선택 기준을 인터뷰 질문에 포함해 부정 리뷰 편향을 보완한다."),
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle)), csv.DictReader


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def review_key(card):
    return card["utterance_id"].split("-")[0]


def main():
    cards, _ = read_csv(AI_CARDS)
    card_fields = list(cards[0])
    by_id = {card["card_id"]: card for card in cards}

    validation, _ = read_csv(VALIDATION)
    for row in validation:
        decision, researcher_tag, action, rationale = DECISIONS[row["card_id"]]
        row["researcher_primary_tag"] = researcher_tag
        row["researcher_decision"] = decision
        row["split_or_merge_action"] = action
        row["reallocation_rationale"] = rationale
        row["verification_status"] = "verified"
    write_csv(VALIDATION, list(validation[0]), validation)

    remove = {card_id for card_id, values in DECISIONS.items() if values[0] == "exclude"}
    remove |= EXTRA_REMOVE

    # The paid-unlock error already has an experience-quality card (GP012).
    remove.add("GP011")
    by_id["GP012"]["secondary_tag"] = "호스트상업화"
    by_id["GP012"]["researcher_memo"] += " 2차 검토에서 결제 후 잠금 오류 카드와 병합함."
    by_id["GP012"]["coding_status"] = "verified"

    # GP064 repeats the dating-profile paywall already captured by GP061.
    by_id["GP061"]["secondary_tag"] = "호스트상업화"
    by_id["GP061"]["researcher_memo"] += " 2차 검토에서 동일 발화의 결제 카드와 병합함."
    by_id["GP061"]["coding_status"] = "verified"

    # Deceptive staff attendance is primarily a trust signal, not evidence of
    # commercial scale. Retain GP081 and merge the duplicate GP080.
    by_id["GP081"]["secondary_tag"] = "호스트상업화"
    by_id["GP081"]["researcher_memo"] += " 2차 검토에서 동일 발화의 호스트상업화 카드와 병합함."
    by_id["GP081"]["coding_status"] = "verified"

    for card_id, (decision, researcher_tag, action, rationale) in DECISIONS.items():
        if card_id in remove:
            continue
        card = by_id[card_id]
        if decision == "change":
            card["primary_tag"] = researcher_tag
        card["researcher_memo"] += f" 2차 검토: {rationale}"
        card["coder"] = "Codex(AI 1차+2차 검토)"
        card["coding_status"] = "verified"

    reviewed = [card for card in cards if card["card_id"] not in remove]
    assert len({card["card_id"] for card in reviewed}) == len(reviewed)
    assert len({card["dedupe_key"] for card in reviewed}) == len(reviewed)
    write_csv(REVIEWED, card_fields, reviewed)

    existing, _ = read_csv(CANONICAL)
    preserved = [row for row in existing if not (row["source_type"] == "app_review" and row["source_id"] == "S001")]
    merged = preserved + reviewed
    assert len({row["card_id"] for row in merged}) == len(merged)
    write_csv(CANONICAL, card_fields, merged)

    positives = [card["card_id"] for card in reviewed if card["primary_tag"] == "긍정·반례"][:5]
    cluster_rows = []
    for cluster_id, name, tags, summary, need, implication in CLUSTER_DEFS:
        included = [card for card in reviewed if card["primary_tag"] in tags]
        cluster_rows.append({
            "cluster_id": cluster_id,
            "cluster_name": name,
            "included_card_ids": "|".join(card["card_id"] for card in included),
            "pattern_summary": summary,
            "need_statement": need,
            "contradictory_card_ids": "" if cluster_id == "C05" else "|".join(positives),
            "supporting_card_count": len(included),
            "source_type_count": 1,
            "confidence": "medium",
            "design_implication": implication,
            "owner": "Codex AI 2차 검토; 사람 독립 검증 미실시",
            "status": "draft_reviewed",
        })
    write_csv(CLUSTERS, list(cluster_rows[0]), cluster_rows)

    counts = defaultdict(int)
    reviews_by_tag = defaultdict(set)
    for card in reviewed:
        counts[card["primary_tag"]] += 1
        reviews_by_tag[card["primary_tag"]].add(review_key(card))
    agree = sum(row["researcher_decision"] == "agree" for row in validation)
    changed = sum(row["researcher_decision"] == "change" for row in validation)
    excluded = sum(row["researcher_decision"] == "exclude" for row in validation)
    lines = [
        "# Google Play 리뷰 2차 검토 보고",
        "",
        "## 검증 결과",
        "",
        f"- 층화 표본 20장: 유지 {agree}, 변경 {changed}, 제외 {excluded}",
        f"- 단순 일치율: {agree / len(validation):.1%} (제외·변경 전 기준)",
        "- 초기 규칙 출력 113장에서 동일 발화의 인접 태그 중복 14장을 먼저 병합해 99장으로 정리",
        f"- 99장 중 2차 원문 검토로 중복·오탐 6장을 추가 제거·병합해 최종 {len(reviewed)}장",
        f"- 기존 정성 카드에서 S001 초기 카드 2장을 대체하고 비앱 리뷰 카드 {len(preserved)}장은 보존",
        "",
        "이 검토는 동일 AI의 2차 검토이므로 독립 코더 신뢰도 검증이 아니다. 보고서에는",
        "`AI 1차 분류 → 규칙 기반 중복 제거 → AI 2차 원문 대조`로 표기해야 한다.",
        "",
        "## 2차 검토로 바뀐 기준",
        "",
        "- 타인에게 ‘가지 말라’는 권고는 작성자의 이탈 행동으로 코딩하지 않음",
        "- 파티·술모임을 언급한 도입 문장만으로 기대 불일치를 확정하지 않음",
        "- 결제 후 콘텐츠가 열리지 않는 사례는 상업화보다 경험품질로 재배치",
        "- 동일 문장의 소개팅 신호/기대 불일치, 대체서비스/이탈행동 중복을 한 카드로 병합",
        "- 지역명만으로 탐색피로를 부여하지 않고 실제 공급 부족·탐색 곤란 표현을 요구",
        "",
        "## 최종 태그 분포",
        "",
        "| 태그 | 카드 | 고유 리뷰 |",
        "|---|---:|---:|",
    ]
    for tag in sorted(counts, key=lambda key: (-counts[key], key)):
        lines.append(f"| {tag} | {counts[tag]} | {len(reviews_by_tag[tag])} |")
    lines += [
        "",
        "카드 수는 한 리뷰를 여러 발화로 분리한 값이므로 사용자 비율로 해석하지 않는다.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"validation agree={agree} change={changed} exclude={excluded}")
    print(f"reviewed_cards={len(reviewed)} canonical_cards={len(merged)} clusters={len(cluster_rows)}")


if __name__ == "__main__":
    main()
