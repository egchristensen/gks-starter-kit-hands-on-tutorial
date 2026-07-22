# Tutorial data

This directory contains small ClinVar and PubMed tutorial fixtures. Unmodified
source snapshots live under `native/`, upstream GKS representations under `gks/`,
and a deterministic tutorial-derived result under `expected/`.

Every data file must be declared in `manifest.yaml` with its source, release
policy, retrieval date and URL, license or terms, selection method, source
identifier, and SHA-256 checksum. GKS outputs also require transformer and pinned
model-version metadata. A file containing standalone normative objects can set
`gks_product` to `vrs`, `cat-vrs`, or `va-spec` so the integrity command validates
each object with the pinned model package.

Run `make verify-data` after changing fixtures or metadata. Native source bytes
must never be edited in place to resemble transformed output.
