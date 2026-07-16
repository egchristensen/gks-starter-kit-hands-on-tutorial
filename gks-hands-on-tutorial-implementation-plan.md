# GKS Hands-On Tutorial Prototype — Implementation Plan

**Date:** 2026-07-15  
**Status:** Prototype plan  
**Recommended delivery model:** Repository-first, with optional Google Colab launchers  
**Proposed prototype repository:** `gks-hands-on-tutorial`  
**Primary audience:** Developers, data modelers, technical product owners, and scientifically literate newcomers to GA4GH GKS

---

## 1. Decision

Build the tutorial as a **small, self-contained Python repository** that runs on an ordinary Linux laptop or server and whose notebooks can also be opened in Google Colab.

Do **not** make Colab the only supported environment. Colab is useful as a launch surface, but a repository should remain the source of truth because it provides:

- versioned code, data snapshots, tests, and documentation;
- deterministic execution outside a transient hosted notebook session;
- straightforward continuous integration;
- a path for community contributions through GitHub;
- the ability to pin GKS model versions and upstream data releases;
- a way to run without network access after dependencies are installed; and
- compatibility with both local Jupyter and Colab using the same notebooks.

The prototype should be a **companion to**, rather than application code embedded directly in, the current `ga4gh/gks-starter-kit` documentation repository. The Starter Kit can link each vignette to a runnable tutorial.

---

## 2. Product vision

The tutorial should let a learner follow the same real-world record through three views:

1. **Native source representation**  
   Examples: VCF, ClinVar XML/JSON, MaveDB metadata and score tables.

2. **GKS representation**  
   Examples: VRS Alleles, Cat-VRS categorical variants, and VA-Spec statements.

3. **Practical operation**  
   Examples: validation, content-based matching, traversal of linked objects, filtering, serialization, and comparison across sources.

The tutorial should teach GKS through concrete data transformations rather than through schema exposition alone.

### Core learner outcomes

After completing the core tutorial, a learner should be able to:

- explain the different roles of VRS, Cat-VRS, and VA-Spec;
- inspect a native genomic knowledge record and identify the information preserved in GKS;
- load and validate GKS JSON using the GA4GH Python reference implementations;
- trace a VA-Spec statement to a Cat-VRS object and then to a VRS variation;
- understand why content-derived variation identifiers enable matching;
- serialize objects to JSON and YAML without losing provenance;
- distinguish a normative specification object from an implementation-specific profile; and
- identify what additional infrastructure is needed for full normalization of arbitrary HGVS or VCF input.

---

## 3. Scope boundaries

### In scope for the prototype

- Python 3.11-compatible code.
- Jupyter notebooks paired with text using Jupytext.
- Small, committed data snapshots.
- VRS, Cat-VRS, and VA-Spec model validation.
- Native-to-GKS side-by-side examples.
- A simple VCF-to-VRS exercise for already-normalized variants.
- A real ClinVar-to-GKS example using outputs from ClinVar-GKS.
- Optional Colab badges.
- A lightweight Docker image that contains only the tutorial runtime.
- Automated notebook execution and data validation in CI.
- Provenance metadata for every bundled dataset.

### Explicitly out of scope for the prototype

- Shipping a complete SeqRepo archive.
- Shipping UTA or PostgreSQL.
- Requiring Docker to complete the core tutorial.
- Processing a complete ClinVar or gnomAD release.
- Supporting every VCF normalization edge case.
- Reproducing the full ClinVar-GKS BigQuery pipeline.
- Defining a normative new VA-Spec profile for MaveDB.
- Building a production data registry or public API.
- Duplicating the product Quick Start documentation.

### Design rule

The **core path must not require a local service, database, cloud account, or large reference dataset**. Full normalization should be an optional extension.

---

## 4. Recommended real-world examples

## Example A — ClinVar native records and ClinVar-GKS objects

**Priority:** Required for the minimum viable tutorial.

Use a small, curated set of ClinVar records for which both native source data and GKS representations are available.

### Bundle

- one compact native ClinVar XML or API JSON snapshot;
- one small native VCF excerpt when available;
- matching ClinVar-GKS `variation` JSONL records;
- matching `scv_inline` or `vcv_inline` VA-Spec records;
- a manifest that documents the ClinVar release, record identifiers, retrieval date, source URL, transformation version, and checksums.

