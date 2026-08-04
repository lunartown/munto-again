#!/usr/bin/env python3
"""Compare a completed blinded validation sample with the AI first pass."""

import argparse
import csv
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coded", type=Path,
                        default=PROJECT_ROOT / "data/listings/processed/munto_socialings_coded.csv")
    parser.add_argument("--sample", type=Path,
                        default=PROJECT_ROOT / "data/listings/validation/munto_validation_sample_20.csv")
    args = parser.parse_args()
    with args.coded.open(encoding="utf-8-sig", newline="") as handle:
        ai = {row["id"]: row["최종분류"] for row in csv.DictReader(handle)}
    with args.sample.open(encoding="utf-8-sig", newline="") as handle:
        sample = list(csv.DictReader(handle))
    completed = [row for row in sample if row["검증자분류"].strip().upper() in {"A", "B", "C"}]
    if not completed:
        print("검증자분류가 입력된 행이 없습니다. A/B/C 중 하나를 입력하세요.")
        return 2
    pairs = [(ai[row["id"]], row["검증자분류"].strip().upper()) for row in completed]
    matches = sum(left == right for left, right in pairs)
    print(f"완료: {len(completed)}/{len(sample)}")
    print(f"일치: {matches}/{len(completed)} ({matches / len(completed):.1%})")
    print("혼동표 (AI -> 검증자):")
    for (left, right), count in sorted(Counter(pairs).items()):
        print(f"  {left} -> {right}: {count}")
    if len(completed) < len(sample):
        print("주의: 표본이 전부 완료되지 않아 중간 결과입니다.")
    return 0 if matches / len(completed) >= 0.8 and len(completed) == len(sample) else 1


if __name__ == "__main__":
    raise SystemExit(main())
