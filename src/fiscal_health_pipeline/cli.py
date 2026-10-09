"""Command-line utilities for fiscal health ratio analysis."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

from .ingestion import read_input_records
from .normalization import normalize_records
from .ratios import RATIO_LABELS, compute_ratios
from .schema import CANONICAL_FIELDS


RATIO_METADATA_FIELDS = ("locality", "fiscal_year", "source_file", "report_type")


def build_ratio_rows(records: Iterable[dict[str, str]]) -> list[dict[str, object]]:
    """Compute ratio output rows from normalized input records."""

    rows: list[dict[str, object]] = []
    for record in records:
        ratios = compute_ratios(record)
        row: dict[str, object] = {
            field: record.get(field, "") for field in RATIO_METADATA_FIELDS
        }
        for ratio_name in RATIO_LABELS:
            value = ratios[ratio_name]
            row[ratio_name] = "" if value is None else round(value, 6)
        rows.append(row)
    return rows


def write_ratio_output(rows: list[dict[str, object]], path: str | Path) -> None:
    """Write ratio rows to a CSV file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [*RATIO_METADATA_FIELDS, *RATIO_LABELS.keys()]
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_normalized_output(rows: list[dict[str, object]], path: str | Path) -> None:
    """Write normalized records to a CSV file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CANONICAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run(
    input_path: str | Path,
    output_path: str | Path,
    normalized_output_path: str | Path | None = None,
) -> int:
    """Read records, normalize them, compute ratios, and write CSV output."""

    raw_records = read_input_records(input_path)
    records = normalize_records(raw_records)
    rows = build_ratio_rows(records)
    write_ratio_output(rows, output_path)
    if normalized_output_path:
        write_normalized_output(records, normalized_output_path)
    return len(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute Virginia fiscal health ratios from CSV or JSON records."
    )
    parser.add_argument("input", help="Path to a fiscal records CSV or JSON file.")
    parser.add_argument(
        "--output",
        default="outputs/ratio_results.csv",
        help="Path for the generated ratio CSV.",
    )
    parser.add_argument(
        "--normalized-output",
        help="Optional path for the normalized records CSV.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    count = run(args.input, args.output, args.normalized_output)
    print(f"Wrote {count} ratio row(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
