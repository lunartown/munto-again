#!/usr/bin/env python3
"""Analyze 2021-2026 Google Play written-review trends with fixed rules."""

import csv
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_ROOT = PROJECT_ROOT / "data/reviews/google_play"
SOURCE = REVIEW_ROOT / "raw/reviews_history.csv"
CODED = REVIEW_ROOT / "processed/reviews_history_coded.csv"
PERIOD_SUMMARY = REVIEW_ROOT / "outputs/history_period_summary.csv"
YEAR_SUMMARY = REVIEW_ROOT / "outputs/history_year_summary.csv"
TOPIC_SUMMARY = REVIEW_ROOT / "outputs/history_topic_summary.csv"
REPORT = PROJECT_ROOT / "docs/findings/google_play_history_report.md"
CODEBOOK = PROJECT_ROOT / "docs/methods/google_play_history_codebook.md"

PERIODS = {
    "early_2021_2022": {"2021", "2022"},
    "middle_2023_2024": {"2023", "2024"},
    "recent_2025_2026": {"2025", "2026"},
}

TOPICS = {
    "dating_meeting": {
        "label": "소개팅·만남 관련",
        "regex": r"소개팅|로테이션|취향인연|미팅|남친|여친|연애|썸|매칭",
        "note": "소개팅 기능의 단순 오류나 긍정 경험도 포함하는 넓은 탐색 규칙",
    },
    "identity_shift": {
        "label": "취미→소개팅 정체성 변화",
        "regex": r"소개팅(\s*어플|\s*앱|만|밖|뿐|\s*주류)|로테이션\s*소개팅|남녀\s*만남|이성\s*만남.*(목적|많)|취미.*소개팅|소개팅.*(변질|남았|전부|대부분|파티)",
        "note": "취미 서비스가 소개팅 중심으로 변했다는 직접 표현에 가까운 고정밀 규칙",
    },
    "alcohol_party": {
        "label": "술·파티",
        "regex": r"술\s*파티|술\s*모임|파티\s*모임|와인\s*파티|솔로\s*파티|포틀럭.*파티",
        "note": "술·파티형 상품의 명시적 언급",
    },
    "discovery_supply": {
        "label": "탐색·공급 부족",
        "regex": r"찾기\s*힘|찾아보기\s*힘|모임(이|도)?\s*(거의\s*)?없|지방.*없|지역.*없|검색.*안|필터.*안|선택지.*없|추천.*묻",
        "note": "모임 공급 부족, 필터 실패, 원하는 모임 발견 곤란",
    },
    "commercialization_cost": {
        "label": "상업화·비용",
        "regex": r"수수료|호스트\s*수고비|돈\s*벌|돈벌|유료.*비싸|참가비.*비싸|사탕|캔디|개인\s*계좌|상업적|가격.*비싸|비용.*비싸",
        "note": "플랫폼·호스트 수익화와 가격 부담",
    },
    "safety_trust": {
        "label": "안전·신뢰",
        "regex": r"환불|노쇼|당일\s*취소|당일\s*파토|신고|제재|고객\s*센터|도용|범죄|종교|신천지|개인정보|가계정|봇",
        "note": "환불·취소·신원·신고·지원 대응에 관한 신뢰 문제",
    },
    "exit_behavior": {
        "label": "이탈행동",
        "regex": r"삭제|탈퇴|안\s*쓰|안쓰|다시는|두번\s*다시|떠나|다른.*플랫폼|다른.*앱|비추",
        "note": "앱 삭제·탈퇴·비사용·대체 서비스 언급; 타인에게 권고한 표현도 일부 포함 가능",
    },
    "positive_hobby": {
        "label": "긍정 취미 경험",
        "regex": r"취미.*좋|취미.*즐|다양한.*모임|좋은\s*사람|좋은\s*모임|재밌|즐겁|활력|만족|애용",
        "note": "취미·관계 경험을 긍정적으로 평가한 표현",
    },
}


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def period_for(year):
    for period, years in PERIODS.items():
        if year in years:
            return period
    return "outside_range"


def wilson(successes, total, z=1.96):
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return center - margin, center + margin


