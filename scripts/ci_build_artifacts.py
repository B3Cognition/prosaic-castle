"""Build wheel/sdist, rebuild the sdist, and require byte-identical wheel payloads.

Usage: python scripts/ci_build_artifacts.py --project . --output /tmp/artifacts/worker
The interpreter must have build and the project's build backend installed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile


def require_same_payload(direct: Path, rebuilt: Path) -> None:
    def payload(path):
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            assert len(names) == len(set(names)), "duplicate wheel payload paths"
            return {name: archive.read(name) for name in names}

    assert payload(direct) == payload(rebuilt), "sdist rebuild changed wheel payload"


def unpack_sdist(source: Path, destination: Path) -> Path:
    destination.mkdir(parents=True)
    with tarfile.open(source) as archive:
        # CI uses Python 3.12+. Explicit filtering prevents path/link escapes.
        archive.extractall(destination, filter="data")
    roots = list(destination.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError("sdist must have one source directory")
    return roots[0]


def only(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, f"expected exactly one {pattern} artifact: {matches}"
    return matches[0]


def build(project: Path, destination: Path, *targets: str) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            *targets,
            "--outdir",
            str(destination),
            str(project),
        ],
        check=True,
        timeout=180,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True)
    build(args.project.resolve(), output / "direct", "--wheel", "--sdist")
    direct = only(output / "direct", "*.whl")
    sdist = only(output / "direct", "*.tar.gz")
    source = unpack_sdist(sdist, output / "source")
    build(source, output / "rebuilt", "--wheel")
    rebuilt = only(output / "rebuilt", "*.whl")
    require_same_payload(direct, rebuilt)
    report = {
        "payloadsIdentical": True,
        "artifacts": {
            str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (direct, sdist, rebuilt)
        },
    }
    (output / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
