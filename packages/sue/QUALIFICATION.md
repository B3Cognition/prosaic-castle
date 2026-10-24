# Lightweight SUE package qualification

Date: 2026-10-24. Unpublished candidate; no live provider calls, remote push,
publication or merge authorized by this qualification.

Canonical source revision: `58f4242080212c2bebcca0c685af0f5e1090aa94`.
The change adds only `packages/sue/`; existing Castle production code, dependencies,
versions, tests, policy resources and selected r7 release archives are unchanged.
Every mapped canonical file was compared byte-for-byte with the direct wheel and
checked against `source-manifest.json`. No reducer or lens copy is maintained here.

## Candidate identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `dist/cognitive_castle_sue-0.1.0-py3-none-any.whl` | 47,924 | `fdfb1690505a85b4cbb49e2b4845c91e318efe945068a379ac230c3b4ebf9b75` |
| `dist/cognitive_castle_sue-0.1.0.tar.gz` | 49,416 | `8846789e9c8534a33dd73807bf6e34543b64b24c1ace26ead05d503515a5cf8a` |

Rebuilt-sdist wheel is byte-identical to the direct wheel. Repeated direct wheel
and sdist builds are also byte-identical. The engine identity digest returned by
`capabilities()` is `bbde4669d1eb069dcb8c72e121cd08be4ca953b349f9243b9e650e0d1b596f0b`.
It hashes the UTF-8 JSON representation of the complete `files` mapping with
sorted keys and compact separators. Its thirteen hashes cover the ten canonical
resources plus `SOURCES.json`, `__init__.py` and `_loader.py`. The separate
`sourceManifestDigest` remains
`7b14272b3720261d71a472aadaa8b6a23fa8ec0e07f07c7a4c23aa75a887b892`;
it hashes the exact unchanged canonical `SOURCES.json` bytes.

Build interpreter: `/private/tmp/castle-release-build-env-20261024/bin/python`,
Python 3.12.15; build 1.6.1, hatchling 1.32.4, packaging 26.3. Runtime metadata
declares MIT, Python >=3.10, no dependencies and no entry points.

## Verification

TDD began with the missing standalone package assertion failing before package
implementation. Final focused command:

```sh
/private/tmp/castle-release-build-env-20261024/bin/python -m pytest packages/sue/tests tests/test_brain_engine.py -q
```

121 passed: 75 additive packaging/differential checks plus 46 unchanged canonical
engine checks. The new lane checks all nine lenses against the existing public
Castle engine for success, silence, partial answers, revision, exhaustion,
invalid quotation and changed-claim rejection. It compares each accepted state,
error, question, schema and coverage projection. Existing source scenarios are
reused; installed engines are not monkey-patched.

Two fresh Python 3.12 virtual environments independently installed the direct
wheel and rebuilt wheel using ordinary `pip install --no-index <wheel>`.
Both `pip check` runs passed, and both environments contained only pip and
cognitive-castle-sue. `tests/standalone_smoke.py` passed in both: every lens reached
RESOLVED in seven accepted turns; invalid turns were rejected; import guards
blocked Castle and the heavy/model dependencies, while audit hooks blocked
network and process dispatch throughout import and pure API operations.
Tampered canonical build snapshots and tampered installed policy resources were
rejected. Both artifacts passed `twine check`.

Independent review found that upstream's bare script aliases originally allowed
the new and legacy distributions to share a runner, and a hostile preexisting
`sue_runner` alias could break import. Three new subprocess reproductions were
watched failing, then passing after adding package-local vendor import views.
Both import orders preserve the legacy aliases and load independent helpers
from their own paths; hostile bare aliases remain untouched and do not select
the standalone package's helpers. Pickle roundtrips and type-hint resolution
confirm qualified dataclass module registration. Python's actual global importer,
importlib spec factory and sys.modules object remain unchanged. The loader never
temporarily replaces global aliases or functions. Canonical source hashes remain
unchanged. Review additionally required binding the complete execution boundary
for resume: watched RED/GREEN tests show that modifying either the wrapper or
loader changes engine identity while preserving the canonical manifest digest.
Another test confirms identical execution identity from the rebuilt wheel.

