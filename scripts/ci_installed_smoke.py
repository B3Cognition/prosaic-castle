"""Offline synthetic installed-artifact check. Run with python -I outside checkout."""

from __future__ import annotations

import argparse
import hashlib
import importlib
from importlib import metadata
import json
from pathlib import Path
import subprocess
import sys
import tempfile


TEXT = "Castle CI synthetic decision: keep source evidence exact. 🙂\r\n\x00End  \n"
NAMESPACE = "castle-ci-synthetic"
FORBIDDEN = ("torch", "spacy", "sentence_transformers", "cognitive_castle.soar_bridge")
WORKER_BOOTSTRAP = """
import runpy, sys
def guard(event, args):
    if event == 'import':
        fullname = args[0]
        if any(fullname == n or fullname.startswith(n + '.') for n in (
            'torch', 'spacy', 'sentence_transformers', 'cognitive_castle.soar_bridge',
            'cognitive_castle.judge', 'cognitive_castle.llm_client', 'cognitive_castle.sue')):
            raise AssertionError('optional engine imported: ' + fullname)
sys.addaudithook(guard)
runpy.run_module('prosaic_castle.provider_worker', run_name='__main__')
assert not any(n in sys.modules for n in ('torch', 'spacy', 'sentence_transformers'))
"""


def require_installed(module_name, distribution_name):
    module = importlib.import_module(module_name)
    assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), (
        "module loaded outside installed environment: " + module_name
    )
    owner = metadata.distribution(distribution_name)
    assert owner.version
    return owner.version


def prepare_fixture(root):
    from cognitive_castle.config import CognitiveCastleConfig
    from cognitive_castle.context import CastleContext, PalacePaths

    palace, config_path = root / "palace", root / "config.json"
    data = {"embedder_model": "ci-synthetic-no-model", "embedder_dim": 4}
    config_path.write_text(json.dumps(data), encoding="utf-8")
    config = CognitiveCastleConfig(config_dir=root)
    config._file_config = data
    paths = PalacePaths.resolve(palace, config_dir=root)
    with CastleContext.open(paths, config=config, create=True, read_only=False) as context:
        collection = context.get_collection()
        collection.upsert(
            ids=["approved", "denied", "partial"],
            documents=[TEXT, "Castle CI synthetic private decision", "Castle CI incomplete"],
            metadatas=[
                {"wing": "project", "revision": "ci-r1", "source_file": "/synthetic/source"},
                {"wing": "private"},
                {"wing": "project", "ingest_complete": False},
            ],
            embeddings=[[0.0] * 4 for _ in range(3)],
        )
        # Fail visibly if the native platform cannot construct its FTS index.
        collection._table.create_fts_index("text", replace=True)
    paths.provider.mkdir()
    (paths.provider / "identity.json").write_text(
        json.dumps({"schema_version": 1, "namespace": NAMESPACE}), encoding="utf-8"
    )
    return palace, config_path


def assert_reads(health, search, fetched, snapshot):
    digest = hashlib.sha256(TEXT.encode()).hexdigest()
    assert health["profile"] == "memory-fts-v1"
    assert health["recency_boost"] is False
    assert [hit["record_id"] for hit in search["hits"]] == ["approved"]
    hit = search["hits"][0]
    assert hit["wing"] == "project" and hit["revision"] == "ci-r1"
    assert hit["text_sha256"] == digest
    assert fetched["text"] == TEXT and fetched["complete"] is True
    assert fetched["text_sha256"] == fetched["slice_sha256"] == digest
    assert snapshot["texts"] == [TEXT]
    assert snapshot["sources"][0]["text_sha256"] == digest
    assert len(snapshot["digest"]) == 64
    assert "/synthetic/source" not in json.dumps([search, fetched, snapshot])


def worker_argv(palace, config_path, namespace=NAMESPACE):
    return [
        sys.executable,
        "-I",
        "-c",
        WORKER_BOOTSTRAP,
        "--palace",
        str(palace),
        "--config",
        str(config_path),
        "--namespace",
        namespace,
        "--wing",
        "project",
    ]


