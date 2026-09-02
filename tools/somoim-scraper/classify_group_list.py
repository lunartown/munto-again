#!/usr/bin/env python3
"""목록의 모임명·50자 소개·키워드만으로 명시적 목적 신호를 분류한다.

이 결과는 실제 모임 운영 목적의 판정이 아니라 목록에서 관찰되는 표현의 분류다.
개별 모임 상세 페이지나 외부 URL은 요청하지 않는다.
"""

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_DB = HERE / "data" / "somoim-groups.sqlite3"
CLASSIFIER_VERSION = "list-signals-v2"


DIRECT_DATING_PATTERNS = {
    "소개팅": r"소개팅",
    "로테이션 만남": r"로테이션\s*(?:소개팅|미팅|만남)",
    "스피드 데이트": r"스피드\s*데이트",
    "카톡 소개": r"카톡\s*소개",
    "매칭": r"(?:이성|커플|연애|소개팅|남녀).{0,8}매칭|매칭.{0,8}(?:이성|커플|연애|소개팅|남녀)",
    "성혼": r"성혼",
    "연애": r"연애",
    "커플 형성": r"커플.{0,8}(?:만들|탄생|성사)|(?:만들|탄생|성사).{0,8}커플",
    "남친·여친": r"남친|여친",
    "썸": r"썸\s*타",
    "이성과 만남": r"이성.{0,8}만남|만남.{0,8}이성",
}

DATING_SELECTION_PATTERNS = {
    "싱글·미혼 제한": r"법적\s*싱글|미혼\s*(?:만|모임|남|여)|싱글\s*(?:만|모임|남|여|분|들|즈|라이프|아지트|친목)",
    "돌싱": r"돌싱",
    "솔로": r"솔로",
    "성비": r"성비|남녀\s*(?:비율|구성)",
    "성별 모집 조절": r"(?:남자|남성|여자|여성|여횐)\s*(?:마감|모집|우대|환영|무료|할인)|(?:남|여)\s*\d+\s*[/·:]\s*(?:남|여)?\s*\d+",
    "외모 강조": r"훈남|훈녀|존잘|존예|비주얼|외모|사진빨",
}

DRINKING_SOCIAL_PATTERNS = {
    "술자리": r"술자리",
    "술모임": r"(?:^|[\s#·,&/+])술\s*모임",
    "술벙": r"술벙",
    "음주가무": r"음주가무",
    "혼술": r"혼술",
    "쏘맥": r"쏘맥",
    "술꾼": r"술꾼",
    "술집": r"술집",
    "술 한잔": r"(?:술|소주|맥주|와인|위스키|칵테일)\s*한\s*잔",
    "술 중심 표현": r"(?:^|[\s#·,&/+])술(?:\s|[,&/+]|과|도|을|이|좋|친구)",
}

PARTY_PATTERNS = {
    "파티": r"파티",
}

ALCOHOL_HOBBY_PATTERNS = {
    "와인": r"와인|wine",
    "위스키": r"위스키|whisky|whiskey",
    "칵테일": r"칵테일|cocktail",
    "전통주": r"전통주|막걸리|사케",
    "맥주": r"맥주|beer",
    "주류 시음": r"시음|테이스팅|소믈리에",
}

DIRECT_DATING_KEYWORDS = {"소개팅", "카톡소개", "연애", "연애결혼", "커플"}
DRINKING_SOCIAL_KEYWORDS = {"술"}
ALCOHOL_HOBBY_KEYWORDS = {"와인", "위스키", "칵테일", "전통주", "맥주"}

NEGATED_ALCOHOL = re.compile(
    r"논알콜|노알콜|무알콜|금주|술(?:을|은)?\s*(?:없이|없는|금지|지양|강요\s*없)",
    re.I,
)
PARTY_FALSE_POSITIVES = re.compile(r"파티\s*게임|파티게임|파티원|티파티|파티시엘", re.I)


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS classification_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classified_at TEXT NOT NULL,
    classifier_version TEXT NOT NULL,
    source_collection_run_id INTEGER,
    total_count INTEGER NOT NULL,
    note TEXT NOT NULL,
    FOREIGN KEY (source_collection_run_id) REFERENCES collection_runs(id)
);

