"""Normalize input records into the canonical fiscal health schema."""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

from .schema import CANONICAL_FIELDS, METADATA_FIELDS, NUMERIC_FIELDS

FIELD_ALIASES = {
    "cash": "cash_and_equivalents",
    "cash_and_cash_equivalents": "cash_and_equivalents",
    "cash_equivalents": "cash_and_equivalents",
    "year": "fiscal_year",
    "fy": "fiscal_year",
    "city": "locality",
    "county": "locality",
    "source": "source_file",
    "file": "source_file",
    "type": "report_type",
    "total_expenses_gw": "total_expenses",
    "total_revenues_gf": "total_revenues",
    "total_revenues_gw": "total_revenues",
    "real_estate_fmv": "fmv_taxable_real_estate",
    "taxable_real_estate_fmv": "fmv_taxable_real_estate",
}


def _to_snake_case(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").lower()


def _canonical_field_name(field_name: str) -> str:
    snake = _to_snake_case(field_name)
    return FIELD_ALIASES.get(snake, snake)


def _flatten_record(record: Mapping[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}

    def walk(value: Mapping[str, Any]) -> None:
        for key, item in value.items():
            if isinstance(item, Mapping):
                walk(item)
                continue
            flattened[_canonical_field_name(key)] = item

    walk(record)
    return flattened


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = f"-{cleaned[1:-1]}"
        if cleaned in {"", "-", "n/a", "N/A"}:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _to_int(value: Any) -> int | str:
    if value is None or value == "":
        return ""
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return str(value)


def normalize_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return a canonical record with metadata and numeric fields normalized."""

    flattened = _flatten_record(record)
    normalized: dict[str, Any] = {field: "" for field in CANONICAL_FIELDS}

    normalized["locality"] = str(flattened.get("locality", "") or "")
    normalized["fiscal_year"] = _to_int(flattened.get("fiscal_year"))
    normalized["source_file"] = str(flattened.get("source_file", "") or "")
    normalized["report_type"] = str(flattened.get("report_type", "") or "")

    for field in NUMERIC_FIELDS:
        normalized[field] = _to_float(flattened.get(field))

    return normalized


def normalize_records(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Normalize a sequence of input records."""

    return [normalize_record(record) for record in records]