### Learner activities

- inspect how a classification is represented in the native ClinVar record;
- inspect the corresponding VRS, Cat-VRS, and VA-Spec objects;
- validate the GKS objects with Pydantic models;
- traverse statement → categorical variation → defining VRS variation;
- compare native identifiers with content-derived GKS identifiers;
- query a JSONL collection for classifications about the same variation;
- export a compact, self-contained GKS bundle.

### Why this should be first

ClinVar-GKS already demonstrates all three major GKS products and provides a concrete producer implementation. It is the best example for showing the ecosystem rather than one specification in isolation.

---

## Example B — Small gnomAD VCF excerpt to VRS

**Priority:** Required for the minimum viable tutorial.

Use a very small, preselected VCF excerpt, preferably 10–30 variants from a single GRCh38 region. The end user should never need to download a complete chromosome VCF.

### Bundle

- a header-preserving VCF excerpt;
- a stripped TSV view containing only `CHROM`, `POS`, `ID`, `REF`, `ALT`, and selected allele-frequency fields;
- a chromosome-to-sequence-accession mapping;
- expected VRS JSON objects;
- expected VRS identifiers;
- a provenance manifest with release and selection coordinates.

### Learner activities

- parse VCF coordinates and alleles;
- convert one-based VCF coordinates to inter-residue coordinates;
- construct VRS Alleles for already-normalized SNVs and simple indels;
- compute or verify identifiers;
- group equivalent input rows by VRS identifier;
- compare the compact VRS representation with source annotations that are intentionally not carried into VRS.

### Important limitation

The core notebook should clearly state that it demonstrates **representation and identity**, not a complete general-purpose VCF normalization pipeline. It should reject unsupported symbolic alleles, breakends, multiallelic rows not yet split, and variants requiring complex normalization.

### Optional extension

Add a separate notebook showing how the same input can be processed with a SeqRepo-backed or REST-backed data proxy. This notebook must be skipped automatically when the optional service is unavailable.

---

## Example C — MaveDB native score data to a candidate VA-Spec profile

**Priority:** Advanced module after the core prototype works.

Use a small MaveDB score set snapshot containing metadata plus a limited number of variant scores.

### Bundle

- score set metadata JSON;
- a small score table;
- mapped VRS variation objects when available;
- an explicitly labeled **experimental** VA-Spec representation;
- a profile notes document listing unresolved mapping questions.

### Learner activities

- inspect native assay and score metadata;
- map variant descriptions to VRS objects;
- represent a functional-impact result as a VA-Spec statement;
- preserve assay context and score provenance;
- identify which fields require a formal community profile decision.

### Governance rule

Do not present the output as a finalized normative MaveDB/VA-Spec profile. Treat it as an implementation experiment that can inform the open integration work.

---

## 5. Tutorial sequence

Keep the core path to four notebooks. Put optional material in an `advanced/` folder.

### `00_start_here.ipynb`

- Explain the tutorial map.
- Display installed package versions.
- Load the data manifest.
- Run a small environment health check.
- Explain VRS, Cat-VRS, and VA-Spec using one sentence each.
- Show the same example entity at each GKS layer.
- Confirm that all bundled files pass checksum verification.

### `01_clinvar_native_and_gks.ipynb`

- Load a native ClinVar record.
- Load the paired ClinVar-GKS variation and assertion records.
- Display a field mapping table.
- Validate objects with the Python model packages.
- Traverse linked objects.
- Answer small exercises using ordinary Python.
- Write a compact GKS bundle to `outputs/`.

### `02_vcf_to_vrs.ipynb`

- Read the small gnomAD VCF excerpt.
- Split alleles if necessary.
- Explain coordinate conversion.
- Construct supported VRS Alleles.
- Verify expected identifiers.
- Demonstrate deduplication by VRS identifier.
- Record unsupported rows and reasons without crashing.

### `03_query_and_exchange.ipynb`

- Load a mixed JSONL collection.
- Filter by variation identifier, condition, classification, and provenance.
- Compare inline and by-reference representations.
- Serialize selected objects to JSON and YAML.
- Build a simple exchange package with a manifest.
- Explain how a consumer could replace local files with a registered implementer endpoint later.

