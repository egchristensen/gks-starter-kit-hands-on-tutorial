# GKS Hands-On Tutorial

This repository is the executable companion prototype for learning GA4GH VRS,
Cat-VRS, and VA-Spec through small, provenance-tracked examples. Phase 1 and its
Colab smoke test are complete. Phase 2 currently includes a compact native
ClinVar API snapshot and candidate linked VRS objects; exact release-matched
Cat-VRS and VA-Spec records remain a documented upstream-data prerequisite.

## Run in Google Colab

[![Open Start Here in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egchristensen/gks-starter-kit-hands-on-tutorial/blob/main/notebooks/00_start_here.ipynb)

[![Open ClinVar and GKS in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egchristensen/gks-starter-kit-hands-on-tutorial/blob/main/notebooks/01_clinvar_native_and_gks.ipynb)

This is the primary zero-local-setup path. Click the badge, select **Runtime → Run
all**, and accept Colab's standard warning for a notebook loaded from GitHub. The
first cell automatically:

1. clones this public repository into the temporary Colab runtime;
2. installs the fully pinned packages in `requirements-colab.txt`; and
3. installs the tutorial package from that checkout.

Nothing is installed on the learner's computer. Colab does download packages into
its disposable cloud runtime, so the first run requires internet access and can take
a few minutes. Runtime files and notebook changes disappear when Colab recycles the
session; download any wanted output before disconnecting.

During prototype development the badge follows `main`. Published tutorial releases
will use a release tag so that notebooks, fixtures, and dependencies cannot drift.

## Local setup

Python 3.11 is the tested baseline. With `uv`:

```bash
uv sync --extra tutorial --extra dev
uv run make verify-data
uv run make test
uv run make lab
```

Pip fallback:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[tutorial,dev]'
make verify-data test
make lab
```

The core tutorial is designed to run offline after dependencies are installed.
Local setup is intended primarily for contributors and maintainers.

## Docker

```bash
docker compose up --build
```

Open the URL printed by Jupyter. The image contains only the tutorial runtime and
committed small fixtures—no SeqRepo, UTA, PostgreSQL, or reference archive.

## Project status

The implementation follows `gks-hands-on-tutorial-implementation-plan.md` phase by
phase. Phase 2 is active and is not yet acceptance-complete. See
`docs/data-provenance.md` and `docs/clinvar-fixture-selection.md` for the exact
status and limitations of the bundled records.
