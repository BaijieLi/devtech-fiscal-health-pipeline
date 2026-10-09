# Project Requirements

## Objective

Build a prototype fiscal health analysis system that can turn local government
financial reports into normalized data and fiscal health ratios.

## Input Scope

The planned pipeline should support:

- PDF CAFR/ACFR reports
- Markdown exports
- JSON exports

## Extraction Targets

The system should identify and standardize:

- Government-wide statement values
- Fund-level statement values
- Assets, liabilities, fund balances, revenues, expenses, and debt measures
- Enterprise fund values where available
- Metadata such as locality, fiscal year, source file, and confidence

## Output Scope

The project should produce:

- Normalized CSV or SQL-ready tables
- Computed fiscal health ratios
- Data quality warnings for missing or inconsistent inputs
- Documentation explaining formulas, assumptions, and limitations

## Public Repository Rule

This repo should not include private client files, raw unpublished reports, old
class exports, or generated data unless each file is intentionally reviewed for
public sharing.
