"""Aggregate quality review outputs into portfolio-friendly audit metrics."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Iterable, Mapping

from .quality_review import parse_numeric
from .schema import NUMERIC_FIELDS


AUDIT_FIELDNAMES = ("section", "name", "value", "percent")
QUALITY_STATUSES = ("PASS", "CAUTION", "REVIEW")


def split_pipe_list(value: object) -> list[str]:
    """Split pipe-delimited review fields into clean values."""

    return [item for item in str(value or "").split("|") if item]


def _int_value(value: object) -> int:
    try:
        return int(float(str(value or "0")))
    except ValueError:
        return 0


def _percent(count: int, total: int) -> str:
    if total == 0:
        return ""
    return f"{count / total:.2%}"


def _counter_rows(
    section: str, counter: Counter[str], total: int | None = None
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        rows.append(
            {
                "section": section,
                "name": name,
                "value": count,
                "percent": _percent(count, total) if total is not None else "",
            }
        )
    return rows


def _warning_target(warning: str) -> str:
    if ":" not in warning:
        return warning
    return warning.split(":", 1)[1].split("=", 1)[0]


def summarize_quality_review(
    quality_rows: Iterable[Mapping[str, object]],
    normalized_records: Iterable[Mapping[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Summarize quality rows and optional normalized-record field coverage."""

    reviews = list(quality_rows)
    records = list(normalized_records) if normalized_records is not None else []
    review_count = len(reviews)
    status_counts = Counter(str(row.get("quality_status", "")) for row in reviews)
    warning_categories: Counter[str] = Counter()
    warning_targets: Counter[str] = Counter()
    missing_core_fields: Counter[str] = Counter()

    for row in reviews:
        for warning in split_pipe_list(row.get("warnings")):
            warning_categories[warning.split(":", 1)[0]] += 1
            warning_targets[_warning_target(warning)] += 1
        missing_core_fields.update(split_pipe_list(row.get("missing_core_fields")))

    filled_counts = [_int_value(row.get("filled_field_count")) for row in reviews]
    total_warnings = sum(_int_value(row.get("warning_count")) for row in reviews)

    rows: list[dict[str, object]] = [
        {
            "section": "summary",
            "name": "record_count",
            "value": review_count,
            "percent": "",
        },
        {
            "section": "summary",
            "name": "average_filled_field_count",
            "value": f"{mean(filled_counts):.2f}" if filled_counts else "0.00",
            "percent": "",
        },
        {
            "section": "summary",
            "name": "total_warning_count",
            "value": total_warnings,
            "percent": "",
        },
    ]

    for status in QUALITY_STATUSES:
        rows.append(
            {
                "section": "quality_status",
                "name": status,
                "value": status_counts[status],
                "percent": _percent(status_counts[status], review_count),
            }
        )

    rows.extend(_counter_rows("warning_category", warning_categories))
    rows.extend(_counter_rows("warning_target", warning_targets, review_count))
    rows.extend(_counter_rows("missing_core_field", missing_core_fields, review_count))

    if records:
        for field in NUMERIC_FIELDS:
            filled = sum(
                1 for record in records if parse_numeric(record.get(field)) is not None
            )
            rows.append(
                {
                    "section": "field_coverage",
                    "name": field,
                    "value": filled,
                    "percent": _percent(filled, len(records)),
                }
            )

    return rows
