# ClinVar native snapshot

`VCV000012582.67-esummary.json` is the unmodified byte response from NCBI
ClinVar ESummary for UID `12582`, retrieved on 2026-07-16. It is source data,
not a GKS representation.

`VCV000044991.8-esummary.json` is the corresponding unmodified response for UID
`44991`, retrieved on 2026-07-17. Its supporting-submission list includes
`SCV005093950`, which is the versioned implementation-profile example used for
the cross-product traversal exercise.

Maintainers can refresh it with:

```bash
uv run python scripts/refresh_clinvar_native_fixture.py
```

Because ClinVar is a living database, the script refuses to replace this file
if the API has advanced beyond accession version `.67`. In that case, choose a
new versioned output path and expected `--accession`, review the result, update
`data/manifest.yaml`, and re-pair it with a compatible ClinVar-GKS snapshot.
Network access is never required to run against the committed snapshot.
