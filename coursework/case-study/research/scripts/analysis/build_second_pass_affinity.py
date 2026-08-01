#!/usr/bin/env python3
"""Build a reviewable second-pass affinity grouping for current Google Play reviews.

This does not define the final problem. It restructures the fresh open cards into
experience-condition, experience-value, and behavioral-result lanes. Ambiguous
or compound cards remain visibly flagged for researcher review.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[2]
CURRENT_DIR = RESEARCH_ROOT / "data/reviews/reanalysis/current"
INPUT_PATH = CURRENT_DIR / "open_cards_draft.csv"
OUTPUT_PATH = CURRENT_DIR / "affinity_second_pass_cards.csv"
SUMMARY_PATH = CURRENT_DIR / "affinity_second_pass_summary.csv"


GROUPS = {
    "C01": ("이용을 막는 앱 오류·기능 실패", "experience_condition"),
    "C02": ("앱 사용 편의와 정보 표현", "experience_condition"),
    "C03": ("모임 성사 여부의 불확실성", "experience_condition"),
    "C04": ("환불 기준과 비용 책임의 공정성", "experience_condition"),
    "C05": ("문제 발생 시 문의·해결 가능성", "experience_condition"),
    "C06": ("규칙 집행과 제재의 일관성", "experience_condition"),
    "C07": ("호스트·참여자·정보의 신뢰성", "experience_condition"),
    "C08": ("참여 전 사람과 모임을 판단할 단서", "experience_condition"),
    "C09": ("가격·수수료 대비 가치", "experience_condition"),
    "C10": ("수익 구조가 모임 구성에 미치는 영향", "experience_condition"),
    "C11": ("연애·파티 목적과 기대의 일치", "experience_condition"),
    "C12": ("특정 목적의 과다 노출로 인한 탐색 방해", "experience_condition"),
    "C13": ("원치 않는 접근과 관계 경계", "experience_condition"),
    "C14": ("필터·추천·검색을 통한 발견 가능성", "experience_condition"),
    "C15": ("지역별 모임 공급의 격차", "experience_condition"),
    "C16": ("모임 유형과 선택 폭", "experience_condition"),
    "V01": ("취미를 함께하며 얻는 활동 가치", "experienced_value"),
    "V02": ("새로운 활동을 시도하고 취향을 발견하는 가치", "experienced_value"),
    "V03": ("잘 맞는 사람과 편안하게 관계 맺는 가치", "experienced_value"),
    "V04": ("반복 모임이 만드는 관계·활동의 지속성", "experienced_value"),
    "H01": ("호스트가 모임을 개설·운영하는 조건", "host_experience"),
    "R01": ("재참여·지속 이용", "behavioral_result"),
    "R02": ("이용 중단·외부 이동", "behavioral_result"),
    "R03": ("추천·소개를 통한 유입과 확산", "behavioral_result"),
    "X00": ("맥락 부족 또는 단독 의미 없음", "hold"),
}


MANUAL_GROUP = {
    # Previously reviewed cards.
    "OCR001": "C03",
    "OCR002": "C04",
    "OCR003": "C07",
    "OCR004": "C03",
    "OCR005": "C01",
    "OCR006": "C01",
    "OCR007": "C07",
    "OCR008": "C07",
    "OCR009": "C06",
    "OCR010": "C03",
    "OCR011": "C07",
    "OCR012": "C07",
    "OCR013": "V01",
    "OCR014": "V03",
    "OCR015": "C01",
    # Clear exceptions to the first-pass keyword buckets.
    "OCR045": "C02",
    "OCR050": "C08",
    "OCR067": "V03",
    "OCR105": "V03",
    "OCR126": "C02",
    "OCR159": "C07",
    "OCR177": "C09",
    "OCR186": "C02",
    "OCR193": "C14",
    "OCR199": "C08",
    "OCR217": "C06",
    "OCR237": "C02",
    "OCR240": "C14",
    "OCR258": "C02",
    "OCR269": "C11",
    "OCR277": "R02",
    "OCR285": "C01",
    "OCR290": "C01",
    "OCR298": "C07",
    "OCR301": "X00",
    "OCR302": "V03",
    "OCR307": "C01",
    "OCR310": "C01",
    "OCR311": "C07",
    "OCR315": "R02",
    "OCR316": "C01",
    "OCR318": "C06",
    "OCR034": "C06",
    "OCR038": "C12",
    "OCR042": "C02",
    "OCR069": "R03",
    "OCR072": "R02",
    "OCR073": "C02",
    "OCR089": "V01",
    "OCR127": "C01",
    "OCR128": "C01",
    "OCR133": "C03",
    "OCR135": "R02",
    "OCR141": "C01",
    "OCR175": "C01",
    "OCR184": "C02",
    "OCR189": "C16",
    "OCR190": "C16",
    "OCR191": "C08",
    "OCR192": "R02",
    "OCR200": "X00",
    "OCR204": "R03",
    "OCR206": "C07",
    "OCR207": "R03",
    "OCR213": "R03",
    "OCR216": "C09",
    "OCR218": "C08",
    "OCR223": "V02",
    "OCR224": "V03",
    "OCR235": "C08",
    "OCR245": "V04",
    "OCR247": "R01",
    "OCR249": "C16",
    "OCR261": "C14",
    "OCR270": "C12",
    "OCR271": "C08",
    "OCR276": "C02",
    "OCR110": "V02",
    "OCR112": "R03",
    "OCR187": "H01",
    "OCR028": "X00",
    "OCR040": "X00",
    "OCR100": "V03",
    "OCR326": "C02",
    "OCR327": "C02",
    "OCR328": "C02",
}


COMPOUND_CARDS = {
    "OCR084": "기능 오류와 신규 메시지 기능 요구가 함께 있음",
    "OCR148": "분쟁 구조 평가와 소비자 부담 결과가 함께 있음",
    "OCR155": "비활성·봇 추천과 유료 재화 손실이 함께 있음",
    "OCR242": "유료 지원 요구와 모임 분위기 변질 우려가 함께 있음",
    "OCR287": "비싼 술모임 노출과 취미 모임 탐색 실패가 함께 있음",
}

COMPOUND_SPLITS = {
    "OCR060": [
        ("채팅이 불편한 점이 있긴 하지만", "채팅 기능을 사용하는 과정이 불편했다.", "C01"),
        (
            "문토를 통해 다양한 활동을 경험할 수 있어서 좋습니다.",
            "문토를 통해 다양한 활동을 경험할 수 있다는 점을 긍정적으로 평가했다.",
            "V01",
        ),
    ],
    "OCR070": [
        (
            "수도권이 아닌 지역 모임이 적은것은 아쉽지만",
            "수도권 외 지역에는 참여할 수 있는 모임이 적어 아쉬웠다.",
            "C15",
        ),
        (
            "모임을 하면서 지루한 삶에 활력이 될 수가 있었습니다.",
            "모임에 참여하면서 지루한 일상에 활력을 얻었다.",
            "V01",
        ),
    ],
    "OCR074": [
        ("지인 추천으로 시작했는데", "지인의 추천을 받아 문토를 사용하기 시작했다.", "R03"),
        (
            "생각보다 주제가 정말 다양해서 놀랐어요!",
            "예상보다 모임 주제가 다양하다는 점을 긍정적으로 평가했다.",
            "C16",
        ),
    ],
    "OCR120": [
        ("처음에 지인 추천해서 어플 사용해봤는데", "지인의 추천으로 앱을 사용하기 시작했다.", "R03"),
        (
            "생각보다 더 체계적이고 좋은 거 같아요!!",
            "앱이 예상보다 체계적으로 구성됐다고 느꼈다.",
            "C02",
        ),
    ],
    "OCR166": [
        (
            "5일 이상 여유있는 날짜의 모임은 없는데",
            "신청까지 5일 이상 여유가 있는 모임을 찾기 어려웠다.",
            "C16",
        ),
        (
            "한번 신청하면 3일전부터 환불불가인게 개별로에요.",
            "신청 후 3일 전부터 환불이 불가능한 기준을 부정적으로 평가했다.",
            "C04",
        ),
    ],
    "OCR172": [
        (
            "본인 사진인지 검증안해서 타인 사진 도용한 사람도 있고",
            "프로필 사진의 본인 여부가 검증되지 않아 타인 사진 도용을 경험했다.",
            "C07",
        ),
        ("어플 오류도 심해요.", "취향인연을 이용하며 앱 오류가 심하다고 느꼈다.", "C01"),
    ],
    "OCR182": [
        (
            "가까운 지역에 모임이 없을뿐만 아니라",
            "가까운 지역에서 참여할 모임을 찾지 못했다.",
            "C15",
        ),
        (
            "회원탈퇴 과정도 복잡하게 되어 있어 비추합니다",
            "회원 탈퇴 과정이 복잡하다고 느껴 앱을 추천하지 않았다.",
            "C02",
        ),
    ],
    "OCR210": [
        (
            "지방사람들은 이용하는 사람이 적어서 아쉬워서 한번 씩 서울에서 모임을 찾아 참여합니다",
            "지방 이용자가 적어 서울의 모임을 찾아 참여했다.",
            "C15",
        ),
        (
            "연애 이야기 관련 모임이였는데 제가 그렇게 썸이 긴지 몰랐습니다.",
            "연애 이야기 모임에 참여해 자신의 관계를 새롭게 이해했다.",
            "C11",
        ),
    ],
    "OCR231": [
        (
            "유료소셜링이 많아진 만큼 활성화가 잘 되어 너무 좋다고 생각합니다",
            "유료 소셜링 증가와 모임 활성화를 긍정적으로 평가했다.",
            "C16",
        ),
        (
            "취미나 사람간의 교류 로 인한 친목 위주가 아닌 소개팅 어플이 되어 가는거 같아서 좀 안타깝긴 합니다",
            "취미·교류 중심에서 소개팅 앱으로 변해간다고 느껴 아쉬워했다.",
            "C12",
        ),
    ],
    "OCR265": [
        (
            "문토 소셜링에서 친해진 친구들이 취미생활과 결이 잘 맞아서 오히려 학창시절 친구들보다자주 봐요",
            "취미 성향이 잘 맞는 친구를 만나 기존 친구보다 자주 관계를 이어갔다.",
            "V04",
        ),
        (
            "재테크, 문화생활 등 정말 다양한 종류의 소셜링들이 있어서 알찬 주말 혹은 퇴근 시간을 보낼 수 있어요",
            "다양한 종류의 소셜링으로 주말과 퇴근 후 시간을 알차게 보냈다.",
            "V01",
        ),
    ],
    "OCR272": [
        (
            "수준 이하의 인성으로 운영하는 호스트, 참여자 돈으로 술먹고 지인들 불러 놀려고 모임 여는 호스트",
            "참여자 비용을 사적으로 이용하는 호스트가 있다고 인식했다.",
            "C07",
        ),
        (
            "여기저기서 모객해와서 참여자마다 다 참여비가 다른 모임들",
            "같은 모임에서도 참여자마다 참가비가 다르게 책정되는 일을 경험했다고 밝혔다.",
            "C10",
        ),
    ],
    "OCR314": [
        (
            "요즘 너무 무의미하고 다 비슷비슷한 술파티로 뒤덮여 있어요 차단해도 끝이 없고",
            "비슷한 술 파티가 과도하게 노출되고 차단해도 계속 보였다.",
            "C12",
        ),
        (
            "질 나쁜 모객 메시지도 너무 많이 와서 짜증나요",
            "원하지 않는 모객 메시지를 반복해서 받았다.",
            "C13",
        ),
    ],
}


EMPTY_FRAGMENTS = {
    "OCR029", "OCR032", "OCR035", "OCR036", "OCR041", "OCR058",
    "OCR080", "OCR082", "OCR097", "OCR113", "OCR131",
    "OCR156", "OCR180", "OCR195", "OCR196",
    "OCR212", "OCR228", "OCR230", "OCR232", "OCR233", "OCR236",
    "OCR238", "OCR241", "OCR254", "OCR255", "OCR278",
    "OCR284", "OCR296", "OCR297", "OCR303", "OCR304", "OCR305", "OCR308",
    "OCR319", "OCR325", "OCR329", "OCR330",
}


def has(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE))


def assign_group(row: dict[str, str]) -> str:
    card_id = row["card_id"]
    if card_id in EMPTY_FRAGMENTS:
        return "X00"
    if card_id in MANUAL_GROUP:
        return MANUAL_GROUP[card_id]

    text = f'{row["source_span"]} {row["card_text"]}'
    first = row["cluster_candidate"]

    if first == "P01":
        if has(text, r"가계정|도용|개인정보|본인 사진"):
            return "C07"
        if has(text, r"깔끔|인터페이스|UI|접근성|신청 절차|간편|편리|보기 편|멤버 검색|결제내역|탈퇴 후"):
            return "C02"
        return "C01"

    if first == "P02":
        if has(text, r"고객센터|문의|답장|답변|상담|소통"):
            return "C05"
        if has(text, r"환불|책임 주체|부담.*떠안|3일"):
            return "C04"
        return "C03"

    if first == "P03":
        if has(text, r"매너 온도|후기|평점관리|클린"):
            return "C08"
        if has(text, r"규정|제재|제제|정지|벌점|보호규정|필터링|문제해결|운영"):
            return "C06"
        return "C07"

    if first == "P04":
        if has(text, r"유료.*전환|돈벌|비싼 술모임.*편성|무료.*여자|참여자.*다 참여비|개인계좌"):
            return "C10"
        return "C09"

    if first == "P05":
        if has(text, r"DM|디엠|플러팅|모객 메시지"):
            return "C13"
        if has(text, r"많아져|만 남|뒤덮|변질|찾기|노출|전멸|따로 묶"):
            return "C12"
        return "C11"

    if first == "P06":
        if has(text, r"지방|수도권|서울|경기권|대전|부산|전북|전남|경남|가까운 지역"):
            return "C15"
        if has(text, r"필터|추천|찾|요일|날짜|위치|관심지역|노출"):
            return "C14"
        return "C16"

    if first == "P07":
        if has(text, r"새로운 경험|도전|배우|발견|클래스|버킷리스트|처음|나 자신|리프래시"):
            return "V02"
        return "V01"

    if first == "P08":
        return "V03"

    if first == "P09":
        if has(text, r"호스트|모임.*열|소셜링.*열|개설"):
            return "H01"
        if has(text, r"지속|꾸준|매주|클럽"):
            return "V04"
        return "R01"

    if first == "P10":
        return "R02"

    # Recover meaningful cards that the first-pass keyword scan missed.
    if has(text, r"알람|알림"):
        return "C01"
    if has(text, r"중복되게 만나|사전에 확인"):
        return "C08"
    if has(text, r"교류 중|친구.*4년|이어"):
        return "V04"
    if has(text, r"좋은 사람|도와|힘이 됐|관계|외로움"):
        return "V03"
    if has(text, r"모임|소셜링.*참여"):
        return "V01"
    return "X00"


def polarity(row: dict[str, str]) -> str:
    text = f'{row["source_span"]} {row["card_text"]}'
    negative = has(
        text,
        r"불편|오류|안.?되|없|아쉽|별로|문제|취소|파토|노쇼|"
        r"비싸|낭비|정지|제재|짜증|실망|변질|도용|범죄|갑질|힘들",
    )
    positive = has(
        text,
        r"좋|즐겁|재밌|만족|유익|편리|편안|감사|풍요|특별|"
        r"추천|매력|안심|활력|보람|알차",
    )
    if negative and positive:
        return "mixed"
    if negative:
        return "negative"
    if positive:
        return "positive"
    return "neutral"


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    output = []
    review_sets: dict[str, set[str]] = defaultdict(set)
    april_review_sets: dict[str, set[str]] = defaultdict(set)
    other_review_sets: dict[str, set[str]] = defaultdict(set)
    low_rating_review_sets: dict[str, set[str]] = defaultdict(set)
    high_rating_review_sets: dict[str, set[str]] = defaultdict(set)
    card_counts: dict[str, int] = defaultdict(int)
    polarity_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    expanded_rows: list[tuple[dict[str, str], str | None]] = []
    for row in rows:
        splits = COMPOUND_SPLITS.get(row["card_id"])
        if not splits:
            expanded_rows.append((row, None))
            continue
        for index, (source_span, card_text, group_id) in enumerate(splits, start=1):
            split_row = {
                **row,
                "card_id": f'{row["card_id"]}-{index}',
                "unit_index": f'{row["unit_index"]}.{index}',
                "source_span": source_span,
                "card_text": card_text,
            }
            expanded_rows.append((split_row, group_id))

    for row, split_group in expanded_rows:
        group_id = split_group or assign_group(row)
        group_name, lane = GROUPS[group_id]
        row_polarity = polarity(row)
        review_state = "needs_split" if row["card_id"] in COMPOUND_CARDS else "second_pass_grouped"
        output.append(
            {
                **row,
                "affinity_group": group_id,
                "affinity_group_name": group_name,
                "experience_lane": lane,
                "polarity": row_polarity,
                "second_pass_status": review_state,
                "review_note": COMPOUND_CARDS.get(row["card_id"], ""),
            }
        )
        card_counts[group_id] += 1
        review_sets[group_id].add(row["corpus_id"])
        if row["cohort"] == "april_2026_burst":
            april_review_sets[group_id].add(row["corpus_id"])
        else:
            other_review_sets[group_id].add(row["corpus_id"])
        if int(row["rating"]) <= 3:
            low_rating_review_sets[group_id].add(row["corpus_id"])
        else:
            high_rating_review_sets[group_id].add(row["corpus_id"])
        polarity_counts[group_id][row_polarity] += 1

    fields = list(output[0].keys())
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)

    summary = []
    for group_id, (group_name, lane) in GROUPS.items():
        summary.append(
            {
                "affinity_group": group_id,
                "affinity_group_name": group_name,
                "experience_lane": lane,
                "card_count": card_counts[group_id],
                "unique_review_count": len(review_sets[group_id]),
                "april_burst_unique_reviews": len(april_review_sets[group_id]),
                "other_recent_unique_reviews": len(other_review_sets[group_id]),
                "low_rating_unique_reviews": len(low_rating_review_sets[group_id]),
                "high_rating_unique_reviews": len(high_rating_review_sets[group_id]),
                "positive_cards": polarity_counts[group_id]["positive"],
                "negative_cards": polarity_counts[group_id]["negative"],
                "mixed_cards": polarity_counts[group_id]["mixed"],
                "neutral_cards": polarity_counts[group_id]["neutral"],
                "status": "second_pass_complete_not_problem_definition",
            }
        )

    with SUMMARY_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    print(f"cards={len(output)}")
    print(f"cards_split={len(COMPOUND_SPLITS)}")
    print(f"compound_cards_remaining={len(COMPOUND_CARDS)}")
    print(f"output={OUTPUT_PATH}")
    print(f"summary={SUMMARY_PATH}")


if __name__ == "__main__":
    main()