### `advanced/04_mavedb_va_spec_experiment.ipynb`

- Load a native MaveDB score set.
- Construct or load VRS variations.
- Build an experimental VA-Spec representation.
- Validate what can be validated.
- List profile gaps and design questions.

### `advanced/05_full_normalization_optional.ipynb`

- Detect a configured data proxy.
- Demonstrate normalization of selected HGVS or VCF inputs.
- Skip with a clear message when no proxy is configured.
- Never block completion of the core tutorial.

---

## 6. Proposed repository layout

```text
gks-hands-on-tutorial/
├── README.md
├── LICENSE
├── CITATION.cff
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── pyproject.toml
├── uv.lock
├── requirements-colab.txt
├── Makefile
├── Dockerfile
├── compose.yaml
├── .python-version
├── .gitignore
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── data-integrity.yml
├── notebooks/
│   ├── 00_start_here.ipynb
│   ├── 00_start_here.py
│   ├── 01_clinvar_native_and_gks.ipynb
│   ├── 01_clinvar_native_and_gks.py
│   ├── 02_vcf_to_vrs.ipynb
│   ├── 02_vcf_to_vrs.py
│   ├── 03_query_and_exchange.ipynb
│   ├── 03_query_and_exchange.py
│   └── advanced/
│       ├── 04_mavedb_va_spec_experiment.ipynb
│       ├── 04_mavedb_va_spec_experiment.py
│       ├── 05_full_normalization_optional.ipynb
│       └── 05_full_normalization_optional.py
├── src/
│   └── gks_tutorial/
│       ├── __init__.py
│       ├── environment.py
│       ├── io.py
│       ├── manifests.py
│       ├── clinvar.py
│       ├── vcf.py
│       ├── gks_models.py
│       ├── bundles.py
│       ├── display.py
│       └── resources/
│           └── sequence_accessions.yaml
├── data/
│   ├── manifest.yaml
│   ├── native/
│   │   ├── clinvar/
│   │   ├── gnomad/
│   │   └── mavedb/
│   ├── gks/
│   │   ├── clinvar/
│   │   ├── gnomad/
│   │   └── mavedb_experimental/
│   └── expected/
│       └── identifiers.json
├── scripts/
│   ├── refresh_clinvar_fixture.py
│   ├── refresh_gnomad_fixture.py
│   ├── refresh_mavedb_fixture.py
│   ├── verify_data.py
│   ├── generate_colab_requirements.py
│   └── execute_notebooks.py
├── tests/
│   ├── test_data_manifest.py
│   ├── test_clinvar_examples.py
│   ├── test_vcf_conversion.py
│   ├── test_gks_validation.py
│   ├── test_bundle_roundtrip.py
│   └── test_notebooks.py
├── docs/
│   ├── architecture.md
│   ├── data-provenance.md
│   ├── tutorial-authoring.md
│   ├── limitations.md
│   └── starter-kit-integration.md
└── outputs/
    └── .gitkeep
```

---

## 7. Dependency strategy

Use a `pyproject.toml` as the primary dependency declaration and commit a lock file.

### Runtime dependencies

Pin compatible releases of:

- `ga4gh.vrs`
- `ga4gh.cat_vrs`
- `ga4gh.va_spec`
- `pydantic`
- `PyYAML`
- `requests` or `httpx`
- `pandas`
- `jupyterlab`
- `jupytext`
- `rich`
- `jsonschema`

### Development dependencies

- `pytest`
- `pytest-cov`
- `nbmake` or `pytest-notebook`
- `ruff`
- `pre-commit`
- `mypy`, if type checking remains low-friction
- `build`

### Optional normalization dependencies

Keep these in a separate extra such as `[project.optional-dependencies.normalization]`:

- SeqRepo support
- HGVS support
- `pysam`
- any data-proxy client needed by the selected implementation

### Packaging rules

- Support Python 3.11 as the tested baseline.
- Avoid direct Git dependencies in the default environment.
- Pin GKS package versions for each tutorial release.
- Generate `requirements-colab.txt` from the lock or resolved environment.
- Document package versions in notebook output.
- Update versions only through a tested dependency-update pull request.

