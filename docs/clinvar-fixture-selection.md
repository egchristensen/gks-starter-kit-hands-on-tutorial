# ClinVar fixture-selection research

**Status:** blocked pending an exact, release-matched native/GKS export

**Research date:** 2026-07-16

This task records the evidence required before committing a Phase 2 biological
fixture. It intentionally does not treat a plausible record as a verified pairing.

## Candidate

`VCV000012582.67` (ClinVar Variation ID `12582`) is an educationally useful
candidate:

- KRAS `NM_004985.5:c.35G>A` (`p.Gly12Asp`);
- a simple GRCh38 SNV with canonical SPDI `NC_000012.12:25245349:C:T`;
- ClinVar-GKS categorical variant `clinvar:12582`;
- defining VRS allele `ga4gh:VA.LDaqvF3c3y1IG8wF4mORiRfB--9Jjfzp`;
- germline pathogenicity, somatic clinical-impact, and oncogenicity statements;
- multiple SCV records, including `SCV000191996.5`; and
- a direct statement → proposition → categorical variant → VRS allele traversal.

These identifiers were observed in the public sources below; they are recorded as
research evidence, not yet copied into `data/` as tutorial fixtures.

## Sources inspected

### NCBI ClinVar

- Version-specific E-utilities URL:
  <https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=clinvar&rettype=vcv&id=VCV000012582.67>
- Retrieved response size: 342,146 bytes.
- The response reported `VariationID="12582"`, `Version="67"`, and
  `DateLastUpdated="2026-07-15"`.
- ClinVar documents that monthly comprehensive releases are archived, while weekly
  releases are not. It also documents that some staff updates do not increment a VCV
  version. Therefore, a version-specific E-utilities response is not sufficient by
  itself to prove identity with a particular monthly transformation input.
- Download and release documentation:
  <https://www.ncbi.nlm.nih.gov/clinvar/docs/downloads/> and
  <https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/>.

### ClinVar-GKS

- Repository: <https://github.com/clingen-data-model/clinvar-gks>
- Inspected commit: `b3f485375172f789e26b8626854ef1ac4db2e130`.
- Release index updated `2026-07-07T23:04:00Z`:
  <https://pub-9c5470edadb8496fb0abbf396291660b.r2.dev/index.json>.
- Monthly `2026-06` JSON bundle size: 4,469,818,847 bytes.
- Bundle ETag: `bd6e0d969c6885a07ce645ea1dccde8f-533`.
- Selective queries against the public Parquet exports confirmed the candidate IDs.
  The `sequenceReference`, `location`, and `allele` sections currently expose
  authoritative JSON object strings in key/value rows. The Cat-VRS and VA-Spec
  sections remain flattened, despite newer upstream documentation describing a
  common `data` column, and cannot provide exact objects.

The repository's checked-in examples are unsuitable as fixtures because some
contain JSON comments, placeholder conditions such as `"some condition"`, and
incomplete `TBD` structures.

## Prototype API snapshot

To make progress without downloading a complete release, the repository now
bundles the exact JSON response returned by the public NCBI ClinVar ESummary
API for UID `12582` on 2026-07-16. The response identifies itself as
`VCV000012582.67`. This is an authoritative, compact native-source snapshot,
but it is **not** a release-pinned monthly archive.

The snapshot does not resolve the blocker below: a ClinVar-GKS analytical
export updated on a nearby date is not automatically proven to have been
derived from this exact NCBI response. Until an exact pairing is verified, the
native snapshot may be inspected independently but must not be presented as a
byte-for-byte matched ClinVar-GKS transformation.

## Versioned profile fallback

The pinned ClinVar-GKS commit also contains a complete JSON example for
`SCV005093950.2`, describing ClinVar Variation ID `44991`. The live NCBI summary
for `VCV000044991.8` lists `SCV005093950` among its supporting submissions. The
example provides an exact implementation-profile statement with inline normative
Cat-VRS and VRS objects, enabling offline cross-product traversal.

This fallback is identifier- and accession-version-paired, but not
release-paired. Its enclosing oncogenicity proposition uses the ClinVar profile's
`objectCondition` representation and does not validate against the currently
pinned normative VA-Spec model, which requires `objectTumorType`. The tutorial
preserves that upstream object unchanged and tests the incompatibility explicitly.

## Required resolution

Obtain one of the following from the ClinVar-GKS maintainers or a documented
release-extraction process:

1. a small authoritative export for a named ClinVar release containing the native
   VCV record and every linked GKS object; or
2. a documented, range-efficient extraction procedure that reproduces exact JSON
   objects from an archived release without downloading the multi-gigabyte bundle.

The export must identify:

- the ClinVar release date and native archive path;
- the ClinVar-GKS transformer commit and release artifact;
- exact VCV and SCV accession versions;
- the VRS, Cat-VRS, and VA-Spec versions/profile schemas used;
- every linked object required for traversal; and
- SHA-256 checksums for both native and transformed files.

## Fixture acceptance checklist

- [x] A compact, authoritative native API snapshot is bundled without modifying
      its bytes and can be inspected offline.
- [x] The live-API limitation, retrieval date, source URL, and checksum are
      recorded explicitly.
- [x] Exact candidate VRS object values are selectively extracted, stored under
      `data/gks/`, and validated without adding DuckDB to runtime dependencies.
- [x] An exact versioned ClinVar-GKS profile example supports offline statement →
      Cat-VRS → VRS traversal, with normative nested objects validated separately.
- [ ] Native XML comes from the same pinned ClinVar release used by the transformer.
- [x] GKS JSON is copied from an authoritative output, not reconstructed from a
      flattened analytical table.
- [ ] Every source identifier is present in both the native/GKS pairing metadata.
- [ ] Normative VRS, Cat-VRS, and VA-Spec objects validate with pinned packages.
- [ ] ClinVar-specific profile extensions are labeled and validated separately.
- [x] Statement traversal resolves without network access.
- [x] Native bytes remain unchanged under `data/native/clinvar/`.
- [x] GKS bytes are stored separately under `data/gks/clinvar/`.
- [ ] The manifest records URLs, releases, retrieval time, licenses, transformer
      commit, model versions, and checksums.
