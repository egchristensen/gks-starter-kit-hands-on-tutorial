# Data provenance

Every committed input must have a `data/manifest.yaml` dataset entry containing its
source name and release or explicit release policy, retrieval date and URL, license
or terms, selection method and source identifiers, file paths, and SHA-256 checksums.
Transformed GKS outputs also record transformer repository/commit and pinned VRS,
Cat-VRS, and VA-Spec versions. Native bytes are never edited during transformation.

`python scripts/verify_data.py` enforces the minimum metadata fields, confines
declared paths to `data/`, rejects duplicate declarations, checks sizes and
SHA-256 digests, parses JSON/JSONL, and validates files annotated with a
`gks_product` using the pinned normative models.

The first Phase 2 native fixture is an exact NCBI ESummary response. Its manifest
explicitly records that it comes from the live weekly API rather than a pinned
monthly archive. It is not described as paired with ClinVar-GKS until the exact
transformation input and output can be verified; see
`docs/clinvar-fixture-selection.md`.

The candidate VRS collection preserves the JSON value strings exposed by three
ClinVar-GKS key/value Parquet sections. Its manifest records the section ETags
and makes the unversioned-release limitation explicit. It must not be described
as an exact transformation pair until upstream release metadata supports that
claim.

The literature discovery vignette uses an unmodified PubMed ESummary snapshot
for PMID `23220880`. PubMed supplies bibliographic metadata, not a GKS mapping.
The notebook labels its paper-to-Cat-VRS connection as a tutorial-curated
candidate and does not attach a precise VRS allele to the protein-only mention.
