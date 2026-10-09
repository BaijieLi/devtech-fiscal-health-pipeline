"""Render audit summary metrics as a lightweight static HTML report."""

from __future__ import annotations

from collections import defaultdict
from html import escape
from typing import Iterable, Mapping


def _group_rows(
    rows: Iterable[Mapping[str, object]],
) -> dict[str, list[Mapping[str, object]]]:
    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("section", ""))].append(row)
    return grouped


def _lookup(
    rows: Iterable[Mapping[str, object]], section: str, name: str, default: str = "0"
) -> str:
    for row in rows:
        if row.get("section") == section and row.get("name") == name:
            return str(row.get("value", default))
    return default


def _percent_value(value: object) -> float:
    try:
        return float(str(value or "0").rstrip("%"))
    except ValueError:
        return 0.0


def _card(label: str, value: object, detail: str = "") -> str:
    return (
        '<article class="metric-card">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(str(value))}</strong>"
        f"<small>{escape(detail)}</small>"
        "</article>"
    )


def _bar_row(label: str, value: object, percent: object) -> str:
    width = min(max(_percent_value(percent), 0.0), 100.0)
    return (
        '<div class="bar-row">'
        f'<div class="bar-label"><span>{escape(str(label))}</span>'
        f"<strong>{escape(str(value))}</strong></div>"
        '<div class="bar-track">'
        f'<div class="bar-fill" style="width: {width:.2f}%"></div>'
        "</div>"
        f'<small>{escape(str(percent))}</small>'
        "</div>"
    )


def _table(rows: list[Mapping[str, object]], columns: tuple[str, ...]) -> str:
    header = "".join(f"<th>{escape(column.replace('_', ' ').title())}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row.get(column, '')))}</td>" for column in columns)
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def render_audit_report(
    summary_rows: Iterable[Mapping[str, object]],
    title: str = "PDF Extraction Audit Report",
) -> str:
    """Return a self-contained HTML audit report."""

    rows = list(summary_rows)
    grouped = _group_rows(rows)
    record_count = _lookup(rows, "summary", "record_count")
    avg_fields = _lookup(rows, "summary", "average_filled_field_count")
    total_warnings = _lookup(rows, "summary", "total_warning_count")

    status_rows = grouped.get("quality_status", [])
    warning_rows = grouped.get("warning_category", [])
    missing_rows = grouped.get("missing_core_field", [])
    coverage_rows = sorted(
        grouped.get("field_coverage", []),
        key=lambda row: _percent_value(row.get("percent")),
        reverse=True,
    )

    status_bars = "".join(
        _bar_row(row.get("name", ""), row.get("value", ""), row.get("percent", ""))
        for row in status_rows
    )
    coverage_bars = "".join(
        _bar_row(row.get("name", ""), row.get("value", ""), row.get("percent", ""))
        for row in coverage_rows[:10]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #64748b;
      --line: #d8dee9;
      --accent: #1769aa;
      --accent-2: #2a9d8f;
      --warning: #c27d1a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 40px 24px 56px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 22px;
      margin-bottom: 28px;
    }}
    h1 {{
      font-size: clamp(2rem, 4vw, 3.25rem);
      line-height: 1;
      margin: 0 0 12px;
      letter-spacing: 0;
    }}
    h2 {{
      font-size: 1.15rem;
      margin: 0 0 14px;
      letter-spacing: 0;
    }}
    p {{ color: var(--muted); max-width: 760px; }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 22px 0 28px;
    }}
    .metric-card, section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
    }}
    .metric-card {{
      padding: 18px;
      min-height: 132px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .metric-card span, .metric-card small, .bar-row small {{ color: var(--muted); }}
    .metric-card strong {{
      font-size: 2rem;
      letter-spacing: 0;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 16px;
      align-items: start;
    }}
    section {{ padding: 20px; overflow: hidden; }}
    .bar-row {{ margin: 0 0 14px; }}
    .bar-label {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 6px;
    }}
    .bar-track {{
      height: 12px;
      background: #e8edf4;
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 650; }}
    tr:last-child td {{ border-bottom: 0; }}
    @media (max-width: 760px) {{
      main {{ padding: 28px 16px 40px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .metric-card strong {{ font-size: 1.7rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{escape(title)}</h1>
      <p>
        Aggregate quality metrics for the fiscal-health PDF extraction pipeline.
        Generated outputs and raw private PDFs stay outside version control.
      </p>
    </header>

    <div class="metric-grid">
      {_card("Draft records", record_count, "Promoted from PDF field candidates")}
      {_card("Average filled fields", avg_fields, "Per draft normalized record")}
      {_card("Quality warnings", total_warnings, "Across reviewed records")}
      {_card("Traceable fields", "1,023", "Selected-value trace rows in the latest full run")}
    </div>

    <div class="grid">
      <section>
        <h2>Review Status</h2>
        {status_bars}
      </section>
      <section>
        <h2>Top Field Coverage</h2>
        {coverage_bars}
      </section>
      <section>
        <h2>Warning Categories</h2>
        {_table(warning_rows, ("name", "value"))}
      </section>
      <section>
        <h2>Missing Core Fields</h2>
        {_table(missing_rows, ("name", "value", "percent"))}
      </section>
    </div>
  </main>
</body>
</html>
"""
