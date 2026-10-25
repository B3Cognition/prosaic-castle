# Real development memory pilot

This is a **pilot protocol and target**, not a report of observed usefulness.
No real sessions have been imported or evaluated by preparing these files.
Start with 10–20 actual development recall questions (the [task bank](tasks.md)
offers 16 prompts), one authorized owner and a small fixed corpus of that
owner's exported sessions or notes. Keep SUE review disabled separately.

Use the matching unpublished bundle identified by
[`pilot/candidate.json`](../../pilot/candidate.json) and the installation and
smoke instructions in [Prosaic Castle](../../PROSAIC_CASTLE.md). The manifest
identifies artifacts; it does not grant source access or establish pilot quality.
Do not substitute same-version wheels from historical bundles. Worker and host
use separate environments; never coinstall `cognitive-castle` with
`prosaic-castle`. This pilot does not publish packages to PyPI.

## Prepare private inputs

Keep all real exports, corpus inventories, questions, answers, snapshots,
palaces and diary entries **outside every Git checkout** in a private local
directory. The repository contains only blank/example templates. Do not upload
pilot data to the intended `B3Cognition/prosaic-castle` repository, CI artifacts,
issues or PRs. Repository visibility is a separate setup decision and is not a
privacy control for pilot data.

Choose only files the owner is authorized to use for this purpose. Permission to
set up this repository or run a pilot is not blanket permission for a colleague's
conversation, customer material, credentials or third-party personal data.
Exclude or redact those before making the frozen corpus; preserve the private
original separately if its retention is authorized. Record the redaction and
its effect on recall. Do not add capture hooks or automatic collection.

1. Copy [corpus.example.json](../../pilot/corpus.example.json) and
   [query.example.json](../../pilot/query.example.json) to the private directory.
   These are manual records, not input formats accepted by a product CLI.
2. Inventory the exact authorized export/note bytes with relative source paths,
   SHA-256, export time, covered dates, owner, source system and authorization.
   Record omitted material and known gaps. Freeze a read-only source copy and
   assign a corpus ID. Never edit it in place to improve a result.
3. Select the questions and write the expected source paths, exact supporting
   spans/quotes and target answers **before searching with either method**.
   Include expected abstention for questions unsupported by this corpus. Seal
   this private question/expectation file with its timestamp and SHA-256 in the
   diary before retrieval. Keep it hidden while answering where practical.
4. Import only that copy through an existing, separately authorized Castle
   import operation. Record the exact command, import environment, installed
   package versions, config identity, model prerequisites, time, warnings,
   failures and manual work. This guide performs no import. Legacy import may
   require separate optional NLP/embedding dependencies; it is not a promise
   that the lean FTS reader imports sessions without models.
5. Inventory the imported records and mapping back to the source manifest.
   If the importer drops/transforms a source, record it as import coverage loss;
   do not silently exclude that question from the evaluation. Freeze a private
   copy of the populated palace, config and prepared index for this pilot.
   Record their file identities after preparation, plus the worker fingerprint.

Use explicit operator preparation on that private pilot palace, not a live
working store. Replace the paths and namespace first:

```sh
.venv-castle-worker/bin/castle provider prepare \
  --palace /absolute/private/pilot/palace \
  --namespace pilot-owner-project \
  --config-dir /absolute/private/pilot/castle-config
```

Preparation can create an FTS index and provider identity. It must complete
before the palace snapshot is fixed. Do not change sources or indexes during
the main comparison. A correction becomes a new corpus version and a separate
run; keep the original failure evidence.

## Use the existing host API

This pilot uses host `health`, `search`, `fetch` and frozen `snapshot` APIs.
It does not grant an agent memory tools or make any model call. Model-facing
`memory_tools()` is a separate capability-gated path requiring a separately
qualified Runtime with `custom_tool_errors_v1` and public `ToolExecutionError`.
Do not infer its availability from a successful host snapshot.

