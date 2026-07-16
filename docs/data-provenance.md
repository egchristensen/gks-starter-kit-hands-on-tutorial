# Data provenance

Every committed input must have a `data/manifest.yaml` dataset entry containing its
source name and release, retrieval date and URL, license or terms, selection method
and source identifiers, file paths and SHA-256 checksums. Transformed GKS outputs
also record transformer repository/commit and pinned VRS, Cat-VRS, and VA-Spec
versions. Native bytes are never edited during transformation.

Phase 1's empty manifest is intentional. ClinVar record selection is a Phase 2
research task and must use exact upstream public data rather than invented content.
