from fiscal_health_pipeline.audit_report import render_audit_report


def test_render_audit_report_includes_summary_and_status():
    html = render_audit_report(
        [
            {
                "section": "summary",
                "name": "record_count",
                "value": "128",
                "percent": "",
            },
            {
                "section": "summary",
                "name": "average_filled_field_count",
                "value": "7.99",
                "percent": "",
            },
            {
                "section": "summary",
                "name": "total_warning_count",
                "value": "170",
                "percent": "",
            },
            {
                "section": "quality_status",
                "name": "PASS",
                "value": "54",
                "percent": "42.19%",
            },
            {
                "section": "field_coverage",
                "name": "total_liabilities",
                "value": "124",
                "percent": "96.88%",
            },
        ],
        title="Portfolio Audit",
    )

    assert "<h1>Portfolio Audit</h1>" in html
    assert "Draft records" in html
    assert "128" in html
    assert "PASS" in html
    assert "width: 42.19%" in html
    assert "total_liabilities" in html