---

## 8. Data provenance contract

Every input snapshot must have an entry in `data/manifest.yaml`.

Example structure:

```yaml
datasets:
  clinvar_example:
    kind: native
    source_name: ClinVar
    source_release: "YYYY-MM-DD"
    retrieved_at: "YYYY-MM-DD"
    source_url: "https://..."
    license: "public-domain-or-source-terms"
    files:
      - path: data/native/clinvar/example.xml
        sha256: "..."
    selection:
      identifiers: ["VCV...", "SCV..."]
    paired_outputs:
      - data/gks/clinvar/variation.jsonl
      - data/gks/clinvar/vcv_inline.jsonl
    transformer:
      name: ClinVar-GKS
      repository: "https://github.com/clingen-data-model/clinvar-gks"
      commit: "<commit-sha>"
    gks_versions:
      vrs: "<version>"
      cat_vrs: "<version>"
      va_spec: "<version>"
```

### Data rules

- Commit only small educational snapshots.
- Never silently refresh data.
- Refresh scripts must write to a temporary directory first.
- A refresh must produce a manifest diff.
- CI must verify all checksums.
- Record upstream license or usage terms.
- Preserve source identifiers.
- Keep source data unchanged; write transformations to separate paths.
- Include a human-readable README in each dataset directory.
- Do not include protected, patient-level, or access-controlled data.

---

## 9. Lightweight VCF-to-VRS design

Implement only the subset needed for an educational exercise.

### Supported in the core converter

- GRCh38 contigs with explicit accession mapping.
- Single alternate allele per emitted record.
- SNVs.
- Simple insertions and deletions already represented in normalized form.
- Literal sequence states.
- Deterministic construction and serialization.

### Rejected with a structured reason

- symbolic ALT values;
- breakends;
- spanning deletions;
- records with missing REF or ALT;
- variants on unknown contigs;
- genotypes and sample-level processing;
- complex normalization cases;
- variants that require reference sequence lookup to resolve ambiguity.

### API sketch

```python
@dataclass(frozen=True)
class ConversionResult:
    source_key: str
    allele: object | None
    identifier: str | None
    warnings: tuple[str, ...]
    error: str | None


def convert_vcf_row(
    chrom: str,
    pos: int,
    ref: str,
    alt: str,
    sequence_accessions: Mapping[str, str],
) -> ConversionResult:
    ...
```

The notebook should show the essential conversion logic, while reusable error handling and manifest operations live in `src/gks_tutorial/`.

---

## 10. Notebook authoring standard

Each notebook must follow the same structure:

1. **Why this matters**
2. **Learning objectives**
3. **Input data and provenance**
4. **Native representation**
5. **GKS representation or transformation**
6. **Validation**
7. **Practical query or operation**
8. **Exercises**
9. **Expected takeaways**
10. **Limitations and next steps**

### Notebook rules

- Use relative paths.
- Do not depend on execution order outside the notebook.
- Seed any randomness.
- Keep output small.
- Avoid hidden state.
- Do not require secrets.
- Fail clearly when data is missing.
- Include a Colab bootstrap cell that is a no-op locally.
- Pair every notebook with a Jupytext `.py` file.
- Clear transient outputs before commit, except intentionally retained small examples.
- Put longer reusable code in the package rather than hiding it in notebook cells.

---

## 11. Local user experience

A new user should be able to choose either standard Python or Docker.

### Standard Python

```bash
git clone <repository-url>
cd gks-hands-on-tutorial
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[tutorial]"
make verify-data
make lab
```

### Locked environment with uv

```bash
git clone <repository-url>
cd gks-hands-on-tutorial
uv sync --extra tutorial
uv run make verify-data
uv run jupyter lab
```

### Docker

```bash
git clone <repository-url>
cd gks-hands-on-tutorial
docker compose up --build
```

The Docker image must contain the Python tutorial environment and bundled fixtures only. It must not contain a full SeqRepo or database.

---

## 12. Colab compatibility

Colab should be a secondary launch path using the same notebooks.

### Implementation

- Add an “Open in Colab” badge to each core notebook.
- Put one bootstrap cell near the top:

