#!/usr/bin/env python
"""Execute core notebooks through pytest/nbmake."""

import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "pytest", "--nbmake", "notebooks/00_start_here.ipynb"],
    check=True,
)
