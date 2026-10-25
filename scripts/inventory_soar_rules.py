"""Read-only local SOAR rule/config inventory; emits locations and hashes, never values."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re


_SHIPPED_SHA256 = "2f733306d6e5464cd2d63a1b639650a9730953b6217469d054fd05ce076821f9"
_DEFAULT_ROOTS = [
    "/Users/michalbachorik/work/cognitive-castle",
    "/Users/michalbachorik/work/prosaics/prosaic",
    "/Users/michalbachorik/work/prosaics/prosaic-harness",
    "/Users/michalbachorik/work/prosaics/prosaic-runtime",
    "/Users/michalbachorik/work/prosaics/prosaic-integration-lab",
]
_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
_CONFIG_EXTENSIONS = {".toml", ".yaml", ".yml", ".json", ".jsonc", ".ini", ".cfg", ".env"}
_KEY = re.compile(r"\b(soar_rules_path|CASTLE_SOAR_RULES(?:_PATH)?)\b")


def inventory(roots):
    report = {
        "schema_version": 1,
        "roots": [],
        "rules": [],
        "config_occurrences": [],
        "unreadable_paths": [],
    }
    for supplied in sorted(set(map(str, roots))):
        root = Path(supplied).absolute()
        report["roots"].append({"path": str(root), "exists": root.is_dir()})
        if not root.is_dir():
            continue

        def unreadable(error):
            report["unreadable_paths"].append(str(error.filename))

        for directory, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
            dirs[:] = sorted(
                name
                for name in dirs
                if name not in _SKIP_DIRS and not Path(directory, name).is_symlink()
            )
            for name in sorted(files):
                path = Path(directory, name)
                if path.is_symlink():
                    continue
                is_rule = path.suffix.lower() == ".soar"
                is_config = (
                    path.suffix.lower() in _CONFIG_EXTENSIONS
                    or name == ".env"
                    or name.startswith(".env.")
                )
                if not (is_rule or is_config):
                    continue
                try:
                    data = path.read_bytes()
                except OSError:
                    report["unreadable_paths"].append(str(path))
                    continue
                if is_rule:
                    digest = hashlib.sha256(data).hexdigest()
                    report["rules"].append(
                        {
                            "path": str(path),
                            "sha256": digest,
                            "kind": "shipped-exact" if digest == _SHIPPED_SHA256 else "custom",
                        }
                    )
                if is_config:
                    for number, line in enumerate(
                        data.decode("utf-8", errors="replace").splitlines(), 1
                    ):
                        for key in sorted(set(_KEY.findall(line))):
                            report["config_occurrences"].append(
                                {"path": str(path), "line": number, "key": key}
                            )
    report["rules"].sort(key=lambda row: row["path"])
    report["config_occurrences"].sort(key=lambda row: (row["path"], row["line"], row["key"]))
    report["unreadable_paths"].sort()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        action="append",
        help="Repeat for each local root; defaults to the five workspaces",
    )
    args = parser.parse_args()
    print(json.dumps(inventory(args.root or _DEFAULT_ROOTS), indent=2))


if __name__ == "__main__":
    main()
