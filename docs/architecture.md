# Architecture decisions

This is a separate executable companion repository. `uv.lock` is authoritative,
with a pip fallback for local contributors and generated pinned requirements for
Colab. Core notebooks are paired with percent-format Python files through
Jupytext and executed with nbmake.

Reusable loading, validation, traversal, and deterministic serialization logic
lives in `src/gks_tutorial/`; notebooks provide the teaching narrative and small
operations. Committed data is separated into native, GKS, and expected-output
paths and governed by the YAML manifest's executable provenance contract.

The Phase 2 compact profile bundle is explicitly tutorial-specific, not a GA4GH
standard. Full normalization services, LinkML runtime, SeqRepo, UTA, databases,
and large reference archives remain outside the core architecture. Later bundle
and conversion designs remain open until their corresponding phases begin.
