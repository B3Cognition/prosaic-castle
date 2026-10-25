# Prosaic Castle

## Repository and unpublished pilot

The independent repository is `B3Cognition/prosaic-castle`. Package candidates
are built by CI and retained as workflow artifacts; **nothing is published to
PyPI by this repository**. Memory and SUE are independently disabled in the
consumer by default. SUE remains experimental; it cannot replace the protected
canonical critic review. The latest opt-in cycle guard is included without
changing the default legacy engine behavior.

Repository formatting corrections preserve the parsed code but change SUE's
exact-byte identity. The new manifest identifies that candidate explicitly.
Resume an older saved review with its original pinned engine wheel; do not
rewrite saved identity or silently adopt this candidate. Previous wheels and
failed review evidence remain preserved.

There are three independently installable distributions:

| Path | Distribution | Role |
| --- | --- | --- |
| repository root | `prosaic-castle==3.4.2` | Separate read worker |
| `adapters/prosaic` | `b3-prosaic-memory-castle==0.1.0` | Host adapter |
| `packages/sue` | `cognitive-castle-sue==0.1.0` | Pure experimental SUE engine |

These retained candidate version numbers are not an instruction to install
arbitrary same-version wheels. Use only the matching hashes in
[`pilot/candidate.json`](pilot/candidate.json). Historical bundles remain
immutable. A future published release needs a distinct version and its own
approval; publishing is outside the pilot.

Obtain the matching wheel/sdist bundle from the maintainer and verify it before
installing. `BUNDLE` must contain the `worker/`, `adapter/` and `sue/` directories
listed in the manifest. A newly built CI artifact has its own qualification.json
hashes; it is not silently equivalent to this pinned pilot bundle.

```sh
export BUNDLE=/absolute/path/to/pilot-bundle
python3.12 scripts/verify_pilot_bundle.py "$BUNDLE"
python3.12 -m venv .venv-castle-worker
python3.12 -m venv .venv-castle-host
.venv-castle-worker/bin/python -m pip install \
  "lancedb==0.40.0" "pyarrow==26.0.0" "PyYAML==6.0.3"
.venv-castle-worker/bin/python -m pip install --no-deps \
  "$BUNDLE/worker/prosaic_castle-3.4.2-py3-none-any.whl"
.venv-castle-host/bin/python -m pip install "b3-prosaic-runtime==0.9.8"
.venv-castle-host/bin/python -m pip install --no-deps \
  "$BUNDLE/adapter/b3_prosaic_memory_castle-0.1.0-py3-none-any.whl"
.venv-castle-worker/bin/python -m pip check
.venv-castle-host/bin/python -m pip check
.venv-castle-worker/bin/python -I scripts/ci_installed_smoke.py --component provider
.venv-castle-host/bin/python -I adapters/prosaic/scripts/wheel_smoke.py --host-only
```

The two smoke commands use synthetic data; they import no real sessions and
make no model calls. They do not turn memory on in an application. Run the
worker smoke from this checkout so its script can be found; Python isolated
mode ensures imports come from the installed environment. Legacy ingestion
still needs separately provisioned optional dependencies; FTS reading alone
does not promise a model-free import path. Current support is the host snapshot
API; model-facing tools require a separately qualified Runtime capability.

To rebuild candidates, install `build`, `hatchling`, `setuptools>=77` and `wheel`
in a build environment, then run for each of `.`, `adapters/prosaic` and
`packages/sue` with a fresh output directory:

```sh
SOURCE_DATE_EPOCH=1700000000 python scripts/ci_build_artifacts.py \
  --project . --output /absolute/new/worker-build
```

The builder checks the complete wheel payload against a rebuild from its sdist
and writes `qualification.json`. Compare its hashes to the pinned pilot
manifest; do not regenerate the manifest to hide a mismatch. Dependency locks
and native CI evidence are platform-specific. Do not infer a native Linux
qualification from local macOS or a PostgreSQL container alone.

Continue with the [real-world memory pilot](docs/pilot/README.md). Its sixteen
task prompts and blank private diary are preparation, not measured results.
SUE is not needed for the memory pilot and should remain uninstalled/disabled.

## Preserved fork and compatibility

Prosaic Castle is an independent local fork of Cognitive Castle at commit
`53637196cc215e9bd5b85b9253b3430b2781b884`. This checkout and its local artifacts
are not a release or publication of the original project. No backports or pushes
to the original project are part of this fork.

The distribution is `prosaic-castle`; its public import is `prosaic_castle` and
its provider command is `prosaic-castle-provider`. The initial fork retains the
qualified baseline version `3.4.2`, including the unchanged legacy module and
plugin versions. The distribution name and provenance distinguish this fork.

## Install and run

Use a dedicated virtual environment and install the locally built wheel:

```sh
python -m venv .venv
.venv/bin/python -m pip install /absolute/path/to/prosaic_castle-3.4.2-py3-none-any.whl
.venv/bin/prosaic-castle-provider --help
```

The base dependencies are LanceDB, PyArrow and YAML (plus `tomli` on Python
3.10). The default `memory-fts-v1` provider uses full-text retrieval and does
not require model downloads, sentence-transformers, spaCy, PyTorch or SOAR.
The worker requires an absolute palace path, a host-supplied config file,
namespace and allowed wings. It opens the palace read-only. It does not grant
itself permission to access any source or execute any workflow.

Dense retrieval remains available only by installing the `dense` extra and
explicitly choosing the legacy `memory-v1` profile. The `legacy` extra supplies
sentence-transformers and spaCy for retained historical tools. GPU acceleration
extras retain their upstream meaning. Optional extras do not authorize model
execution. Legacy commands and modes remain available with their original
behavior; use the Prosaic command for the deterministic provider profile.

## Import namespace compatibility

**Do not coinstall `prosaic-castle` and `cognitive-castle`.** Both distributions
own the `cognitive_castle` import namespace and the retained `castle*` scripts.
Package installers cannot safely arbitrate these overlapping files. Use a fresh,
separate virtual environment. The Prosaic command checks for installed
`cognitive-castle` distribution metadata and refuses to start if it is present.
Direct legacy imports and legacy commands retain upstream behavior and do not
enforce this guard. Unmanaged copied source directories can also shadow imports;
run installed artifacts outside source checkouts when qualifying an installation.

The legacy `cognitive_castle` namespace remains for API and on-disk compatibility.
Its engine identity is not silently relabeled. SUE remains a separately built
`cognitive-castle-sue` distribution with the `castle_sue` import. The canonical
SUE source, source manifest, build hook and Castle adapter API are preserved.

## Provenance and verification

The upstream [README](README.md), license, historic evidence and legacy tests
remain in this repository. Upstream branding in retained files identifies their
origin; it does not identify a new upstream release. See [fork provenance](docs/PROSAIC_FORK_PROVENANCE.md)
for the fork boundary and local build instructions.
