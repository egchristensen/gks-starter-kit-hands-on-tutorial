from pathlib import Path

import yaml

from gks_tutorial.manifests import load_manifest, sha256, verify_manifest


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
