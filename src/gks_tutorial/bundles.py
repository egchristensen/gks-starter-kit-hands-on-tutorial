"""Helpers for small, self-contained tutorial object collections."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

SECTION_BY_TYPE = {
    "SequenceReference": "sequenceReference",
    "SequenceLocation": "location",
    "Allele": "allele",
}


def object_identifier(value: Mapping[str, Any]) -> str:
    """Return the local bundle key used by a supported GKS object."""
    identifier = value.get("id")
    if not identifier and value.get("type") == "SequenceReference":
        identifier = value.get("refgetAccession")
    if not isinstance(identifier, str):
        raise ValueError(f"{value.get('type')!r} object has no identifier")
    return identifier


def index_objects(
    values: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, Mapping[str, Any]]]:
    """Index a small collection using ClinVar-GKS bundle section names."""
    sections: dict[str, dict[str, Mapping[str, Any]]] = {}
    for value in values:
        object_type = value.get("type")
        try:
            section = SECTION_BY_TYPE[str(object_type)]
        except KeyError as error:
            raise ValueError(
                f"unsupported bundle object type: {object_type!r}"
            ) from error
        sections.setdefault(section, {})[object_identifier(value)] = value
    return sections


def resolve_reference(
    reference: str, sections: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> Mapping[str, Any]:
    """Resolve a `#/section/key` reference inside an indexed collection."""
    if not reference.startswith("#/"):
        raise ValueError(f"not a local bundle reference: {reference!r}")
    try:
        section, key = reference[2:].split("/", 1)
        return sections[section][key]
    except (ValueError, KeyError) as error:
        raise KeyError(f"unresolved local reference: {reference!r}") from error


def build_clinvar_profile_bundle(
    native_record: Mapping[str, Any], statement: Mapping[str, Any]
) -> dict[str, Any]:
    """Build the deterministic Phase 2 bundle around an exact profile record."""
    supporting = native_record.get("supporting_submissions", {}).get("scv", [])
    statement_id = object_identifier(statement).removeprefix("clinvar.submission:")
    accession = statement_id.split(".", 1)[0]
    if accession not in supporting:
        raise ValueError(f"native record does not list supporting {accession}")
    return {
        "bundleType": "gks-tutorial-clinvar-profile",
        "bundleVersion": 1,
        "nativeIdentifiers": {
            "clinvarVariationId": native_record["uid"],
            "vcvAccession": native_record["accession_version"],
            "scvAccession": statement_id,
        },
        "profileStatus": (
            "ClinVar-GKS implementation profile with normative inline "
            "Cat-VRS and VRS objects"
        ),
        "statement": statement,
    }
