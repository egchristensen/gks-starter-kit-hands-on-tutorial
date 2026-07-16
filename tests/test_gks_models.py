import pytest

from gks_tutorial.gks_models import UnsupportedGksTypeError, validate_gks_object


def test_unknown_product_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown GKS product"):
        validate_gks_object({"type": "Example"}, product="unknown")


def test_profile_object_is_not_silently_treated_as_normative() -> None:
    with pytest.raises(UnsupportedGksTypeError, match="ClinvarScvStatement"):
        validate_gks_object({"type": "ClinvarScvStatement"}, product="va-spec")
