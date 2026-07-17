#!/usr/bin/env python
"""Extract exact VRS JSON values from public ClinVar-GKS Parquet files.

This maintainer utility intentionally extracts only key/value sections. It
refuses flattened tables because reconstructing those rows would not preserve
the authoritative upstream GKS object. DuckDB is not a runtime dependency.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

try:
    import duckdb
except ImportError as error:  # pragma: no cover - maintainer-only path
    raise SystemExit(
        "Run with: uv run --with duckdb python "
        "scripts/refresh_clinvar_gks_vrs_fixture.py"
    ) from error

BASE_URL = "https://pub-9c5470edadb8496fb0abbf396291660b.r2.dev/datasets/parquet"
DEFAULT_OUTPUT = Path("data/gks/clinvar/VCV000012582.67-vrs.jsonl")
OBJECTS = (
    ("sequenceReference", "SQ.6wlJpONE3oNb4D69ULmEXhqyDZ4vwNfl"),
    ("location", "ga4gh:SL.qaHcVvdl8j0lpLRt49hE-bFI81128Mk9"),
    ("allele", "ga4gh:VA.LDaqvF3c3y1IG8wF4mORiRfB--9Jjfzp"),
)


def extract_value(section: str, key: str) -> str:
    """Return a JSON value only when the section is key/value shaped."""
    url = f"{BASE_URL}/{section}.parquet"
    columns = {
        row[0]
        for row in duckdb.sql(
            f"DESCRIBE SELECT * FROM read_parquet('{url}')"
        ).fetchall()
    }
    if not {"key", "value"}.issubset(columns):
        raise ValueError(f"{section}.parquet has no key/value representation")
    row = duckdb.sql(
        f"SELECT value FROM read_parquet('{url}') WHERE key = ?", params=[key]
    ).fetchone()
    if row is None:
        raise KeyError(f"{key!r} not found in {section}.parquet")
    value = row[0]
    document = json.loads(value)
    observed = (
        document.get("refgetAccession")
        if document.get("type") == "SequenceReference"
        else document.get("id")
    )
    if observed != key:
        raise ValueError(f"expected {key!r}, got {observed!r}")
    return value


def refresh(output: Path) -> None:
    """Stage all objects, validate their links, and atomically replace output."""
    values = [extract_value(section, key) for section, key in OBJECTS]
    _, location, allele = map(json.loads, values)
    if location["sequenceReference"].rsplit("/", 1)[-1] != OBJECTS[0][1]:
        raise ValueError("location does not reference the selected sequence")
    if allele["location"].rsplit("/", 1)[-1] != OBJECTS[1][1]:
        raise ValueError("allele does not reference the selected location")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".clinvar-gks-fixture-", dir=output.parent
    ) as directory:
        staged = Path(directory) / output.name
        staged.write_text("\n".join(values) + "\n", encoding="utf-8")
        os.replace(staged, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    refresh(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
