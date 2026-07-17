import json
from pathlib import Path

import pytest

from gks_tutorial.io import iter_jsonl, load_json, load_jsonl, load_xml, write_jsonl


def test_load_json(tmp_path: Path) -> None:
    path = tmp_path / "record.json"
    path.write_text(json.dumps({"kind": "format-test"}), encoding="utf-8")
    assert load_json(path) == {"kind": "format-test"}


def test_iter_jsonl_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text('{"row": 1}\n\n{"row": 2}\n', encoding="utf-8")
    assert list(iter_jsonl(path)) == [{"row": 1}, {"row": 2}]
    assert load_jsonl(path) == [{"row": 1}, {"row": 2}]


def test_write_jsonl_is_compact_deterministic_and_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    values = [{"z": 2, "a": 1}, {"row": 2}]

    write_jsonl(path, values)

    assert path.read_text(encoding="utf-8") == '{"a":1,"z":2}\n{"row":2}\n'
    assert load_jsonl(path) == values


def test_iter_jsonl_reports_line_number(tmp_path: Path) -> None:
    path = tmp_path / "broken.jsonl"
    path.write_text('{"row": 1}\nnot-json\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"broken\.jsonl:2: invalid JSONL"):
        list(iter_jsonl(path))


def test_load_xml(tmp_path: Path) -> None:
    path = tmp_path / "record.xml"
    path.write_text('<record accession="format-test"/>', encoding="utf-8")
    assert load_xml(path).attrib == {"accession": "format-test"}
