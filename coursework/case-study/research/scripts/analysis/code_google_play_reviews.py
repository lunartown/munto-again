#!/usr/bin/env python3
"""Create an auditable AI first-pass coding of the Google Play review sample.

The script screens all 65 sampled reviews, splits reviews into rough utterance
units, and emits at most one card per primary tag per review. It deliberately
marks every card as `coded`, not `verified`; a researcher must review excerpts,
tag assignments, and multi-issue splits before affinity clustering.
"""

import csv
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_ROOT = PROJECT_ROOT / "data/reviews/google_play"
SOURCE = REVIEW_ROOT / "samples/review_sample_65.csv"
CARDS = REVIEW_ROOT / "interim/review_cards_ai.csv"
SCREENING = REVIEW_ROOT / "interim/review_screening.csv"

CARD_FIELDS = [
    "card_id", "source_type", "source_id", "utterance_id", "event_or_publish_date",
    "collected_date", "period_bucket", "platform", "source_url", "rating",
    "verbatim_excerpt", "paraphrase", "context", "trigger_signal", "behavior",
    "outcome", "alternative_service", "primary_tag", "secondary_tag", "sentiment",
    "evidence_type", "evidence_strength", "dedupe_key", "cluster_id", "need_statement",
    "researcher_memo", "pii_removed", "coder", "coding_status",
]

SCREEN_FIELDS = [
    "review_id", "rating", "review_date", "sample_group", "screening_status",
    "exclusion_reason", "generated_card_count", "ai_review_required",
]

# More specific rules come first. One review may produce several cards, but no
# more than one card for the same primary tag.
RULES = [
    {
        "tag": "대체서비스", "secondary": "이탈행동",
        "patterns": [r"넷플연가", r"다른 모임으로 떠", r"외부이탈", r"다른 데로 떠"],
        "paraphrase": "더 적합한 모임이나 운영자를 찾아 다른 서비스·외부 관계로 이동했다고 설명했다.",
        "behavior": "대체 채널로 이동", "outcome": "문토 이용 감소 또는 이탈",
        "type": "behavior",
    },
    {
        "tag": "이탈행동", "secondary": "경험품질",
        "patterns": [r"삭제", r"탈퇴", r"두번 다시", r"다시는 설치", r"떠나", r"이탈", r"비추", r"가지마", r"중단"],
        "paraphrase": "반복된 불편이나 서비스 방향 변화 뒤 이용 중단·삭제·탈퇴 의사를 밝혔다.",
        "behavior": "이용 중단 또는 회피", "outcome": "재이용 의향 저하",
        "type": "behavior",
    },
    {
        "tag": "숨은만남신호", "secondary": "기대불일치",
        "patterns": [r"소개팅", r"온라인소개팅", r"1대1매칭", r"로테이션", r"여자친구", r"남자친구", r"연애"],
        "paraphrase": "취미 커뮤니티에서 소개팅·매칭 목적이 전면화되었다고 판단했다.",
        "behavior": "서비스 목적을 재평가", "outcome": "취미 중심 서비스라는 기대 약화",
        "type": "observed_signal",
    },
    {
        "tag": "성비·조건", "secondary": "안전·신뢰",
        "patterns": [r"성비", r"여자 게스트", r"섭외 여성", r"여자분들은 꽁", r"여자만", r"남자들이 비용", r"알바"],
        "paraphrase": "성별에 따른 초대·비용 차이나 인위적인 성비 운영을 의심하거나 관찰했다.",
        "behavior": "파티 구성과 비용 구조를 평가", "outcome": "공정성과 참가자 진정성에 대한 불신",
        "type": "observed_signal",
    },
    {
        "tag": "탐색피로", "secondary": "기대불일치",
        "patterns": [r"찾아보기도 힘", r"찾으려면", r"바닷가에서 진주", r"추천.*묻", r"윗쪽에 편성", r"모임도 없", r"지방은 없", r"지역에 모임이 없", r"전북전남", r"관심지역.*없"],
        "paraphrase": "지역·추천 구조 때문에 원하는 취미 모임을 발견하기 어렵다고 보고했다.",
        "behavior": "원하는 모임을 탐색", "outcome": "탐색 비용 증가와 선택지 축소",
        "type": "outcome",
    },
    {
        "tag": "호스트상업화", "secondary": "안전·신뢰",
        "patterns": [r"호스트 수고비", r"호스트수고비", r"개인계좌", r"수수료", r"유료", r"돈 벌", r"돈장난", r"참여비", r"별점 돌려막기", r"별점 몰아주기", r"스탭이 참여자인척", r"무료로 여자", r"사탕", r"캔디"],
        "paraphrase": "호스트·플랫폼의 수익화 방식이나 인위적인 인기 신호가 경험의 질을 해친다고 인식했다.",
        "behavior": "비용과 운영 방식을 평가", "outcome": "운영자와 플랫폼에 대한 신뢰 저하",
        "type": "perception",
    },
    {
        "tag": "안전·신뢰", "secondary": "경험품질",
        "patterns": [r"당일취소", r"당일파토", r"노쇼", r"환불", r"고객센터", r"문의", r"전화번호", r"개인정보", r"가계정", r"봇", r"도용", r"범죄자", r"승인이 안", r"신뢰", r"블랙리스트", r"신고", r"제제", r"제재", r"책임 전가", r"정지먹", r"하지도 않은.*사진", r"사진만들어서"],
        "paraphrase": "취소·환불·신원·분쟁 대응 과정에서 플랫폼의 보호와 운영을 신뢰하기 어렵다고 보고했다.",
        "behavior": "문제를 신고하거나 지원을 요청", "outcome": "참여 안전감과 플랫폼 신뢰 저하",
        "type": "outcome",
    },
    {
        "tag": "기대불일치", "secondary": "숨은만남신호",
        "patterns": [r"술파티.*소개팅만", r"술모임", r"파티모임", r"파티나 모임", r"소개팅 술모임", r"변질", r"참신한 모임.*전멸", r"로테이션 소개팅.*파티"],
        "paraphrase": "다양한 취미 활동을 기대했지만 술·파티·소개팅 중심으로 변했다고 평가했다.",
        "behavior": "현재 목록과 과거 경험을 비교", "outcome": "서비스 정체성에 대한 기대 불일치",
        "type": "perception",
    },
    {
        "tag": "경험품질", "secondary": "안전·신뢰",
        "patterns": [r"오류", r"버그", r"알림", r"채팅", r"결제", r"결재", r"로그인", r"인증번호", r"(?<!가)계정", r"앱이 안", r"어플이 안", r"업데이트", r"사진전송", r"관심 표시", r"관심.*잠", r"보낸 관심.*사라", r"프로필.*(오류|네트워크|안지워)", r"시작 화면.*멈", r"아이디 찾기", r"비밀번호", r"승인"],
        "paraphrase": "앱 기능이나 운영 절차의 오류·지연 때문에 모임 이용 과정이 끊겼다고 보고했다.",
        "behavior": "재설치·재시도 또는 문의", "outcome": "이용 실패와 시간 손실",
        "type": "outcome",
    },
    {
        "tag": "긍정·반례", "secondary": "경험품질",
        "patterns": [r"좋", r"즐거", r"다양한 활동", r"다양한 경험", r"취미생활", r"취미를 공유", r"활력", r"풍요", r"값진 경험", r"주제가 정말 다양", r"선택의 폭", r"안심"],
        "paraphrase": "관심사 중심 활동과 사람 간 교류가 실제 취미 경험과 일상 만족을 높였다고 평가했다.",
        "behavior": "취미 모임에 참여하거나 반복 이용", "outcome": "취미 목적 충족과 긍정적 관계 형성",
        "type": "outcome",
    },
]

