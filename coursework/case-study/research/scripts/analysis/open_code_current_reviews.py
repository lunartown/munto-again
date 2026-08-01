#!/usr/bin/env python3
"""Create a fresh, traceable first-pass open coding of current reviews.

Inputs are limited to the new 12-month raw-review corpus and its screening
decisions. Existing review cards, clusters, and findings are not read.

This is a first pass for researcher review, not a final affinity result.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
CURRENT_DIR = RESEARCH_ROOT / "data/reviews/reanalysis/current"
CORPUS_PATH = CURRENT_DIR / "google_play_current_12m_120.csv"
SCREENING_PATH = CURRENT_DIR / "screening_decisions_120.csv"
CARDS_PATH = CURRENT_DIR / "open_cards_draft.csv"
SUMMARY_PATH = CURRENT_DIR / "cluster_candidates_draft.csv"
AMBIGUOUS_PATH = CURRENT_DIR / "ambiguous_cards_for_review.csv"

MANUAL_UNITS = {
    "CUR001": [
        {
            "source": "신청한 모임 시간 다 돼가는데 승인이 안 돼서 호스트 문의하려고 했더니 문의가 안 됨",
            "card": "모임 시간이 다 되어가는데 승인이 되지 않았고 호스트에게 문의할 수도 없었다.",
        },
        {
            "source": "이런 경우 환불이 되는지도 모르겠음",
            "card": "승인되지 않은 모임의 환불 가능 여부를 알 수 없었다.",
        },
    ],
    "CUR002": [
        {
            "source": "전화번호 뒷자리 요구하고",
            "card": "대전권 소셜링에서 전화번호 뒷자리를 요구받았다.",
        },
        {
            "source": "항상 당일취소 당하네요 앱 사용하면서 5번정도 소셜링 신청했는데 모임 진행된적이 단 한 번도 없어요",
            "card": "대전권에서 소셜링을 약 5번 신청했지만 당일 취소가 반복돼 실제 진행된 모임이 한 번도 없었다.",
        },
    ],
    "CUR003": [
        {
            "source": "갠톡이 굉장히 늦게 오고",
            "card": "개인 채팅 메시지가 늦게 도착했다.",
        },
        {
            "source": "알림이 여러번 뜨는 등",
            "card": "같은 알림이 여러 번 표시됐다.",
        },
    ],
    "CUR004": [
        {
            "source": "호스트들끼리 자기네들 마음에 안드는 참여자 있으면 시비거리 만들어서 쫒아내고",
            "card": "작성자는 호스트가 마음에 들지 않는 참여자를 모임에서 내보내는 일이 있다고 인식했다.",
        },
        {
            "source": "호스트들끼리 맘에 안드는 참여자에 대해 블랙리스트 공유로 모임활동 방해",
            "card": "작성자는 호스트들이 참여자 블랙리스트를 공유해 다른 모임 활동까지 방해한다고 인식했다.",
        },
        {
            "source": "참여자들에 대한 보호규정은 더 강화하고 지켜줘야 될 필요가 있으며 모든 호스트들은 더 숨막힐 정도로 엄격하게 처리하고",
            "card": "참여자 보호 규정을 강화하고 신고된 호스트에게 더 엄격한 제재를 적용하기를 원했다.",
        },
    ],
    "CUR005": [
        {
            "source": "소셜링이 전부 다 당일파토가 나고 있으며",
            "card": "대전권에서 확인한 소셜링이 당일 취소되는 일을 반복해서 경험했다고 밝혔다.",
        },
        {
            "source": "주회하는 사람들 대부분이 전화번호등을 요구하면서",
            "card": "대전권 소셜링 주최자들이 전화번호 등을 요구했다고 밝혔다.",
        },
        {
            "source": "클럽은 방장이 하지도 않은 소셜링 한 것처럼 사진만들어서 올리구 있구요",
            "card": "클럽 운영자가 진행하지 않은 소셜링을 진행한 것처럼 사진을 게시했다고 주장했다.",
        },
    ],
    "CUR006": [
        {
            "source": "혼자서 할 때보다 즐거운 취미 생활! 문토 덕분에 많이 즐거운 요즘이에요",
            "card": "다른 사람과 함께 취미를 하면서 혼자 할 때보다 즐거웠고 일상도 더 즐거워졌다고 느꼈다.",
        },
        {
            "source": "편안하게 대화할 수 있는 모임",
            "card": "모임에서 다른 사람들과 편안하게 대화할 수 있었다.",
        },
    ],
    "CUR007": [
        {
            "source": "업댓후 만들어진 모임에 채팅이안되요 복구좀해주세요",
            "card": "앱 업데이트 후 새로 만들어진 모임에서 채팅을 사용할 수 없어 기능 복구를 요청했다.",
        },
    ],
}

MANUAL_CLUSTER_OVERRIDES = {
    ("CUR001", 1): "P02",
    ("CUR001", 2): "P02",
    ("CUR002", 1): "P03",
    ("CUR002", 2): "P02",
    ("CUR003", 1): "P01",
    ("CUR003", 2): "P01",
    ("CUR004", 1): "P03",
    ("CUR004", 2): "P03",
    ("CUR004", 3): "P03",
    ("CUR005", 1): "P02",
    ("CUR005", 2): "P03",
    ("CUR005", 3): "P03",
    ("CUR006", 1): "P07",
    ("CUR006", 2): "P08",
    ("CUR007", 1): "P01",
}


# These are provisional semantic buckets used only to make the first pass
# reviewable. They were defined from the current raw corpus, not prior outputs.
CLUSTERS = {
    "P01": (
        "앱 접근·기본 기능",
        (
            r"로그인|인증번호|계정|업데이트|앱이? 안|어플이? 안|안 열",
            r"채팅|알림|네트워크|버그|오류|렉|튕|프로필|사진|결제오류",
            r"멤버 검색|만족도 조사|복구|자동 로그인|가입",
            r"인터페이스|UI|깔끔|감성|접근성|신청 절차|편리",
            r"탭이 안|관심 보내기|시작 화면|결재내역|30일",
        ),
    ),
    "P02": (
        "취소·환불·문의 해결",
        (
            r"환불|당일.?취소|당일.?파토|노쇼|승인",
            r"고객센터|문의|답변|상담|책임 주체",
            r"참석이 불가|부담.*떠안|상세한 설명",
        ),
    ),
    "P03": (
        "규칙·제재·신뢰",
        (
            r"신고|제재|제제|정지|강제탈퇴|벌점|블랙리스트",
            r"호스트.*갑질|스태프|가계정|범죄자|사진 도용|개인정보",
            r"알바|섭외|평점|온도|보호규정|규정",
            r"나이를 속|운영은 진짜 못|참여자.*보호",
        ),
    ),
    "P04": (
        "비용·상업화",
        (
            r"유료|수수료|수고비|노쇼방지비|참여비|모임비",
            r"비싸|과금|캔디|사탕|돈|비용|개인계좌|캐시백",
            r"꽁술|돈벌|삥뜯",
        ),
    ),
    "P05": (
        "소개팅·술·파티 성격",
        (
            r"소개팅|술모임|술파티|파티|짝짓기|취향인연",
            r"여자친구|남자친구|연애|성비|플러팅|혼성",
            r"떳다방|짝짓기",
        ),
    ),
    "P06": (
        "탐색·지역·공급",
        (
            r"지역|지방|서울|경기권|대전|부산|전북|전남|경남",
            r"모임.*없|찾기|찾으|필터|카테고리|추천|노출",
            r"관심지역|요일|날짜|위치|선택",
            r"취지에.?맞는.*찾|취향에 맞는 모임.*쉽게",
        ),
    ),
    "P07": (
        "취미·활동·새로운 경험",
        (
            r"취미|활동|클래스|경험|자기계발|강연|운동",
            r"베이킹|드로잉|독서|등산|러닝|카약|나들이",
            r"다양한 모임|다양한 소셜링|주제|버킷리스트",
            r"즐거운 요즘|풍요|리프래시|설레임|힐링|의미 있는 시간",
            r"유익한 모임|시간 가는 줄|재밌",
        ),
    ),
    "P08": (
        "사람·관계·대화",
        (
            r"좋은.?사람|친구|인연|대화|공감대|멤버",
            r"사람.*만나|사람들과|사람.*교류|사회성|함께|연결",
            r"편안하게|분위기|추억|사람이 별로|정상적인 사람",
            r"결이 맞|취향이 맞|취향.*멤버",
            r"농담|게임|중복되게 만나",
        ),
    ),
    "P09": (
        "반복 이용·운영 지속",
        (
            r"지속|꾸준|매주|자주 이용|계속 이용|애용",
            r"호스트|모임.*열|소셜링.*열|개설|클럽",
            r"\d+년|여러 번|반복|첫.?모임|첫.?소셜링",
            r"앞으로도|좋은 모임.*생기|계속.*이어",
        ),
    ),
    "P10": (
        "이용 중단·외부 이동",
        (
            r"삭제|탈퇴|두번 다시|더 이상.*않|이탈",
            r"다른.*(?:앱|어플).*사용|그.*(?:앱|어플).*사용",
            r"넷플연가|외부이탈|떠나",
            r"사용.*않|미사용|비추|가지.?말",
            r"시간.*낭비",
        ),
    ),
}

PROBLEM_PATTERN = re.compile(
    r"불편|안.?되|없|오류|버그|렉|튕|늦|중복|짜증|아쉽|실망|"
    r"별로|문제|취소|파토|노쇼|정지|삭제|탈퇴|과금|비싸|"
    r"신뢰.*떨어|힘들|어렵|낭비|갑질|범죄|도용"
)
VALUE_PATTERN = re.compile(
    r"좋|즐겁|재밌|만족|유익|편리|편안|활력|보람|감사|"
    r"풍요|특별|추천|장점|가치|추억"
)
NEED_PATTERN = re.compile(
    r"해.?주세요|바랍니다|했으면|필요|개선|지원|원합니다|"
    r"바꿔|강화|추가|생기면|보강|할 수 있게"
)
BEHAVIOR_PATTERN = re.compile(
    r"신청|참여|사용|이용|설치|삭제|탈퇴|문의|신고|차단|"
    r"재가입|재설치|열었|만들|찾|결제|지출|가입"
)
OUTCOME_PATTERN = re.compile(
    r"한 번도|계속|더 이상|앞으로도|다시.*않|이탈|떠나|"
    r"만났|친구.*만들|교류.*중|진행.*않|시간.*낭비"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def split_units(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    # Numbered lists in long reviews are strong author-provided boundaries.
    text = re.sub(r"(?<!\d)(?<!\.)\s+([1-9]\.)", r" || \1", text)
    chunks = []
    for numbered_chunk in text.split("||"):
        numbered_chunk = numbered_chunk.strip()
        if not numbered_chunk:
            continue
        numbered_chunk = re.sub(r"^[1-9]\.\s*", "", numbered_chunk)
        sentence_chunks = re.split(r"(?<=[.!?])\s+", numbered_chunk)
        for chunk in sentence_chunks:
            chunk = chunk.strip(" \t")
            if chunk:
                if (
                    chunks
                    and len(chunk) <= 14
                    and re.search(
                        r"감사|화이팅|번창|평화|^[^가-힣A-Za-z0-9]+$",
                        chunk,
                    )
                ):
                    chunks[-1] = f"{chunks[-1]} {chunk}"
                else:
                    chunks.append(chunk)
    return chunks or [text]


def card_roles(text: str) -> str:
    roles = []
    if PROBLEM_PATTERN.search(text):
        roles.append("problem")
    if VALUE_PATTERN.search(text):
        roles.append("value")
    if NEED_PATTERN.search(text):
        roles.append("need")
    if BEHAVIOR_PATTERN.search(text):
        roles.append("behavior")
    if OUTCOME_PATTERN.search(text):
        roles.append("outcome")
    return "|".join(roles or ["perception"])


def evidence_specificity(text: str) -> str:
    concrete_signals = (
        bool(re.search(r"\d|번|당일|업데이트 후|삭제.*다시|문의|신고", text))
        + bool(BEHAVIOR_PATTERN.search(text))
        + bool(re.search(r"채팅|알림|환불|로그인|필터|전화번호|사진", text))
    )
    if concrete_signals >= 2:
        return "high"
    if concrete_signals == 1 or len(text) >= 35:
        return "medium"
    return "low"


def scope_for(text: str) -> str:
    if re.search(r"들었|얘기.*나오|분들이 있었|사람들이.*말", text):
        return "hearsay_or_collective_claim"
    if re.search(r"것 같|느낌|생각|인식|아닐까|인듯", text):
        return "perception"
    return "firsthand_or_direct_claim"


def cluster_scores(text: str) -> dict[str, int]:
    scores = {}
    for cluster_id, (_, patterns) in CLUSTERS.items():
        score = sum(bool(re.search(pattern, text, re.I)) for pattern in patterns)
        if score:
            scores[cluster_id] = score
    return scores


def primary_cluster(text: str) -> tuple[str, str, bool]:
    scores = cluster_scores(text)
    if not scores:
        return "U00", "미분류", True
    highest = max(scores.values())
    winners = [cluster_id for cluster_id, score in scores.items() if score == highest]
    selected = winners[0]
    return selected, CLUSTERS[selected][0], len(winners) > 1


def main() -> None:
    corpus = {row["corpus_id"]: row for row in read_rows(CORPUS_PATH)}
    screening = read_rows(SCREENING_PATH)
    included_ids = [
        row["corpus_id"]
        for row in screening
        if row["inclusion_status"] == "include"
    ]
    screening_by_id = {row["corpus_id"]: row for row in screening}

    cards = []
    card_number = 0
    for corpus_id in included_ids:
        review = corpus[corpus_id]
        manual_units = MANUAL_UNITS.get(corpus_id)
        if manual_units:
            units = manual_units
        else:
            units = [
                {"source": unit, "card": unit}
                for unit in split_units(review["review_text"])
            ]
        for unit_index, unit_record in enumerate(units, start=1):
            source_span = unit_record["source"]
            card_text = unit_record["card"]
            card_number += 1
            override = MANUAL_CLUSTER_OVERRIDES.get((corpus_id, unit_index))
            if override:
                cluster_id = override
                cluster_name = CLUSTERS[override][0]
                tied = False
            else:
                cluster_id, cluster_name, tied = primary_cluster(card_text)
            cards.append(
                {
                    "card_id": f"OCR{card_number:03d}",
                    "corpus_id": corpus_id,
                    "review_id": review["review_id"],
                    "cohort": review["cohort"],
                    "rating": review["rating"],
                    "unit_index": unit_index,
                    "source_span": source_span,
                    "card_text": card_text,
                    "card_role": card_roles(card_text),
                    "evidence_specificity": evidence_specificity(card_text),
                    "evidence_scope": scope_for(card_text),
                    "cluster_candidate": cluster_id,
                    "cluster_candidate_name": cluster_name,
                    "cluster_tie": "Y" if tied else "N",
                    "special_flag": screening_by_id[corpus_id]["special_flag"],
                    "review_status": "first_pass_unverified",
                }
            )

    by_cluster: dict[str, list[dict[str, object]]] = defaultdict(list)
    for card in cards:
        by_cluster[str(card["cluster_candidate"])].append(card)

    summary = []
    for cluster_id in [*CLUSTERS, "U00"]:
        cluster_cards = by_cluster.get(cluster_id, [])
        if not cluster_cards:
            continue
        review_ids = {str(card["corpus_id"]) for card in cluster_cards}
        april_ids = {
            str(card["corpus_id"])
            for card in cluster_cards
            if card["cohort"] == "april_2026_burst"
        }
        other_ids = review_ids - april_ids
        low_ids = {
            str(card["corpus_id"])
            for card in cluster_cards
            if int(str(card["rating"])) <= 3
        }
        event_ids = {
            str(card["corpus_id"])
            for card in cluster_cards
            if "event_declared" in str(card["special_flag"])
        }
        candidates = sorted(
            cluster_cards,
            key=lambda card: (
                {"high": 0, "medium": 1, "low": 2}[
                    str(card["evidence_specificity"])
                ],
                abs(len(str(card["source_span"])) - 90),
            ),
        )
        representative_ids = []
        seen_reviews = set()
        for card in candidates:
            corpus_id = str(card["corpus_id"])
            if corpus_id in seen_reviews:
                continue
            representative_ids.append(str(card["card_id"]))
            seen_reviews.add(corpus_id)
            if len(representative_ids) == 3:
                break

        cluster_name = (
            CLUSTERS[cluster_id][0] if cluster_id in CLUSTERS else "미분류"
        )
        summary.append(
            {
                "cluster_candidate": cluster_id,
                "cluster_candidate_name": cluster_name,
                "card_count": len(cluster_cards),
                "unique_review_count": len(review_ids),
                "april_burst_unique_reviews": len(april_ids),
                "other_recent_unique_reviews": len(other_ids),
                "low_rating_unique_reviews": len(low_ids),
                "event_declared_unique_reviews": len(event_ids),
                "representative_card_ids": "|".join(representative_ids),
                "status": "candidate_requires_researcher_review",
            }
        )

    ambiguous = [
        card
        for card in cards
        if (
            card["cluster_candidate"] == "U00"
            and len(str(card["source_span"])) >= 20
        )
        or (
            card["cluster_tie"] == "Y"
            and card["evidence_specificity"] == "high"
            and len(str(card["source_span"])) >= 60
        )
        or card["evidence_scope"] == "hearsay_or_collective_claim"
        or len(str(card["source_span"])) > 240
    ]

    card_fields = [
        "card_id",
        "corpus_id",
        "review_id",
        "cohort",
        "rating",
        "unit_index",
        "source_span",
        "card_text",
        "card_role",
        "evidence_specificity",
        "evidence_scope",
        "cluster_candidate",
        "cluster_candidate_name",
        "cluster_tie",
        "special_flag",
        "review_status",
    ]
    summary_fields = [
        "cluster_candidate",
        "cluster_candidate_name",
        "card_count",
        "unique_review_count",
        "april_burst_unique_reviews",
        "other_recent_unique_reviews",
        "low_rating_unique_reviews",
        "event_declared_unique_reviews",
        "representative_card_ids",
        "status",
    ]
    write_rows(CARDS_PATH, cards, card_fields)
    write_rows(SUMMARY_PATH, summary, summary_fields)
    write_rows(AMBIGUOUS_PATH, ambiguous, card_fields)

    print(f"Included reviews: {len(included_ids)}")
    print(f"Open cards: {len(cards)}")
    print(f"Candidate clusters: {len(summary)}")
    print(f"Ambiguous cards: {len(ambiguous)}")
    print("Roles:", dict(Counter(str(card["card_role"]) for card in cards)))
    print(f"Wrote {CARDS_PATH}")
    print(f"Wrote {SUMMARY_PATH}")
    print(f"Wrote {AMBIGUOUS_PATH}")


if __name__ == "__main__":
    main()
