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
# # From a paper mention to GKS-linked discovery
#
# [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egchristensen/gks-starter-kit-hands-on-tutorial/blob/main/notebooks/literature_to_gks_discovery.ipynb)
#
# ## Why this matters
#
# A paper may name a variant in the language its readers expect, while databases
# use a gene alias, a three-letter amino-acid expression, transcript HGVS, genomic
# coordinates, or an internal accession. Exact text search fragments discovery
# across those representations.
#
# This notebook starts with the HER2 V777L variant discussed by Bose et al. in
# [Cancer Discovery](https://doi.org/10.1158/2159-8290.CD-12-0349)
# ([PMID 23220880](https://pubmed.ncbi.nlm.nih.gov/23220880/)). It then uses
# existing ClinVar-GKS objects to demonstrate how Cat-VRS concept identity and
# precise VRS allele identity support different, complementary discovery steps.
#
# ## Learning objectives
#
# - observe why source-native variant strings do not join reliably;
# - validate and inspect Cat-VRS and VRS objects;
# - use a Cat-VRS identifier for broad concept discovery;
# - use a VRS identifier for precise genomic matching; and
# - preserve uncertainty when a paper reports only a protein-level label.

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

from gks_tutorial.clinvar import esummary_record, inline_variation_path
from gks_tutorial.discovery import (
    build_discovery_index,
    identity_search,
    publication_identifiers,
    pubmed_record,
    text_search,
)
from gks_tutorial.gks_models import validate_gks_object
from gks_tutorial.io import load_json, write_json
from gks_tutorial.manifests import load_manifest, sha256, verify_manifest


def pretty_print(value: object) -> None:
    """Render structured cell output as stable, indented JSON."""
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


# %% [markdown]
# ## Input data and provenance
#
# The notebook uses three committed snapshots:
#
# 1. an unmodified PubMed ESummary record for the paper;
# 2. an unmodified ClinVar ESummary record for Variation ID 44991; and
# 3. an exact ClinVar-GKS profile example with inline Cat-VRS and VRS objects.
#
# The manifest records their sources and limitations. No network access is needed
# after the tutorial environment is installed.

# %%
manifest_path = repository_root / "data" / "manifest.yaml"
manifest = load_manifest(manifest_path)
issues = verify_manifest(manifest_path, repository_root=repository_root)
assert not issues

pretty_print(
    {
        "paper": manifest["datasets"]["literature_pubmed_esummary_23220880"],
        "clinvarNative": manifest["datasets"]["clinvar_native_esummary_44991"],
        "clinvarGks": manifest["datasets"][
            "clinvar_gks_profile_scv005093950_2"
        ],
    }
)

# %%
article = pubmed_record(
    load_json(
        repository_root / "data/native/literature/PMID23220880-esummary.json"
    ),
    "23220880",
)
article_ids = publication_identifiers(article)
paper_variant_label = "HER2 V777L"

pretty_print(
    {
        "title": article["title"],
        "journal": article["fulljournalname"],
        "published": article["pubdate"],
        "pmid": article_ids["pubmed"],
        "pmcid": article_ids["pmc"],
        "doi": article_ids["doi"],
        "sourceNativeVariantLabel": paper_variant_label,
    }
)

# %% [markdown]
# ## Native representation
#
# The paper uses the protein label HER2 V777L. ClinVar uses the official gene
# symbol ERBB2, a transcript expression, and the three-letter protein form
# p.Val777Leu. The GKS profile uses the ClinVar title. All are readable, but none
# is a stable cross-source join key.

# %%
native_document = load_json(
    repository_root / "data/native/clinvar/VCV000044991.8-esummary.json"
)
native_record = esummary_record(native_document, "44991")
profile_statement = load_json(
    repository_root / "data/gks/clinvar/SCV005093950.2-S-ONCO.profile.json"
)
categorical_variant, allele = inline_variation_path(profile_statement)

source_native_records = [
    {
        "recordType": "literature",
        "sourceId": "PMID:23220880",
        "reportedVariant": paper_variant_label,
    },
    {
        "recordType": "native-knowledgebase",
        "sourceId": native_record["accession_version"],
        "reportedVariant": native_record["title"],
    },
    {
        "recordType": "gks-knowledge-statement",
        "sourceId": profile_statement["id"],
        "reportedVariant": categorical_variant["name"],
    },
]
pretty_print(source_native_records)

# %% [markdown]
# ## Baseline discovery: exact source text
#
# Searching the source-native strings for the phrase from the paper returns only
# the paper. It misses ERBB2, Val777Leu, transcript HGVS, and genomic expressions.

# %%
text_hits = text_search(source_native_records, paper_variant_label)
pretty_print(
    {
        "query": paper_variant_label,
        "hitCount": len(text_hits),
        "sourceIds": [record["sourceId"] for record in text_hits],
    }
)
assert [record["sourceId"] for record in text_hits] == ["PMID:23220880"]

# %% [markdown]
# ## GKS representation and validation
#
# The profile contains a normative Cat-VRS CategoricalVariant and a normative VRS
# Allele. Cat-VRS supplies the broader ClinVar concept, while VRS supplies the
# precise GRCh38 allele and its equivalent expressions.

# %%
validated_concept = validate_gks_object(categorical_variant, product="cat-vrs")
validated_allele = validate_gks_object(allele, product="vrs")

gks_view = {
    "catVrs": {
        "type": validated_concept.type,
        "id": validated_concept.id,
        "name": categorical_variant["name"],
    },
    "vrs": {
        "type": validated_allele.type,
        "id": validated_allele.id,
        "name": allele["name"],
        "expressions": allele["expressions"],
    },
}
pretty_print(gks_view)

