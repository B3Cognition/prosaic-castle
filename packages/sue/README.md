# Castle SUE engine

`cognitive-castle-sue` 0.1.0 is an additive, MIT-licensed, standard-library-only
distribution of Castle's existing pure SUE engine. It requires Python 3.10+
and declares no runtime dependencies. Import it as `castle_sue`; it can coexist
with `cognitive-castle` without replacing that distribution or its modules.
This is an unpublished release candidate.

```python
import castle_sue

identity = castle_sue.capabilities()
state = castle_sue.initial_state("Only administrators may export.", lens="euthyphro")
prompt = castle_sue.question(state)
output_schema = castle_sue.schema(state)
# The host obtains an answer separately and supplies exact source lines:
# state, error = castle_sue.advance(state, answer, source_lines)
profile = castle_sue.coverage(state)
```

The five engine functions retain the canonical public `brain_engine` signatures
and state/validation semantics. `advance` returns a fresh accepted state, or the
unchanged state and an error code. Hosts own answering, source admission,
durable state, deadlines, approval, budgets and recovery. This package creates
no process, network connection, model, memory store, hook or background worker.
It has no CLI or entry points. Keep it outside a host's default-disabled import
path. SUE is a structured self-check, not independent verification: `RESOLVED`
means required dimensions of the current claim were examined, not truth or
implementation correctness. The nine lenses are available independently.

`capabilities()` returns `apiVersion: 1`, `schemaVersion: 2`,
`policyVersion: "2026-09-24"`, `lenses` and `engineIdentity`. Identity uses
`algorithm: "sha256"` and `files`, a mapping from package-relative resource names
to their SHA-256 hashes. It includes all canonical resources plus `SOURCES.json`,
the package wrapper `__init__.py`, and `_loader.py`. Its `digest` hashes UTF-8 JSON
of that complete mapping with sorted keys and compact separators (`,` and `:`).
`sourceManifestDigest` separately hashes the exact canonical `SOURCES.json` bytes.
Each call verifies pinned canonical resources and returns fresh data. Missing or
changed canonical resources fail closed. Wrapper or loader changes alter the
complete identity even when canonical policy bytes remain identical. A host
must retain and compare the full engine identity before resuming a frozen
review, alongside its exact wheel pin. This binds the canonical adapter, vendored
engine/policy, licenses, upstream provenance and package execution boundary.

## Canonical sources and builds

There is no manually maintained copy of the reducer or lenses here.
`source-manifest.json` pins the source revision, source paths, installed paths
and hashes. The Hatch custom hook reads the canonical repository files and
maps their exact bytes under `castle_sue`. The source archive includes those
same bytes under `_canonical/`; a rebuild uses that included snapshot instead
of reaching into any surrounding checkout. Both builds reject a hash mismatch.
The wheel includes Castle's MIT license, Echelon's MIT license and its pinned
`UPSTREAM.json` (commit `a4286d83427d03b1b1d019c98c68f5d2e0fac741`). All pinned
vendor files are retained for provenance, including the legacy transport
helpers; the public pure API never dispatches them.

The package-local loader executes these unchanged sources with qualified
`castle_sue._vendor.sue` module names. Its private module views route upstream's
standalone `sue_challenge` and `sue_runner` lookups into that namespace. It never
replaces Python's global importer, importlib functions or bare `sys.modules`
aliases, even temporarily. Castle and the standalone distribution can therefore
coexist in either import order; unrelated preexisting script aliases do not
select the package's engine helpers. Qualified module registration preserves
dataclass type-hint lookup and pickling.

```sh
python -m build --no-isolation --wheel --sdist packages/sue
python -m pytest packages/sue/tests -q
python -m venv /tmp/sue-check
/tmp/sue-check/bin/python -m pip install packages/sue/dist/cognitive_castle_sue-0.1.0-py3-none-any.whl
/tmp/sue-check/bin/python -m pip check
```

Build tooling requires `build` and `hatchling>=1.27`; these are build-only.
Set `SUE_BUILD_PYTHON` when the test interpreter lacks them. Packaging tests
compare direct and source-archive wheel payloads, qualify all nine lenses
against the unchanged public Castle engine with existing scripted scenarios,
reject invalid citations and changed claims, and block heavy imports and
network/process dispatch during pure operations. Differential qualification
from the repository uses the existing Castle test fixtures; it is not a runtime
dependency of the standalone distribution.
