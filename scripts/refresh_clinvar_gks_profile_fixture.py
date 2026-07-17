#!/usr/bin/env python
"""Refresh the exact versioned ClinVar-GKS SCV profile example."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.request
from pathlib import Path

COMMIT = "b3f485375172f789e26b8626854ef1ac4db2e130"
SOURCE_URL = (
    "https://raw.githubusercontent.com/clingen-data-model/clinvar-gks/"
    f"{COMMIT}/examples/scv/SCV005093950.2-S-ONCO.json"
)
DEFAULT_OUTPUT = Path("data/gks/clinvar/SCV005093950.2-S-ONCO.profile.json")


def fetch() -> bytes:
    request = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "gks-hands-on-tutorial/0.1"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def validate(payload: bytes) -> None:
    statement = json.loads(payload)
    if statement.get("id") != "clinvar.submission:SCV005093950.2":
        raise ValueError("unexpected ClinVar-GKS statement identifier")
    subject = statement["proposition"]["subjectVariant"]
    if subject.get("id") != "clinvar:44991":
        raise ValueError("statement does not describe ClinVar Variation ID 44991")
    if not any(member.get("type") == "Allele" for member in subject["members"]):
        raise ValueError("categorical variant has no inline VRS Allele")


def refresh(output: Path) -> None:
    payload = fetch()
    validate(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".clinvar-gks-profile-", dir=output.parent
    ) as directory:
        staged = Path(directory) / output.name
        staged.write_bytes(payload)
        os.replace(staged, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    refresh(args.output)
    print(f"Wrote {args.output}")
    print(f"Source: {SOURCE_URL}")


if __name__ == "__main__":
    main()
