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


def inline_variation_path(
    statement: Mapping[str, Any],
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Return inline Cat-VRS and VRS objects from a ClinVar profile statement."""
    try:
        categorical_variant = statement["proposition"]["subjectVariant"]
        allele = next(
            member
            for member in categorical_variant["members"]
            if member.get("type") == "Allele"
        )
    except (KeyError, StopIteration, TypeError) as error:
        raise ValueError(
            "statement has no inline categorical variant and allele"
        ) from error
    return categorical_variant, allele
