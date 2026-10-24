"""Release qualification of the installed, dependency-free SUE distribution."""

import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BUILD_PYTHON = os.environ.get("SUE_BUILD_PYTHON", sys.executable)
LENSES = (
    "euthyphro",
    "meno",
    "parmenides",
    "cratylus",
    "theaetetus",
    "sophist",
    "gorgias",
    "republic",
    "philebus",
)


def build(source, destination, *targets, check=True):
    return subprocess.run(
        [
            BUILD_PYTHON,
            "-m",
            "build",
            "--no-isolation",
            *targets,
            "--outdir",
            str(destination),
            str(source),
        ],
        capture_output=True,
        text=True,
        check=check,
    )


@pytest.fixture(scope="session")
def release(tmp_path_factory):
    assert (ROOT / "pyproject.toml").is_file(), "standalone SUE package is missing"
    work = tmp_path_factory.mktemp("sue-release")
    build(ROOT, work / "direct", "--wheel", "--sdist")
    wheel = next((work / "direct").glob("*.whl"))
    sdist = next((work / "direct").glob("*.tar.gz"))
    with tarfile.open(sdist) as archive:
        archive.extractall(work / "source", filter="data")
    source = next((work / "source").iterdir())
    build(source, work / "rebuilt", "--wheel")
    rebuilt = next((work / "rebuilt").glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(work / "installed")
    sys.path.insert(0, str(work / "installed"))
    yield work, wheel, sdist, rebuilt, source
    sys.path.remove(str(work / "installed"))


def payload(path):
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def test_release_is_dependency_free_and_rebuilds_identically(release):
    _, wheel, _, rebuilt, _ = release
    direct = payload(wheel)
    assert direct == payload(rebuilt)
    metadata = direct["cognitive_castle_sue-0.1.0.dist-info/METADATA"].decode()
    assert "Name: cognitive-castle-sue\n" in metadata
    assert "Version: 0.1.0\n" in metadata
    assert "License-Expression: MIT\n" in metadata
    assert "Requires-Dist:" not in metadata
    assert not any(name.startswith("cognitive_castle/") for name in direct)
    manifest = json.loads(direct["castle_sue/SOURCES.json"])
    for item in manifest["files"]:
        data = direct[item["destination"]]
        assert data == (REPO / item["source"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item["sha256"]
    assert "castle_sue/_vendor/sue/LICENSE" in direct
    assert "castle_sue/_vendor/sue/UPSTREAM.json" in direct
    assert "castle_sue/LICENSE" in direct


def test_capabilities_bind_exact_engine_bytes(release):
    import castle_sue

    caps = castle_sue.capabilities()
    assert caps["apiVersion"] == 1
    assert caps["schemaVersion"] == 2
    assert caps["policyVersion"] == "2026-09-24"
    assert set(caps["lenses"]) == set(LENSES)
    identity = caps["engineIdentity"]
    assert identity["algorithm"] == "sha256"
    assert {"SOURCES.json", "__init__.py", "_loader.py"} <= set(identity["files"])
    for name, digest in identity["files"].items():
        assert (
            hashlib.sha256((Path(castle_sue.__file__).parent / name).read_bytes()).hexdigest()
            == digest
        )
    caps["lenses"].clear()
    assert len(castle_sue.capabilities()["lenses"]) == 9


@pytest.mark.parametrize("control", ["__init__.py", "_loader.py"])
def test_engine_identity_changes_with_execution_boundary(release, tmp_path, control):
    import castle_sue

    original = castle_sue.capabilities()["engineIdentity"]
    target = tmp_path / "castle_sue"
    shutil.copytree(release[0] / "installed/castle_sue", target)
    path = target / control
    path.write_bytes(path.read_bytes() + b"\n# execution boundary changed\n")
    script = f"import sys,json; sys.path.insert(0, {str(tmp_path)!r}); import castle_sue; print(json.dumps(castle_sue.capabilities()['engineIdentity']))"
    result = subprocess.run(
        [sys.executable, "-I", "-c", script], capture_output=True, text=True, check=True
    )
    changed = json.loads(result.stdout)
    assert (target / "SOURCES.json").read_bytes() == (
        release[0] / "installed/castle_sue/SOURCES.json"
    ).read_bytes()
    assert changed["sourceManifestDigest"] == original["sourceManifestDigest"]
    assert changed["digest"] != original["digest"]


def test_rebuilt_wheel_has_same_execution_identity(release):
    import castle_sue

    target = release[0] / "rebuilt-installed"
    with zipfile.ZipFile(release[3]) as archive:
        archive.extractall(target)
    script = f"import sys,json; sys.path.insert(0, {str(target)!r}); import castle_sue; print(json.dumps(castle_sue.capabilities()['engineIdentity']))"
    result = subprocess.run(
        [sys.executable, "-I", "-c", script], capture_output=True, text=True, check=True
    )
    assert json.loads(result.stdout) == castle_sue.capabilities()["engineIdentity"]


def test_build_rejects_modified_canonical_snapshot(release, tmp_path):
    source = release[4]
    shutil.copytree(source, tmp_path / "source")
    engine = tmp_path / "source/_canonical/cognitive_castle/brain_engine.py"
    engine.write_bytes(engine.read_bytes() + b"\n# changed\n")
    result = build(tmp_path / "source", tmp_path / "dist", "--wheel", check=False)
    assert result.returncode != 0
    assert "source hash mismatch" in result.stderr


@pytest.mark.parametrize("lens", LENSES)
@pytest.mark.parametrize(
    "scenario",
    ["success", "silence", "partial", "revision", "exhaustion", "invalid_quote", "wrong_claim"],
)
def test_all_lenses_match_public_castle_engine(release, lens, scenario):
    import castle_sue
    from cognitive_castle import brain_engine as public

    # Reuse the established scripted scenarios; never patch an installed engine.
    sys.path.insert(0, str(REPO / "tests"))
    try:
        fixtures = importlib.import_module("test_brain_engine")
    finally:
        sys.path.pop(0)
    answer, claim, lines = fixtures.answer, fixtures.CLAIM, fixtures.SOURCE.splitlines()
    path = public.vendor.LENSES[lens]["path"]
    cap = 2 if scenario == "exhaustion" else 14
    replies = [answer(op) for op in path]
    if scenario == "silence":
        replies = [answer("DEFINE", "UNKNOWN")]
    elif scenario == "partial":
        replies = [answer("DEFINE", "INCOMPLETE"), answer("DISTINGUISH", "UNKNOWN")]
    elif scenario == "revision":
        replies = [answer(op) for op in path[: path.index("COUNTEREXAMPLE")]]
        replies.append(answer("COUNTEREXAMPLE", "FOUND"))
        replies.append(
            answer(
                "REVISE",
                addresses=list(range(1, len(replies) + 1)),
                revision_reason="Retain role and consent.",
            )
        )
        replies.extend(answer(op) for op in path if op != "DEFINE")
    elif scenario == "invalid_quote":
        replies = [answer("DEFINE", evidence=[{"line": 1, "quote": "fabricated"}])]
    elif scenario == "wrong_claim":
        replies = [answer("DEFINE"), answer(path[1], claim="A different unsupported claim.")]
    actual = castle_sue.initial_state(claim, lens=lens, max_turns=cap)
    expected = public.initial_state(claim, lens=lens, max_turns=cap)
    assert actual == expected
    for reply in replies:
        assert castle_sue.question(actual) == public.question(expected)
        assert castle_sue.schema(actual) == public.schema(expected)
        actual, error = castle_sue.advance(actual, reply, lines)
        expected, expected_error = public.advance(expected, reply, lines)
        assert (actual, error) == (expected, expected_error)
        assert castle_sue.coverage(actual) == public.coverage(expected)
        if actual["terminal"]:
            assert castle_sue.question(actual) is None
            assert castle_sue.schema(actual) is None
            assert castle_sue.advance(actual, {}, lines) == (actual, "engine_terminal")
            break
    if scenario in ("invalid_quote", "wrong_claim"):
        assert error == "invalid_turn"


def test_pure_api_has_no_heavy_imports_or_dispatch(release):
    installed = release[0] / "installed"
    smoke = ROOT / "tests/standalone_smoke.py"
    script = f"import sys,runpy; sys.path.insert(0, {str(installed)!r}); runpy.run_path({str(smoke)!r}, run_name='__main__')"
    subprocess.run([sys.executable, "-I", "-c", script], check=True)


def test_capabilities_reject_changed_resource(release, tmp_path):
    shutil.copytree(release[0] / "installed/castle_sue", tmp_path / "castle_sue")
    lens = tmp_path / "castle_sue/_vendor/sue/sue_lenses.py"
    lens.write_bytes(lens.read_bytes() + b"\n# altered\n")
    script = f"import sys; sys.path.insert(0, {str(tmp_path)!r}); import castle_sue; castle_sue.capabilities()"
    result = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True)
    assert result.returncode != 0
    assert "engine resource hash mismatch: _vendor/sue/sue_lenses.py" in result.stderr


def test_repeated_builds_are_reproducible(release, tmp_path):
    build(ROOT, tmp_path, "--wheel", "--sdist")
    assert next(tmp_path.glob("*.whl")).read_bytes() == release[1].read_bytes()
    assert next(tmp_path.glob("*.tar.gz")).read_bytes() == release[2].read_bytes()


@pytest.mark.parametrize("order", ["standalone_first", "castle_first", "hostile_aliases"])
def test_vendor_modules_are_private_and_preserve_legacy_aliases(release, order):
    installed = release[0] / "installed"
    script = f"""
import sys, types, pickle, typing, builtins, importlib.util
sys.path.insert(0, {str(installed)!r})
sys.path.insert(0, {str(REPO)!r})
aliases = ('sue_runner', 'sue_challenge', 'sue_lenses')
if {order!r} == 'hostile_aliases':
    for name in aliases:
        sys.modules[name] = types.ModuleType(name)
if {order!r} == 'castle_first':
    from cognitive_castle import brain_engine as legacy
before = {{name: sys.modules.get(name) for name in aliases}}
original_import = builtins.__import__
original_spec = importlib.util.spec_from_file_location
original_modules = sys.modules
import castle_sue
private = castle_sue.brain_engine.vendor
assert {{name: sys.modules.get(name) for name in aliases}} == before
assert builtins.__import__ is original_import
assert importlib.util.spec_from_file_location is original_spec
assert sys.modules is original_modules
assert len(castle_sue.capabilities()['lenses']) == 9
assert private.v1.__name__ == 'castle_sue._vendor.sue.sue_challenge'
assert private.v1.runner.__name__ == 'castle_sue._vendor.sue.sue_runner'
assert private.v1.runner.__file__.startswith({str(installed)!r})
failure = private.v1.ParseFailure(reason='private namespace roundtrip')
assert pickle.loads(pickle.dumps(failure)) == failure
typing.get_type_hints(type(failure))
typing.get_type_hints(private.v1.runner.ModelInvocation)
if {order!r} == 'standalone_first':
    from cognitive_castle import brain_engine as legacy
if {order!r} != 'hostile_aliases':
    assert private.v1 is not legacy.vendor.v1
    assert private.v1.runner is not legacy.vendor.v1.runner
    state = legacy.initial_state('A claim')
    assert legacy.question(state)
    assert legacy.advance(state, {{}}, ['A source'])[1] == 'invalid_turn'
state = castle_sue.initial_state('A claim')
assert castle_sue.question(state)
assert castle_sue.advance(state, {{}}, ['A source'])[1] == 'invalid_turn'
"""
    result = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