```python
try:
    import google.colab  # type: ignore
except ImportError:
    IN_COLAB = False
else:
    IN_COLAB = True

if IN_COLAB:
    # Clone a tagged tutorial release, install pinned requirements,
    # and change into the repository directory.
    ...
```

### Colab constraints

- Open a tagged release rather than an arbitrary moving branch for published tutorials.
- Install from `requirements-colab.txt`.
- Use only bundled small data in the core path.
- Do not require Docker, mounted cloud drives, or credentials.
- Make notebook cells idempotent.
- Display a warning that the Colab filesystem is temporary.
- Test Colab requirements in CI using a normal Linux Python environment.

---

## 13. Continuous integration

Create two workflows.

### `test.yml`

Run on pull requests and pushes:

1. set up the tested Python versions;
2. install the locked tutorial and development environment;
3. run Ruff;
4. run unit tests;
5. validate all GKS fixtures;
6. execute all core notebooks;
7. execute advanced notebooks with optional sections skipped;
8. verify Jupytext pairs are synchronized;
9. build a source distribution and wheel.

### `data-integrity.yml`

Run on data-related changes and manually:

1. validate `data/manifest.yaml`;
2. verify checksums;
3. ensure every data file is declared;
4. ensure every declared file exists;
5. verify no file exceeds the agreed repository limit;
6. validate JSON and JSONL syntax;
7. load all GKS objects with pinned model versions;
8. compare expected identifiers;
9. report provenance changes in the job summary.

### Required checks

- `lint`
- `unit-tests`
- `gks-validation`
- `notebooks`
- `data-integrity`
- `package-build`

---

## 14. Integration with the GKS Starter Kit

Keep the narrative and executable layers connected but separately maintainable.

### In the tutorial repository

Create `docs/starter-kit-integration.md` describing:

- the related Starter Kit vignette slug;
- the tutorial notebook path;
- the GKS products used;
- the dataset and implementer;
- the tutorial maturity status;
- the tested package versions.

Optionally add machine-readable metadata:

```yaml
title: "ClinVar native data to GKS"
starter_kit_vignette: "clinvar-gks-knowledgebase-exchange"
notebook: "notebooks/01_clinvar_native_and_gks.ipynb"
products:
  - VRS
  - Cat-VRS
  - VA-Spec
status: prototype
```

### In the Starter Kit repository

For each associated vignette, add a small section:

```markdown
## Try it yourself

Run the companion hands-on tutorial locally or open it in Google Colab.
```

Do not duplicate notebook content in the vignette. The vignette explains the value and real-world story; the companion repository provides executable training.

---

## 15. Implementation phases

## Phase 1 — Repository bootstrap

- [ ] Create the repository with the proposed layout.
- [ ] Add license, citation, contribution, and conduct files.
- [ ] Create `pyproject.toml`, lock file, and Python version file.
- [ ] Add the package skeleton.
- [ ] Add Make targets: `setup`, `verify-data`, `test`, `notebooks`, `lab`, and `clean`.
- [ ] Add Ruff and pytest configuration.
- [ ] Add a minimal Dockerfile and Compose configuration.
- [ ] Add a smoke-test notebook.
- [ ] Establish CI before adding real tutorial content.

**Acceptance criteria**

- A clean clone installs successfully.
- `make test` passes.
- Jupyter Lab starts.
- Docker starts the same notebook environment.
- The repository contains no large reference archive or service dependency.

---

## Phase 2 — ClinVar fixture and end-to-end notebook

- [ ] Select a small set of ClinVar records with educationally useful variation and assertion content.
- [ ] Pin a ClinVar release.
- [ ] Locate or generate matching ClinVar-GKS records.
- [ ] Record source and transformation provenance.
- [ ] Add checksum verification.
- [ ] Implement JSON, JSONL, XML, and manifest loaders.
- [ ] Implement GKS model-validation helpers.
- [ ] Build `01_clinvar_native_and_gks.ipynb`.
- [ ] Add exercises and expected answers.
- [ ] Add unit tests for every bundled GKS object.
- [ ] Add one compact exported bundle as an expected output fixture.

**Acceptance criteria**

- Every native record has at least one clearly documented paired GKS object.
- The notebook runs without network access after installation.
- All GKS objects validate with pinned packages.
- A learner can traverse from a VA-Spec statement to its variation representation.
- Provenance and identifiers are visible in the notebook.

