"""Command-line utilities for fiscal health ratio analysis."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

from .ratios import RATIO_LABELS, compute_ratios

METADATA_FIELDS = ("locality", "fiscal_year")


def read_records(path: str | Path) -> list[dict[str, str]]:
    """Read normalized fiscal records from a CSV file."""

    input_path = Path(path)
    with input_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def build_ratio_rows(records: Iterable[dict[str, str]]) -> list[dict[str, object]]:
    """Compute ratio output rows from normalized input records."""

    rows: list[dict[str, object]] = []
    for record in records:
        ratios = compute_ratios(record)
        row: dict[str, object] = {
            "locality": record.get("locality", ""),
            "fiscal_year": record.get("fiscal_year", ""),
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
    fieldnames = [*METADATA_FIELDS, *RATIO_LABELS.keys()]
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(input_path: str | Path, output_path: str | Path) -> int:
    """Read normalized records, compute ratios, and write a CSV output."""

    records = read_records(input_path)
    rows = build_ratio_rows(records)
    write_ratio_output(rows, output_path)
    return len(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute Virginia fiscal health ratios from normalized CSV data."
    )
    parser.add_argument("input", help="Path to a normalized fiscal records CSV.")
    parser.add_argument(
        "--output",
        default="outputs/ratio_results.csv",
        help="Path for the generated ratio CSV.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    count = run(args.input, args.output)
    print(f"Wrote {count} ratio row(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
