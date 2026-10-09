# Audit Summary

This document summarizes local audit metrics from the private PDF corpus. Raw
PDFs, generated candidate rows, trace rows, and review outputs remain outside
Git under ignored local directories.

## Latest Local Full-Run Snapshot

The current local batch run scanned 153 PDF files from the private backup
corpus.

| Metric | Value |
| --- | ---: |
| PDF files scanned | 153 |
| PDF extraction errors logged | 1 |
| Field candidate rows extracted | 2,541 |
| Draft normalized records promoted | 128 |
| Selected-value trace rows written | 1,023 |
| Average filled fields per draft record | 7.99 |
| Total quality warnings | 170 |

## Quality Review Status

| Status | Count | Share |
| --- | ---: | ---: |
| PASS | 54 | 42.19% |
| CAUTION | 47 | 36.72% |
| REVIEW | 27 | 21.09% |

`PASS` records have no current quality warnings. `CAUTION` records are missing
one or more core fields. `REVIEW` records include suspicious values, negative
values where a field is expected to be nonnegative, or unusually large ratio
outputs that likely need analyst review.

## Most Common Warning Categories

| Warning category | Count |
| --- | ---: |
| missing_core_field | 135 |
| large_ratio | 16 |
| suspicious_small_value | 11 |
| negative_value | 8 |

## Core Field Coverage

| Field | Filled records | Coverage |
| --- | ---: | ---: |
| total_liabilities | 124 | 96.88% |
| cash_and_equivalents | 109 | 85.16% |
| total_expenses | 98 | 76.56% |
| total_revenues | 98 | 76.56% |
| current_liabilities | 94 | 73.44% |
| charges_for_services | 85 | 66.41% |
| total_fund_balance | 76 | 59.38% |
| investments | 73 | 57.03% |

The weakest core field is `total_fund_balance`, missing in 52 of 128 draft
records. That makes fund-balance extraction the highest-priority next heuristic
improvement.

## Reproduction Commands

```bash
PYTHONPATH=src python scripts/extract_pdf_candidates.py \
  data/raw/private/supabase_backup/testing_subset \
  --recursive \
  --max-pages 40 \
  --output outputs/pdf_field_candidates_full.csv \
  --errors-output outputs/pdf_extraction_errors_full.csv

PYTHONPATH=src python scripts/promote_pdf_candidates.py \
  outputs/pdf_field_candidates_full.csv \
  --records-output outputs/pdf_draft_normalized_records_full.csv \
  --trace-output outputs/pdf_draft_trace_full.csv

PYTHONPATH=src python scripts/review_pdf_drafts.py \
  outputs/pdf_draft_normalized_records_full.csv \
  --output outputs/pdf_draft_quality_review_full.csv

PYTHONPATH=src python scripts/summarize_quality_review.py \
  outputs/pdf_draft_quality_review_full.csv \
  --records-csv outputs/pdf_draft_normalized_records_full.csv \
  --output outputs/pdf_draft_audit_summary_full.csv
```