---

## Phase 3 — gnomAD VCF-to-VRS notebook

- [ ] Select a small GRCh38 region and pin the gnomAD release.
- [ ] Create a maintainer-only extraction script.
- [ ] Commit a small VCF excerpt and stripped tabular view.
- [ ] Add sequence accession mappings.
- [ ] Implement the supported conversion subset.
- [ ] Implement structured rejection for unsupported rows.
- [ ] Add expected identifiers.
- [ ] Build `02_vcf_to_vrs.ipynb`.
- [ ] Add tests for coordinate conversion and object generation.
- [ ] Explain the boundary between representation and full normalization.

**Acceptance criteria**

- Users do not download a whole chromosome file.
- Supported rows produce deterministic expected identifiers.
- Unsupported rows produce readable reasons.
- The notebook makes no claim of being a complete VCF normalizer.
- The core notebook requires no SeqRepo or UTA service.

---

## Phase 4 — Query and exchange notebook

- [ ] Define a compact tutorial bundle format.
- [ ] Load mixed GKS JSONL files.
- [ ] Add filtering and joins by identifiers.
- [ ] Demonstrate inline and by-reference forms.
- [ ] Add JSON and YAML serialization.
- [ ] Add round-trip tests.
- [ ] Build `03_query_and_exchange.ipynb`.
- [ ] Document how a future live implementer endpoint could replace fixture files.

**Acceptance criteria**

- A learner can answer practical questions using the GKS records.
- The exported bundle includes a manifest and checksums.
- Round-trip serialization preserves the modeled content.
- The notebook remains understandable without reading schema source files.

---

## Phase 5 — Colab and portability hardening

- [ ] Add Colab bootstrap cells and badges.
- [ ] Generate pinned Colab requirements.
- [ ] Test every core notebook using those requirements.
- [ ] Test a clean virtual environment.
- [ ] Test Docker.
- [ ] Ensure paths work on Linux and Colab.
- [ ] Add troubleshooting guidance.
- [ ] Add an environment diagnostics command.

**Acceptance criteria**

- The same notebook files run locally and in Colab.
- No core notebook requires secrets or external services.
- A failed optional service check produces a skip, not a tutorial failure.
- The repository remains small enough for routine cloning.

---

## Phase 6 — Advanced MaveDB experiment

- [ ] Select a small public MaveDB score set.
- [ ] Snapshot native metadata and score data.
- [ ] Document licenses and provenance.
- [ ] Map a limited set of variants to VRS.
- [ ] Draft an experimental VA-Spec mapping.
- [ ] List unresolved profile questions.
- [ ] Build the advanced notebook.
- [ ] Ask VA-Spec and MaveDB maintainers to review the mapping.
- [ ] Keep the module labeled experimental until the profile is agreed.

**Acceptance criteria**

- The notebook clearly separates normative models from experimental profiling.
- Native assay context and provenance are not silently discarded.
- Open modeling questions are captured as issues or a review document.
- The advanced notebook cannot break the core tutorial CI.

---

## Phase 7 — Starter Kit integration and release

- [ ] Create or identify corresponding Starter Kit vignettes.
- [ ] Add “Try it yourself” links.
- [ ] Add release tags.
- [ ] Use tagged URLs in Colab badges.
- [ ] Publish a release with the exact data manifest and dependency lock.
- [ ] Add a contributor guide for new tutorial modules.
- [ ] Add a tutorial-template notebook.
- [ ] Gather structured learner feedback.

**Acceptance criteria**

- Each published tutorial has a stable tagged URL.
- Each tutorial is linked to a narrative Starter Kit vignette.
- A contributor can add another dataset without reverse-engineering the repository.
- Published data and package versions are reproducible.

---

## 16. Prototype success criteria

The prototype is successful when all of the following are true:

- It runs on a CPU-only Linux environment.
- The core tutorial needs no database or local service.
- All core data is bundled and provenance-tracked.
- All core notebooks execute automatically in CI.
- The same notebooks work in local Jupyter and Colab.
- At least two real-world native formats are shown.
- At least one example spans VRS, Cat-VRS, and VA-Spec.
- At least one exercise demonstrates content-based variant matching.
- All GKS examples validate using pinned Python reference implementations.
- Unsupported transformation cases are explicit rather than silently approximated.
- The tutorial links to product Quick Starts instead of replacing them.
- The repository has a documented path for adding new implementer examples.

