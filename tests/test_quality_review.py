from fiscal_health_pipeline.quality_review import (
    missing_core_fields,
    review_record,
)


def test_missing_core_fields_detects_blank_values():
    missing = missing_core_fields(
        {
            "cash_and_equivalents": "",
            "total_liabilities": "1200",
            "total_expenses": "9000",
            "total_revenues": "10000",
            "total_fund_balance": "1500",
        }
    )

    assert missing == ["cash_and_equivalents"]


def test_review_record_flags_negative_nonnegative_field():
    row = review_record(
        {
            "locality": "Example City",
            "fiscal_year": "2025",
            "total_liabilities": "-100",
            "total_expenses": "9000",
            "total_revenues": "10000",
            "total_fund_balance": "1500",
            "cash_and_equivalents": "2000",
        }
    )

    assert row["quality_status"] == "REVIEW"
    assert "negative_value:total_liabilities=-100" in row["warnings"]


def test_review_record_flags_suspicious_small_money_value():
    row = review_record(
        {
            "locality": "Example City",
            "fiscal_year": "2025",
            "cash_and_equivalents": "2.4",
            "total_liabilities": "1200",
            "total_expenses": "9000",
            "total_revenues": "10000",
            "total_fund_balance": "1500",
        }
    )

    assert row["quality_status"] == "REVIEW"
    assert "suspicious_small_value:cash_and_equivalents=2.4" in row["warnings"]


def test_review_record_flags_large_ratio():
    row = review_record(
        {
            "locality": "Example City",
            "fiscal_year": "2025",
            "cash_and_equivalents": "200000",
            "investments": "100000",
            "total_liabilities": "1",
            "total_expenses": "9000",
            "total_revenues": "10000",
            "total_fund_balance": "1500",
        }
    )

    assert row["quality_status"] == "REVIEW"
    assert "large_ratio:ratio_02_solvency=300000" in row["warnings"]


def test_review_record_returns_pass_for_complete_reasonable_record():
    row = review_record(
        {
            "locality": "Example City",
            "fiscal_year": "2025",
            "cash_and_equivalents": "2000",
            "investments": "1000",
            "current_liabilities": "1000",
            "total_liabilities": "3000",
            "total_expenses": "9000",
            "total_revenues": "10000",
            "total_fund_balance": "1500",
            "charges_for_services": "2000",
            "general_revenues": "8000",
        }
    )

    assert row["quality_status"] == "PASS"
    assert row["warning_count"] == 0
