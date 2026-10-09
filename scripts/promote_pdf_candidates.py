"""Promote PDF field candidates into draft normalized records."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from fiscal_health_pipeline.candidate_promotion import promote_candidates
from fiscal_health_pipeline.schema import CANONICAL_FIELDS


TRACE_FIELDNAMES = [
    "locality",
    "fiscal_year",
    "source_file",
    "source_path",
    "field_name",
    "selected_value",
    "candidate_value",
    "page_number",
    "confidence",
    "line_text",
]


def read_candidates(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(
    path: str | Path, rows: list[dict[str, object]], fieldnames: list[str] | tuple[str, ...]
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Promote PDF field candidates into draft normalized records."
    )
    parser.add_argument("candidates_csv", help="Candidate CSV from extract_pdf_candidates.")
    parser.add_argument(
        "--records-output",
        default="outputs/pdf_draft_normalized_records.csv",
        help="Draft normalized records CSV.",
    )
    parser.add_argument(
        "--trace-output",
        default="outputs/pdf_draft_trace.csv",
        help="Selected-value trace CSV.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    candidates = read_candidates(args.candidates_csv)
    records, trace_rows = promote_candidates(candidates)
    write_csv(args.records_output, records, CANONICAL_FIELDS)
    write_csv(args.trace_output, trace_rows, TRACE_FIELDNAMES)
    print(f"Promoted {len(records)} draft record(s).")
    print(f"Wrote {len(trace_rows)} selected trace row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