CREATE TABLE IF NOT EXISTS group_classifications (
    gid TEXT PRIMARY KEY,
    classification_run_id INTEGER NOT NULL,
    classifier_version TEXT NOT NULL,
    primary_label TEXT NOT NULL,
    direct_dating_signal INTEGER NOT NULL,
    dating_selection_signal INTEGER NOT NULL,
    drinking_social_signal INTEGER NOT NULL,
    party_signal INTEGER NOT NULL,
    alcohol_hobby_signal INTEGER NOT NULL,
    evidence_json TEXT NOT NULL,
    classified_at TEXT NOT NULL,
    FOREIGN KEY (gid) REFERENCES groups(gid),
    FOREIGN KEY (classification_run_id) REFERENCES classification_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_classifications_label
    ON group_classifications(primary_label);
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def matched(patterns, text):
    return [label for label, pattern in patterns.items() if re.search(pattern, text, re.I)]


def normalized_text(name, excerpt, keyword):
    text = " ".join((name or "", excerpt or "", keyword or ""))
    text = re.sub(r"\s+", " ", text).strip()
    # 스포츠 실력의 '싱글'과 포괄 표현은 관계 상태·성비 신호가 아니다.
    text = re.sub(r"싱글\s*(?:칠|치기|핸디|플레이|골퍼)", " ", text)
    text = text.replace("남녀노소", " ").replace("남녀혼성", " ")
    return text


def classify(row):
    gid, name, excerpt, keyword = row
    text = normalized_text(name, excerpt, keyword)
    title_text = normalized_text(name, "", keyword)

    direct = matched(DIRECT_DATING_PATTERNS, text)
    if keyword in DIRECT_DATING_KEYWORDS:
        direct.append(f"키워드:{keyword}")

    selection = matched(DATING_SELECTION_PATTERNS, text)

    drinking = [] if NEGATED_ALCOHOL.search(text) else matched(DRINKING_SOCIAL_PATTERNS, text)
    if keyword in DRINKING_SOCIAL_KEYWORDS and f"키워드:{keyword}" not in drinking:
        drinking.append(f"키워드:{keyword}")

    party_text = PARTY_FALSE_POSITIVES.sub(" ", title_text)
    party = matched(PARTY_PATTERNS, party_text)

    hobby = matched(ALCOHOL_HOBBY_PATTERNS, text)
    if keyword in ALCOHOL_HOBBY_KEYWORDS:
        hobby.append(f"키워드:{keyword}")

    # 술자리·이성교류와 결합되지 않은 주류 자체 취미만 별도 보존한다.
    alcohol_hobby_only = bool(hobby) and not drinking and not direct and not selection

    direct_flag = bool(direct)
    selection_flag = bool(selection)
    drinking_flag = bool(drinking)
    party_flag = bool(party)

    if (direct_flag or selection_flag) and drinking_flag:
        label = "dating_and_drinking_social"
    elif direct_flag:
        label = "direct_dating"
    elif selection_flag:
        label = "dating_selection_social"
    elif drinking_flag:
        label = "drinking_social"
    elif party_flag:
        label = "party_social"
    elif alcohol_hobby_only:
        label = "alcohol_hobby"
    else:
        label = "no_explicit_signal"

    evidence = {
        "direct_dating": sorted(set(direct)),
        "dating_selection": sorted(set(selection)),
        "drinking_social": sorted(set(drinking)),
        "party": sorted(set(party)),
        "alcohol_hobby": sorted(set(hobby)),
    }
    return {
        "gid": gid,
        "label": label,
        "direct": int(direct_flag),
        "selection": int(selection_flag),
        "drinking": int(drinking_flag),
        "party": int(party_flag),
        "hobby": int(alcohol_hobby_only),
        "evidence": json.dumps(evidence, ensure_ascii=False, separators=(",", ":")),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()

    connection = sqlite3.connect(args.db)
    connection.executescript(SCHEMA)
    rows = connection.execute(
        "SELECT gid, name, description_excerpt, keyword FROM groups ORDER BY gid"
    ).fetchall()
    source_run = connection.execute(
        "SELECT id FROM collection_runs WHERE status = 'complete' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    classified_at = utc_now()

    cursor = connection.execute(
        """
        INSERT INTO classification_runs (
            classified_at, classifier_version, source_collection_run_id,
            total_count, note
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            classified_at,
            CLASSIFIER_VERSION,
            source_run[0] if source_run else None,
            len(rows),
            "모임명·목록 소개·키워드의 명시적 표현만 사용; 상세 페이지 미요청",
        ),
    )
    classification_run_id = cursor.lastrowid

    with connection:
        for row in rows:
            result = classify(row)
            connection.execute(
                """
                INSERT INTO group_classifications (
                    gid, classification_run_id, classifier_version, primary_label,
                    direct_dating_signal, dating_selection_signal,
                    drinking_social_signal, party_signal, alcohol_hobby_signal,
                    evidence_json, classified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(gid) DO UPDATE SET
                    classification_run_id = excluded.classification_run_id,
                    classifier_version = excluded.classifier_version,
                    primary_label = excluded.primary_label,
                    direct_dating_signal = excluded.direct_dating_signal,
                    dating_selection_signal = excluded.dating_selection_signal,
                    drinking_social_signal = excluded.drinking_social_signal,
                    party_signal = excluded.party_signal,
                    alcohol_hobby_signal = excluded.alcohol_hobby_signal,
                    evidence_json = excluded.evidence_json,
                    classified_at = excluded.classified_at
                """,
                (
                    result["gid"],
                    classification_run_id,
                    CLASSIFIER_VERSION,
                    result["label"],
                    result["direct"],
                    result["selection"],
                    result["drinking"],
                    result["party"],
                    result["hobby"],
                    result["evidence"],
                    classified_at,
                ),
            )

    total = len(rows)
    print(f"classified={total} version={CLASSIFIER_VERSION}")
    for label, count in connection.execute(
        """
        SELECT primary_label, COUNT(*)
        FROM group_classifications
        GROUP BY primary_label
        ORDER BY COUNT(*) DESC
        """
    ):
        print(f"{label}={count} ({count / total * 100:.2f}%)")
    connection.close()


if __name__ == "__main__":
    main()