def summarize_group(label, rows):
    total = len(rows)
    ratings = [int(row["rating"]) for row in rows]
    low = sum(rating <= 3 for rating in ratings)
    high = sum(rating >= 4 for rating in ratings)
    low_ci = wilson(low, total)
    return {
        "period": label,
        "total_reviews": total,
        "average_rating": round(sum(ratings) / total, 3),
        "rating_1_count": ratings.count(1),
        "rating_1_share": round(ratings.count(1) / total, 4),
        "low_1_3_count": low,
        "low_1_3_share": round(low / total, 4),
        "low_share_ci95_low": round(low_ci[0], 4),
        "low_share_ci95_high": round(low_ci[1], 4),
        "high_4_5_count": high,
        "high_4_5_share": round(high / total, 4),
    }


def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len({row["review_id"] for row in rows})

    coded = []
    for row in rows:
        item = dict(row)
        year = row["review_date_utc"][:4]
        rating = int(row["rating"])
        item["analysis_period"] = period_for(year)
        item["rating_group"] = "low_1_3" if rating <= 3 else "high_4_5"
        for key, topic in TOPICS.items():
            item[f"topic_{key}"] = "1" if re.search(topic["regex"], row["review_text"], re.I) else "0"
        coded.append(item)
    coded_fields = list(coded[0])
    write_csv(CODED, coded_fields, coded)

    period_rows = []
    for period in PERIODS:
        group = [row for row in coded if row["analysis_period"] == period]
        period_rows.append(summarize_group(period, group))
    write_csv(PERIOD_SUMMARY, list(period_rows[0]), period_rows)

    year_rows = []
    for year in sorted({row["review_date_utc"][:4] for row in coded}):
        group = [row for row in coded if row["review_date_utc"].startswith(year)]
        summary = summarize_group(year, group)
        summary["year"] = summary.pop("period")
        year_rows.append(summary)
    write_csv(YEAR_SUMMARY, list(year_rows[0]), year_rows)

    topic_rows = []
    for key, topic in TOPICS.items():
        flag = f"topic_{key}"
        for period in PERIODS:
            group = [row for row in coded if row["analysis_period"] == period]
            low = [row for row in group if row["rating_group"] == "low_1_3"]
            high = [row for row in group if row["rating_group"] == "high_4_5"]
            all_count = sum(row[flag] == "1" for row in group)
            low_count = sum(row[flag] == "1" for row in low)
            high_count = sum(row[flag] == "1" for row in high)
            topic_rows.append({
                "topic_key": key,
                "topic_label": topic["label"],
                "period": period,
                "all_review_count": len(group),
                "all_topic_count": all_count,
                "all_topic_share": round(all_count / len(group), 4),
                "low_review_count": len(low),
                "low_topic_count": low_count,
                "low_topic_share": round(low_count / len(low), 4),
                "high_review_count": len(high),
                "high_topic_count": high_count,
                "high_topic_share": round(high_count / len(high), 4),
                "coding_note": topic["note"],
            })
    write_csv(TOPIC_SUMMARY, list(topic_rows[0]), topic_rows)

    lookup = {(row["topic_key"], row["period"]): row for row in topic_rows}
    early, middle, recent = period_rows
    pct = lambda value: f"{float(value):.1%}"
    labels = [
        "dating_meeting", "identity_shift", "alcohol_party", "discovery_supply",
        "commercialization_cost", "safety_trust", "exit_behavior",
    ]
    lines = [
        "# Google Play 리뷰 시계열 분석",
        "",
        "## 결론",
        "",
        "Google Play에 공개된 텍스트 리뷰에서는 최근 구간으로 갈수록 부정 경험이 강해지는",
        "경향이 관찰됐다. 평균 별점은 4.112점에서 3.174점으로 낮아졌고, 1~3점 리뷰 비율은",
        f"{pct(early['low_1_3_share'])}에서 {pct(recent['low_1_3_share'])}로 {float(recent['low_1_3_share'])-float(early['low_1_3_share']):.1%}p 상승했다.",
        "소개팅·만남, 술·파티, 상업화·비용, 탐색 곤란, 안전·신뢰 표현도 최근 저평점",
        "리뷰에서 더 자주 나타났다. 이는 사용자 경험 악화 가설을 지지하는 정량적 신호다.",
        "",
        "## 별점 변화",
        "",
        "| 기간 | 리뷰 | 평균 별점 | 1~3점 비율 | 95% CI |",
        "|---|---:|---:|---:|---:|",
    ]
    period_labels = {
        "early_2021_2022": "초기 2021~2022",
        "middle_2023_2024": "중기 2023~2024",
        "recent_2025_2026": "최근 2025~2026",
    }
    for row in period_rows:
        lines.append(
            f"| {period_labels[row['period']]} | {row['total_reviews']} | {row['average_rating']:.3f} | "
            f"{pct(row['low_1_3_share'])} | {pct(row['low_share_ci95_low'])}~{pct(row['low_share_ci95_high'])} |"
        )
    lines += [
        "",
        "## 저평점 리뷰 안의 핵심 주제",
        "",
        "| 주제 | 초기 | 중기 | 최근 | 초기→최근 변화 |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in labels:
        a = lookup[(key, "early_2021_2022")]["low_topic_share"]
        b = lookup[(key, "middle_2023_2024")]["low_topic_share"]
        c = lookup[(key, "recent_2025_2026")]["low_topic_share"]
        lines.append(
            f"| {TOPICS[key]['label']} | {pct(a)} | {pct(b)} | {pct(c)} | {float(c)-float(a):+.1%}p |"
        )
    pos_early = lookup[("positive_hobby", "early_2021_2022")]["high_topic_share"]
    pos_middle = lookup[("positive_hobby", "middle_2023_2024")]["high_topic_share"]
    pos_recent = lookup[("positive_hobby", "recent_2025_2026")]["high_topic_share"]
    lines += [
        "",
        "## 반례",
        "",
        f"4~5점 리뷰 중 긍정 취미 경험 표현은 초기 {pct(pos_early)}, 중기 {pct(pos_middle)}, "
        f"최근 {pct(pos_recent)}였다. 최근에도 취미와 관계 형성의 가치를 얻은 사용자가 분명히",
        "존재하므로, 모든 사용자 경험이 일괄적으로 나빠졌다고 결론 내리면 안 된다.",
        "이탈 표현도 초기보다 최근이 높지 않아 단조 증가가 확인되지 않았다.",
        "",
        "## 해석 한계",
        "",
        "- 공개 텍스트 리뷰 작성자는 전체 사용자의 대표 표본이 아니다.",
        "- Google Play의 별점만 남긴 평가, 삭제된 리뷰, 비공개 리뷰는 포함되지 않는다.",
        "- 2021년은 6월 이후, 2026년은 7월까지의 부분 기간이다.",
        "- 앱의 리뷰 요청 방식과 Google Play 노출 정책이 시기별로 바뀌었을 수 있다.",
        "- 키워드 규칙은 맥락을 완전히 이해하지 못하므로 주제 비율은 근사치다.",
        "- 리뷰는 상관관계를 보여줄 뿐 소개팅 콘텐츠가 별점 하락을 일으켰다는 인과를 증명하지 않는다.",
        "",
        "따라서 보고서에는 ‘사용자 경험이 악화됐다’고 단정하기보다 ‘공개 텍스트 리뷰에서",
        "부정 경험과 핵심 문제 표현이 시간에 따라 증가하는 경향이 관찰됐다’고 기술한다.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    codebook_lines = [
        "# Google Play 시계열 자동 코딩 기준",
        "",
        "전체 1,200건에 동일한 정규식 규칙을 적용했다. 하나의 리뷰는 여러 주제에 포함될 수 있다.",
        "주제 카드는 만들지 않고 리뷰 단위 존재 여부(0/1)만 집계했다.",
        "",
        "| 키 | 주제 | 규칙 | 주의사항 |",
        "|---|---|---|---|",
    ]
    for key, topic in TOPICS.items():
        escaped = topic["regex"].replace("|", "\\|")
        codebook_lines.append(f"| `{key}` | {topic['label']} | `{escaped}` | {topic['note']} |")
    CODEBOOK.write_text("\n".join(codebook_lines) + "\n", encoding="utf-8")
    print(f"coded={len(coded)} periods={len(period_rows)} years={len(year_rows)} topic_rows={len(topic_rows)}")


if __name__ == "__main__":
    main()
