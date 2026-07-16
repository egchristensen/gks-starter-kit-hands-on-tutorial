# GKS Hands-On Tutorial

This repository is the executable companion prototype for learning GA4GH VRS,
Cat-VRS, and VA-Spec through small, provenance-tracked examples. Phase 1 contains
the repository and validation scaffold only; real ClinVar content belongs to Phase 2.

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

## Docker

```bash
docker compose up --build
```

Open the URL printed by Jupyter. The image contains only the tutorial runtime and
committed small fixtures—no SeqRepo, UTA, PostgreSQL, or reference archive.

## Project status

The implementation follows `gks-hands-on-tutorial-implementation-plan.md` phase by
phase. The current scaffold intentionally includes no biological records. See
`docs/data-provenance.md` before adding data.