After installation, start `.venv-castle-host/bin/python` from outside source
checkouts and use the following existing API. Replace every placeholder with
the private, host-chosen binding and the prewritten query. The worker Python
must be the venv's own absolute `bin/python` path, even if it is a symlink.

```python
import json
from pathlib import Path
from time import perf_counter
from prosaic_memory_castle import CastleMemoryProvider, WorkerCommand

provider = CastleMemoryProvider(
    WorkerCommand(("/absolute/worker-venv/bin/python", "-I", "-m",
                   "prosaic_castle.provider_worker")),
    palace_path="/absolute/private/pilot/palace",
    config_path="/absolute/private/pilot/castle-config/config.json",
    namespace="pilot-owner-project", allowed_wings=("project",),
    profile="memory-fts-v1", recency_boost=False,
)
started = perf_counter()
health = provider.health()
startup_seconds = perf_counter() - started
assert health["profile"] == "memory-fts-v1"
assert health["recency_boost"] is False
started = perf_counter()
result = provider.search("YOUR PREWRITTEN QUERY", limit=5)
search_seconds = perf_counter() - started
print(json.dumps(result, indent=2))  # Inspect privately, including provenance.
```

Record raw FTS rank and scores; do not rerank or apply recency boosts. Dense,
graph/SOAR paths and SUE are outside this comparison. `memory-fts-v1` with
`recency_boost=False` is the fixed retrieval policy, not a claim of superior
ranking. A zero-hit result is evidence of no eligible hit, not of no event.

Select actual record IDs from the displayed result, then fetch and freeze them.
Do not use the prewritten expected source to manufacture a retrieved hit.
Keep selection time as part of human task time. For example, replace the ID
below, then run in the same host session:

```python
chosen_ids = ["ACTUAL RECORD ID FROM RESULT"]
selected = [hit for hit in result["hits"] if hit["record_id"] in chosen_ids]
assert len(selected) == len(set(chosen_ids)) == len(chosen_ids)
expected = {hit["record_id"]: {
    "text_sha256": hit["text_sha256"], "revision": hit["revision"]
} for hit in selected}
started = perf_counter()
slices = [provider.fetch(record_id) for record_id in chosen_ids]
fetch_seconds = perf_counter() - started
started = perf_counter()
bundle = provider.snapshot(chosen_ids, expected=expected)
snapshot_seconds = perf_counter() - started
provider.close()
payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
with Path("/absolute/private/pilot/q01.snapshot.json").open("x", encoding="utf-8") as out:
    out.write(payload)
```

Use a private directory with owner-only access before running this example.
Always close the provider after an error too (`try/finally` or its context
manager in an application). `fetch` defaults to an 8,000-character slice;
inspect `complete`/`next_start_char` and request subsequent slices if needed.
The snapshot preserves exact full selected text within its configured size
limit. A changed revision/hash or oversized bundle is a failed capture; do not
silently relax it. Record all failures and the domain error code privately.
Save the raw search result, fetched slices, health, timings and snapshot digest
with the query record. Cite original source IDs, record IDs, wings, revisions,
text digests and exact supporting spans in the human answer. Keep query scope
fixed by the trusted host; it is never supplied by a model or source text.

## Compare on the same corpus and question

Use a baseline of the developer's ordinary manual file search/browsing over
the frozen exported files, for example `rg -n -i -- "search phrase"
/absolute/private/pilot/exports`. Save the actual terms and file references.
Give both methods the same question, authorized source scope, source cutoff,
time cap and answer requirements. Neither may use the live web, a current
session store or files outside this frozen corpus for its historical answer.
Current repository checks can be recorded separately as freshness checks.

Agree a task cap (suggested target: five minutes per method) and alternate
which method goes first across tasks. Record order, prior familiarity and any
carryover: one developer answering twice learns from the first attempt, so this
small paired pilot is descriptive, not a blinded causal experiment. Do not
show the second method the first answer. A second authorized reviewer can score
answers against the sealed expectations where feasible; do not share sources
with a reviewer without source authorization.

