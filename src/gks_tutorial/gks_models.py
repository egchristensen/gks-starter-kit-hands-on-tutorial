"""Validation dispatch for normative objects in the pinned GKS packages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ga4gh.cat_vrs import models as cat_vrs_models
from ga4gh.va_spec.base import core as va_spec_models
from ga4gh.vrs import models as vrs_models
from pydantic import BaseModel


class UnsupportedGksTypeError(ValueError):
    """Raised when no pinned normative model corresponds to an object type."""


def _model_map(module: object, names: tuple[str, ...]) -> dict[str, type[BaseModel]]:
    return {name: getattr(module, name) for name in names}


VRS_MODELS = _model_map(
    vrs_models,
    (
        "SequenceReference",
        "SequenceLocation",
        "Allele",
        "CisPhasedBlock",
        "CopyNumberCount",
        "CopyNumberChange",
    ),
)
CAT_VRS_MODELS = _model_map(
    cat_vrs_models,
    ("CategoricalVariant", "DefiningAlleleConstraint", "DefiningLocationConstraint"),
)
VA_SPEC_MODELS = _model_map(
    va_spec_models,
    (
        "Statement",
        "EvidenceLine",
        "VariantPathogenicityProposition",
        "VariantOncogenicityProposition",
        "VariantDiagnosticProposition",
        "VariantPrognosticProposition",
        "VariantTherapeuticResponseProposition",
        "ExperimentalVariantFunctionalImpactProposition",
    ),
)


def validate_gks_object(
    value: Mapping[str, Any], *, product: str
) -> BaseModel:
    """Validate a normative object using an explicitly selected GKS product."""
    registries = {
        "vrs": VRS_MODELS,
        "cat-vrs": CAT_VRS_MODELS,
        "va-spec": VA_SPEC_MODELS,
    }
    try:
        registry = registries[product]
    except KeyError as error:
        raise ValueError(f"unknown GKS product: {product}") from error
    object_type = value.get("type")
    try:
        model = registry[str(object_type)]
    except KeyError as error:
        raise UnsupportedGksTypeError(
            f"unsupported {product} object type: {object_type!r}"
        ) from error
    return model.model_validate(value)
