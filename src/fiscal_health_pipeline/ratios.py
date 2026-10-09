"""Fiscal health ratio calculations.

The functions in this module operate on normalized records represented as a
mapping or a dataclass-like object. Missing values and zero denominators return
None so downstream exports can flag incomplete inputs without crashing.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

RatioResult = dict[str, float | None]

RATIO_LABELS: dict[str, str] = {
    "ratio_01_liquidity": "Liquidity",
    "ratio_02_solvency": "Solvency",
    "ratio_03_unrestricted_net_position": "Unrestricted net position",
    "ratio_04_net_position_growth": "Net position growth",
    "ratio_05_debt_burden": "Debt burden",
    "ratio_06_fiscal_cushion": "Fiscal cushion",
    "ratio_07_fund_balance": "Fund balance",
    "ratio_08_structural_balance": "Structural balance",
    "ratio_09_debt_service_coverage": "Debt service coverage",
    "ratio_10_fund_balance_change": "Fund balance change",
    "ratio_11_intergovernmental_dependency": "Intergovernmental dependency",
    "ratio_12_enterprise_performance": "Enterprise performance",
}


def _as_mapping(record: Any) -> Mapping[str, Any]:
    if is_dataclass(record):
        return asdict(record)
    if isinstance(record, Mapping):
        return record
    raise TypeError("record must be a mapping or dataclass instance")


def _value(record: Mapping[str, Any], field: str) -> float | None:
    value = record.get(field)
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sum_values(*values: float | None) -> float | None:
    if any(value is None for value in values):
        return None
    return sum(value for value in values if value is not None)


def _safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def compute_ratios(record: Any) -> RatioResult:
    """Compute all 12 fiscal health ratios for one normalized record."""

    r = _as_mapping(record)

    cash = _value(r, "cash_and_equivalents")
    investments = _value(r, "investments")
    current_liabilities = _value(r, "current_liabilities")
    total_liabilities = _value(r, "total_liabilities")
    unrestricted_net_position = _value(r, "unrestricted_net_position")
    total_expenses = _value(r, "total_expenses")
    charges_for_services = _value(r, "charges_for_services")
    general_revenues = _value(r, "general_revenues")
    net_position_beginning = _value(r, "net_position_beginning")
    net_position_ending = _value(r, "net_position_ending")
    total_tax_supported_debt = _value(r, "total_tax_supported_debt")
    fmv_taxable_real_estate = _value(r, "fmv_taxable_real_estate")
    assessed_tangible_personal_property = _value(
        r, "assessed_tangible_personal_property"
    )
    assessed_public_service_corporations = _value(
        r, "assessed_public_service_corporations"
    )
    unassigned_fund_balance = _value(r, "unassigned_fund_balance")
    assigned_fund_balance = _value(r, "assigned_fund_balance")
    committed_fund_balance = _value(r, "committed_fund_balance")
    other_committed_reserves = _value(r, "other_committed_reserves") or 0.0
    total_fund_balance = _value(r, "total_fund_balance")
    total_revenues = _value(r, "total_revenues")
    debt_service_principal = _value(r, "debt_service_principal")
    debt_service_interest = _value(r, "debt_service_interest")
    prior_unassigned_fund_balance = _value(r, "prior_unassigned_fund_balance")
    intergovernmental_operating_revenues = _value(
        r, "intergovernmental_operating_revenues"
    )
    enterprise_change_in_net_position = _value(
        r, "enterprise_change_in_net_position"
    )
    enterprise_net_transfers = _value(r, "enterprise_net_transfers")
    enterprise_total_expenses = _value(r, "enterprise_total_expenses")

    liquid_assets = _sum_values(cash, investments)
    operating_revenue = _sum_values(charges_for_services, general_revenues)
    assessed_value_base = _sum_values(
        fmv_taxable_real_estate,
        assessed_tangible_personal_property,
        assessed_public_service_corporations,
    )
    available_fund_balance = _sum_values(
        unassigned_fund_balance,
        assigned_fund_balance,
        committed_fund_balance,
        other_committed_reserves,
    )
    debt_service = _sum_values(debt_service_principal, debt_service_interest)

    liquidity_numerator = (
        liquid_assets - current_liabilities
        if liquid_assets is not None and current_liabilities is not None
        else None
    )
    net_position_change = (
        net_position_ending - net_position_beginning
        if net_position_ending is not None and net_position_beginning is not None
        else None
    )
    fund_balance_change = (
        unassigned_fund_balance - prior_unassigned_fund_balance
        if unassigned_fund_balance is not None
        and prior_unassigned_fund_balance is not None
        else None
    )
    enterprise_adjusted_change = (
        enterprise_change_in_net_position - enterprise_net_transfers
        if enterprise_change_in_net_position is not None
        and enterprise_net_transfers is not None
        else None
    )

    return {
        "ratio_01_liquidity": _safe_div(liquidity_numerator, operating_revenue),
        "ratio_02_solvency": _safe_div(liquid_assets, total_liabilities),
        "ratio_03_unrestricted_net_position": _safe_div(
            unrestricted_net_position, total_expenses
        ),
        "ratio_04_net_position_growth": _safe_div(
            net_position_change, net_position_beginning
        ),
        "ratio_05_debt_burden": _safe_div(
            total_tax_supported_debt, assessed_value_base
        ),
        "ratio_06_fiscal_cushion": _safe_div(available_fund_balance, total_expenses),
        "ratio_07_fund_balance": _safe_div(total_fund_balance, total_revenues),
        "ratio_08_structural_balance": _safe_div(total_revenues, total_expenses),
        "ratio_09_debt_service_coverage": _safe_div(debt_service, total_revenues),
        "ratio_10_fund_balance_change": _safe_div(
            fund_balance_change, prior_unassigned_fund_balance
        ),
        "ratio_11_intergovernmental_dependency": _safe_div(
            intergovernmental_operating_revenues, total_revenues
        ),
        "ratio_12_enterprise_performance": _safe_div(
            enterprise_adjusted_change, enterprise_total_expenses
        ),
    }
