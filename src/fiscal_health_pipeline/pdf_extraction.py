"""Lightweight PDF text extraction and fiscal field candidate detection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pdfplumber


FIELD_PATTERNS: dict[str, tuple[str, ...]] = {
    "cash_and_equivalents": (
        "cash and cash equivalents",
        "cash equivalents",
        "cash and investments",
    ),
    "investments": ("investments",),
    "current_liabilities": ("current liabilities",),
    "total_liabilities": ("total liabilities",),
    "unrestricted_net_position": (
        "unrestricted net position",
        "unrestricted net assets",
    ),
    "total_expenses": ("total expenses", "total expenditures"),
    "charges_for_services": ("charges for services", "charges for service"),
    "general_revenues": ("general revenues",),
    "total_revenues": ("total revenues",),
    "total_fund_balance": ("total fund balance", "total fund balances"),
    "unassigned_fund_balance": (
        "unassigned fund balance",
        "unassigned fund balances",
    ),
    "assigned_fund_balance": ("assigned fund balance", "assigned fund balances"),
    "committed_fund_balance": ("committed fund balance", "committed fund balances"),
    "debt_service_principal": ("principal retirement", "principal payments"),
    "debt_service_interest": ("interest and fiscal charges", "interest expense"),
    "total_tax_supported_debt": ("tax supported debt", "tax-supported debt"),
    "intergovernmental_operating_revenues": (
        "intergovernmental revenue",
        "intergovernmental revenues",
    ),
}

NUMBER_RE = re.compile(r"\(?-?\$?\s*\d[\d,]*(?:\.\d+)?\)?")
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")


@dataclass(frozen=True)
class PdfMetadata:
    locality: str
    fiscal_year: int | None
    source_file: str
    source_path: str


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class FieldCandidate:
    field_name: str
    matched_pattern: str
    value_text: str
    page_number: int
    line_text: str
    confidence: float


def _humanize_locality(value: str) -> str:
    cleaned = value.replace("_", " ").replace("-", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.title() if cleaned else "Unknown"


def infer_metadata_from_path(path: str | Path) -> PdfMetadata:
    """Infer locality and fiscal year from the storage-style PDF path."""

    pdf_path = Path(path)
    parts = pdf_path.parts
    fiscal_year: int | None = None
    locality = ""

    for index, part in enumerate(parts):
        if YEAR_RE.fullmatch(part):
            fiscal_year = int(part)
            if index > 0:
                locality = parts[index - 1]
            break

    if not locality:
        stem_parts = re.split(r"[,/]", pdf_path.stem)
        locality = stem_parts[-1].strip() if stem_parts else pdf_path.stem

    return PdfMetadata(
        locality=_humanize_locality(locality),
        fiscal_year=fiscal_year,
        source_file=pdf_path.name,
        source_path=str(pdf_path),
    )


def extract_pdf_text(path: str | Path, max_pages: int | None = None) -> list[PageText]:
    """Extract text from a PDF, returning one record per page."""

    pages: list[PageText] = []
    with pdfplumber.open(path) as pdf:
        selected_pages = pdf.pages[:max_pages] if max_pages else pdf.pages
        for index, page in enumerate(selected_pages, start=1):
            text = page.extract_text() or ""
            pages.append(PageText(page_number=index, text=text))
    return pages


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def _parse_number_text(value: str) -> str:
    return re.sub(r"\s+", "", value.replace("$", ""))


def _looks_financial_number(raw_value: str) -> bool:
    cleaned = re.sub(r"[^0-9]", "", raw_value)
    return (
        "$" in raw_value
        or "," in raw_value
        or "(" in raw_value
        or len(cleaned) >= 4
    )


def _line_numbers(line: str) -> list[str]:
    return [
        _parse_number_text(match.group(0))
        for match in NUMBER_RE.finditer(line)
        if _looks_financial_number(match.group(0))
    ]


def _phrase_matches(line_lower: str, phrase: str) -> bool:
    pattern = r"\b" + r"\s+".join(re.escape(part) for part in phrase.split()) + r"\b"
    return re.search(pattern, line_lower) is not None


def find_field_candidates(pages: Iterable[PageText]) -> list[FieldCandidate]:
    """Find field/value candidates from extracted page text."""

    candidates: list[FieldCandidate] = []
    seen: set[tuple[str, int, str]] = set()

    for page in pages:
        for raw_line in page.text.splitlines():
            line = _normalize_line(raw_line)
            if not line:
                continue
            line_lower = line.lower()
            values = _line_numbers(line)
            if not values:
                continue

            for field_name, patterns in FIELD_PATTERNS.items():
                for pattern in patterns:
                    if _phrase_matches(line_lower, pattern):
                        key = (field_name, page.page_number, line)
                        if key in seen:
                            continue
                        seen.add(key)
                        candidates.append(
                            FieldCandidate(
                                field_name=field_name,
                                matched_pattern=pattern,
                                value_text=values[-1],
                                page_number=page.page_number,
                                line_text=line,
                                confidence=0.65,
                            )
                        )
                        break

    return candidates


def extract_pdf_candidates(
    path: str | Path, max_pages: int | None = 40
) -> tuple[PdfMetadata, list[FieldCandidate]]:
    """Extract metadata and fiscal field candidates from one PDF."""

    metadata = infer_metadata_from_path(path)
    pages = extract_pdf_text(path, max_pages=max_pages)
    candidates = find_field_candidates(pages)
    return metadata, candidates
