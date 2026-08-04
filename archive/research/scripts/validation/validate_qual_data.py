#!/usr/bin/env python3
"""Validate qualitative research CSV schemas and categorical values."""

import csv
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "data/interviews/interview_sessions.csv": [
        "participant_id", "interview_date", "minutes", "service_experience",
        "last_used_period", "current_status", "original_goal", "recruitment_channel",
        "notes_consent", "recording_consent", "anonymized", "interviewer",
        "session_status", "notes",
    ],
    "data/synthesis/qualitative_cards.csv": [
        "card_id", "source_type", "source_id", "utterance_id", "event_or_publish_date",
        "collected_date", "period_bucket", "platform", "source_url", "rating",
        "verbatim_excerpt", "paraphrase", "context", "trigger_signal", "behavior",
        "outcome", "alternative_service", "primary_tag", "secondary_tag", "sentiment",
        "evidence_type", "evidence_strength", "dedupe_key", "cluster_id", "need_statement",
        "researcher_memo", "pii_removed", "coder", "coding_status",
    ],
    "data/synthesis/affinity_clusters.csv": [
        "cluster_id", "cluster_name", "included_card_ids", "pattern_summary",
        "need_statement", "contradictory_card_ids", "supporting_card_count",
        "source_type_count", "evidence_role", "confidence", "design_implication", "owner", "status",
    ],
    "data/metadata/source_inventory.csv": [
        "source_id", "source_type", "source_name", "source_url", "published_period",
        "time_bucket", "quality_level", "intended_use", "collection_status", "notes",
    ],
}
ALLOWED = {
    "source_type": {"interview", "app_review", "community", "blog", "product_analysis"},
    "period_bucket": {"early", "middle", "recent", "unknown", ""},
    "time_bucket": {"early", "middle", "recent", "unknown", ""},
    "sentiment": {"positive", "neutral", "negative", "mixed", ""},
    "evidence_type": {"perception", "observed_signal", "behavior", "outcome", ""},
    "evidence_strength": {"high", "medium", "low", ""},
    "quality_level": {"high", "medium", "low", ""},
    "pii_removed": {"Y", "N", ""},
    "coding_status": {"uncoded", "coded", "verified", ""},
    "evidence_role": {"문제", "긍정 반례", "결과"},
    "notes_consent": {"Y", "N", ""},
    "recording_consent": {"Y", "N", ""},
    "anonymized": {"Y", "N", ""},
}


def main() -> int:
    errors = []
    for name, expected in EXPECTED.items():
        path = ROOT / name
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != expected:
                errors.append(f"{name}: header mismatch")
                continue
            rows = list(reader)
        seen_ids = set()
        id_field = expected[0]
        for line, row in enumerate(rows, start=2):
            row_id = row[id_field].strip()
            if not row_id:
                errors.append(f"{name}:{line}: missing {id_field}")
            elif row_id in seen_ids:
                errors.append(f"{name}:{line}: duplicate {id_field}={row_id}")
            seen_ids.add(row_id)
            for field, allowed in ALLOWED.items():
                if field in row and row[field].strip() not in allowed:
                    errors.append(f"{name}:{line}: invalid {field}={row[field]!r}")
            if "source_url" in row and row["source_url"].strip():
                parsed = urlparse(row["source_url"].strip())
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    errors.append(f"{name}:{line}: invalid source_url")
    if errors:
        print("\n".join(errors))
        return 1
    print("QUAL DATA QA PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
