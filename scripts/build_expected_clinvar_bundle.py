#!/usr/bin/env python
"""Rebuild the deterministic expected Phase 2 tutorial bundle."""

from pathlib import Path

from gks_tutorial.bundles import build_clinvar_profile_bundle
from gks_tutorial.clinvar import esummary_record
from gks_tutorial.io import load_json, write_json

NATIVE = Path("data/native/clinvar/VCV000044991.8-esummary.json")
PROFILE = Path("data/gks/clinvar/SCV005093950.2-S-ONCO.profile.json")
OUTPUT = Path("data/expected/clinvar-profile-bundle.json")


def main() -> None:
    native = esummary_record(load_json(NATIVE), "44991")
    statement = load_json(PROFILE)
    write_json(OUTPUT, build_clinvar_profile_bundle(native, statement))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
