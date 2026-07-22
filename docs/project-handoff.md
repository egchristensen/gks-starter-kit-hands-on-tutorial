# Project handoff

**Updated:** 2026-07-22
**Branch:** `main`
**Implementation phase:** Phase 2 — ClinVar fixture and end-to-end notebook

## Current state

Phase 1 is complete and the lightweight tutorial runs locally, in Docker, and
in an ordinary Google Colab runtime. Phase 2 is substantially implemented but
is not acceptance-complete because an exact release-matched ClinVar native/GKS
pair is not publicly available in a small extract.

The repository intentionally has not started Phase 3. The implementation plan
prohibits beginning the gnomAD module until the first ClinVar milestone passes
all required checks.

## Implemented deliverables

- Pinned Python, GKS model, development, and Colab dependencies.
- Data manifest, checksum verifier, JSON/JSONL/XML loaders, and GKS validation
  dispatch.
- Paired Jupytext notebooks:
  - `notebooks/00_start_here.ipynb`
  - `notebooks/01_clinvar_native_and_gks.ipynb`
- Colab bootstrap logic that clones or updates the repository, installs pinned
  requirements, and clears stale Python modules in reused runtimes.
- Two exact native NCBI ClinVar ESummary snapshots.
- Three exact candidate VRS object values selectively extracted from
  ClinVar-GKS key/value Parquet sections.
- One exact versioned ClinVar-GKS implementation-profile statement,
  `SCV005093950.2`, from pinned commit
  `b3f485375172f789e26b8626854ef1ac4db2e130`.
- Offline statement → Cat-VRS `CategoricalVariant` → VRS `Allele` traversal.
- Normative validation of the inline Cat-VRS and VRS objects.
- An explicit, tested demonstration that the outer ClinVar implementation
  profile is not the current normative VA-Spec oncogenicity representation.
- Deterministic JSON/JSONL export and an expected compact profile bundle.
- An executable provenance contract that validates required metadata, confines
  paths to `data/`, checks digests and syntax, and dispatches annotated normative
  objects to the pinned GKS models.
- A locked, non-root Docker image with token-authenticated Jupyter exposed only
  on the host loopback interface.
- A clean Colab-requirements CI smoke test and synchronization checks for every
  Jupytext notebook pair.
- Maintainer-only fixture refresh/build scripts that do not add DuckDB or other
  heavy tools to the tutorial runtime.

## Important provenance distinction

The bundled `SCV005093950.2` profile and the NCBI record for Variation ID
`44991` share verified identifiers: NCBI lists `SCV005093950` as a supporting
submission, and the profile identifies version `.2`. This supports the tutorial
traversal, but it does not prove that the two files came from the same ClinVar
release.

The public ClinVar-GKS Parquet files are unversioned. Their VRS key/value
sections expose exact JSON values, while the currently published Cat-VRS and
VA-Spec sections are flattened and do not expose original object JSON. The full
JSON release is several gigabytes and is explicitly outside tutorial scope.

Do not describe the current fixtures as an exact release-matched transformation
pair. Do not reconstruct flattened profile rows and present them as authoritative
upstream JSON.

Full research notes and acceptance status are in
`docs/clinvar-fixture-selection.md`.

## Validation baseline

The following passed immediately before this handoff:

```text
uv run ruff check .                              passed
uv run pytest                                    24 passed
uv run python scripts/verify_data.py             passed
uv run python scripts/execute_notebooks.py       2 notebooks passed
clean requirements-colab.txt environment         2 notebook pairs passed
uv run python -m build                           sdist and wheel built
docker compose build/up and container smoke      passed
git diff --check                                 passed
```

The repository contains no SeqRepo archive, UTA, PostgreSQL, full reference
archive, or mandatory Docker dependency.

## Preview links

- [Start Here in Colab](https://colab.research.google.com/github/egchristensen/gks-starter-kit-hands-on-tutorial/blob/main/notebooks/00_start_here.ipynb)
- [ClinVar native and GKS in Colab](https://colab.research.google.com/github/egchristensen/gks-starter-kit-hands-on-tutorial/blob/main/notebooks/01_clinvar_native_and_gks.ipynb)

For a clean Colab verification, use **Runtime → Disconnect and delete runtime**
and then **Runtime → Run all**.

## Recommended next steps

1. Obtain a small authoritative export from the ClinVar-GKS maintainers that
   identifies the exact ClinVar release, transformer commit, SCV/VCV versions,
   and all linked original GKS JSON objects.
2. Add the release-matched native and GKS files under their existing separate
   `data/native/clinvar/` and `data/gks/clinvar/` paths.
3. Record release URLs, model/profile versions, transformer commit, selection
   identifiers, retrieval time, licensing, and SHA-256 checksums in
   `data/manifest.yaml`.
4. Validate every normative object with the pinned packages and validate the
   ClinVar profile separately with its pinned profile schema.
5. Replace the candidate-pair caveats in notebook 01 only after the exact
   pairing is proven. Rerun every validation command listed above.
6. Compare the result with every Phase 2 acceptance criterion in
   `gks-hands-on-tutorial-implementation-plan.md`.
7. Begin Phase 3 (`02_vcf_to_vrs`) only after Phase 2 is acceptance-complete.

If an authoritative small export cannot be obtained, record that upstream
dependency rather than weakening provenance claims. Any proposal to relax the
release-pairing acceptance criterion should be an explicit project decision,
not an undocumented implementation shortcut.

## Fresh-machine setup

```bash
git clone https://github.com/egchristensen/gks-starter-kit-hands-on-tutorial.git
cd gks-starter-kit-hands-on-tutorial
uv sync --extra tutorial --extra dev
uv run python scripts/verify_data.py
uv run pytest
uv run python scripts/execute_notebooks.py
```

Before editing, read `gks-hands-on-tutorial-implementation-plan.md` in full and
check `git status -sb` to avoid overwriting unrelated work.
