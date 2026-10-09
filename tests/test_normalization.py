from fiscal_health_pipeline.normalization import normalize_record


def test_normalize_nested_json_record():
    normalized = normalize_record(
        {
            "metadata": {
                "locality": "Example City",
                "fiscalYear": "2025",
                "sourceFile": "example.json",
                "reportType": "synthetic",
            },
            "governmentWide": {
                "cashAndEquivalents": "12,000",
                "investments": "(500)",
            },
        }
    )

    assert normalized["locality"] == "Example City"
    assert normalized["fiscal_year"] == 2025
    assert normalized["source_file"] == "example.json"
    assert normalized["report_type"] == "synthetic"
    assert normalized["cash_and_equivalents"] == 12000.0
    assert normalized["investments"] == -500.0


def test_normalize_alias_fields():
    normalized = normalize_record(
        {
            "city": "Demo Town",
            "year": "2024",
            "cash": 10,
            "total_expenses_gw": 20,
            "total_revenues_gf": 25,
        }
    )

    assert normalized["locality"] == "Demo Town"
    assert normalized["fiscal_year"] == 2024
    assert normalized["cash_and_equivalents"] == 10.0
    assert normalized["total_expenses"] == 20.0
    assert normalized["total_revenues"] == 25.0
