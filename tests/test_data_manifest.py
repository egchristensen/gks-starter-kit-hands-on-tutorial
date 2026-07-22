from pathlib import Path

import yaml

from gks_tutorial.manifests import load_manifest, sha256, verify_manifest


def _provenance(files: list[dict[str, str]]) -> dict[str, object]:
    return {
        "source": "Test source",
        "source_record_uid": "123",
        "retrieval_date": "2026-07-22",
        "retrieval_url": "https://example.org/record/123",
        "release_policy": "Pinned test fixture",
        "license": "CC0-1.0",
        "selection_method": "Selected for a verifier unit test",
        "files": files,
    }


def test_repository_manifest_is_valid() -> None:
    path = Path("data/manifest.yaml")
    manifest = load_manifest(path)
    assert manifest["manifest_version"] == 1
    assert "clinvar_native_esummary_12582" in manifest["datasets"]
    assert verify_manifest(path, repository_root=Path.cwd()) == []


def test_sha256_known_content(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture.txt"
    fixture.write_text("gks\n", encoding="utf-8")
    expected = "39a27e8a72b084d13ca9b6786ff19d0ae973216ab5a7419d7fe3ec9563de672f"
    assert sha256(fixture) == expected


def test_undeclared_data_file_is_rejected(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    manifest = data / "manifest.yaml"
    manifest.write_text(
        yaml.safe_dump({"manifest_version": 1, "datasets": {}}), encoding="utf-8"
    )
    (data / "invented.json").write_text("{}", encoding="utf-8")
    issues = verify_manifest(manifest, repository_root=tmp_path)
    assert issues[0].message == "data file is not declared"


def test_missing_provenance_fields_are_reported(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    fixture = data / "fixture.json"
    fixture.write_text("{}\n", encoding="utf-8")
    manifest = data / "manifest.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "manifest_version": 1,
                "datasets": {
                    "incomplete": {
                        "files": [
                            {
                                "path": "data/fixture.json",
                                "sha256": sha256(fixture),
                            }
                        ]
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    messages = {
        issue.message for issue in verify_manifest(manifest, repository_root=tmp_path)
    }

    assert "source is required" in messages
    assert "retrieval_date is required" in messages
    assert "a source URL is required" in messages
    assert "license or terms is required" in messages
    assert "a source identifier is required" in messages


def test_manifest_paths_must_remain_under_data(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}\n", encoding="utf-8")
    manifest = data / "manifest.yaml"
    dataset = _provenance(
        [{"path": "data/../outside.json", "sha256": sha256(outside)}]
    )
    manifest.write_text(
        yaml.safe_dump(
            {"manifest_version": 1, "datasets": {"unsafe": dataset}}
        ),
        encoding="utf-8",
    )

    issues = verify_manifest(manifest, repository_root=tmp_path)

    assert any(
        issue.message == "path must be normalized under data/" for issue in issues
    )


def test_manifest_annotation_validates_normative_gks_objects(tmp_path: Path) -> None:
    data = tmp_path / "data" / "gks"
    data.mkdir(parents=True)
    fixture = data / "invalid.jsonl"
    fixture.write_text('{"type":"NotVrs"}\n', encoding="utf-8")
    manifest = tmp_path / "data" / "manifest.yaml"
    dataset = _provenance(
        [
            {
                "path": "data/gks/invalid.jsonl",
                "sha256": sha256(fixture),
                "gks_product": "vrs",
            }
        ]
    )
    dataset["transformer"] = {
        "name": "Test transformer",
        "repository": "https://example.org/transformer",
        "commit": "abc123",
    }
    dataset["gks_versions"] = {"vrs_validator": "2.3.3"}
    manifest.write_text(
        yaml.safe_dump(
            {"manifest_version": 1, "datasets": {"invalid_gks": dataset}}
        ),
        encoding="utf-8",
    )

    issues = verify_manifest(manifest, repository_root=tmp_path)

    assert any("invalid vrs object" in issue.message for issue in issues)
