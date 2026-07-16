# Architecture decisions

Phase 1 adopts the plan's recommended initial choices: this is a separate companion
repository; `uv` is authoritative with a pip fallback; nbmake executes notebooks;
data uses a YAML manifest and (in later phases) JSONL objects; bundled snapshots are
the default; LinkML runtime and normalization services are excluded unless needed.

The exact bundle format and fixture-selection decisions remain deliberately open
until their implementing phases. Reusable behavior belongs in `src/gks_tutorial/`.
