"""A pinned pilot bundle must reject substitutions before any installation."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def verifier():
    path = ROOT / "scripts/verify_pilot_bundle.py"
    assert path.is_file(), "pilot bundle verifier is missing"
    spec = importlib.util.spec_from_file_location("verify_pilot_bundle", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify_bundle


def bundle(tmp_path):
    projects = []
    for name in ("prosaic-castle", "b3-prosaic-memory-castle", "cognitive-castle-sue"):
        files = []
        for kind, suffix in (("wheel", ".whl"), ("sdist", ".tar.gz")):
            filename = name + suffix
            data = (name + kind).encode()
            (tmp_path / filename).write_bytes(data)
            files.append(
                {
                    "kind": kind,
                    "filename": filename,
                    "sha256": sha256(data).hexdigest(),
                    "bytes": len(data),
                }
            )
        projects.append({"distribution": name, "version": "test", "files": files})
    manifest = {
        "schemaVersion": 1,
        "publicationAuthorized": False,
        "memory": {"enabled": False, "profile": "memory-fts-v1", "recencyBoost": False},
        "sue": {"enabled": False, "experimental": True},
        "packages": projects,
    }
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(manifest))
    return path, manifest


def test_pilot_bundle_verifies_all_six_artifacts_without_installing(tmp_path):
    manifest, _ = bundle(tmp_path)
    assert verifier()(tmp_path, manifest) == {
        "verified": True,
        "artifacts": 6,
        "memoryEnabled": False,
        "sueEnabled": False,
    }


def test_substituted_same_version_candidate_is_rejected(tmp_path):
    manifest, data = bundle(tmp_path)
    path = tmp_path / data["packages"][0]["files"][0]["filename"]
    path.write_bytes(b"substituted candidate")
    with pytest.raises(ValueError, match="artifact mismatch"):
        verifier()(tmp_path, manifest)


@pytest.mark.parametrize("filename", ["../outside.whl", "/tmp/outside.whl"])
def test_pilot_manifest_cannot_escape_bundle_directory(tmp_path, filename):
    manifest, data = bundle(tmp_path)
    data["packages"][0]["files"][0]["filename"] = filename
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="artifact path"):
        verifier()(tmp_path, manifest)


def test_pilot_bundle_requires_all_packages_and_both_artifact_kinds(tmp_path):
    manifest, data = bundle(tmp_path)
    data["packages"][0]["files"].pop()
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="wheel and sdist"):
        verifier()(tmp_path, manifest)


def test_pilot_manifest_cannot_silently_enable_features(tmp_path):
    manifest, data = bundle(tmp_path)
    data["sue"]["enabled"] = True
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="pilot defaults"):
        verifier()(tmp_path, manifest)
