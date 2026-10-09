"""Review draft PDF-derived normalized records for extraction quality."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from fiscal_health_pipeline.quality_review import review_records


QUALITY_FIELDNAMES = [
    "locality",
    "fiscal_year",
    "source_file",
    "report_type",
    "quality_status",
    "filled_field_count",
    "missing_core_fields",
    "missing_ratio_count",
    "missing_ratios",
    "warning_count",
    "warnings",
]


def read_records(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_quality_output(path: str | Path, rows: list[dict[str, object]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=QUALITY_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review draft normalized records created from PDF candidates."
    )
    parser.add_argument("records_csv", help="Draft normalized records CSV.")
    parser.add_argument(
        "--output",
        default="outputs/pdf_draft_quality_review.csv",
        help="Quality review CSV.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    records = read_records(args.records_csv)
    rows = review_records(records)
    write_quality_output(args.output, rows)

    status_counts = Counter(row["quality_status"] for row in rows)
    summary = ", ".join(
        f"{status}={count}" for status, count in sorted(status_counts.items())
    )
    print(f"Reviewed {len(rows)} draft record(s).")
    print(f"Status summary: {summary or 'no records'}")
    print(f"Wrote quality review to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
