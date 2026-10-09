import json

from fiscal_health_pipeline.ingestion import read_input_records


def test_read_json_records_wrapper(tmp_path):
    input_path = tmp_path / "records.json"
    input_path.write_text(
        json.dumps({"records": [{"metadata": {"locality": "Example City"}}]}),
        encoding="utf-8",
    )

    records = read_input_records(input_path)

    assert records == [{"metadata": {"locality": "Example City"}}]


def test_read_csv_records(tmp_path):
    input_path = tmp_path / "records.csv"
    input_path.write_text("locality,fiscal_year\nExample City,2025\n", encoding="utf-8")

    records = read_input_records(input_path)

    assert records == [{"locality": "Example City", "fiscal_year": "2025"}]