# %% [markdown]
# ## Improved discovery index
#
# We now add explicit identity keys to small tutorial wrapper records. The
# wrappers are not a new GKS specification; they demonstrate how an application
# can index normative GKS identifiers.
#
# The literature record receives a tutorial-curated candidate Cat-VRS mapping.
# Its VRS allele remains null because the protein-only paper label does not, by
# itself, prove one exact genomic allele.

# %%
discovery_records = build_discovery_index(
    article,
    native_record,
    profile_statement,
    paper_variant_label=paper_variant_label,
)
pretty_print(discovery_records)

# %% [markdown]
# ## Broad discovery with Cat-VRS
#
# A Cat-VRS concept query connects the paper, native ClinVar record, and GKS
# profile despite the HER2/ERBB2 and V777L/Val777Leu string differences.

# %%
concept_id = categorical_variant["id"]
concept_hits = identity_search(discovery_records, concept_id)
pretty_print(
    {
        "query": concept_id,
        "hitCount": len(concept_hits),
        "sources": [
            {
                "sourceId": record["sourceId"],
                "mappingStatus": record["mappingStatus"],
            }
            for record in concept_hits
        ],
    }
)
assert len(concept_hits) == 3

# %% [markdown]
# ## Precise discovery with VRS
#
# The VRS query returns only records that justify the exact genomic allele. The
# paper is intentionally absent. This is safer than silently converting a
# protein-level mention into a genomic claim.

# %%
allele_id = allele["id"]
allele_hits = identity_search(discovery_records, allele_id)
pretty_print(
    {
        "query": allele_id,
        "hitCount": len(allele_hits),
        "sourceIds": [record["sourceId"] for record in allele_hits],
        "paperIncluded": any(
            record["recordType"] == "literature" for record in allele_hits
        ),
    }
)
assert len(allele_hits) == 2
assert not any(record["recordType"] == "literature" for record in allele_hits)

# %% [markdown]
# ## Statement layer and practical interpretation
#
# The profile connects variation identity to an oncogenicity proposition and
# classification. Its inline Cat-VRS and VRS objects are normative. The enclosing
# ClinVar statement is an implementation profile, not the currently pinned
# normative VA-Spec representation, so the distinction remains visible.

# %%
try:
    validate_gks_object(profile_statement, product="va-spec")
except ValueError as profile_error:
    normative_va_spec = False
    validation_note = (
        "ClinVar implementation profile; current normative VA-Spec requires "
        "a different oncogenicity proposition shape"
    )
    assert "objectTumorType" in str(profile_error)
else:  # pragma: no cover
    normative_va_spec = True
    validation_note = "Unexpectedly validated as normative VA-Spec"

pretty_print(
    {
        "statement": profile_statement["id"],
        "propositionType": profile_statement["proposition"]["type"],
        "classification": profile_statement["classification"]["name"],
        "catVrsId": concept_id,
        "vrsAlleleId": allele_id,
        "normativeVaSpec": normative_va_spec,
        "note": validation_note,
    }
)
assert not normative_va_spec

# %% [markdown]
# ## Before and after

# %%
comparison = [
    {
        "strategy": "source-native text",
        "identityLevel": "literal phrase",
        "hits": len(text_hits),
        "tradeoff": "highly sensitive to aliases and notation",
    },
    {
        "strategy": "Cat-VRS concept",
        "identityLevel": "curated categorical variant",
        "hits": len(concept_hits),
        "tradeoff": "broad discovery; mapping provenance must remain visible",
    },
    {
        "strategy": "VRS allele",
        "identityLevel": "precise genomic variation",
        "hits": len(allele_hits),
        "tradeoff": "precise matching; excludes under-specified paper mentions",
    },
]
pretty_print(comparison)

# %% [markdown]
# ## Deterministic offline export
#
# The final cell exports the tutorial discovery index. The exported wrapper is
# application-specific; its GKS identity values point to the normative objects
# validated above.

# %%
output_path = repository_root / "outputs/erbb2-v777l-discovery-index.json"
write_json(output_path, discovery_records)
assert load_json(output_path) == discovery_records

pretty_print(
    {
        "path": output_path.relative_to(repository_root).as_posix(),
        "records": len(discovery_records),
        "sha256": sha256(output_path),
    }
)

# %% [markdown]
# ## Exercises and expected answers
#
# 1. Why did the text query return only one record? **The sources use different
#    gene aliases and variant syntaxes.**
# 2. Why did the Cat-VRS query return the paper? **A curator attached a candidate
#    concept mapping with explicit provenance.**
# 3. Why did the VRS query exclude the paper? **HER2 V777L alone does not prove
#    one exact genomic allele.**
# 4. Which objects are normative? **The inline Cat-VRS CategoricalVariant and VRS
#    Allele.**
# 5. Is the discovery wrapper a GKS standard? **No. It is tutorial application
#    data indexed by normative GKS identities.**
#
# ## Expected takeaways
#
# GKS improves discovery by separating broad categorical identity from precise
# molecular identity. It also makes uncertainty actionable: a source can
# participate in concept discovery without being assigned unsupported genomic
# precision.
#
# ## Limitations and next steps
#
# This compact example uses one paper, one live-PubMed bibliographic snapshot,
# and identifier-linked ClinVar fixtures that are not proven release-matched.
# The paper-to-Cat-VRS link is tutorial-curated and should be reviewed in a real
# curation workflow. No NLP system, general normalizer, live search service, or
# exhaustive literature index is included. The outer ClinVar profile remains
# non-normative with respect to the currently pinned VA-Spec model.
