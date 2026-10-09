from fiscal_health_pipeline.audit_summary import summarize_quality_review


def test_summarize_quality_review_counts_statuses_and_warnings():
    rows = summarize_quality_review(
        [
            {
                "quality_status": "PASS",
                "filled_field_count": "5",
                "warning_count": "0",
                "warnings": "",
                "missing_core_fields": "",
            },
            {
                "quality_status": "REVIEW",
                "filled_field_count": "3",
                "warning_count": "2",
                "warnings": (
                    "missing_core_field:cash_and_equivalents|"
                    "large_ratio:ratio_02_solvency=12"
                ),
                "missing_core_fields": "cash_and_equivalents",
            },
        ]
    )

    by_key = {(row["section"], row["name"]): row for row in rows}

    assert by_key[("summary", "record_count")]["value"] == 2
    assert by_key[("summary", "average_filled_field_count")]["value"] == "4.00"
    assert by_key[("quality_status", "PASS")]["percent"] == "50.00%"
    assert by_key[("warning_category", "large_ratio")]["value"] == 1
    assert by_key[("missing_core_field", "cash_and_equivalents")]["value"] == 1


def test_summarize_quality_review_adds_field_coverage():
    rows = summarize_quality_review(
        [
            {
                "quality_status": "PASS",
                "filled_field_count": "1",
                "warning_count": "0",
            }
        ],
        normalized_records=[
            {"cash_and_equivalents": "1200", "total_liabilities": ""},
            {"cash_and_equivalents": "", "total_liabilities": "3000"},
        ],
    )

    by_key = {(row["section"], row["name"]): row for row in rows}

    assert by_key[("field_coverage", "cash_and_equivalents")]["value"] == 1
    assert by_key[("field_coverage", "cash_and_equivalents")]["percent"] == "50.00%"
    assert by_key[("field_coverage", "total_liabilities")]["value"] == 1
