"""Helpers for the literature-to-GKS discovery tutorial."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from gks_tutorial.clinvar import inline_variation_path


def pubmed_record(document: Mapping[str, Any], uid: str) -> Mapping[str, Any]:
    """Return one record from an unmodified PubMed ESummary response."""
    result = document.get("result")
    if not isinstance(result, Mapping):
        raise ValueError("PubMed ESummary document has no result object")
    record = result.get(uid)
    if not isinstance(record, Mapping):
        raise KeyError(f"PubMed ESummary document has no UID {uid!r}")
    return record


def publication_identifiers(record: Mapping[str, Any]) -> dict[str, str]:
    """Index the usable identifiers in a PubMed ESummary record by type."""
    identifiers: dict[str, str] = {}
    values = record.get("articleids", [])
    if not isinstance(values, list):
        return identifiers
    for value in values:
        if not isinstance(value, Mapping):
            continue
        identifier_type = value.get("idtype")
        identifier = value.get("value")
        if isinstance(identifier_type, str) and isinstance(identifier, str):
            identifiers[identifier_type] = identifier
    return identifiers


def build_discovery_index(
    article: Mapping[str, Any],
    native_record: Mapping[str, Any],
    profile_statement: Mapping[str, Any],
    *,
    paper_variant_label: str,
) -> list[dict[str, Any]]:
    """Build tutorial records sharing explicit Cat-VRS and VRS identity keys.

    The wrapper records are tutorial-specific. The paper receives only a
    candidate Cat-VRS concept mapping because a protein label alone does not
    establish one precise genomic VRS Allele.
    """
    article_uid = article.get("uid")
    if not isinstance(article_uid, str) or not article_uid:
        raise ValueError("PubMed record has no UID")
    if not paper_variant_label.strip():
        raise ValueError("paper variant label must not be empty")

    categorical_variant, allele = inline_variation_path(profile_statement)
    categorical_id = categorical_variant.get("id")
    allele_id = allele.get("id")
    variation_id = native_record.get("uid")
    if not all(
        isinstance(value, str) and value
        for value in (categorical_id, allele_id, variation_id)
    ):
        raise ValueError("ClinVar records have incomplete GKS identity")
    if categorical_id != f"clinvar:{variation_id}":
        raise ValueError("native and profile ClinVar variation identifiers differ")

    common_concept = {"categoricalVariantId": categorical_id}
    precise_identity = {
        **common_concept,
        "vrsAlleleId": allele_id,
    }
    return [
        {
            "recordType": "literature",
            "sourceId": f"PMID:{article_uid}",
            "label": article.get("title"),
            "reportedVariant": paper_variant_label,
            "gksIdentity": {
                **common_concept,
                "vrsAlleleId": None,
            },
            "mappingStatus": "tutorial-curated-candidate-concept",
        },
        {
            "recordType": "native-knowledgebase",
            "sourceId": native_record.get("accession_version"),
            "label": native_record.get("title"),
            "reportedVariant": native_record.get("title"),
            "gksIdentity": precise_identity,
            "mappingStatus": "identifier-linked-not-release-paired",
        },
        {
            "recordType": "gks-knowledge-statement",
            "sourceId": profile_statement.get("id"),
            "label": categorical_variant.get("name"),
            "reportedVariant": categorical_variant.get("name"),
            "gksIdentity": precise_identity,
            "mappingStatus": "upstream-inline-gks",
        },
    ]


def text_search(
    records: Iterable[Mapping[str, Any]], query: str
) -> list[Mapping[str, Any]]:
    """Find records whose source-native variant text contains a query."""
    normalized_query = query.strip().casefold()
    if not normalized_query:
        raise ValueError("query must not be empty")
    return [
        record
        for record in records
        if normalized_query in str(record.get("reportedVariant", "")).casefold()
    ]


def identity_search(
    records: Iterable[Mapping[str, Any]], identifier: str
) -> list[Mapping[str, Any]]:
    """Find records linked to a Cat-VRS or VRS identifier."""
    if not identifier.strip():
        raise ValueError("identifier must not be empty")
    matches: list[Mapping[str, Any]] = []
    for record in records:
        identity = record.get("gksIdentity")
        if isinstance(identity, Mapping) and identifier in identity.values():
            matches.append(record)
    return matches
