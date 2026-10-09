# Project Plan

## Phase 1: Clean Public Scaffold

- Create a professional README.
- Define repo structure.
- Document requirements, architecture, ratios, and data schema.
- Implement a tested ratio calculation module using synthetic data.

## Phase 2: Minimal Working Pipeline

- Add a small synthetic input file. Done.
- Add JSON ingestion. Done for synthetic records.
- Normalize JSON records into the canonical schema. Done for synthetic records.
- Export ratio results to CSV. Done for normalized CSV inputs.

## Phase 3: Document Extraction Prototype

- Add safe Supabase local configuration documentation. Done.
- Add PDF parsing prototype. Done for text candidate extraction.
- Promote PDF candidates into draft normalized records. Done.
- Add draft-record quality review. Done for missing fields, suspicious values,
  and unusually large ratios.
- Improve PDF extraction heuristics from quality findings. Done for split
  currency values, fiscal-year noise, and date fragments.
- Add full-run audit summary metrics. Done for review status, warning
  categories, and field coverage.
- Add extraction error logging for malformed PDFs. Done.
- Document local full-run audit results without committing private outputs. Done.
- Add static HTML audit report renderer. Done.
- Add Markdown parser.
- Improve extraction confidence and field-specific warning rules.

## Phase 4: Portfolio Polish

- Add example outputs from public or synthetic data.
- Add screenshots or dashboard demo. Done for aggregate audit report preview.
- Add resume bullets and technical summary. Done.
- Review the repo for private data, class-only wording, and unnecessary files.
