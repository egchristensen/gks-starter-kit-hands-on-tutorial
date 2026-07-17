from pathlib import Path

import pytest

from gks_tutorial.clinvar import (
    classification_summary,
    esummary_record,
)
from gks_tutorial.io import load_json

FIXTURE = Path("data/native/clinvar/VCV000012582.67-esummary.json")


def test_bundled_clinvar_snapshot_identity_and_classifications() -> None:
    record = esummary_record(load_json(FIXTURE), "12582")

    assert record["accession"] == "VCV000012582"
    assert record["accession_version"] == "VCV000012582.67"
    assert classification_summary(record) == {
        "germline": "Pathogenic/Likely pathogenic",
        "clinical_impact": "Tier I - Strong",
        "oncogenicity": "Oncogenic",
    }


def test_esummary_record_rejects_missing_uid() -> None:
    with pytest.raises(KeyError, match="999"):
        esummary_record({"result": {}}, "999")
