# Architecture

## Pipeline Overview

```text
input report
  -> ingest
  -> extract candidate financial fields
  -> normalize to canonical schema
  -> validate fields
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

### Normalization

Responsible for converting extracted fields into a consistent schema, including
unit scaling, locality naming, fiscal year parsing, and field validation.
The current implementation normalizes common snake_case and camelCase fields
from synthetic examples into the canonical ratio schema.

### Ratio Engine

Responsible for computing the 12 Virginia fiscal health ratios from normalized
records. This layer is implemented first because it can be tested with synthetic
data without needing private source documents.

### Outputs

Planned outputs include normalized records, ratio tables, quality summaries, and
dashboard-ready tables.
Current local PDF extraction outputs are candidate CSV files under `outputs/`,
which is ignored by Git.
