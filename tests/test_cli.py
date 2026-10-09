import csv

from fiscal_health_pipeline.cli import build_ratio_rows, run


def test_build_ratio_rows_keeps_metadata():
    rows = build_ratio_rows(
        [
            {
                "locality": "Example City",
                "fiscal_year": "2024",
                "source_file": "example.csv",
                "report_type": "synthetic",
                "cash_and_equivalents": "120",
                "investments": "30",
                "total_liabilities": "300",
            }
        ]
    )

    assert rows[0]["locality"] == "Example City"
    assert rows[0]["fiscal_year"] == "2024"
    assert rows[0]["source_file"] == "example.csv"
    assert rows[0]["report_type"] == "synthetic"
    assert rows[0]["ratio_02_solvency"] == 0.5


def test_run_writes_ratio_csv(tmp_path):
    input_path = tmp_path / "records.csv"
    output_path = tmp_path / "ratios.csv"
    input_path.write_text(
        "locality,fiscal_year,cash_and_equivalents,investments,total_liabilities\n"
        "Example City,2024,120,30,300\n",
        encoding="utf-8",
    )

    count = run(input_path, output_path)

    assert count == 1
    with output_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["locality"] == "Example City"
    assert rows[0]["ratio_02_solvency"] == "0.5"


def test_run_writes_normalized_json_input(tmp_path):
    input_path = tmp_path / "records.json"
    output_path = tmp_path / "ratios.csv"
    normalized_path = tmp_path / "normalized.csv"
    input_path.write_text(
        """
        {
          "records": [
            {
              "metadata": {"locality": "Example City", "fiscalYear": 2025},
              "governmentWide": {
                "cashAndEquivalents": 120,
                "investments": 30,
                "totalLiabilities": 300
              }
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    count = run(input_path, output_path, normalized_path)

    assert count == 1
    with output_path.open(newline="", encoding="utf-8") as file:
        ratio_rows = list(csv.DictReader(file))
    with normalized_path.open(newline="", encoding="utf-8") as file:
        normalized_rows = list(csv.DictReader(file))

    assert ratio_rows[0]["ratio_02_solvency"] == "0.5"
    assert normalized_rows[0]["cash_and_equivalents"] == "120.0"
