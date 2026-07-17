#!/usr/bin/env python
"""Execute core notebooks through pytest/nbmake."""

import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "pytest", "--nbmake", "notebooks"],
    check=True,
)
