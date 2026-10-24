"""Pure, bounded SUE state transitions; no model or transport is invoked.

The engine and sourced lenses are mapped from Castle's canonical source files
at build time. ``capabilities`` binds their exact bytes for resumable hosts.
"""

import hashlib
import json
from pathlib import Path

from ._loader import load_vendor as _load_vendor

_load_vendor()

from .brain_engine import advance, coverage, initial_state, question, schema  # noqa: E402
from .brain_engine import vendor as _vendor  # noqa: E402

__version__ = "0.1.0"
__all__ = ["initial_state", "question", "schema", "advance", "coverage", "capabilities"]


def capabilities() -> dict:
    """Return versioned policy discovery and verified immutable engine identity.

    Missing or changed resources raise ``ValueError``/``OSError``; a host must
    not silently resume a saved review with different code or policy bytes.
    """
    root = Path(__file__).parent
    manifest_bytes = (root / "SOURCES.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    files = {}
    for item in manifest["files"]:
        relative = item["destination"].removeprefix("castle_sue/")
        actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        if actual != item["sha256"]:
            raise ValueError(f"engine resource hash mismatch: {relative}")
        files[relative] = actual
    # Canonical policy identity alone does not bind the wrapper/import boundary.
    # Include its exact installed bytes so a host's saved identity also changes
    # when package-local execution behavior changes between candidate builds.
    for relative in ("SOURCES.json", "__init__.py", "_loader.py"):
        files[relative] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    identity_bytes = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "apiVersion": 1,
        "schemaVersion": _vendor.SCHEMA_VERSION,
        "policyVersion": _vendor.POLICY_VERSION,
        "lenses": list(_vendor.LENSES),
        "engineIdentity": {
            "algorithm": "sha256",
            "digest": hashlib.sha256(identity_bytes).hexdigest(),
            "sourceManifestDigest": hashlib.sha256(manifest_bytes).hexdigest(),
            "files": files,
        },
    }
