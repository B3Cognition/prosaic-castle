"""Fork packaging contracts, separate from the preserved upstream identity tests."""

import json
import os
from pathlib import Path
import subprocess
import sys

from packaging.requirements import Requirement

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[2]


def test_base_install_does_not_request_model_execution_dependencies():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    dependencies = {Requirement(value).name for value in project["dependencies"]}
    assert {"lancedb", "pyarrow", "pyyaml"} <= dependencies
    assert not dependencies & {"sentence-transformers", "spacy", "torch", "transformers"}
    extras = project["optional-dependencies"]
    assert "sentence-transformers" in {Requirement(value).name for value in extras["dense"]}
    assert "spacy" in {Requirement(value).name for value in extras["legacy"]}


def test_fork_metadata_exposes_an_independent_provider_command():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert (project["name"], project["version"]) == ("prosaic-castle", "3.4.2")
    assert project["scripts"]["prosaic-castle-provider"] == "prosaic_castle.provider_worker:main"


def test_public_provider_help_does_not_import_model_or_rule_engines():
    code = """
import importlib.abc
import sys
class NoModelImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'torch', 'transformers', 'sentence_transformers', 'spacy', 'sml'}:
            raise AssertionError('unwanted model/rule import: ' + fullname)
sys.meta_path.insert(0, NoModelImports())
sys.argv = ['prosaic-castle-provider', '--help']
from prosaic_castle.provider_worker import main
main()
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "memory-fts-v1" in result.stdout


def test_provider_rejects_a_coinstalled_upstream_distribution(tmp_path):
    metadata = tmp_path / "cognitive_castle-3.4.2.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: cognitive-castle\nVersion: 3.4.2\n"
    )
    env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(tmp_path), str(ROOT))))
    result = subprocess.run(
        [sys.executable, "-m", "prosaic_castle.provider_worker", "--help"],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "cognitive-castle" in result.stderr
    assert "separate virtual environment" in result.stderr
    assert "usage:" not in result.stdout


def test_fork_public_version_does_not_relabel_the_legacy_engine():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, prosaic_castle, cognitive_castle; print(json.dumps([prosaic_castle.__version__, cognitive_castle.__version__]))",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == ["3.4.2", "3.4.2"]
