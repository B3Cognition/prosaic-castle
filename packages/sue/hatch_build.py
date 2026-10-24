"""Map immutable canonical sources into wheels and self-contained source archives."""

import hashlib
import json
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CanonicalSourcesHook(BuildHookInterface):
    def initialize(self, version, build_data):
        root = Path(self.root)
        manifest_path = root / "source-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        # An sdist is self-contained. Never reach out to a neighboring checkout
        # when rebuilding one, even if a Castle checkout happens to be present.
        source_root = root / "_canonical"
        if not source_root.is_dir():
            source_root = root.parents[1]
        for item in manifest["files"]:
            source = source_root / item["source"]
            if hashlib.sha256(source.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError(f"source hash mismatch: {item['source']}")
            destination = (
                f"_canonical/{item['source']}"
                if self.target_name == "sdist"
                else item["destination"]
            )
            build_data["force_include"][str(source)] = destination
        if self.target_name == "wheel":
            build_data["force_include"][str(manifest_path)] = "castle_sue/SOURCES.json"
