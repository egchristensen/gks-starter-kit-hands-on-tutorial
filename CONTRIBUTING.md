# Contributing

Use Python 3.11 and install `.[tutorial,dev]`. Keep changes within the current
implementation phase and run `make lint verify-data test notebooks build`.

Do not invent records or identifiers. New data must be small, public, unchanged in
`data/native/`, separated from transformed data in `data/gks/`, and fully declared
in `data/manifest.yaml`. Include the required provenance fields documented in
`data/README.md`, and annotate standalone normative object files with
`gks_product`. Pair each notebook with Jupytext and put reusable logic in
`src/gks_tutorial/`.
