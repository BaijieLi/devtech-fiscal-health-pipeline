# Architecture

## Pipeline Overview

```text
input report
  -> ingest
  -> extract candidate financial fields
  -> normalize to canonical schema
  -> validate fields
  -> review draft quality
  -> summarize audit metrics
  -> compute fiscal ratios
  -> export analysis-ready outputs
```

## Components

### Ingestion

Responsible for loading supported input files and passing them to the
appropriate parser. The current implementation supports normalized CSV and
nested JSON examples. PDF and Markdown extraction will be added in a later
phase.

### Extraction

Responsible for finding candidate line items and numeric values in financial
statements. Future implementation may combine table parsing, text patterns, and
layout-aware heuristics.
The current PDF prototype scans extracted page text and records page-level
candidate matches so analysts can review source lines before accepting values.
It also handles common PDF text artifacts such as split currency values, fiscal
years near narrative amounts, and date fragments that resemble small numbers.
Malformed files are logged to an extraction-error CSV so a batch run can
continue when individual PDFs fail to parse.

### Normalization

Responsible for converting extracted fields into a consistent schema, including
unit scaling, locality naming, fiscal year parsing, and field validation.
The current implementation normalizes common snake_case and camelCase fields
from synthetic examples into the canonical ratio schema.
PDF candidate promotion creates draft normalized records plus a trace CSV; these
records remain review-first outputs until selected values are audited.

### Quality Review

Responsible for flagging incomplete or suspicious draft records before they are
used for ratio analysis. Current checks include missing core fields, negative
values in fields that should be nonnegative, suspiciously small monetary values,
and unusually large ratio outputs that often indicate extraction or unit-scaling
issues.

### Ratio Engine

Responsible for computing the 12 Virginia fiscal health ratios from normalized
records. This layer is implemented first because it can be tested with synthetic
data without needing private source documents.

### Outputs

Planned outputs include normalized records, ratio tables, quality summaries, and
dashboard-ready tables.
Current local PDF extraction outputs are candidate CSV files under `outputs/`,
which is ignored by Git.
Quality review outputs are also written under `outputs/` so public source code
stays separate from generated private review artifacts.
Audit summary outputs aggregate review status, warning categories, and field
coverage so pipeline quality can be tracked without exposing source PDFs.
The latest local full-batch summary is documented in `docs/audit_summary.md`.
The static audit report renderer converts those aggregate CSV metrics into a
local HTML page suitable for screenshots and portfolio review.
