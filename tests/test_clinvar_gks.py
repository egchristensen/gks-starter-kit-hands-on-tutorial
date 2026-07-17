from pathlib import Path

import pytest
from pydantic import ValidationError

from gks_tutorial.bundles import (
    build_clinvar_profile_bundle,
    index_objects,
    resolve_reference,
)
from gks_tutorial.clinvar import esummary_record, inline_variation_path
from gks_tutorial.gks_models import validate_gks_object
from gks_tutorial.io import load_json, load_jsonl, write_jsonl
from gks_tutorial.manifests import sha256

FIXTURE = Path("data/gks/clinvar/VCV000012582.67-vrs.jsonl")
PROFILE = Path("data/gks/clinvar/SCV005093950.2-S-ONCO.profile.json")
PROFILE_NATIVE = Path("data/native/clinvar/VCV000044991.8-esummary.json")
EXPECTED_BUNDLE = Path("data/expected/clinvar-profile-bundle.json")


def test_every_bundled_clinvar_gks_object_validates() -> None:
    values = load_jsonl(FIXTURE)

    assert len(values) == 3
    for value in values:
        validate_gks_object(value, product="vrs")


def test_bundled_allele_resolves_to_location_and_sequence() -> None:
    sections = index_objects(load_jsonl(FIXTURE))
    allele = sections["allele"]["ga4gh:VA.LDaqvF3c3y1IG8wF4mORiRfB--9Jjfzp"]
    location = resolve_reference(allele["location"], sections)
    sequence = resolve_reference(location["sequenceReference"], sections)

    assert location["start"] == "25245349"
    assert location["end"] == "25245350"
    assert sequence["name"] == "NC_000012.12"


def test_candidate_vrs_export_is_byte_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "export.jsonl"

    write_jsonl(output, load_jsonl(FIXTURE))

    assert sha256(output) == sha256(FIXTURE)


def test_profile_contains_normative_cat_vrs_and_vrs_objects() -> None:
    statement = load_json(PROFILE)
    categorical_variant, allele = inline_variation_path(statement)

    validate_gks_object(categorical_variant, product="cat-vrs")
    validate_gks_object(allele, product="vrs")
    assert statement["id"] == "clinvar.submission:SCV005093950.2"
    assert categorical_variant["id"] == "clinvar:44991"


def test_profile_statement_is_not_misrepresented_as_normative_va_spec() -> None:
    statement = load_json(PROFILE)

    with pytest.raises(ValidationError, match="objectTumorType"):
        validate_gks_object(statement, product="va-spec")


def test_expected_profile_bundle_matches_reusable_builder() -> None:
    native = esummary_record(load_json(PROFILE_NATIVE), "44991")
    statement = load_json(PROFILE)

    generated = build_clinvar_profile_bundle(native, statement)

    assert generated == load_json(EXPECTED_BUNDLE)
    assert generated["nativeIdentifiers"] == {
        "clinvarVariationId": "44991",
        "vcvAccession": "VCV000044991.8",
        "scvAccession": "SCV005093950.2",
    }