UNINFORMATIVE = [
    re.compile(r"^미사용앱[.! ]*$"),
    re.compile(r"^사람이 별로임[.! ]*$"),
    re.compile(r"^내 소중한 시간 낭비하도록 해서 짜증남 내가 운이 없었음[.! ]*$"),
]

LOW_RATING_POSITIVE = re.compile(
    r"다양한 활동.*좋|다른모임은 좋아|문토를 좋아했고|타 어플들보단 물이 좋은",
    re.I,
)


def clauses(text: str):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?。])\s+|\s+(?=\d+[.)])|\n+", text)
    return [p.strip(" -") for p in parts if p.strip(" -")]


def best_clause(text: str, patterns):
    candidates = clauses(text)
    for part in candidates:
        if any(re.search(pattern, part, re.I) for pattern in patterns):
            return part
    return text


def trigger(text: str, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(0)[:40]
    return ""


def excerpt(text: str, patterns):
    value = best_clause(text, patterns)
    return value if len(value) <= 110 else value[:107].rstrip() + "…"


def strength(text: str, tag: str):
    concrete = bool(re.search(r"\d|여러 차례|몇 번|반복|당일|삭제|탈퇴|신고|재설치|떠나", text))
    if tag in {"이탈행동", "대체서비스"} and concrete:
        return "high"
    if len(text) < 18:
        return "low"
    return "medium"


def sentiment(rating: int, tag: str, text: str):
    if tag == "긍정·반례":
        return "mixed" if rating <= 3 or re.search(r"아쉽|불편|빌런", text) else "positive"
    return "negative" if rating <= 3 else "mixed"


def alternative(text: str):
    found = []
    if "넷플연가" in text:
        found.append("넷플연가")
    if "외부이탈" in text or "만났던사람끼리" in text:
        found.append("기존 참여자 간 외부 관계")
    return " / ".join(found)


def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        reviews = list(csv.DictReader(handle))

    cards = []
    screening = []
    for review_index, row in enumerate(reviews, start=1):
        text = row["review_text"].strip()
        rating = int(row["rating"])
        matched = []
        if not any(pattern.fullmatch(text) for pattern in UNINFORMATIVE):
            for rule in RULES:
                if any(re.search(pattern, text, re.I) for pattern in rule["patterns"]):
                    if rule["tag"] == "긍정·반례" and rating <= 3 and not LOW_RATING_POSITIVE.search(text):
                        continue
                    if rule["tag"] == "이탈행동":
                        retry_context = re.search(r"삭제했다\s*다시|삭제했다가\s*다시|탈퇴\s*후\s*재가입", text)
                        forced_context = "강제탈퇴" in text and not re.search(r"비추|두번 다시|다시는 설치|이탈|떠나", text)
                        if retry_context or forced_context:
                            continue
                    matched.append(rule)

        # One generic positive counterexample card for high-rated reviews even
        # when their wording does not match a narrow phrase in the rule list.
        if rating == 5 and text and not any(r["tag"] == "긍정·반례" for r in matched):
            matched.append(RULES[-1])

        # Keep at most one card per primary tag and cap unusually broad reviews
        # so the first pass does not overweight a single author.
        unique = []
        seen_tags = set()
        for rule in matched:
            if rule["tag"] not in seen_tags:
                seen_tags.add(rule["tag"])
                unique.append(rule)
        unique = unique[:6]

        for unit_index, rule in enumerate(unique, start=1):
            card_id = f"GP{len(cards) + 1:03d}"
            short_id = row["review_id"].split("-")[0]
            cards.append({
                "card_id": card_id,
                "source_type": "app_review",
                "source_id": "S001",
                "utterance_id": f"{short_id}-{unit_index}",
                "event_or_publish_date": row["review_date_utc"][:10],
                "collected_date": row["collected_date"],
                "period_bucket": row["period_bucket"],
                "platform": "Google Play",
                "source_url": row["source_url"],
                "rating": rating,
                "verbatim_excerpt": excerpt(text, rule["patterns"]),
                "paraphrase": rule["paraphrase"],
                "context": "Google Play 공개 리뷰에서 문토 이용 경험을 회고함",
                "trigger_signal": trigger(text, rule["patterns"]),
                "behavior": rule["behavior"],
                "outcome": rule["outcome"],
                "alternative_service": alternative(text) if rule["tag"] == "대체서비스" else "",
                "primary_tag": rule["tag"],
                "secondary_tag": rule["secondary"],
                "sentiment": sentiment(rating, rule["tag"], text),
                "evidence_type": rule["type"],
                "evidence_strength": strength(text, rule["tag"]),
                "dedupe_key": f"gplay-{row['review_id']}-{rule['tag']}",
                "cluster_id": "",
                "need_statement": "",
                "researcher_memo": "AI 1차 분류. 원문 맥락·발화 분리·태그를 연구자가 검증해야 함.",
                "pii_removed": "Y",
                "coder": "Codex(AI)",
                "coding_status": "coded",
            })

        if unique:
            status, reason = "included", ""
        elif any(pattern.fullmatch(text) for pattern in UNINFORMATIVE):
            status, reason = "excluded", "구체적인 상황·신호·행동이 없는 단문"
        else:
            status, reason = "excluded", "현재 코드북과 직접 연결되는 근거가 탐지되지 않음"
        screening.append({
            "review_id": row["review_id"],
            "rating": rating,
            "review_date": row["review_date_utc"][:10],
            "sample_group": row["sample_group"],
            "screening_status": status,
            "exclusion_reason": reason,
            "generated_card_count": len(unique),
            "ai_review_required": "Y",
        })

    # Merge cards where the same exact excerpt was assigned to two conceptual
    # levels of one observation. This prevents double counting while retaining
    # the second concept as a secondary tag.
    grouped = {}
    for card in cards:
        key = (card["utterance_id"].split("-")[0], card["verbatim_excerpt"])
        grouped.setdefault(key, []).append(card)
    drop_ids = set()
    merge_pairs = [
        ("대체서비스", "이탈행동"),
        ("숨은만남신호", "기대불일치"),
        ("안전·신뢰", "경험품질"),
        ("성비·조건", "호스트상업화"),
    ]
    for group in grouped.values():
        by_tag = {card["primary_tag"]: card for card in group}
        for keep_tag, drop_tag in merge_pairs:
            if keep_tag in by_tag and drop_tag in by_tag:
                keep, drop = by_tag[keep_tag], by_tag[drop_tag]
                keep["secondary_tag"] = drop_tag
                keep["researcher_memo"] += f" 동일 발화의 {drop_tag} 카드를 2차 검토에서 병합함."
                drop_ids.add(drop["card_id"])
    cards = [card for card in cards if card["card_id"] not in drop_ids]
    for index, card in enumerate(cards, start=1):
        card["card_id"] = f"GP{index:03d}"

    for path, fields, rows in [
        (CARDS, CARD_FIELDS, cards),
        (SCREENING, SCREEN_FIELDS, screening),
    ]:
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    print(f"screened={len(screening)} included={sum(r['screening_status']=='included' for r in screening)} cards={len(cards)}")


if __name__ == "__main__":
    main()