---

## 17. Risks and mitigations

| Risk | Mitigation |
|---|---|
| GKS package APIs change | Pin versions per tutorial release; test dependency updates in CI. |
| Tutorial becomes a second specification site | Keep explanations use-case-driven and link to authoritative product documentation. |
| Native and GKS records drift apart | Pair them in a manifest and validate source identifiers and checksums. |
| Full VRS normalization requires heavy infrastructure | Keep the core example pre-normalized and make data-proxy normalization optional. |
| Colab installs become unstable | Use tagged releases and a generated, pinned requirements file. |
| Notebook code becomes hard to test | Put reusable logic in `src/`, pair notebooks with Jupytext, and execute them in CI. |
| MaveDB profile is mistaken for a standard | Label it experimental and document unresolved profile decisions. |
| Bundled data grows too large | Enforce file-size and repository-size checks in CI. |
| Learners cannot see the connection between products | Use one ClinVar record that traverses VRS → Cat-VRS → VA-Spec. |
| Live endpoints are unavailable | Make bundled snapshots the default and live fetching an optional exercise. |

---

## 18. Decisions to record before implementation

Create an Architecture Decision Record for each:

1. Separate companion repository versus a subdirectory in `gks-starter-kit`.
2. `uv` plus pip fallback versus pip-only installation.
3. `nbmake` versus `pytest-notebook`.
4. Exact tutorial bundle format.
5. Exact ClinVar records and release.
6. Exact gnomAD region and release.
7. Whether identifier generation is taught directly or only verified.
8. Whether `linkml-runtime` is included in the core environment.
9. Whether rendered notebooks are published as static HTML.
10. Criteria for promoting the MaveDB module from experimental.

Recommended initial choices:

- separate companion repository;
- `uv` lock with documented pip fallback;
- `nbmake`;
- YAML manifest plus JSONL objects;
- bundled snapshots as the default;
- no LinkML runtime dependency in the first core release unless a notebook directly uses it;
- no full normalization service in the default environment.

---

## 19. Codex execution instructions

Copy this file into an empty repository as `IMPLEMENTATION_PLAN.md`, then give Codex the following instruction:

> Implement the GKS Hands-On Tutorial prototype described in `IMPLEMENTATION_PLAN.md`. Work phase by phase. Start with Phase 1 and Phase 2 only unless the repository already contains those deliverables. Keep the core environment lightweight and network-independent after dependency installation. Do not add SeqRepo, UTA, PostgreSQL, or a large reference archive to the default environment. Use small public fixtures with complete provenance. Pin dependencies, write tests before or alongside implementation, execute every core notebook in CI, and commit after each coherent task. Where exact upstream records or package APIs are uncertain, create a documented fixture-selection task rather than inventing data. Preserve a clear distinction between normative GKS objects and experimental profiles.

### First Codex milestone

The first milestone should deliver:

- repository scaffold;
- locked Python environment;
- data manifest schema and checksum verifier;
- one paired ClinVar native/GKS fixture;
- `00_start_here.ipynb`;
- `01_clinvar_native_and_gks.ipynb`;
- unit tests;
- notebook execution in CI;
- local and Docker launch instructions.

Do not begin the gnomAD or MaveDB modules until the first milestone passes all checks.

---

## 20. Source context

The plan was drafted from the following project context:

- GA4GH GKS Portal issue 79, “Genomic Knowledge Starter Kit”
- GA4GH GKS Portal issue 25, “VRS in a Box”
- GA4GH GKS Portal issue 28, “Consolidated GKS documentation”
- GA4GH GKS Portal issue 32, “Specifying MaveDB Data with VA-Spec”
- GA4GH GKS Portal issue 61, “Generate Quickstart content for VRS, Cat-VRS and VA-Spec”
- `ga4gh/gks-starter-kit`
- `clingen-data-model/clinvar-gks`
- `ga4gh/vrs-python`
- `ga4gh/cat-vrs-python`
- `ga4gh/va-spec-python`
