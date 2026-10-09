# Resume Bullets

Use the version that best matches the role. The project uses private source
PDFs locally, so keep resume wording focused on the pipeline, audit metrics, and
engineering decisions rather than raw document contents.

## Software Engineering Version

- Built a Python ETL pipeline that extracts fiscal fields from municipal
  CAFR/ACFR PDFs, normalizes records into a canonical schema, computes 12
  fiscal health ratios, and exports traceable CSV outputs.
- Added quality-review and audit-summary layers that classify draft records as
  `PASS`, `CAUTION`, or `REVIEW`, enabling analysts to identify missing fields,
  suspicious values, and malformed source PDFs before downstream analysis.
- Hardened batch PDF processing with parser error logging, layout-noise
  heuristics, unit-scaling logic, and 34 automated tests covering extraction,
  promotion, ratio computation, and reporting.

## Data Engineering Version

- Designed an end-to-end fiscal data pipeline for 153 private municipal
  financial PDFs, producing 2,541 field candidates, 128 draft normalized
  records, and 1,023 selected-value trace rows for analyst review.
- Implemented schema normalization, PDF candidate promotion, data quality
  checks, audit summaries, and static HTML reporting while keeping raw private
  files and generated outputs out of version control.
- Improved pipeline resilience by logging malformed PDF failures instead of
  stopping full-batch runs, with audit metrics showing 54 `PASS`, 47 `CAUTION`,
  and 27 `REVIEW` draft records in the latest local run.

## Data Analyst Version

- Created a repeatable workflow for reviewing local government financial
  reports, extracting key fiscal fields, and computing 12 Virginia fiscal
  health ratios from normalized records.
- Built quality reports that surface missing core fields, suspicious ratios, and
  field coverage gaps, helping prioritize the next extraction improvements.
- Summarized full-batch audit results in a portfolio-ready HTML report and
  documentation without exposing private source documents.

## Short Project Description

Python-based fiscal health analytics pipeline that turns messy municipal
financial PDFs into reviewable structured records, computes Virginia fiscal
health ratios, and generates quality-audit summaries for portfolio and analyst
review.

## Technical Keywords

Python, ETL, PDF extraction, pdfplumber, data validation, data quality checks,
schema normalization, CLI tooling, CSV exports, audit reporting, pytest,
Supabase Storage, fiscal analytics.
