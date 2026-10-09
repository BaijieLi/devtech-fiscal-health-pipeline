"""Promote extracted PDF field candidates into draft normalized records.

This module intentionally creates draft records, not final audited values. Each
selected value keeps a trace row so analysts can review the source page and line
before using the record for ratio analysis.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable, Mapping

from .normalization import _to_float
from .schema import CANONICAL_FIELDS, METADATA_FIELDS, NUMERIC_FIELDS

SOURCE_KEY_FIELDS = ("locality", "fiscal_year", "source_file", "source_path")


def parse_candidate_value(value: object) -> float | None:
    """Parse a candidate value string into a float."""

    return _to_float(value)


def scaled_candidate_value(candidate: Mapping[str, object]) -> float | None:
    """Parse a candidate value and apply line-level unit hints."""

    value = parse_candidate_value(candidate.get("candidate_value"))
    if value is None:
        return None
    line = str(candidate.get("line_text", "")).lower()
    candidate_value = str(candidate.get("candidate_value", ""))
    field_name = str(candidate.get("field_name", ""))
    if field_name in {"debt_service_interest", "debt_service_principal"}:
        value = abs(value)
    if "billion" in line:
        return value * 1_000_000_000
    if "million" in line:
        return value * 1_000_000
    if "thousand" in line:
        return value * 1_000
    decimal_values = re.findall(r"\b\d{1,3}\.\d+\b", line)
    if (
        "." in candidate_value
        and "," not in candidate_value
        and len(decimal_values) >= 3
        and 0 < abs(value) < 10_000
    ):
        return value * 1_000_000
    return value


def _page_number(candidate: Mapping[str, object]) -> int:
    try:
        return int(str(candidate.get("page_number", "")).strip())
    except ValueError:
        return 999999


def _confidence(candidate: Mapping[str, object]) -> float:
    try:
        return float(str(candidate.get("confidence", "")).strip())
    except ValueError:
        return 0.0


def _line_score(candidate: Mapping[str, object]) -> float:
    """Score a candidate line for draft promotion."""

    line = str(candidate.get("line_text", "")).lower()
    score = _confidence(candidate)
    if "total" in line:
        score += 0.15
    if "$" in line:
        score += 0.05
    if re.search(r"\d,\d{3}", line):
        score += 0.05
    value = scaled_candidate_value(candidate)
    if value is not None and abs(value) >= 1_000_000:
        score += 0.2
    if any(word in line for word in ("increase", "increased", "decrease", "decreased")):
        score -= 0.05
    # Prefer statement/table rows over narrative management discussion.
    if len(line) > 180:
        score -= 0.1
    return score


def choose_best_candidate(
    candidates: Iterable[Mapping[str, object]],
) -> Mapping[str, object] | None:
    """Choose the highest-scoring parseable candidate for one field."""

    parseable = [
        candidate
        for candidate in candidates
        if scaled_candidate_value(candidate) is not None
    ]
    if not parseable:
        return None
    return max(
        parseable,
        key=lambda candidate: (
            _line_score(candidate),
            -_page_number(candidate),
            abs(scaled_candidate_value(candidate) or 0),
        ),
    )


def _record_key(candidate: Mapping[str, object]) -> tuple[str, str, str, str]:
    return tuple(str(candidate.get(field, "") or "") for field in SOURCE_KEY_FIELDS)


def promote_candidates(
    candidates: Iterable[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Create draft normalized records and selected-value trace rows."""

    grouped: dict[tuple[str, str, str, str], dict[str, list[Mapping[str, object]]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    metadata: dict[tuple[str, str, str, str], Mapping[str, object]] = {}

    for candidate in candidates:
        field_name = str(candidate.get("field_name", ""))
        if field_name not in NUMERIC_FIELDS:
            continue
        key = _record_key(candidate)
        grouped[key][field_name].append(candidate)
        metadata[key] = candidate

    records: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []

    for key in sorted(grouped):
        source = metadata[key]
        record = {field: "" for field in CANONICAL_FIELDS}
        record["locality"] = str(source.get("locality", "") or "")
        record["fiscal_year"] = str(source.get("fiscal_year", "") or "")
        record["source_file"] = str(source.get("source_file", "") or "")
        record["report_type"] = "pdf_candidate_draft"

        for field_name, field_candidates in sorted(grouped[key].items()):
            selected = choose_best_candidate(field_candidates)
            if selected is None:
                continue
            parsed_value = scaled_candidate_value(selected)
            record[field_name] = parsed_value if parsed_value is not None else ""
            trace_rows.append(
                {
                    "locality": record["locality"],
                    "fiscal_year": record["fiscal_year"],
                    "source_file": record["source_file"],
                    "source_path": str(selected.get("source_path", "") or ""),
                    "field_name": field_name,
                    "selected_value": record[field_name],
                    "candidate_value": str(selected.get("candidate_value", "") or ""),
                    "page_number": str(selected.get("page_number", "") or ""),
                    "confidence": str(selected.get("confidence", "") or ""),
                    "line_text": str(selected.get("line_text", "") or ""),
                }
            )

        records.append(record)

    return records, trace_rows
