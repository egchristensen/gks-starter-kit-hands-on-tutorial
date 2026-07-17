"""Small helpers for the bundled ClinVar ESummary snapshot."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def esummary_record(document: Mapping[str, Any], uid: str) -> Mapping[str, Any]:
    """Return one record from an unmodified ClinVar ESummary response."""
    result = document.get("result")
    if not isinstance(result, Mapping):
        raise ValueError("ClinVar ESummary document has no result object")
    record = result.get(uid)
    if not isinstance(record, Mapping):
        raise KeyError(f"ClinVar ESummary document has no UID {uid!r}")
    return record


def classification_summary(record: Mapping[str, Any]) -> dict[str, str]:
    """Select the three classification labels displayed in the tutorial."""
    fields = {
        "germline": "germline_classification",
        "clinical_impact": "clinical_impact_classification",
        "oncogenicity": "oncogenicity_classification",
    }
    summary: dict[str, str] = {}
    for label, field in fields.items():
        value = record.get(field)
        if isinstance(value, Mapping) and isinstance(value.get("description"), str):
            summary[label] = value["description"]
    return summary
