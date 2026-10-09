# Virginia Fiscal Health Ratio Definitions

The ratio engine uses a normalized record with one field per financial concept.
Missing denominators or zero denominators return `None` instead of raising an
exception.

| Ratio | Formula |
| --- | --- |
| 1. Liquidity | `(cash_and_equivalents + investments - current_liabilities) / (charges_for_services + general_revenues)` |
| 2. Solvency | `(cash_and_equivalents + investments) / total_liabilities` |
| 3. Unrestricted net position | `unrestricted_net_position / total_expenses` |
| 4. Net position growth | `(net_position_ending - net_position_beginning) / net_position_beginning` |
| 5. Debt burden | `total_tax_supported_debt / (fmv_taxable_real_estate + assessed_tangible_personal_property + assessed_public_service_corporations)` |
| 6. Fiscal cushion | `(unassigned_fund_balance + assigned_fund_balance + committed_fund_balance + other_committed_reserves) / total_expenses` |
| 7. Fund balance | `total_fund_balance / total_revenues` |
| 8. Structural balance | `total_revenues / total_expenses` |
| 9. Debt service coverage | `(debt_service_principal + debt_service_interest) / total_revenues` |
| 10. Fund balance change | `(unassigned_fund_balance - prior_unassigned_fund_balance) / prior_unassigned_fund_balance` |
| 11. Intergovernmental dependency | `intergovernmental_operating_revenues / total_revenues` |
| 12. Enterprise performance | `(enterprise_change_in_net_position - enterprise_net_transfers) / enterprise_total_expenses` |
