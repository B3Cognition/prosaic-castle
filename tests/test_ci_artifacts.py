"""The artifact gate must detect payload drift and unsafe source archives."""

import importlib.util
import io
from pathlib import Path
import tarfile
import zipfile
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ci_build_artifacts.py"


def load_gate():
    assert SCRIPT.is_file(), "artifact qualification script is missing"
    spec = importlib.util.spec_from_file_location("ci_build_artifacts", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wheel(path, payload):
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in payload.items():
            archive.writestr(name, content)


def test_rebuilt_wheel_requires_identical_payload(tmp_path):
    gate = load_gate()
    direct, rebuilt = tmp_path / "direct.whl", tmp_path / "rebuilt.whl"
    wheel(direct, {"package/core.py": b"original", "package/LICENSE": b"license"})
    wheel(rebuilt, {"package/core.py": b"changed", "package/LICENSE": b"license"})
    with pytest.raises(AssertionError, match="payload"):
        gate.require_same_payload(direct, rebuilt)
    wheel(rebuilt, {"package/core.py": b"original", "package/LICENSE": b"license"})
    gate.require_same_payload(direct, rebuilt)


def test_sdist_rebuild_rejects_archive_escape(tmp_path):
    gate = load_gate()
    source = tmp_path / "source.tar.gz"
    with tarfile.open(source, "w:gz") as archive:
        member = tarfile.TarInfo("../escaped")
        member.size = 1
        archive.addfile(member, io.BytesIO(b"x"))
    with pytest.raises((ValueError, tarfile.FilterError)):
        gate.unpack_sdist(source, tmp_path / "unpacked")
    assert not (tmp_path / "escaped").exists()


def test_installed_smoke_rejects_nonisolated_execution(tmp_path):
    script = SCRIPT.with_name("ci_installed_smoke.py")
    assert script.is_file(), "installed smoke is missing"
    result = subprocess.run(
        [sys.executable, str(script), "--component", "provider"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "requires python -I" in result.stderr


def test_installed_smoke_rejects_checkout_imports(tmp_path):
    script = SCRIPT.with_name("ci_installed_smoke.py")
    assert script.is_file(), "installed smoke is missing"
    bootstrap = (
        "import sys,runpy; "
        f"sys.path.insert(0, {str(SCRIPT.parent.parent)!r}); "
        f"sys.argv = [{str(script)!r}, '--component', 'provider']; "
        f"runpy.run_path({str(script)!r}, run_name='__main__')"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", bootstrap],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "outside installed environment" in result.stderr


def test_worker_guard_allows_availability_probe_but_rejects_actual_import(tmp_path):
    script = SCRIPT.with_name("ci_installed_smoke.py")
    bootstrap = (
        "import runpy,importlib.util; "
        f"m=runpy.run_path({str(script)!r}); "
        "exec(m['WORKER_BOOTSTRAP'].split('runpy.run_module')[0]); "
        "importlib.util.find_spec('torch'); print('availability-probe-ok'); import torch"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", bootstrap],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "availability-probe-ok" in result.stdout
    assert result.returncode != 0
    assert "optional engine imported: torch" in result.stderr
