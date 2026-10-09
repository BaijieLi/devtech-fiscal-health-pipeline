"""Extract fiscal field candidates from local CAFR/ACFR PDFs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from fiscal_health_pipeline.pdf_extraction import extract_pdf_candidates


FIELDNAMES = [
    "locality",
    "fiscal_year",
    "source_file",
    "source_path",
    "field_name",
    "matched_pattern",
    "candidate_value",
    "page_number",
    "confidence",
    "line_text",
]


def discover_pdfs(paths: list[str], recursive: bool = False) -> list[Path]:
    """Return PDF files from explicit files or directories."""

    discovered: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file() and path.suffix.lower() == ".pdf":
            discovered.append(path)
        elif path.is_dir():
            pattern = "**/*.pdf" if recursive else "*.pdf"
            discovered.extend(sorted(path.glob(pattern)))
    return sorted(discovered)


def extract_rows(pdf_paths: list[Path], max_pages: int | None) -> list[dict[str, object]]:
    """Extract candidate rows from PDF paths."""

    rows: list[dict[str, object]] = []
    for pdf_path in pdf_paths:
        metadata, candidates = extract_pdf_candidates(pdf_path, max_pages=max_pages)
        for candidate in candidates:
            rows.append(
                {
                    "locality": metadata.locality,
                    "fiscal_year": metadata.fiscal_year or "",
                    "source_file": metadata.source_file,
                    "source_path": metadata.source_path,
                    "field_name": candidate.field_name,
                    "matched_pattern": candidate.matched_pattern,
                    "candidate_value": candidate.value_text,
                    "page_number": candidate.page_number,
                    "confidence": candidate.confidence,
                    "line_text": candidate.line_text,
                }
            )
    return rows


def write_rows(rows: list[dict[str, object]], output_path: str | Path) -> None:
    """Write candidate rows to CSV."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract fiscal field candidates from local PDF files."
    )
    parser.add_argument("paths", nargs="+", help="PDF files or directories.")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search directories for PDFs.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=40,
        help="Maximum pages to inspect per PDF. Use 0 for all pages.",
    )
    parser.add_argument("--limit", type=int, help="Limit the number of PDFs.")
    parser.add_argument(
        "--output",
        default="outputs/pdf_field_candidates.csv",
        help="Output CSV path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    pdf_paths = discover_pdfs(args.paths, recursive=args.recursive)
    if args.limit is not None:
        pdf_paths = pdf_paths[: args.limit]
    max_pages = None if args.max_pages == 0 else args.max_pages
    rows = extract_rows(pdf_paths, max_pages=max_pages)
    write_rows(rows, args.output)
    print(f"Scanned {len(pdf_paths)} PDF file(s).")
    print(f"Wrote {len(rows)} candidate row(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
