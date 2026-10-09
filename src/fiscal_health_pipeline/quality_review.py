"""Quality checks for draft normalized fiscal records.

PDF-derived records are treated as review artifacts until they pass basic
sanity checks. These checks flag missing inputs, suspicious field magnitudes,
and ratio outputs that are likely caused by extraction or unit-scaling errors.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from .normalization import _to_float
from .ratios import compute_ratios
from .schema import NUMERIC_FIELDS


CORE_FIELDS = (
    "cash_and_equivalents",
    "total_liabilities",
    "total_expenses",
    "total_revenues",
    "total_fund_balance",
)

NONNEGATIVE_FIELDS = tuple(
    field
    for field in NUMERIC_FIELDS
    if field
    not in {
        "unrestricted_net_position",
        "net_position_beginning",
        "net_position_ending",
        "enterprise_change_in_net_position",
        "enterprise_net_transfers",
    }
)

MIN_EXPECTED_DOLLAR_VALUE = 1_000
RATIO_ABSOLUTE_LIMIT = 10


def parse_numeric(value: object) -> float | None:
    """Parse a normalized-record value into a float."""

    return _to_float(value)


def filled_numeric_fields(record: Mapping[str, object]) -> list[str]:
    """Return numeric fields with parseable values."""

    return [
        field
        for field in NUMERIC_FIELDS
        if parse_numeric(record.get(field)) is not None
    ]


def missing_core_fields(record: Mapping[str, object]) -> list[str]:
    """Return core fields missing from a draft normalized record."""

    return [
        field
        for field in CORE_FIELDS
        if parse_numeric(record.get(field)) is None
    ]


def field_warnings(record: Mapping[str, object]) -> list[str]:
    """Return field-level quality warning codes."""

    warnings: list[str] = []
    for field in NUMERIC_FIELDS:
        value = parse_numeric(record.get(field))
        if value is None:
            continue
        if field in NONNEGATIVE_FIELDS and value < 0:
            warnings.append(f"negative_value:{field}={value:g}")
        if 0 < abs(value) < MIN_EXPECTED_DOLLAR_VALUE:
            warnings.append(f"suspicious_small_value:{field}={value:g}")
    return warnings


def ratio_warnings(record: Mapping[str, object]) -> tuple[list[str], list[str]]:
    """Return missing ratio names and suspicious ratio warning codes."""

    ratios = compute_ratios(record)
    missing = [name for name, value in ratios.items() if value is None]
    warnings = [
        f"large_ratio:{name}={value:.6g}"
        for name, value in ratios.items()
        if value is not None and abs(value) > RATIO_ABSOLUTE_LIMIT
    ]
    return missing, warnings


def review_record(record: Mapping[str, object]) -> dict[str, object]:
    """Create one CSV-friendly quality review row for a normalized record."""

    filled_fields = filled_numeric_fields(record)
    missing_fields = missing_core_fields(record)
    missing_ratios, suspicious_ratios = ratio_warnings(record)
    warnings = [
        *[f"missing_core_field:{field}" for field in missing_fields],
        *field_warnings(record),
        *suspicious_ratios,
    ]

    if suspicious_ratios or any(
        warning.startswith(("negative_value:", "suspicious_small_value:"))
        for warning in warnings
    ):
        status = "REVIEW"
    elif missing_fields:
        status = "CAUTION"
    else:
        status = "PASS"

    return {
        "locality": record.get("locality", ""),
        "fiscal_year": record.get("fiscal_year", ""),
        "source_file": record.get("source_file", ""),
        "report_type": record.get("report_type", ""),
        "quality_status": status,
        "filled_field_count": len(filled_fields),
        "missing_core_fields": "|".join(missing_fields),
        "missing_ratio_count": len(missing_ratios),
        "missing_ratios": "|".join(missing_ratios),
        "warning_count": len(warnings),
        "warnings": "|".join(warnings),
    }


def review_records(records: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Review normalized records in input order."""

    return [review_record(record) for record in records]
