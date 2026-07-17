# ClinVar-GKS candidate VRS objects

`VCV000012582.67-vrs.jsonl` contains three unmodified JSON object values
selectively extracted from public ClinVar-GKS Parquet key/value sections: a VRS
`SequenceReference`, its linked `SequenceLocation`, and the linked VRS `Allele`
for ClinVar Variation ID `12582`.

These normative VRS objects validate with the pinned `ga4gh.vrs` package and
are kept separate from the native ClinVar response.

The public Parquet files are unversioned and were last modified on 2026-07-07.
These objects are therefore a candidate link to the native record, not proof of
an exact release-matched transformation. No Cat-VRS or VA-Spec object is bundled
yet: their current public Parquet sections are flattened and cannot reproduce
authoritative objects without reconstruction.

Maintainers can rerun the extraction without adding DuckDB to the tutorial:

```bash
uv run --with duckdb python scripts/refresh_clinvar_gks_vrs_fixture.py
```

## Versioned implementation-profile statement

`SCV005093950.2-S-ONCO.profile.json` is an exact file from a pinned
ClinVar-GKS repository commit. Its inline `CategoricalVariant` and `Allele` are
normative and validate with the pinned Cat-VRS and VRS packages. The outer
ClinVar statement is an implementation profile: its proposition does not
validate as the current normative VA-Spec `VariantOncogenicityProposition`.
The tutorial demonstrates and tests that distinction rather than modifying the
upstream record.
