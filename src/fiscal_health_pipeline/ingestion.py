"""Input readers for fiscal health records."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _read_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    if isinstance(payload, dict):
        if "records" not in payload:
            raise ValueError("JSON object inputs must contain a 'records' list")
        payload = payload["records"]

    if not isinstance(payload, list):
        raise ValueError("JSON input must be a list or an object with a 'records' list")

    if not all(isinstance(record, dict) for record in payload):
        raise ValueError("Each JSON record must be an object")

    return payload


def read_input_records(path: str | Path) -> list[dict[str, Any]]:
    """Read input records from CSV or JSON."""

    input_path = Path(path)
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return _read_csv(input_path)
    if suffix == ".json":
        return _read_json(input_path)
    raise ValueError(f"Unsupported input format: {suffix}")
