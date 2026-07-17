"""Small, explicit loaders for committed tutorial data files."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


def load_json(path: Path) -> Any:
    """Load one UTF-8 JSON document."""
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def iter_jsonl(path: Path) -> Iterator[Any]:
    """Yield non-empty UTF-8 JSONL records with line-aware errors."""
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"{path}:{line_number}: invalid JSONL: {error.msg}"
                ) from error


def load_jsonl(path: Path) -> list[Any]:
    """Load all records from a small tutorial JSONL file."""
    return list(iter_jsonl(path))


def write_jsonl(path: Path, values: list[Any]) -> None:
    """Write deterministic, compact JSONL for a small tutorial collection."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for value in values:
            stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")))
            stream.write("\n")


def load_xml(path: Path) -> ElementTree.Element:
    """Parse an XML document and return its root element."""
    return ElementTree.parse(path).getroot()
