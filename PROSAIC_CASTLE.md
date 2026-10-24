# Prosaic Castle

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
