# Prosaic Castle fork provenance

Upstream project: Cognitive Castle. Qualified source baseline:
`53637196cc215e9bd5b85b9253b3430b2781b884`. The MIT license and attribution remain
in `LICENSE`. This independent local fork preserves the original `README.md`,
legacy imports, plugin metadata, historic evidence and tests. It does not imply
an upstream release, endorsement, backport or publication.

The initial fork's distribution is `prosaic-castle==3.4.2`, retaining the baseline
engine version for compatibility. It adds `prosaic_castle` and the
`prosaic-castle-provider` command. Retaining `cognitive_castle` means the fork
cannot safely share an environment with the original `cognitive-castle`
distribution. The new command rejects detected coinstallation before importing
the legacy worker. This guard cannot repair environments already overwritten
by a package installer, nor identify source trees copied without metadata.

Base packaging excludes sentence-transformers and spaCy requirements. The
`dense` and `legacy` extras make those dependencies explicit while preserving
the implementation of historical modes. The deterministic provider policy is
documented alongside its policy implementation and rejects unsupported custom
rules instead of silently ignoring them. Memory remains independently opt-in
in consumers; Runtime owns model execution, Harness owns accepted workflow
state, and Lab owns authorization and evaluation.

SUE remains separately packaged by `packages/sue/pyproject.toml`, importing
`castle_sue`. The Castle adapter continues using the canonical engine APIs.
No dependency or engine identity rename is implied by the fork distribution.

For deterministic local artifacts, set `SOURCE_DATE_EPOCH=1700000000` and run:

```sh
python -m build --no-isolation --outdir /absolute/path/to/direct
python -m tarfile -e /absolute/path/to/direct/prosaic_castle-3.4.2.tar.gz /absolute/path/to/rebuilt-source
cd /absolute/path/to/rebuilt-source/prosaic_castle-3.4.2
python -m build --wheel --no-isolation --outdir /absolute/path/to/rebuilt
```

Compare wheel SHA-256 hashes and install each wheel in a fresh lean environment
outside either source tree. Verify `pip check`, the provider's framed stdio
protocol, real LanceDB FTS retrieval, and rejected scope/revision/provenance
cases without model dependencies. A successful macOS run does not qualify a
native Linux installation. Fixture tests do not measure review quality.
