"""Render a static HTML report from audit summary metrics."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from fiscal_health_pipeline.audit_report import render_audit_report


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a static HTML report from audit summary metrics."
    )
    parser.add_argument("audit_summary_csv", help="CSV from summarize_quality_review.py.")
    parser.add_argument(
        "--output",
        default="outputs/pdf_draft_audit_report.html",
        help="HTML report output path.",
    )
    parser.add_argument(
        "--title",
        default="PDF Extraction Audit Report",
        help="Report title.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    rows = read_csv(args.audit_summary_csv)
    html = render_audit_report(rows, title=args.title)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote audit report to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
