# Data provenance

Every committed input must have a `data/manifest.yaml` dataset entry containing its
source name and release, retrieval date and URL, license or terms, selection method
and source identifiers, file paths and SHA-256 checksums. Transformed GKS outputs
also record transformer repository/commit and pinned VRS, Cat-VRS, and VA-Spec
versions. Native bytes are never edited during transformation.

The first Phase 2 native fixture is an exact NCBI ESummary response. Its manifest
explicitly records that it comes from the live weekly API rather than a pinned
monthly archive. It is not described as paired with ClinVar-GKS until the exact
transformation input and output can be verified; see
`docs/clinvar-fixture-selection.md`.
