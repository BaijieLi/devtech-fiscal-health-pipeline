from fiscal_health_pipeline.candidate_promotion import (
    choose_best_candidate,
    parse_candidate_value,
    promote_candidates,
    scaled_candidate_value,
)


def test_parse_candidate_value_handles_parentheses():
    assert parse_candidate_value("(41,412)") == -41412.0
    assert parse_candidate_value("1,200,000") == 1200000.0


def test_choose_best_candidate_prefers_total_line():
    selected = choose_best_candidate(
        [
            {
                "candidate_value": "100",
                "confidence": "0.65",
                "page_number": "4",
                "line_text": "Narrative mentions liabilities 100",
            },
            {
                "candidate_value": "200",
                "confidence": "0.65",
                "page_number": "5",
                "line_text": "Total liabilities $200",
            },
        ]
    )

    assert selected is not None
    assert selected["candidate_value"] == "200"


def test_scaled_candidate_value_uses_million_hint():
    value = scaled_candidate_value(
        {
            "candidate_value": "7.2",
            "line_text": "Charges for services increased by $7.2 million",
        }
    )

    assert value == 7200000.0


def test_promote_candidates_creates_record_and_trace():
    records, trace = promote_candidates(
        [
            {
                "locality": "Example City",
                "fiscal_year": "2025",
                "source_file": "example.pdf",
                "source_path": "/tmp/example.pdf",
                "field_name": "cash_and_equivalents",
                "candidate_value": "1,000",
                "page_number": "10",
                "confidence": "0.65",
                "line_text": "Cash and cash equivalents 1,000",
            }
        ]
    )

    assert len(records) == 1
    assert records[0]["locality"] == "Example City"
    assert records[0]["report_type"] == "pdf_candidate_draft"
    assert records[0]["cash_and_equivalents"] == 1000.0
    assert trace[0]["field_name"] == "cash_and_equivalents"
