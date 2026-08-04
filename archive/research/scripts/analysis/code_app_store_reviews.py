#!/usr/bin/env python3
"""Curated utterance-level coding for the 30-review App Store comparison sample."""

import csv
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_ROOT = PROJECT_ROOT / "data/reviews/app_store"
SAMPLE = REVIEW_ROOT / "samples/review_sample_30.csv"
CARDS = REVIEW_ROOT / "processed/review_cards_reviewed.csv"
SCREENING = REVIEW_ROOT / "interim/review_screening.csv"
SOURCE_ID = "S006"

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
    "exclusion_reason", "generated_card_count", "review_status",
]


def unit(review_id, primary, secondary, excerpt, paraphrase, behavior, outcome,
         evidence_type, strength="medium", sentiment=None, alternative="", memo=""):
    return {
        "review_id": review_id, "primary": primary, "secondary": secondary,
        "excerpt": excerpt, "paraphrase": paraphrase, "behavior": behavior,
        "outcome": outcome, "evidence_type": evidence_type, "strength": strength,
        "sentiment": sentiment, "alternative": alternative, "memo": memo,
    }


UNITS = [
    unit("12817594399", "안전·신뢰", "경험품질", "신고 지들 ㅈ대로 받고 정정도 안해 납득도 못시켜", "신고 접수와 정정 기준을 납득할 수 없었다고 평가했다.", "운영 판단에 이의를 제기", "플랫폼 신뢰 저하", "perception"),
    unit("12817594399", "이탈행동", "안전·신뢰", "걍 안써", "운영 대응에 불만을 느껴 더 이상 사용하지 않겠다고 밝혔다.", "이용 중단", "재이용 의향 상실", "behavior", "high"),

    unit("12779255589", "숨은만남신호", "기대불일치", "거의 다 이름만 ‘포틀럭파티’인 소개팅파티에요", "표면 명칭과 달리 다수 모임이 소개팅 파티라고 판단했다.", "모임 목록의 실제 목적을 평가", "취미 중심 서비스 기대 약화", "observed_signal", "high"),
    unit("12779255589", "탐색피로", "기대불일치", "독서나 무료로 같이 카페만 가는 그런 모임도 거의 없더라구요", "독서·카페 같은 자연스러운 취미 모임을 찾기 어렵다고 보고했다.", "원하는 취미 모임을 탐색", "선택지 부족과 탐색 비용 증가", "outcome", "high"),
    unit("12779255589", "호스트상업화", "경험품질", "기본 2-3만원부터 시작해서 들어가는 비용도 엄청 가격도 세고", "기본 참가비와 판매형 모임이 많아졌다고 평가했다.", "비용과 상품 구성을 비교", "자연스러운 모임의 참여 장벽 증가", "perception", "medium"),
    unit("12779255589", "안전·신뢰", "호스트상업화", "자기맘에안들면 온도테러하거나 차단해버리는", "호스트가 평점과 차단을 자의적으로 사용할 수 있다고 우려했다.", "호스트 운영을 평가", "호스트와 평점 체계에 대한 불신", "perception", "low", memo="주변에서 들었다는 간접 경험이므로 증거 강도를 낮춤"),
    unit("12779255589", "이탈행동", "기대불일치", "몇번보자마자 그냥 탈퇴했어요", "재가입 후 목록을 확인했지만 기대와 달라 다시 탈퇴했다고 밝혔다.", "재가입 후 탈퇴", "서비스 이탈", "behavior", "high"),

    unit("12775350030", "안전·신뢰", "경험품질", "다운을 받으니 결제가 됐어요 어떻게하면 환불을 받을 수 있을까요?", "앱 설치 뒤 예상하지 못한 결제가 발생했다고 인식하고 환불 경로를 찾았다.", "환불 방법 문의", "결제 신뢰와 통제감 저하", "outcome", "medium"),

    unit("12771672470", "긍정·반례", "안전·신뢰", "참석자 프로필 사진들 보일 때가 편하고 좋았어요", "참석자 정보를 미리 볼 수 있었던 과거 탐색 방식이 판단에 도움이 됐다고 평가했다.", "참석자 정보를 확인", "참여 판단의 확신 증가", "outcome", "medium", "mixed"),
    unit("12771672470", "탐색피로", "경험품질", "갈만한 소규모 소셜링도 거의 없고 찾기 힘들어서", "참여할 만한 소규모 모임의 공급과 발견 가능성이 낮다고 보고했다.", "소규모 모임을 탐색", "선택지 부족과 탐색 비용 증가", "outcome", "high"),
    unit("12771672470", "이탈행동", "탐색피로", "잘 안쓰게 돼요", "원하는 소규모 모임을 찾기 어려워 사용 빈도가 낮아졌다고 밝혔다.", "이용 빈도 감소", "소극적 이탈", "behavior", "high"),

    unit("12751810763", "탐색피로", "경험품질", "모임 하나도 안나와요", "검색 결과에 모임이 나타나지 않는다고 보고했다.", "모임을 검색", "선택지 부재", "outcome", "low"),

    unit("12682998475", "경험품질", "안전·신뢰", "30분 동안 20-30명 인원이 비 맞으며 대기", "우천 대비 없이 다수 참가자가 장시간 대기한 진행 실패를 경험했다.", "현장에서 대기 후 귀가", "시간 손실과 모임 경험 악화", "outcome", "high"),
    unit("12682998475", "안전·신뢰", "호스트상업화", "계정 여러개 돌려서 온도 테러함", "부정 리뷰 후 복수 계정으로 평점 보복을 받았다고 주장했다.", "경험에 낮은 평점을 남김", "보복 우려와 플랫폼 신뢰 저하", "outcome", "medium", memo="작성자 주장으로 사실관계는 별도 확인 필요"),
    unit("12682998475", "이탈행동", "경험품질", "최악의 경험을 마지막으로 앱 삭제함", "반복 이용 후 최악의 현장 경험을 계기로 앱을 삭제했다고 밝혔다.", "앱 삭제", "서비스 이탈", "behavior", "high"),

    unit("12677314409", "경험품질", "안전·신뢰", "카카오 로그인 계속 팅겨서 로그인 안되고", "로그인 오류 때문에 참여를 진행하지 못했다고 보고했다.", "로그인을 반복 시도", "모임 참여 중단", "outcome", "medium"),
    unit("12658909742", "경험품질", "안전·신뢰", "카톡 로그인 시도 10번 넘게 했는데 계속 안됩니다", "열 차례 넘게 로그인에 실패했다고 보고했다.", "로그인 반복 시도", "서비스 진입 실패", "outcome", "high"),
    unit("12538903996", "경험품질", "안전·신뢰", "프사 변경하려고 하면 에러메시지가 뜨네요", "프로필 사진 변경 기능에서 오류를 경험했다.", "프로필 변경 시도", "프로필 관리 실패", "outcome", "medium"),
    unit("12587611257", "경험품질", "안전·신뢰", "프로필 사진을 확대할 수 있는 기능이 있었으면 좋겠습니다", "참석자 프로필을 확대해 확인할 수 있기를 요청했다.", "참석자 프로필 확인", "참여 전 판단 정보의 가독성 부족", "perception", "low", "mixed"),

    unit("12514664882", "안전·신뢰", "호스트상업화", "매너점수? 평점을 메기는 방식으로 인해 가식이 난무하는 곳", "평점 체계가 진솔한 관계보다 평판 관리를 유도한다고 인식했다.", "평점과 이용자 행동을 관찰", "참가자와 평점 신호에 대한 불신", "perception", "medium"),
    unit("12514664882", "호스트상업화", "경험품질", "취미를 빌미로 터무니 없는 금액을 요구하는 장사꾼들이 판치고", "취미를 매개로 과도한 비용을 요구하는 판매형 모임이 많다고 평가했다.", "비용과 호스트 목적을 평가", "참여 비용과 진정성에 대한 불신", "perception", "medium"),
    unit("12514664882", "대체서비스", "이탈행동", "다른 플랫폼 옵션도 고려해 보시길", "문토 외 다른 플랫폼을 대안으로 고려하라고 권했다.", "대체 플랫폼을 고려", "문토 의존도와 재이용 의향 저하", "behavior", "medium", alternative="다른 플랫폼(미명시)"),

    unit("12500684017", "경험품질", "안전·신뢰", "글 작성할때마다 렉 걸리고 사진 로딩하는데 한세월이고 다 썼는데 튕기고", "글 작성·사진 로딩 과정의 지연과 종료로 작성 내용을 잃었다고 보고했다.", "게시글 작성", "시간 손실과 작성 실패", "outcome", "medium"),

    unit("12485415934", "안전·신뢰", "경험품질", "유저들 채팅 데이터 멋대로 모니터링하고 있는 건가요?", "외부 채팅 언급에 대한 벌점 때문에 채팅 감시와 제재 기준을 우려했다.", "벌점 사유를 추론하고 이의 제기", "프라이버시와 운영 신뢰 저하", "perception", "medium"),

    unit("12372005061", "안전·신뢰", "경험품질", "지독한 신천지", "종교 권유로 의심되는 참가자를 경험했다고 짧게 주장했다.", "참가자 위험을 평가", "참여 안전감 저하", "perception", "low", memo="맥락과 구체적 장면이 부족함"),

    unit("12260872739", "긍정·반례", "경험품질", "사람들 많다, 모임 날마다 열림", "참가자와 모임 공급이 충분하다는 장점을 함께 언급했다.", "모임 선택지를 확인", "선택 기회 증가", "outcome", "low", "mixed"),
    unit("12260872739", "호스트상업화", "경험품질", "굉장히 상업적", "참가자 경험과 모임 운영이 지나치게 상업적이라고 평가했다.", "서비스 경험을 평가", "모임 진정성 저하", "perception", "low"),
    unit("12260872739", "이탈행동", "경험품질", "결론: 탈퇴했음", "부정적 경험 후 탈퇴했다고 명시했다.", "회원 탈퇴", "서비스 이탈", "behavior", "high"),

    unit("12084703850", "숨은만남신호", "안전·신뢰", "사교모임 파티에서는 여러이성이랑 한꺼번에 연락하고", "파티 참가자들이 다수의 이성과 동시에 연락하는 만남 목적 행동을 보인다고 주장했다.", "파티 참가자 행동을 평가", "취미보다 연애 목적이라는 인식", "observed_signal", "low"),
    unit("12084703850", "안전·신뢰", "숨은만남신호", "바람피는사람 천지입니다", "사교 파티 참가자의 관계 상태와 행동을 신뢰하기 어렵다고 주장했다.", "참가자 신뢰성을 평가", "파티 참여 회피 의향", "perception", "low"),

    unit("12082781625", "경험품질", "안전·신뢰", "필터링해도 필터도 제대로안됨", "필터가 의도대로 작동하지 않는다고 보고했다.", "필터 사용", "탐색 기능 실패", "outcome", "low"),
    unit("11936916402", "경험품질", "안전·신뢰", "계속 로그아웃 되고 로그인 하려 하면 오류", "반복 로그아웃과 로그인 오류를 경험했다.", "로그인 재시도", "서비스 접근 실패", "outcome", "medium"),

    unit("12827053972", "경험품질", "긍정·반례", "하나밖에 못 만들어서 아쉽습니다", "생성 가능한 모임 수의 제한을 아쉬워했다.", "모임 생성", "호스트 활동 제약", "perception", "low", "mixed"),
    unit("12655340576", "경험품질", "안전·신뢰", "카카오톡 연결이 안됩니다", "카카오톡 연동이 작동하지 않는다고 보고했다.", "카카오톡 연동 시도", "기능 이용 실패", "outcome", "medium", "mixed"),
    unit("12564940538", "경험품질", "긍정·반례", "같은메시지 한개보내면 알람 두개씩 떠요", "동일 메시지 알림이 중복 표시되는 오류를 경험했다.", "알림 확인", "알림 피로", "outcome", "medium", "mixed"),
    unit("12564940538", "긍정·반례", "경험품질", "취미같은 사람끼리 만날수도있어서 좋네요", "비슷한 취미를 가진 사람을 만날 수 있어 즐거웠다고 평가했다.", "취미 모임 참여", "취미 목적과 관계 형성 충족", "outcome", "medium", "positive"),
    unit("12545444556", "긍정·반례", "경험품질", "시간가는줄모르고 떠들다 갑니다", "대화에 몰입할 만큼 즐거운 모임을 경험했다.", "모임에서 대화", "긍정적인 사교 경험", "outcome", "medium", "positive"),
    unit("12536922593", "경험품질", "안전·신뢰", "참석 구성원을 볼 수 있게 표시해주세요", "참석자와 클럽 정보를 탐색 화면에서 확인할 수 있기를 요청했다.", "참석 정보 확인 시도", "참여 전 판단 정보 부족", "perception", "medium", "mixed"),
    unit("12513851630", "긍정·반례", "호스트상업화", "비용도 합리적이고 재밌었습니다", "합리적인 비용으로 재미있는 모임을 경험했다고 평가했다.", "유료 모임 참여", "비용과 경험에 대한 만족", "outcome", "medium", "positive"),
    unit("12178038125", "경험품질", "호스트상업화", "유료모임 열고 정산 기다리는 중인데 언제 해주죠", "유료 모임 정산 지연과 안내 페이지 오류를 경험했다.", "정산 상태 확인과 문의", "호스트 운영 불확실성", "outcome", "high", "mixed"),
    unit("11902854727", "긍정·반례", "경험품질", "참 목적이 좋은 앱입니다", "서비스의 취미·사교 목적을 긍정적으로 평가했다.", "서비스 목적 평가", "전반적 호감", "perception", "low", "positive"),
    unit("11718954312", "긍정·반례", "탐색피로", "종류별로 다양한 모임들이 있어서 편리하게 이용", "다양한 취미 모임을 한곳에서 찾을 수 있어 편리했다고 평가했다.", "취미 모임 탐색", "탐색 편의와 선택지 만족", "outcome", "medium", "positive"),
]

