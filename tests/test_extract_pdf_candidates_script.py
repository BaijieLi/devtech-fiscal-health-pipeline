import importlib


extract_script = importlib.import_module("scripts.extract_pdf_candidates")


def test_extract_rows_records_pdf_parse_errors(monkeypatch, tmp_path):
    pdf_path = tmp_path / "bad.pdf"
    pdf_path.write_text("not really a pdf", encoding="utf-8")

    def raise_error(path, max_pages=None):
        raise RuntimeError("parse failed")

    monkeypatch.setattr(extract_script, "extract_pdf_candidates", raise_error)

    rows, errors = extract_script.extract_rows([pdf_path], max_pages=1)

    assert rows == []
    assert len(errors) == 1
    assert errors[0]["source_file"] == "bad.pdf"
    assert errors[0]["error_type"] == "RuntimeError"
    assert errors[0]["error_message"] == "parse failed"
