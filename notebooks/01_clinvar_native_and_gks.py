# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,kernelspec
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # ClinVar native data and candidate GKS objects
#
# [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egchristensen/gks-starter-kit-hands-on-tutorial/blob/main/notebooks/01_clinvar_native_and_gks.ipynb)
#
# ## Why this matters
#
# This notebook follows a real ClinVar variation from its native API summary to
# three linked VRS objects. It also shows why provenance must be checked before
# calling two records an exact transformation pair.
#
# ## Learning objectives
#
# - inspect native ClinVar identifiers and classifications;
# - validate VRS objects using the pinned reference model;
# - traverse Allele → SequenceLocation → SequenceReference locally; and
# - distinguish a candidate identifier link from a release-matched pairing.

# %%
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import google.colab  # type: ignore[import-not-found]  # noqa: F401
except ImportError:
    IN_COLAB = False
else:
    IN_COLAB = True

if IN_COLAB:
    repository_root = Path("/content/gks-starter-kit-hands-on-tutorial")
    if not (repository_root / ".git").exists():
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                "main",
                "https://github.com/egchristensen/"
                "gks-starter-kit-hands-on-tutorial.git",
                str(repository_root),
            ],
            check=True,
        )
    else:
        subprocess.run(
            ["git", "-C", str(repository_root), "pull", "--ff-only", "origin", "main"],
            check=True,
        )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--requirement",
            str(repository_root / "requirements-colab.txt"),
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--no-deps",
            "--editable",
            str(repository_root),
        ],
        check=True,
    )
    os.chdir(repository_root)
    sys.path.insert(0, str(repository_root / "src"))
    importlib.invalidate_caches()
    for module_name in tuple(sys.modules):
        if module_name == "gks_tutorial" or module_name.startswith("gks_tutorial."):
            del sys.modules[module_name]
else:
    repository_root = (
        Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
    )

from gks_tutorial.bundles import (
    build_clinvar_profile_bundle,
    index_objects,
    resolve_reference,
)
from gks_tutorial.clinvar import (
    classification_summary,
    esummary_record,
    inline_variation_path,
)
from gks_tutorial.gks_models import validate_gks_object
from gks_tutorial.io import load_json, load_jsonl, write_json, write_jsonl
from gks_tutorial.manifests import load_manifest, sha256, verify_manifest


def pretty_print(value: object) -> None:
    """Render structured cell output as stable, indented JSON."""
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))

# %% [markdown]
# ## Input data and provenance
#
# The native file is an unchanged NCBI ESummary response retrieved 2026-07-16.
# The VRS JSON values came from unversioned ClinVar-GKS Parquet files last
# modified 2026-07-07. Checksums make both committed snapshots reproducible.

# %%
manifest_path = repository_root / "data" / "manifest.yaml"
manifest = load_manifest(manifest_path)
issues = verify_manifest(manifest_path, repository_root=repository_root)
assert not issues
pretty_print(
    {
        "native": manifest["datasets"]["clinvar_native_esummary_12582"],
        "gks": manifest["datasets"]["clinvar_gks_candidate_vrs_12582"],
    }
)

# %% [markdown]
# ## Native representation

# %%
native_document = load_json(
    repository_root / "data/native/clinvar/VCV000012582.67-esummary.json"
)
native = esummary_record(native_document, "12582")
native_view = {
    "accession": native["accession_version"],
    "title": native["title"],
    "classifications": classification_summary(native),
}
pretty_print(native_view)

# %% [markdown]
# ## GKS representation
#
# These three objects represent sequence variation, not the clinical assertion.
# VRS deliberately does not carry ClinVar classification fields.

# %%
gks_objects = load_jsonl(repository_root / "data/gks/clinvar/VCV000012582.67-vrs.jsonl")
validated = [validate_gks_object(value, product="vrs") for value in gks_objects]
validated_view = [
    {"type": value.type, "id": getattr(value, "id", None)} for value in validated
]
pretty_print(validated_view)

# %% [markdown]
# ## Validation and traversal

# %%
sections = index_objects(gks_objects)
allele_id = "ga4gh:VA.LDaqvF3c3y1IG8wF4mORiRfB--9Jjfzp"
allele = sections["allele"][allele_id]
location = resolve_reference(allele["location"], sections)
sequence_reference = resolve_reference(location["sequenceReference"], sections)

traversal = {
    "allele": allele["id"],
    "location": location["id"],
    "sequence": sequence_reference["name"],
    "inter_residue_interval": [int(location["start"]), int(location["end"])],
    "state": allele["state"]["sequence"],
}
pretty_print(traversal)

# %% [markdown]
# ## Practical query
#
# VRS expressions let consumers select the notation they understand without
# changing the allele's identity. Here we retrieve the SPDI expression and show
# that the ClinVar classifications remain in the native knowledge record rather
# than being copied into VRS.

# %%
expression_by_syntax = {
    expression["syntax"]: expression["value"] for expression in allele["expressions"]
}
query_result = {
    "spdi": expression_by_syntax["spdi"],
    "vrs_identifier": allele["id"],
    "native_classifications": classification_summary(native),
    "classifications_stored_on_vrs_allele": "classification" in allele,
}
pretty_print(query_result)

# %% [markdown]
# ## Deterministic offline export
#
# The next cell exports the three linked VRS objects as compact JSONL, reloads
# them, validates each object, and compares its checksum with the committed
# source. This is an object-preserving export, not the final multi-product
# tutorial bundle.

