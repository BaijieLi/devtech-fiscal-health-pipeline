"""Summarize PDF draft quality review outputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from fiscal_health_pipeline.audit_summary import (
    AUDIT_FIELDNAMES,
    summarize_quality_review,
)


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(path: str | Path, rows: list[dict[str, object]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=AUDIT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize PDF draft quality review metrics."
    )
    parser.add_argument("quality_review_csv", help="CSV from review_pdf_drafts.py.")
    parser.add_argument(
        "--records-csv",
        help="Optional draft normalized records CSV for field coverage metrics.",
    )
    parser.add_argument(
        "--output",
        default="outputs/pdf_draft_audit_summary.csv",
        help="Audit summary CSV.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    quality_rows = read_csv(args.quality_review_csv)
    records = read_csv(args.records_csv) if args.records_csv else None
    rows = summarize_quality_review(quality_rows, records)
    write_csv(args.output, rows)

    summary = {
        (row["section"], row["name"]): row["value"]
        for row in rows
        if row["section"] in {"summary", "quality_status"}
    }
    print(f"Summarized {summary.get(('summary', 'record_count'), 0)} record(s).")
    print(
        "Status summary: "
        f"PASS={summary.get(('quality_status', 'PASS'), 0)}, "
        f"CAUTION={summary.get(('quality_status', 'CAUTION'), 0)}, "
        f"REVIEW={summary.get(('quality_status', 'REVIEW'), 0)}"
    )
    print(f"Wrote audit summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
