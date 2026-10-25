"""Verify the pinned, unpublished pilot bundle before installing any artifact."""

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath


PROJECTS = {"prosaic-castle", "b3-prosaic-memory-castle", "cognitive-castle-sue"}


def verify_bundle(directory: Path, manifest: Path) -> dict:
    directory = directory.resolve(strict=True)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if (
        data.get("schemaVersion") != 1
        or data.get("publicationAuthorized") is not False
        or data.get("memory")
        != {"enabled": False, "profile": "memory-fts-v1", "recencyBoost": False}
        or data.get("sue") != {"enabled": False, "experimental": True}
    ):
        raise ValueError("unexpected pilot defaults or manifest version")
    projects = data["packages"]
    if len(projects) != 3 or {p["distribution"] for p in projects} != PROJECTS:
        raise ValueError("pilot requires worker, adapter and separate SUE package")
    count = 0
    seen = set()
    for project in projects:
        files = project["files"]
        if len(files) != 2 or {item["kind"] for item in files} != {"wheel", "sdist"}:
            raise ValueError("each package requires one wheel and sdist")
        for item in files:
            relative = PurePosixPath(item["filename"])
            if relative.is_absolute() or ".." in relative.parts or "\\" in item["filename"]:
                raise ValueError("unsafe artifact path")
            path = (directory / relative).resolve()
            if not path.is_relative_to(directory) or path in seen:
                raise ValueError("unsafe or duplicated artifact path")
            seen.add(path)
            if not path.is_file():
                raise ValueError(f"missing artifact: {relative}")
            digest = sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            if path.stat().st_size != item["bytes"] or digest.hexdigest() != item["sha256"]:
                raise ValueError(f"artifact mismatch: {relative}")
            count += 1
    return {"verified": True, "artifacts": count, "memoryEnabled": False, "sueEnabled": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="root containing the pinned candidate files")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "pilot/candidate.json",
    )
    args = parser.parse_args()
    print(json.dumps(verify_bundle(args.directory, args.manifest), sort_keys=True))


if __name__ == "__main__":
    main()
