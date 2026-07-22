# Limitations

The repository includes the Phase 1 environment smoke test and a substantial
Phase 2 ClinVar tutorial, but Phase 2 is not acceptance-complete. The compact
native snapshots and GKS examples share documented identifiers; they are not
proven to come from the same pinned ClinVar release.

The bundled ClinVar-GKS statement is an exact implementation-profile example.
Its inline Cat-VRS and VRS objects are normative, while the enclosing statement
does not validate as the currently pinned normative VA-Spec model. The notebooks
preserve and demonstrate that distinction.

The core path intentionally includes no full ClinVar release, general-purpose
normalizer, SeqRepo archive, UTA instance, PostgreSQL database, or required
network service. It currently teaches the ClinVar example only; the planned VCF,
query/exchange, and advanced modules have not been implemented.
