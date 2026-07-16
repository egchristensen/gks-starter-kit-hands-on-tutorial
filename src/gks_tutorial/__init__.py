"""Reusable support code for the GKS hands-on tutorial."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gks-hands-on-tutorial")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = ["__version__"]
