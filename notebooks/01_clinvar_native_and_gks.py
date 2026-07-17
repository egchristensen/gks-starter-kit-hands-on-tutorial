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
else:
    repository_root = (
        Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
    )

from gks_tutorial.bundles import index_objects, resolve_reference
from gks_tutorial.clinvar import classification_summary, esummary_record
from gks_tutorial.gks_models import validate_gks_object
from gks_tutorial.io import load_json, load_jsonl, write_jsonl
from gks_tutorial.manifests import load_manifest, sha256, verify_manifest

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
print(
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
print(native_view)

# %% [markdown]
# ## GKS representation
#
# These three objects represent sequence variation, not the clinical assertion.
# VRS deliberately does not carry ClinVar classification fields.

# %%
gks_objects = load_jsonl(repository_root / "data/gks/clinvar/VCV000012582.67-vrs.jsonl")
validated = [validate_gks_object(value, product="vrs") for value in gks_objects]
[(value.type, getattr(value, "id", None)) for value in validated]

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
print(traversal)

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
print(query_result)

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
print(export_summary)
assert exported_objects == gks_objects
assert export_summary["matches_committed_bytes"]

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
#
# ## Expected takeaways
#
# VRS provides precise, linked sequence-variation objects. Clinical meaning is a
# separate layer, and provenance is part of correctness rather than optional
# metadata.
#
# ## Limitations and next steps
#
# This is an intentionally incomplete Phase 2 notebook. The public Cat-VRS and
# VA-Spec Parquet sections currently flatten the original objects, and their
# files are unversioned. Until exact objects and release pairing are available,
# this notebook does **not** claim native → GKS transformation equivalence and
# does not fabricate statement traversal. The completed milestone will add
# statement → categorical variant → VRS traversal and the final multi-product
# compact bundle.
