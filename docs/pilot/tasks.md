# Development recall task bank

Choose 10–20 **real** tasks from authorized development exports/notes. These 16
prompts are a starting point; they are not claims that the sources exist or that
Castle answered them. Replace bracketed details, scope and dates before sealing
the expectations. Avoid synthetic success stories in the real pilot totals.

For every task, create a private copy of
[`query.example.json`](../../pilot/query.example.json). Before either retrieval
method, write the expected source path(s), source hash, exact supporting span,
target answer and allowed uncertainty. Freeze the question and expectations
with the corpus ID, namespace, allowed wings, source cutoff and task time cap.
If no authorized source supports an answer, prewrite the expected abstention.
Record uncertainty in the ground truth instead of inventing a source.

| ID | Real question to instantiate | What the prewritten expectation must distinguish |
| --- | --- | --- |
| q01 | Why did we choose [database] for [component] during [date range]? | Decision rationale, decision date and recorded constraints versus current implementation. |
| q02 | Which alternatives to [chosen design] did we reject, and why? | Actual rejected alternatives and evidence; absence of mention is not rejection. |
| q03 | What did we already try for [specific bug], and what happened? | Attempted fixes, observed results and still-open explanations. |
| q04 | What exact steps reproduced [failure] in the earlier investigation? | Environment/version, reproduction sequence and limits on reproducibility. |
| q05 | Which compatibility constraint blocked [proposed refactor]? | Contract, affected consumer and explicit evidence of the constraint. |
| q06 | What did [migration] preserve, and what was intentionally deferred? | Agreed scope versus later assumptions or planned work. |
| q07 | What did [benchmark/test] actually demonstrate? | Measured result, fixture scope and exclusions; plans are not observations. |
| q08 | What was the agreed rollback or recovery procedure for [change]? | The documented procedure and prerequisites; do not execute it. |
| q09 | Which package/build artifact was qualified for [specific environment]? | Source/wheel identities and platform evidence versus a same-version candidate. |
| q10 | What remained unresolved when work on [issue] paused? | Open items, blockers and stale follow-ups rather than inferred completion. |
| q11 | Which earlier assumption about [behavior] was later corrected? | Original statement, dated correction and the evidence that superseded it. |
| q12 | Our notes disagree about [setting/decision]; what can we conclude? | Both conflicting sources, chronology, unresolved uncertainty and current verification needed. |
| q13 | Where is the recorded reason for [unfamiliar code pattern]? | Supporting explanation if captured; otherwise an honest source gap. |
| q14 | Did we decide [a fact absent from the frozen exports]? | Explicitly unsupported answer, no claim that the event never occurred. |
| q15 | What may this project recall about [similar issue in another owner/wing]? | Allowed evidence only; no disclosure from the intentionally excluded scope. Use authorized private fixtures for scope checks if real cross-owner data is not authorized. |
| q16 | What evidence should we resume with for [paused investigation]? | Exact frozen accepted sources, their age and unresolved points, not refreshed search results. |

Use real source dates and preserve disagreements. A question that requires
material omitted from the fixed corpus remains a recorded miss/coverage gap;
it must not disappear from the denominator. Questions added after inspecting
results belong to a later exploratory set, not this sealed comparison.
