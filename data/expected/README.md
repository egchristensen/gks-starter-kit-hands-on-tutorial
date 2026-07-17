# Expected tutorial outputs

`clinvar-profile-bundle.json` is the deterministic expected output for the
Phase 2 profile traversal. It contains source identifiers and the exact upstream
ClinVar-GKS statement, whose normative Cat-VRS and VRS objects are inline.

The container is tutorial-specific and is not presented as a GA4GH standard.
Rebuild it with:

```bash
uv run python scripts/build_expected_clinvar_bundle.py
```
