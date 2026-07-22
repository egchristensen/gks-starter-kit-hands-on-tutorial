"""Manifest loading and checksum verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


@dataclass(frozen=True)
class VerificationIssue:
    path: str
    message: str


_SHA256 = re.compile(r"[0-9a-f]{64}")
_SOURCE_URL_FIELDS = ("retrieval_url", "source_url", "source_base_url")
_LICENSE_FIELDS = ("license", "terms")
_IDENTIFIER_FIELDS = (
    "source_record_uid",
    "source_accession",
    "source_variation_id",
)


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _metadata_issues(
    name: str, dataset: Mapping[str, Any]
) -> list[VerificationIssue]:
    """Validate the repository's minimum per-dataset provenance contract."""
    location = f"datasets.{name}"
    issues: list[VerificationIssue] = []
    for field in ("source", "retrieval_date", "release_policy", "selection_method"):
        if not _nonempty_string(dataset.get(field)):
            issues.append(VerificationIssue(location, f"{field} is required"))

    retrieval_date = dataset.get("retrieval_date")
    if _nonempty_string(retrieval_date):
        try:
            parsed_date = date.fromisoformat(retrieval_date)
        except ValueError:
            parsed_date = None
        if parsed_date is None or parsed_date.isoformat() != retrieval_date:
            issues.append(
                VerificationIssue(location, "retrieval_date must use YYYY-MM-DD")
            )

    if not any(_nonempty_string(dataset.get(field)) for field in _SOURCE_URL_FIELDS):
        issues.append(VerificationIssue(location, "a source URL is required"))
    if not any(_nonempty_string(dataset.get(field)) for field in _LICENSE_FIELDS):
        issues.append(VerificationIssue(location, "license or terms is required"))
    if not any(_nonempty_string(dataset.get(field)) for field in _IDENTIFIER_FIELDS):
        issues.append(VerificationIssue(location, "a source identifier is required"))

    files = dataset.get("files")
    if not isinstance(files, list) or not files:
        issues.append(VerificationIssue(location, "files must be a non-empty list"))
        return issues

    paths = [item.get("path") for item in files if isinstance(item, Mapping)]
    has_gks_output = any(
        isinstance(path, str)
        and (path.startswith("data/gks/") or path.startswith("data/expected/"))
        for path in paths
    )
    if has_gks_output:
        transformer = dataset.get("transformer")
        if not isinstance(transformer, Mapping):
            issues.append(
                VerificationIssue(location, "GKS output requires transformer metadata")
            )
        else:
            for field in ("name", "repository"):
                if not _nonempty_string(transformer.get(field)):
                    issues.append(
                        VerificationIssue(
                            location, f"transformer.{field} is required"
                        )
                    )
            if not any(
                _nonempty_string(transformer.get(field))
                for field in ("commit", "inspected_commit")
            ):
                issues.append(
                    VerificationIssue(location, "transformer commit is required")
                )
        versions = dataset.get("gks_versions")
        if not isinstance(versions, Mapping) or not versions or not all(
            _nonempty_string(value) for value in versions.values()
        ):
            issues.append(
                VerificationIssue(location, "GKS output requires pinned gks_versions")
            )
    return issues


def _validate_gks_values(
    values: list[tuple[str, Any]], *, product: str, path: str
) -> list[VerificationIssue]:
    """Validate manifest-annotated normative objects with the pinned models."""
    from gks_tutorial.gks_models import validate_gks_object

    issues: list[VerificationIssue] = []
    for label, value in values:
        if not isinstance(value, Mapping):
            issues.append(
                VerificationIssue(path, f"{label}: GKS object must be a mapping")
            )
            continue
        try:
            validate_gks_object(value, product=product)
        except (TypeError, ValueError) as error:
            message = " ".join(str(error).split())
            issues.append(
                VerificationIssue(path, f"{label}: invalid {product} object: {message}")
            )
    return issues


def load_manifest(path: Path) -> dict[str, Any]:
    """Load a data manifest and enforce its top-level contract."""
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict) or content.get("manifest_version") != 1:
        raise ValueError("manifest_version must be 1")
    if not isinstance(content.get("datasets"), dict):
        raise ValueError("datasets must be a mapping")
    return content


