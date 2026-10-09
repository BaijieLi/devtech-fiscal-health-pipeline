import csv

from fiscal_health_pipeline.cli import build_ratio_rows, run


def test_build_ratio_rows_keeps_metadata():
    rows = build_ratio_rows(
        [
            {
                "locality": "Example City",
                "fiscal_year": "2024",
                "cash_and_equivalents": "120",
                "investments": "30",
                "total_liabilities": "300",
            }
        ]
    )

    assert rows[0]["locality"] == "Example City"
    assert rows[0]["fiscal_year"] == "2024"
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