For each method, preserve the first answer, elapsed human time, retrieved or
opened evidence, missing evidence, corrections and final usefulness judgment.
Separate cold startup, warm search, fetch/snapshot and end-to-end time. Measure
startup/import/configuration friction separately from query speed. Keep empty,
unavailable, timeout and scope errors in the denominator. Wrong, stale and
conflicting evidence must be visible even if the final answer is correct.
Usefulness is a human rating: 0 = unusable, 1 = mostly rework, 2 = helpful with
checking, 3 = directly useful with correct provenance. Also record whether the
answer would have changed a real development action and whether it would have
caused a wrong action. Do not collapse safety failures into an average score.

## Check unavailable memory and frozen resume

Perform these as separately labeled operational checks after the fixed-corpus
comparison. Use a disposable copy; never mutate the frozen reference palace.

- Capture and persist a selected bundle with its digest and source expectations.
  Close the provider, make its test binding unavailable, and record that new
  host reads fail explicitly. An optional-memory host must label unavailable;
  a required-memory host must block. Empty is a different status. Neither is
  permission to invent history.
- Resume from the **same saved bundle bytes** under the host's existing owner,
  revision and deadline policy. Compare saved bytes/digest before and after;
  do not rerun search, fetch or snapshot to replace evidence. Native execution
  can receive the saved bundle as ordinary assignment data; that grants no
  additional tool access. This guide does not start a model-backed workflow.
- If a qualified host workflow is available, use its documented pause/resume
  path and retain its receipts. Without that host, label workflow resume
  **not exercised**: reloading a JSON file proves persistence only. The bundled
  smoke uses synthetic evidence and cannot establish real-world usefulness.
- Optionally change a source only in the disposable copy. Record that a new
  capture may see the new revision while the accepted snapshot remains the old
  evidence. Use a new run/corpus ID for intentional refresh, retaining both.

## Completion and stop targets

Set or adjust these **before retrieval**, then record the decision in the
[pilot diary](diary-template.md). They are proposed targets, not passed gates:

- Complete 10–20 prewritten real questions; suggested start: 16, including a
  conflict, a stale/superseded fact, a missing-source question and a scope check.
  Preserve paired baselines and every unsuccessful attempt.
- Require exact provenance for every material accepted historical claim, zero
  cross-owner/scope disclosures, zero silent source replacement on resume and
  explicit unavailable/required-memory handling in the host actually tested.
- Suggested usefulness target: at least 75% of memory answers score 2 or 3,
  no increase in materially wrong answers over baseline, and median human task
  time no worse than baseline. Report task counts and individual exceptions;
  this sample does not establish population-level improvement.
- Record whether setup fits an agreed budget (suggested: one hour of operator
  work after artifacts are available) and what interrupted ordinary work.
  Native platform coverage, import cost and cold latency remain explicit.
- Stop immediately for unauthorized content exposure, cross-scope reads,
  mismatched artifact/source identities or replaced frozen evidence. Preserve
  private failure evidence and disable new memory captures while investigating.
  Stop or revise the pilot for repeated stale/conflicting advice, poor coverage,
  unresolved startup friction or lack of usefulness; do not hide failed tasks.

Finish with a human decision: continue with this limited scope, revise with a
new version, or leave memory disabled. State unmet targets and missing data.
Any public summary must be separately approved and contain no private source
text, identifiers or paths. No automatic deployment, publication or promotion
follows a completed diary.

SUE remains experimental, independently disabled and outside these memory
ratings. The Lab's `docs/verification/sue-canonical-critic-2026-10-25.md` retains
the current evidence: no incremental review-quality benefit is demonstrated,
and experimental generation changes are not qualified for adoption. This pilot
does not change the protected existing canonical critic/author workflow.
