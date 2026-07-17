from pathlib import Path

from gks_tutorial.bundles import index_objects, resolve_reference
from gks_tutorial.gks_models import validate_gks_object
from gks_tutorial.io import load_jsonl, write_jsonl
from gks_tutorial.manifests import sha256

FIXTURE = Path("data/gks/clinvar/VCV000012582.67-vrs.jsonl")


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
