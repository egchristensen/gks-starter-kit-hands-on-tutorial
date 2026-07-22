from pathlib import Path

import pytest

from gks_tutorial.clinvar import esummary_record
from gks_tutorial.discovery import (
    build_discovery_index,
    identity_search,
    publication_identifiers,
    pubmed_record,
    text_search,
)
from gks_tutorial.io import load_json

ARTICLE = Path("data/native/literature/PMID23220880-esummary.json")
NATIVE = Path("data/native/clinvar/VCV000044991.8-esummary.json")
PROFILE = Path("data/gks/clinvar/SCV005093950.2-S-ONCO.profile.json")


def _inputs():
    article = pubmed_record(load_json(ARTICLE), "23220880")
    native = esummary_record(load_json(NATIVE), "44991")
    profile = load_json(PROFILE)
    return article, native, profile


def test_pubmed_snapshot_identifies_the_seed_paper() -> None:
    article, _, _ = _inputs()

    assert article["title"].startswith("Activating HER2 mutations")
    assert publication_identifiers(article) == {
        "pubmed": "23220880",
        "mid": "NIHMS424713",
        "pmc": "PMC3570596",
        "pmcid": "pmc-id: PMC3570596;manuscript-id: NIHMS424713;",
        "doi": "10.1158/2159-8290.CD-12-0349",
        "pii": "2159-8290.CD-12-0349",
    }


def test_gks_identity_improves_cross_source_discovery() -> None:
    article, native, profile = _inputs()
    records = build_discovery_index(
        article, native, profile, paper_variant_label="HER2 V777L"
    )

    text_hits = text_search(records, "HER2 V777L")
    concept_hits = identity_search(records, "clinvar:44991")
    allele_hits = identity_search(
        records, "ga4gh:VA.NSu37RTJalr9pzHbxPBHAf-jPHjClxGE"
    )

    assert [record["recordType"] for record in text_hits] == ["literature"]
    assert len(concept_hits) == 3
    assert {record["recordType"] for record in allele_hits} == {
        "native-knowledgebase",
        "gks-knowledge-statement",
    }
    assert records[0]["gksIdentity"]["vrsAlleleId"] is None
    assert records[0]["mappingStatus"] == "tutorial-curated-candidate-concept"


def test_discovery_index_rejects_mismatched_clinvar_records() -> None:
    article, native, profile = _inputs()
    mismatched_native = {**native, "uid": "999"}

    with pytest.raises(ValueError, match="variation identifiers differ"):
        build_discovery_index(
            article,
            mismatched_native,
            profile,
            paper_variant_label="HER2 V777L",
        )
