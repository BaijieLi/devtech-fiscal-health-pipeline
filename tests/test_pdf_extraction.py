from pathlib import Path

from fiscal_health_pipeline.pdf_extraction import (
    PageText,
    find_field_candidates,
    infer_metadata_from_path,
)


def test_infer_metadata_from_storage_path():
    metadata = infer_metadata_from_path(
        Path("testing_subset/City_of_Bristol/2011/2011, City_of_Bristol.pdf")
    )

    assert metadata.locality == "City Of Bristol"
    assert metadata.fiscal_year == 2011
    assert metadata.source_file == "2011, City_of_Bristol.pdf"


def test_find_field_candidates_from_page_text():
    pages = [
        PageText(
            page_number=12,
            text=(
                "Cash and cash equivalents 1,200,000\n"
                "Total liabilities 4,500,000\n"
                "General revenues 6,700,000\n"
            ),
        )
    ]

    candidates = find_field_candidates(pages)

    by_field = {candidate.field_name: candidate for candidate in candidates}
    assert by_field["cash_and_equivalents"].value_text == "1,200,000"
    assert by_field["total_liabilities"].page_number == 12
    assert by_field["general_revenues"].matched_pattern == "general revenues"


def test_candidate_matching_avoids_substring_and_percent_noise():
    pages = [
        PageText(
            page_number=3,
            text=(
                "Unassigned fund balance was $0\n"
                "Assigned fund balance represents 23% of expenses\n"
                "Assigned fund balance 1,500,000\n"
            ),
        )
    ]

    candidates = find_field_candidates(pages)
    assigned_values = [
        candidate.value_text
        for candidate in candidates
        if candidate.field_name == "assigned_fund_balance"
    ]
    unassigned_values = [
        candidate.value_text
        for candidate in candidates
        if candidate.field_name == "unassigned_fund_balance"
    ]

    assert assigned_values == ["1,500,000"]
    assert unassigned_values == ["0"]


def test_number_parser_ignores_table_dashes():
    pages = [
        PageText(
            page_number=8,
            text="Principal Retirement 323,687 - - - - - 323,687",
        )
    ]

    candidates = find_field_candidates(pages)

    assert candidates[0].value_text == "323,687"
