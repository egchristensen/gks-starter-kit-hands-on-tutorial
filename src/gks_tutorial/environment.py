"""Lightweight environment diagnostics used by notebooks."""

from importlib.metadata import PackageNotFoundError, version
from platform import python_version

PACKAGES = ("ga4gh.vrs", "ga4gh.cat_vrs", "ga4gh.va_spec", "pydantic")


def diagnostics() -> dict[str, str]:
    """Return Python and installed GKS package versions without importing them."""
    result = {"python": python_version()}
    for package in PACKAGES:
        try:
            result[package] = version(package)
        except PackageNotFoundError:
            result[package] = "not installed"
    return result