# %%
output_path = repository_root / "outputs/clinvar-12582-vrs.jsonl"
write_jsonl(output_path, gks_objects)
exported_objects = load_jsonl(output_path)
for exported_object in exported_objects:
    validate_gks_object(exported_object, product="vrs")

source_path = repository_root / "data/gks/clinvar/VCV000012582.67-vrs.jsonl"
export_summary = {
    "path": output_path.relative_to(repository_root).as_posix(),
    "objects": len(exported_objects),
    "sha256": sha256(output_path),
    "matches_committed_bytes": sha256(output_path) == sha256(source_path),
}
pretty_print(export_summary)
assert exported_objects == gks_objects
assert export_summary["matches_committed_bytes"]

# %% [markdown]
# ## Statement → Cat-VRS → VRS traversal
#
# A second real record supplies the missing cross-product traversal. NCBI lists
# `SCV005093950` as a supporting submission for Variation ID `44991`. A pinned
# ClinVar-GKS repository commit contains the exact versioned
# `SCV005093950.2` profile statement with its categorical variant and VRS Allele
# inline.

# %%
profile_native_document = load_json(
    repository_root / "data/native/clinvar/VCV000044991.8-esummary.json"
)
profile_native = esummary_record(profile_native_document, "44991")
profile_statement = load_json(
    repository_root / "data/gks/clinvar/SCV005093950.2-S-ONCO.profile.json"
)

assert "SCV005093950" in profile_native["supporting_submissions"]["scv"]
categorical_variant, inline_allele = inline_variation_path(profile_statement)
validated_cat_vrs = validate_gks_object(categorical_variant, product="cat-vrs")
validated_inline_vrs = validate_gks_object(inline_allele, product="vrs")

profile_traversal = {
    "statement": profile_statement["id"],
    "proposition": profile_statement["proposition"]["type"],
    "cat_vrs": validated_cat_vrs.id,
    "vrs": validated_inline_vrs.id,
    "classification": profile_statement["classification"]["name"],
}
pretty_print(profile_traversal)

# %% [markdown]
# ## Normative object or implementation profile?
#
# The inline Cat-VRS and VRS objects are normative and validate above. The outer
# statement is an exact ClinVar-GKS implementation-profile example. It is not a
# normative VA-Spec object under the currently pinned package: the profile uses
# `objectCondition` for this oncogenicity proposition, while normative VA-Spec
# requires `objectTumorType`. We test the expected incompatibility explicitly.

# %%
try:
    validate_gks_object(profile_statement, product="va-spec")
except ValueError as profile_error:
    profile_validation = {
        "normative_va_spec": False,
        "reason_mentions_required_field": "objectTumorType" in str(profile_error),
    }
else:  # pragma: no cover - guards against accidentally changing the claim
    raise AssertionError("ClinVar implementation profile unexpectedly validated")

pretty_print(profile_validation)
assert profile_validation["reason_mentions_required_field"]

# %% [markdown]
# ## Compact self-contained profile bundle
#
# The final operation packages the exact statement and its inline objects with
# the native identifiers used to establish the candidate pairing. The container
# is tutorial-specific, not a new GA4GH standard.

# %%
profile_bundle = build_clinvar_profile_bundle(profile_native, profile_statement)
profile_bundle_path = repository_root / "outputs/clinvar-profile-bundle.json"
write_json(profile_bundle_path, profile_bundle)

expected_bundle = load_json(
    repository_root / "data/expected/clinvar-profile-bundle.json"
)
assert load_json(profile_bundle_path) == expected_bundle
pretty_print(
    {
        "path": profile_bundle_path.relative_to(repository_root).as_posix(),
        "sha256": sha256(profile_bundle_path),
        "matches_expected": True,
    }
)

# %% [markdown]
# ## Field mapping
#
# | Native evidence | VRS representation | Meaning |
# |---|---|---|
# | Variation ID `12582` | `ga4gh:VA...` | Content-derived allele identity |
# | GRCh38 expression | `SequenceLocation` | Inter-residue interval |
# | `NC_000012.12` | `SequenceReference` | Sequence and assembly context |
# | ClinVar classifications | Not in VRS | Belongs in VA-Spec statements |
#
# ## Exercises and expected answers
#
# 1. What base replaces the reference sequence? **`T`**.
# 2. How many residues does the location span? **One** (`end - start`).
# 3. Does successful VRS validation prove release pairing? **No**. Validation
#    proves schema conformance, while pairing requires transformation provenance.
# 4. Does the exported JSONL include classifications? **No**. It preserves the
#    VRS layer; classifications belong in VA-Spec statements.
# 5. Which parts of the second example are normative? **The inline Cat-VRS and
#    VRS objects.** The enclosing ClinVar statement is an implementation profile.
#
# ## Expected takeaways
#
# VRS provides precise, linked sequence-variation objects. Clinical meaning is a
# separate layer, and provenance is part of correctness rather than optional
# metadata.
#
# ## Limitations and next steps
#
# The notebook now demonstrates statement → categorical variant → VRS traversal
# using an exact versioned profile example. It still does **not** claim that the
# live NCBI summary and repository example came from the same ClinVar release.
# The public full-release Cat-VRS and VA-Spec Parquet sections remain flattened
# and unversioned. A release-matched native/profile fixture remains a prerequisite
# for declaring Phase 2 acceptance-complete. The expected profile bundle above
# is a teaching artifact, not a substitute for that missing release provenance.
# Continue with `literature_to_gks_discovery.ipynb` to use these identities in a
# paper-seeded discovery workflow.