def provider_smoke(root, palace, config_path):
    operations = [
        ("hello", {}),
        ("search", {"query": "Castle"}),
        ("fetch", {"record_id": "approved"}),
        (
            "snapshot",
            {
                "record_ids": ["approved"],
                "expected": {
                    "approved": {
                        "text_sha256": hashlib.sha256(TEXT.encode()).hexdigest(),
                        "revision": "ci-r1",
                    }
                },
            },
        ),
        ("fetch", {"record_id": "denied"}),
        ("fetch", {"record_id": "partial"}),
        ("fetch", {"record_id": "absent"}),
        (
            "snapshot",
            {
                "record_ids": ["approved"],
                "expected": {"approved": {"text_sha256": "0" * 64, "revision": "ci-r1"}},
            },
        ),
        ("close", {}),
    ]
    frames = "".join(
        json.dumps({"version": 1, "id": str(i), "op": op, "args": args}) + "\n"
        for i, (op, args) in enumerate(operations)
    )
    result = subprocess.run(
        worker_argv(palace, config_path),
        input=frames,
        text=True,
        capture_output=True,
        cwd=root,
        timeout=60,
    )
    assert result.returncode == 0, "worker failed; no private stderr exposed"
    replies = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(replies) == len(operations)
    assert all(reply["ok"] for reply in replies[:4])
    assert_reads(*(reply["result"] for reply in replies[:4]))
    assert [reply["error"]["code"] for reply in replies[4:7]] == ["not_found"] * 3
    assert replies[7]["error"]["code"] == "incompatible_store"
    assert replies[8]["ok"] is True
    wrong = subprocess.run(
        worker_argv(palace, config_path, "wrong-namespace"),
        input=frames,
        text=True,
        capture_output=True,
        cwd=root,
        timeout=60,
    )
    assert wrong.returncode == 0
    assert json.loads(wrong.stdout.splitlines()[0])["error"]["code"] == "incompatible_store"


def adapter_smoke(palace, config_path):
    from prosaic_memory_castle import CastleMemoryProvider, MemoryProviderError, WorkerCommand

    with CastleMemoryProvider(
        WorkerCommand((sys.executable, "-I", "-c", WORKER_BOOTSTRAP)),
        palace_path=palace,
        namespace=NAMESPACE,
        config_path=config_path,
        allowed_wings=("project",),
    ) as provider:
        expected = {
            "approved": {
                "text_sha256": hashlib.sha256(TEXT.encode()).hexdigest(),
                "revision": "ci-r1",
            }
        }
        assert_reads(
            provider.health(),
            provider.search("Castle"),
            provider.fetch("approved"),
            provider.snapshot(["approved"], expected=expected),
        )
        for record in ("denied", "partial", "absent"):
            try:
                provider.fetch(record)
            except MemoryProviderError as error:
                assert error.code == "not_found"
            else:
                raise AssertionError("unscoped or incomplete source exposed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=("provider", "adapter"), required=True)
    args = parser.parse_args()
    assert sys.flags.isolated == 1, "installed smoke requires python -I"
    versions = {"prosaic-castle": require_installed("prosaic_castle", "prosaic-castle")}
    require_installed("cognitive_castle", "prosaic-castle")
    if args.component == "adapter":
        versions["b3-prosaic-memory-castle"] = require_installed(
            "prosaic_memory_castle", "b3-prosaic-memory-castle"
        )
    installed = {d.metadata["Name"].lower().replace("_", "-") for d in metadata.distributions()}
    assert not {"torch", "spacy", "sentence-transformers", "cognitive-castle"} & installed
    with tempfile.TemporaryDirectory(prefix="castle-ci-") as temporary:
        root = Path(temporary)
        palace, config_path = prepare_fixture(root)
        if args.component == "provider":
            provider_smoke(root, palace, config_path)
        else:
            adapter_smoke(palace, config_path)
    assert not any(name == n or name.startswith(n + ".") for name in sys.modules for n in FORBIDDEN)
    print(
        json.dumps(
            {
                "component": args.component,
                "versions": versions,
                "checks": [
                    "installed",
                    "native-fts",
                    "scope",
                    "provenance",
                    "exact-bytes",
                    "snapshot",
                    "incomplete-rejected",
                    "recency-off",
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
