#!/usr/bin/env python
"""Generate or check the locked, platform-independent Colab requirements file."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


def generate(destination: Path) -> None:
    """Export the pinned Colab dependency graph from uv.lock."""
    subprocess.run(
        [
            "uv",
            "export",
            "--locked",
            "--extra",
            "colab",
            "--no-dev",
            "--no-emit-project",
            "--no-annotate",
            "--no-header",
            "--output-file",
            str(destination),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = Path("requirements-colab.txt")
    if not args.check:
        generate(target)
        return
    with tempfile.TemporaryDirectory() as directory:
        candidate = Path(directory) / target.name
        generate(candidate)
        if candidate.read_bytes() != target.read_bytes():
            raise SystemExit(
                "requirements-colab.txt is stale; run "
                "python scripts/generate_colab_requirements.py"
            )
    print("requirements-colab.txt matches uv.lock.")


if __name__ == "__main__":
    main()
