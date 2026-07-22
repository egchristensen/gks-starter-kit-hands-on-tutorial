#!/usr/bin/env python
"""Refresh the PubMed ESummary fixture used by the discovery tutorial."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_UID = "23220880"
DEFAULT_DOI = "10.1158/2159-8290.CD-12-0349"
DEFAULT_OUTPUT = Path("data/native/literature/PMID23220880-esummary.json")
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def fetch_summary(uid: str) -> tuple[bytes, str]:
    """Fetch one PubMed ESummary document and return its bytes and URL."""
    query = urllib.parse.urlencode(
        {
            "db": "pubmed",
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


def validate_summary(payload: bytes, uid: str, doi: str) -> None:
    """Reject an API response that is not the expected publication."""
    document = json.loads(payload)
    record = document["result"][uid]
    identifiers = {
        value["idtype"]: value["value"] for value in record.get("articleids", [])
    }
    if identifiers.get("doi") != doi:
        raise ValueError(f"expected DOI {doi!r}, got {identifiers.get('doi')!r}")
    if "HER2 mutations" not in record.get("title", ""):
        raise ValueError("unexpected PubMed article title")


def refresh(output: Path, uid: str, doi: str) -> str:
    """Download, validate, and atomically replace the native snapshot."""
    payload, url = fetch_summary(uid)
    validate_summary(payload, uid, doi)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".pubmed-fixture-", dir=output.parent
    ) as directory:
        staged = Path(directory) / output.name
        staged.write_bytes(payload)
        os.replace(staged, output)
    return url


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uid", default=DEFAULT_UID)
    parser.add_argument("--doi", default=DEFAULT_DOI)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    url = refresh(args.output, args.uid, args.doi)
    print(f"Wrote {args.output}")
    print(f"Source: {url}")


if __name__ == "__main__":
    main()