The fixed artifacts were independently rebuilt and installed in two new clean
environments under `execution-identity-fix/`. Both passed `pip check`, all nine full
successful traces, import/dispatch guards, and hostile-alias/pickle smoke checks.
Only pip and cognitive-castle-sue are installed. Namespace RED/GREEN and focused
logs are retained alongside the earlier evidence; both prior candidate artifact
sets are preserved under `pre-namespace-fix-artifacts/` and
`namespace-fix-artifacts/`.

Repository-wide `ruff check .` and `ruff format --check .` passed (297 files).
Original CI launcher lanes ran serially with the existing full dependency
environment, offline cached models and separate coverage evidence:

```sh
HF_HOME=/private/tmp/castle-memory-model-cache HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
COVERAGE_FILE=/private/tmp/castle-sue-qualification-20261024/.coverage-qualified \
/private/tmp/castle-audit-20261023/bin/python scripts/run_ci_pytest.py \
  --timeout 600 --log /private/tmp/castle-sue-qualification-20261024/main-qualified.log \
  -- tests/ -q --ignore=tests/benchmarks --ignore=tests/test_memory_runtime.py \
  --ignore=tests/test_memory_api_integration.py --cov=cognitive_castle \
  --cov-report=term-missing --cov-fail-under=0 --durations=10 \
  -o faulthandler_timeout=60 --junitxml=/private/tmp/castle-sue-qualification-20261024/main-qualified.xml

HF_HOME=/private/tmp/castle-memory-model-cache HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
COVERAGE_FILE=/private/tmp/castle-sue-qualification-20261024/.coverage-qualified \
/private/tmp/castle-audit-20261023/bin/python scripts/run_ci_pytest.py \
  --timeout 120 --log /private/tmp/castle-sue-qualification-20261024/supervision-qualified.log \
  -- tests/test_memory_runtime.py tests/test_memory_api_integration.py -q \
  --cov=cognitive_castle --cov-append --cov-report=term-missing --cov-fail-under=85 \
  --durations=10 -o faulthandler_timeout=60 \
  --junitxml=/private/tmp/castle-sue-qualification-20261024/supervision-qualified.xml
```

Main: 2,518 passed, 11 skipped, 2 deselected, 1,346 existing deprecation/runtime
warnings in 88.76 seconds. Fresh-process supervision: 48 passed in 12.04 seconds.
Both supervisors exited zero; final coverage 85.30% passes the original 85% gate.
This is local macOS arm64 evidence, not a new cross-platform CI claim.
These broad lanes ran for the initial additive package. After the isolated
namespace and identity corrections, the 121-test focused lane and clean installation,
rebuild, source-byte equivalence, lint and artifact checks were rerun. Existing
Castle engine tests remain in the focused lane; canonical Castle code did not
change, so the broad lanes were not repeated solely for the private loader.

An initial diagnostic used the default missing model cache and restricted process
access; it failed existing model/resource tests and was interrupted. Its complete
`main.log` and `main.xml` remain retained beside the successful qualified logs.
The corrected run changed only environment/cache/process access, no assertions,
timeouts, source files or policy gates.

All logs, clean environments, rebuilt source and artifacts are retained under
`/private/tmp/castle-sue-qualification-20261024/`. A ten-process local footprint
observation of the final candidate found median import plus capability verification
60.7 ms and maximum process RSS 23,494,656 bytes on macOS arm64 Python 3.12.15.
These measurements include Python and are observations, not performance guarantees. The package
owns no session storage, lifetime policy, provider process or background work;
the host owns those boundaries. Scripted evidence does not establish SUE's
usefulness on live requirements or certify factual/implementation correctness.
