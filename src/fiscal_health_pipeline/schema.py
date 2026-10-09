"""Canonical schema helpers for fiscal health records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FiscalRecord:
    """Normalized financial fields used by the ratio engine."""

    locality: str
    fiscal_year: int
    cash_and_equivalents: float | None = None
    investments: float | None = None
    current_liabilities: float | None = None
    total_liabilities: float | None = None
    unrestricted_net_position: float | None = None
    total_expenses: float | None = None
    charges_for_services: float | None = None
    general_revenues: float | None = None
    net_position_beginning: float | None = None
    net_position_ending: float | None = None
    total_tax_supported_debt: float | None = None
    fmv_taxable_real_estate: float | None = None
    assessed_tangible_personal_property: float | None = None
    assessed_public_service_corporations: float | None = None
    unassigned_fund_balance: float | None = None
    assigned_fund_balance: float | None = None
    committed_fund_balance: float | None = None
    other_committed_reserves: float | None = None
    total_fund_balance: float | None = None
    total_revenues: float | None = None
    debt_service_principal: float | None = None
    debt_service_interest: float | None = None
    prior_unassigned_fund_balance: float | None = None
    intergovernmental_operating_revenues: float | None = None
    enterprise_change_in_net_position: float | None = None
    enterprise_net_transfers: float | None = None
    enterprise_total_expenses: float | None = None
