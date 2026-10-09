from fiscal_health_pipeline import compute_ratios
from fiscal_health_pipeline.schema import FiscalRecord


def test_compute_ratios_from_mapping():
    record = {
        "cash_and_equivalents": 120.0,
        "investments": 30.0,
        "current_liabilities": 50.0,
        "total_liabilities": 300.0,
        "unrestricted_net_position": 200.0,
        "total_expenses": 500.0,
        "charges_for_services": 80.0,
        "general_revenues": 420.0,
        "net_position_beginning": 1000.0,
        "net_position_ending": 1100.0,
        "total_tax_supported_debt": 250.0,
        "fmv_taxable_real_estate": 5000.0,
        "assessed_tangible_personal_property": 800.0,
        "assessed_public_service_corporations": 200.0,
        "unassigned_fund_balance": 100.0,
        "assigned_fund_balance": 40.0,
        "committed_fund_balance": 60.0,
        "other_committed_reserves": 0.0,
        "total_fund_balance": 250.0,
        "total_revenues": 600.0,
        "debt_service_principal": 30.0,
        "debt_service_interest": 10.0,
        "prior_unassigned_fund_balance": 80.0,
        "intergovernmental_operating_revenues": 90.0,
        "enterprise_change_in_net_position": 70.0,
        "enterprise_net_transfers": 20.0,
        "enterprise_total_expenses": 250.0,
    }

    ratios = compute_ratios(record)

    assert ratios["ratio_01_liquidity"] == 0.2
    assert ratios["ratio_02_solvency"] == 0.5
    assert ratios["ratio_03_unrestricted_net_position"] == 0.4
    assert ratios["ratio_04_net_position_growth"] == 0.1
    assert round(ratios["ratio_05_debt_burden"], 6) == 0.041667
    assert ratios["ratio_06_fiscal_cushion"] == 0.4
    assert round(ratios["ratio_07_fund_balance"], 6) == 0.416667
    assert ratios["ratio_08_structural_balance"] == 1.2
    assert round(ratios["ratio_09_debt_service_coverage"], 6) == 0.066667
    assert ratios["ratio_10_fund_balance_change"] == 0.25
    assert ratios["ratio_11_intergovernmental_dependency"] == 0.15
    assert ratios["ratio_12_enterprise_performance"] == 0.2


def test_compute_ratios_from_dataclass():
    record = FiscalRecord(
        locality="Example City",
        fiscal_year=2026,
        cash_and_equivalents=10.0,
        investments=5.0,
        total_liabilities=30.0,
    )

    ratios = compute_ratios(record)

    assert ratios["ratio_02_solvency"] == 0.5
    assert ratios["ratio_01_liquidity"] is None


def test_zero_denominator_returns_none():
    ratios = compute_ratios(
        {
            "cash_and_equivalents": 10.0,
            "investments": 5.0,
            "total_liabilities": 0.0,
        }
    )

    assert ratios["ratio_02_solvency"] is None