def sha256(path: Path) -> str:
    """Calculate a file SHA-256 digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest(path: Path, *, repository_root: Path) -> list[VerificationIssue]:
    """Verify provenance, declarations, checksums, syntax, and GKS annotations."""
    manifest = load_manifest(path)
    issues: list[VerificationIssue] = []
    declared: set[str] = set()
    repository_root = repository_root.resolve()
    data_root = (repository_root / "data").resolve()
    for name, dataset in manifest["datasets"].items():
        if not isinstance(dataset, Mapping):
            issues.append(
                VerificationIssue(f"datasets.{name}", "dataset must be a mapping")
            )
            continue
        issues.extend(_metadata_issues(str(name), dataset))
        files = dataset.get("files")
        if not isinstance(files, list):
            continue
        for index, item in enumerate(files):
            entry = f"datasets.{name}.files[{index}]"
            if not isinstance(item, Mapping):
                issues.append(VerificationIssue(entry, "file entry must be a mapping"))
                continue
            relative = item.get("path")
            if not _nonempty_string(relative):
                issues.append(VerificationIssue(entry, "path is required"))
                continue
            pure_path = PurePosixPath(relative)
            if (
                pure_path.is_absolute()
                or ".." in pure_path.parts
                or not pure_path.parts
                or pure_path.parts[0] != "data"
                or pure_path.as_posix() != relative
            ):
                issues.append(
                    VerificationIssue(relative, "path must be normalized under data/")
                )
                continue
            if relative in declared:
                issues.append(
                    VerificationIssue(relative, "file is declared more than once")
                )
                continue
            declared.add(relative)
            candidate = (repository_root / relative).resolve()
            if not candidate.is_relative_to(data_root):
                issues.append(
                    VerificationIssue(relative, "path resolves outside data/")
                )
                continue
            if not candidate.is_file():
                issues.append(VerificationIssue(relative, "declared file is missing"))
                continue
            expected_checksum = item.get("sha256")
            if not isinstance(expected_checksum, str) or not _SHA256.fullmatch(
                expected_checksum
            ):
                issues.append(
                    VerificationIssue(
                        relative, "sha256 must be 64 lowercase hex digits"
                    )
                )
            elif sha256(candidate) != expected_checksum:
                issues.append(VerificationIssue(relative, "SHA-256 checksum mismatch"))
            if candidate.stat().st_size > 5 * 1024 * 1024:
                issues.append(VerificationIssue(relative, "file exceeds 5 MiB limit"))
            values: list[tuple[str, Any]] = []
            if candidate.suffix == ".json":
                try:
                    values.append(
                        (
                            "document",
                            json.loads(candidate.read_text(encoding="utf-8")),
                        )
                    )
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    issues.append(VerificationIssue(relative, f"invalid JSON: {error}"))
            elif candidate.suffix == ".jsonl":
                try:
                    lines = candidate.read_text(encoding="utf-8").splitlines()
                except UnicodeDecodeError as error:
                    issues.append(
                        VerificationIssue(relative, f"invalid UTF-8 JSONL: {error}")
                    )
                    lines = []
                for number, line in enumerate(lines, start=1):
                    if not line.strip():
                        continue
                    try:
                        values.append((f"line {number}", json.loads(line)))
                    except json.JSONDecodeError as error:
                        issues.append(
                            VerificationIssue(
                                relative, f"invalid JSONL line {number}: {error}"
                            )
                        )
            product = item.get("gks_product")
            if product is not None:
                if product not in {"vrs", "cat-vrs", "va-spec"}:
                    issues.append(
                        VerificationIssue(
                            relative, f"unknown gks_product: {product!r}"
                        )
                    )
                elif not values:
                    issues.append(
                        VerificationIssue(relative, "no valid GKS objects found")
                    )
                else:
                    issues.extend(
                        _validate_gks_values(values, product=product, path=relative)
                    )

    ignored_names = {".gitkeep", "README.md", "manifest.yaml"}
    for candidate in (repository_root / "data").rglob("*"):
        if candidate.is_file() and candidate.name not in ignored_names:
            relative = candidate.relative_to(repository_root).as_posix()
            if relative not in declared:
                issues.append(VerificationIssue(relative, "data file is not declared"))
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify tutorial data checksums")
    parser.add_argument("--manifest", type=Path, default=Path("data/manifest.yaml"))
    args = parser.parse_args()
    issues = verify_manifest(args.manifest, repository_root=Path.cwd())
    if issues:
        for issue in issues:
            print(f"{issue.path}: {issue.message}")
        raise SystemExit(1)
    print("Data manifest, provenance, checksums, and GKS annotations are valid.")


if __name__ == "__main__":
    main()
