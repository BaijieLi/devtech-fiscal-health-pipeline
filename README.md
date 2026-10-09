# DevTech Fiscal Health Pipeline

End-to-end prototype for extracting local government financial data from
CAFR/ACFR reports, normalizing it into an analysis-ready schema, and computing
Virginia fiscal health ratios.

This repository is being rebuilt as a clean public-facing project. It does not
include legacy class exports, old generated CSVs, raw client documents, or
private data.

## Project Goal

Local government financial reports are often published as PDFs with inconsistent
tables, terminology, and layouts. This project aims to make fiscal health
analysis more repeatable by turning those reports into structured fields and
ratio outputs that analysts can review, compare, and visualize.

## Planned Workflow

```text
CAFR / ACFR report
        |
        v
Document ingestion
        |
        v
Financial field extraction
        |
        v
Schema normalization + validation
        |
        v
12 Virginia fiscal health ratios
        |
        v
CSV / SQL-ready outputs + dashboard-ready tables
```

## Current Repository Status

This is a fresh GitHub project scaffold. The first implemented module is the
ratio computation layer, using synthetic test data only.

Next planned steps:

1. Add a small synthetic example dataset.
2. Build a clean extraction interface for PDF, Markdown, and JSON reports.
3. Add normalization rules and validation warnings.
4. Add reproducible pipeline commands.
5. Add dashboard screenshots or a lightweight Streamlit demo.

## Repository Structure

```text
.
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── project_plan.md
│   ├── ratio_definitions.md
│   ├── requirements.md
│   └── supabase_setup.md
├── src/
│   └── fiscal_health_pipeline/
│       ├── __init__.py
│       ├── ratios.py
│       └── schema.py
├── tests/
│   └── test_ratios.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Run the synthetic example:

```bash
python -m fiscal_health_pipeline.cli \
  data/examples/synthetic_fiscal_records.csv \
  --output outputs/synthetic_ratio_results.csv
```

Run the nested JSON example and write both normalized records and ratios:

```bash
python -m fiscal_health_pipeline.cli \
  data/examples/synthetic_fiscal_records.json \
  --normalized-output outputs/synthetic_normalized_records.csv \
  --output outputs/synthetic_json_ratio_results.csv
```

## Core Features Planned

- Ingest normalized CSV and nested JSON examples.
- Ingest fiscal reports from PDF and Markdown in later phases.
- Extract government-wide and fund-level financial components.
- Normalize fields into a consistent schema.
- Compute 12 Virginia fiscal health ratios with missing-value handling.
- Produce traceable, machine-readable outputs for review and visualization.

## Example Data

The current example dataset is synthetic. It exists only to demonstrate the
pipeline interface and ratio calculations without exposing private client data
or raw school project files.

## Notes

Raw financial reports and generated outputs should stay out of the public repo
unless they are public, documented, and intentionally included.

For private Supabase Storage files, use a local `.env` file based on
`.env.example`; never commit real keys.

To back up private PDFs locally before changing a Supabase project, see
`docs/supabase_setup.md`.

The same guide also explains how to upload the local backup into a new Supabase
Storage bucket.
