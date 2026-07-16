"""Manifest loading and checksum verification."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class VerificationIssue:
    path: str
    message: str


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
    """Verify declarations, checksums, size limits, and structured-file syntax."""
    manifest = load_manifest(path)
    issues: list[VerificationIssue] = []
    declared: set[str] = set()
    for dataset in manifest["datasets"].values():
        for item in dataset.get("files", []):
            relative = item.get("path", "")
            declared.add(relative)
            candidate = repository_root / relative
            if not candidate.is_file():
                issues.append(VerificationIssue(relative, "declared file is missing"))
            elif sha256(candidate) != item.get("sha256"):
                issues.append(VerificationIssue(relative, "SHA-256 checksum mismatch"))
            elif candidate.stat().st_size > 5 * 1024 * 1024:
                issues.append(VerificationIssue(relative, "file exceeds 5 MiB limit"))
            elif candidate.suffix == ".json":
                try:
                    json.loads(candidate.read_text(encoding="utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    issues.append(VerificationIssue(relative, f"invalid JSON: {error}"))
            elif candidate.suffix == ".jsonl":
                for number, line in enumerate(
                    candidate.read_text(encoding="utf-8").splitlines(), start=1
                ):
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as error:
                        issues.append(
                            VerificationIssue(
                                relative, f"invalid JSONL line {number}: {error}"
                            )
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
    print("Data manifest is valid; all declared checksums match.")


if __name__ == "__main__":
    main()
