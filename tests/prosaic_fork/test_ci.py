"""Retained legacy checks need explicit extras; fork publication stays disabled."""

from pathlib import Path
import shlex

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"


def _castle_installs(workflow):
    document = yaml.safe_load((WORKFLOWS / workflow).read_text())
    installs = {}
    for name, job in document["jobs"].items():
        for step in job["steps"]:
            for line in step.get("run", "").splitlines():
                command = shlex.split(line)
                if command[:3] == ["pip", "install", "-e"]:
                    source = command[3]
                    if source == "." or source.startswith(".["):
                        installs[name] = source
    return installs


def test_retained_platform_suites_install_legacy_dependencies():
    assert _castle_installs("ci.yml") == {
        "test-linux": ".[dev,legacy]",
        "test-windows": ".[dev,legacy]",
        "test-macos": ".[dev,legacy]",
    }


def test_retained_research_suites_install_legacy_dependencies():
    assert _castle_installs("research-info-theory.yml") == {
        "unit-and-integration": ".[legacy]",
        "reproducibility-tier4": ".[legacy]",
    }


def test_upstream_publisher_is_archived_and_no_active_workflow_publishes():
    assert (WORKFLOWS / "publish.yml.disabled").is_file()
    assert not (WORKFLOWS / "publish.yml").exists()
    for path in (*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")):
        workflow = yaml.safe_load(path.read_text())
        for job in workflow.get("jobs", {}).values():
            for step in job.get("steps", []):
                assert not step.get("uses", "").startswith("pypa/gh-action-pypi-publish")
