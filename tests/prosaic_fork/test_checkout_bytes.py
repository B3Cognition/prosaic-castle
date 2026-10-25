"""Git's Windows checkout filters must preserve the shipped byte-hash contracts."""

import hashlib
import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / "packages/sue/source-manifest.json").read_bytes())
HASHED_FILES = [(item["source"], item["sha256"]) for item in MANIFEST["files"]]
HASHED_FILES += [
    ("packages/sue/src/castle_sue/__init__.py", None),
    ("packages/sue/src/castle_sue/_loader.py", None),
    ("packages/sue/source-manifest.json", None),
    (
        "cognitive_castle/rules/castle-boost.soar",
        "2f733306d6e5464cd2d63a1b639650a9730953b6217469d054fd05ce076821f9",
    ),
]


@pytest.mark.parametrize("path,pinned_sha256", HASHED_FILES, ids=[p for p, _ in HASHED_FILES])
def test_windows_checkout_filters_preserve_hashed_bytes(path, pinned_sha256):
    raw = subprocess.run(
        ["git", "cat-file", "blob", f"HEAD:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert b"\r\n" not in raw, "canonical Git object must use LF"
    if pinned_sha256 is not None:
        assert hashlib.sha256(raw).hexdigest() == pinned_sha256
    filtered = subprocess.run(
        [
            "git",
            "-c",
            "core.autocrlf=true",
            "-c",
            "core.eol=crlf",
            "cat-file",
            "--filters",
            f"--path={path}",
            f"HEAD:{path}",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert filtered == raw, f"Windows checkout changed byte-hashed payload: {path}"
