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
| `dist/cognitive_castle_sue-0.1.0-py3-none-any.whl` | 45,838 | `41233ac7dfc999b64a7d83c5391f94fcf4a37a51ca44f6dbd48f8235ca2b497e` |
| `dist/cognitive_castle_sue-0.1.0.tar.gz` | 46,725 | `c4b18b0acb66a890f3d8664c536640ea50ffaf3bc5e6cb61b541942ae16255c6` |

Rebuilt-sdist wheel is byte-identical to the direct wheel. Repeated direct wheel
and sdist builds are also byte-identical. The engine identity digest returned by
`capabilities()` is `7b14272b3720261d71a472aadaa8b6a23fa8ec0e07f07c7a4c23aa75a887b892`.
It hashes the exact `SOURCES.json` bytes; the capability response additionally
returns and verifies all ten canonical resource hashes.

Build interpreter: `/private/tmp/castle-release-build-env-20261024/bin/python`,
Python 3.12.15; build 1.6.1, hatchling 1.32.4, packaging 26.3. Runtime metadata
declares MIT, Python >=3.10, no dependencies and no entry points.

## Verification

TDD began with the missing standalone package assertion failing before package
implementation. Final focused command:

```sh
/private/tmp/castle-release-build-env-20261024/bin/python -m pytest packages/sue/tests tests/test_brain_engine.py -q
```

115 passed: 69 additive packaging/differential checks plus 46 unchanged canonical
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

Repository-wide `ruff check .` and `ruff format --check .` passed (296 files).
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

An initial diagnostic used the default missing model cache and restricted process
access; it failed existing model/resource tests and was interrupted. Its complete
`main.log` and `main.xml` remain retained beside the successful qualified logs.
The corrected run changed only environment/cache/process access, no assertions,
timeouts, source files or policy gates.

All logs, clean environments, rebuilt source and artifacts are retained under
`/private/tmp/castle-sue-qualification-20261024/`. A ten-process local footprint
observation found median import plus capability verification 60.7 ms and maximum
process RSS 23,511,040 bytes on macOS arm64 Python 3.12.15. These measurements
include Python and are observations, not performance guarantees. The package
owns no session storage, lifetime policy, provider process or background work;
the host owns those boundaries. Scripted evidence does not establish SUE's
usefulness on live requirements or certify factual/implementation correctness.
