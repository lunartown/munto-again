"""저평점 리뷰(research/data/reviews/filtered/low_rating_2024_2026.csv)에서
명사를 추출해 워드클라우드 이미지를 생성한다.

출력: research/data/reviews/summaries/wordcloud_low_rating_2024_2026.png
"""

import csv
from collections import Counter
from pathlib import Path

from kiwipiepy import Kiwi
from wordcloud import WordCloud

ROOT = Path(__file__).resolve().parents[3]
INPUT_CSV = ROOT / "research/data/reviews/filtered/low_rating_2024_2026.csv"
OUTPUT_PNG = ROOT / "research/data/reviews/summaries/wordcloud_low_rating_2024_2026.png"
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

# 리뷰 본문에서 반복적으로 등장하지만 의미 분석에 도움이 되지 않는 단어
STOPWORDS = {
    "저", "제", "것", "거", "수", "때", "번", "정도", "개", "분", "지금",
    "이번", "요즘", "진짜", "정말", "그냥", "너무", "완전", "그거", "그게",
    "여기", "저기", "거기", "이거", "그거", "위", "듯", "때문", "경우",
    "문토", "앱", "어플", "리뷰",
}


def load_review_texts(csv_path: Path) -> list[str]:
    with csv_path.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    texts = []
    for row in rows:
        for field in ("review_title", "review_text"):
            value = (row.get(field) or "").strip()
            if value:
                texts.append(value)
    return texts


def extract_nouns(texts: list[str], kiwi: Kiwi) -> Counter:
    counter = Counter()
    for text in texts:
        for token in kiwi.tokenize(text):
            if token.tag in ("NNG", "NNP") and len(token.form) > 1:
                word = token.form
                if word not in STOPWORDS:
                    counter[word] += 1
    return counter


def main() -> None:
    texts = load_review_texts(INPUT_CSV)
    print(f"리뷰 {len(texts)}건 로드")

    kiwi = Kiwi()
    counts = extract_nouns(texts, kiwi)
    print(f"고유 명사 {len(counts)}개 추출")
    print("상위 20개:", counts.most_common(20))

    wc = WordCloud(
        font_path=FONT_PATH,
        width=1600,
        height=1000,
        background_color="white",
        max_words=100,
    ).generate_from_frequencies(counts)

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    wc.to_file(str(OUTPUT_PNG))
    print(f"저장: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