EXCLUDED = {
    "12764248398": "의미를 판단할 수 없는 미완성 문장",
    "12556730027": "평점과 상반된 짧은 감상만 있어 맥락을 판단할 수 없음",
    "12210539333": "감사 표현만 있어 상황·행동 근거가 없음",
}


def main():
    with SAMPLE.open(encoding="utf-8-sig", newline="") as handle:
        sample = list(csv.DictReader(handle))
    reviews = {row["review_id"]: row for row in sample}
    by_review = defaultdict(list)
    for item in UNITS:
        assert item["review_id"] in reviews
        by_review[item["review_id"]].append(item)

    cards = []
    unit_counts = defaultdict(int)
    for index, item in enumerate(UNITS, start=1):
        row = reviews[item["review_id"]]
        rating = int(row["rating"])
        sentiment = item["sentiment"] or ("negative" if rating <= 3 else "mixed")
        unit_counts[item["review_id"]] += 1
        cards.append({
            "card_id": f"AS{index:03d}",
            "source_type": "app_review",
            "source_id": SOURCE_ID,
            "utterance_id": f"{item['review_id']}-{unit_counts[item['review_id']]}",
            "event_or_publish_date": row["review_date_utc"][:10],
            "collected_date": row["collected_date"],
            "period_bucket": row["period_bucket"],
            "platform": "Apple App Store",
            "source_url": row["source_url"],
            "rating": rating,
            "verbatim_excerpt": item["excerpt"],
            "paraphrase": item["paraphrase"],
            "context": "Apple App Store 공개 리뷰에서 문토 이용 경험을 회고함",
            "trigger_signal": item["excerpt"][:40],
            "behavior": item["behavior"],
            "outcome": item["outcome"],
            "alternative_service": item["alternative"],
            "primary_tag": item["primary"],
            "secondary_tag": item["secondary"],
            "sentiment": sentiment,
            "evidence_type": item["evidence_type"],
            "evidence_strength": item["strength"],
            "dedupe_key": f"appstore-{item['review_id']}-{item['primary']}-{index}",
            "cluster_id": "",
            "need_statement": "",
            "researcher_memo": (item["memo"] + " 동일 AI의 원문 수기 검토; 독립 사람 코더 검증 아님.").strip(),
            "pii_removed": "Y",
            "coder": "Codex(AI 원문 수기 검토)",
            "coding_status": "verified",
        })

    screen = []
    for row in sample:
        review_id = row["review_id"]
        included = review_id in by_review
        screen.append({
            "review_id": review_id,
            "rating": row["rating"],
            "review_date": row["review_date_utc"][:10],
            "sample_group": row["sample_group"],
            "screening_status": "included" if included else "excluded",
            "exclusion_reason": "" if included else EXCLUDED.get(review_id, "코딩 가능한 독립 근거 없음"),
            "generated_card_count": len(by_review[review_id]),
            "review_status": "reviewed",
        })

    for path, fields, rows in [(CARDS, CARD_FIELDS, cards), (SCREENING, SCREEN_FIELDS, screen)]:
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    print(f"sample={len(sample)} included={sum(r['screening_status']=='included' for r in screen)} cards={len(cards)}")
    print("tags", dict(Counter(card["primary_tag"] for card in cards)))


if __name__ == "__main__":
    main()
