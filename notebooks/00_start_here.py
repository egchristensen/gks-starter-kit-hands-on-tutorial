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
# # Start here
#
# [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egchristensen/gks-starter-kit-hands-on-tutorial/blob/main/notebooks/00_start_here.ipynb)
#
# ## Why this matters
#
# This smoke notebook confirms that the lightweight tutorial environment and data
# integrity foundation work before opening the real Phase 2 example.
#
# ## Learning objectives
#
# - inspect installed GKS package versions;
# - load the tutorial data manifest; and
# - verify all declared fixture checksums.

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
            [
                "git",
                "-C",
                str(repository_root),
                "pull",
                "--ff-only",
                "origin",
                "main",
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
    # Editable installs add a .pth file that is normally read at interpreter
    # startup. Colab's current kernel is already running, so make the package
    # importable immediately without requiring a runtime restart.
    sys.path.insert(0, str(repository_root / "src"))
    importlib.invalidate_caches()
    for module_name in tuple(sys.modules):
        if module_name == "gks_tutorial" or module_name.startswith("gks_tutorial."):
            del sys.modules[module_name]
else:
    repository_root = (
        Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
    )

from gks_tutorial.environment import diagnostics
from gks_tutorial.manifests import load_manifest, verify_manifest


def pretty_print(value: object) -> None:
    """Render structured cell output as stable, indented JSON."""
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))

# %% [markdown]
# ## Input data and provenance
#
# The manifest now includes Phase 2 fixtures. This notebook verifies them without
# making scientific claims; notebook 01 explains their provenance and limitations.

# %%
manifest_path = repository_root / "data" / "manifest.yaml"
installed = diagnostics()
manifest = load_manifest(manifest_path)
issues = verify_manifest(manifest_path, repository_root=repository_root)
summary = {"installed": installed, "manifest": manifest, "issues": issues}
pretty_print(summary)

# %%
assert manifest["manifest_version"] == 1
assert not issues

# %% [markdown]
# ## GKS layers
#
# - **VRS** represents variation precisely.
# - **Cat-VRS** groups variations into useful categorical concepts.
# - **VA-Spec** represents statements and evidence about variation.
#
# Notebook 01 begins with native ClinVar and VRS, then traverses an exact profile
# example through inline Cat-VRS and VRS objects. A normative VA-Spec traversal
# still requires an authoritative release-matched export.
# The literature discovery vignette then shows how the same identities improve
# retrieval when a paper and a knowledgebase use different variant language.
#
# ## Validation and practical operation
#
# The assertions above validate the repository manifest and fixture integrity.
#
# ## Exercises
#
# Identify which installed package corresponds to each GKS layer.
#
# ## Expected takeaways
#
# The tutorial can inspect its environment and verify bundled data offline.
#
# ## Limitations and next steps
#
# This remains an environment smoke test. Continue to notebook 01 for the
# biological example and its explicit limitations.
