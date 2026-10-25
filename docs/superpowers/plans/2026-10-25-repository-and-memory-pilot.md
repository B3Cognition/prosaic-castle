# Repository and memory pilot implementation plan

> Execution: inline using executing-plans, with disjoint CI and documentation
> tasks authorized by AGENTS.md; one fresh final whole-change review.

Goal: establish B3Cognition/prosaic-castle with three tested optional packages,
non-publishing CI, and a reproducible real-world memory pilot.

Architecture: Castle owns scoped read-only retrieval and exact evidence;
Runtime owns execution/usage; Harness owns state/receipts/resume; the consumer
owns authorization and pilot assessment. SUE stays a separate experimental
engine. Existing legacy modes and upstream provenance remain intact.

Tech: Python, LanceDB FTS, independent worker/host environments, GitHub Actions.
Requirements: user request 2026-10-25 and PROSAIC_CASTLE.md boundaries.

Constraints: raw FTS default; dense/recency opt-in; defaults off; no SOAR/model
execution in provider; no PyPI/tag/release; no real sessions or inference during
pilot preparation; no modified historical archives or unknown reservations.

Review focus: installed/source identity, worker/adapter scope errors, synthetic
vs actual pilot evidence, inherited GitHub publishing hooks, private source data
leaking into the new repository, native architecture qualification honesty.

1. Baseline: run existing supervised full suite and isolated supervision lane;
   inventory aef05c5 lineage and exact prior worker/adapter/SUE wheel payloads.
2. Consolidation: build all wheel/sdists; rebuild and compare member payloads;
   source-isolated install and smoke each optional component. Preserve versions
   and old artifacts; add pilot/candidate.json with hashes/provenance/defaults.
3. CI: retain legacy tests/coverage; add native Linux AMD64/ARM64 installed
   package smoke and artifact retention, no publication. Verify YAML/scripts and
   actual behavior locally. Fix actual CI failures rather than skipping checks.
4. Pilot: docs/pilot guide, task and observation templates, same-corpus baseline,
   frozen source identity and fallback/resume instructions. No unapproved import.
5. Repository: create new B3Cognition repository with selected visibility,
   preserve source history, push reviewed branch/default branch only to new
   remote; run exact-head CI and inspect every result. No upstream mutation.
6. Evidence: independent review, complete checks, immutable evidence archive and
   verification report. Identify actual real-world pilot as pending user corpus.

Detailed decisions/results live in the preserved execution ledger under
/private/tmp/prosaic-castle-repo-20261025; no prior qualification claim is replaced.
