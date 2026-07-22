# Tutorial authoring

Use the standard sections specified in the implementation plan, relative paths,
small outputs, and no secrets or hidden state. Keep the existing Colab bootstrap
idempotent and a no-op locally. Pair `.ipynb` and percent-format `.py` files with
Jupytext; CI must verify every pair. Application logic belongs in the package and
requires unit tests.
