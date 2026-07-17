#!/usr/bin/env python
"""Refresh the small ClinVar ESummary fixture used by the tutorial.

This maintainer utility requires network access. It downloads into a temporary
directory, verifies the requested accession, and only then replaces the
committed snapshot. The tutorial itself never calls this script.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_UID = "12582"
DEFAULT_ACCESSION = "VCV000012582.67"
DEFAULT_OUTPUT = Path("data/native/clinvar/VCV000012582.67-esummary.json")
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def fetch_summary(uid: str) -> tuple[bytes, str]:
    """Fetch one ClinVar ESummary document and return its bytes and URL."""
    query = urllib.parse.urlencode(
        {
            "db": "clinvar",
            "id": uid,
            "retmode": "json",
            "tool": "gks_hands_on_tutorial",
        }
    )
    url = f"{BASE_URL}?{query}"
    request = urllib.request.Request(
        url, headers={"User-Agent": "gks-hands-on-tutorial/0.1"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(), url


def validate_summary(payload: bytes, uid: str, accession: str) -> None:
    """Reject an API response that is not the expected ClinVar record."""
    document = json.loads(payload)
    record = document["result"][uid]
    if record["accession_version"] != accession:
        raise ValueError(
            f"expected accession {accession!r}, "
            f"got {record['accession_version']!r}"
        )


def refresh(output: Path, uid: str, accession: str) -> str:
    """Download, validate, and atomically replace the native snapshot."""
    payload, url = fetch_summary(uid)
    validate_summary(payload, uid, accession)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".clinvar-fixture-", dir=output.parent
    ) as directory:
        staged = Path(directory) / output.name
        staged.write_bytes(payload)
        os.replace(staged, output)
    return url


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uid", default=DEFAULT_UID)
    parser.add_argument("--accession", default=DEFAULT_ACCESSION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    url = refresh(args.output, args.uid, args.accession)
    print(f"Wrote {args.output}")
    print(f"Source: {url}")


if __name__ == "__main__":
    main()
