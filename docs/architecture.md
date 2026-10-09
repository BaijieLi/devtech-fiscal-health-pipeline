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

Responsible for loading PDF, Markdown, or JSON files and passing them to the
appropriate parser.

### Extraction

Responsible for finding candidate line items and numeric values in financial
statements. Future implementation may combine table parsing, text patterns, and
layout-aware heuristics.

### Normalization

Responsible for converting extracted fields into a consistent schema, including
unit scaling, locality naming, fiscal year parsing, and field validation.

### Ratio Engine

Responsible for computing the 12 Virginia fiscal health ratios from normalized
records. This layer is implemented first because it can be tested with synthetic
data without needing private source documents.

### Outputs

Planned outputs include normalized records, ratio tables, quality summaries, and
dashboard-ready tables.
