.PHONY: setup verify-data test notebooks lab clean lint build colab-requirements

setup:
	python -m pip install --upgrade pip
	python -m pip install -e '.[tutorial,dev]'

verify-data:
	python scripts/verify_data.py

lint:
	ruff check .

test:
	pytest

notebooks:
	python scripts/execute_notebooks.py
	jupytext --test --to py:percent notebooks/00_start_here.ipynb

lab:
	jupyter lab --ip=0.0.0.0 --port=8888

build:
	python -m build

colab-requirements:
	python scripts/generate_colab_requirements.py --check

clean:
	rm -rf build dist .pytest_cache .ruff_cache src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
