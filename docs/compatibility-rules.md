# Shipped rule compatibility

`cognitive_castle.prosaic_boosts.apply_shipped_boosts` is an explicit opt-in
Python policy for the four retained `castle-boost.soar` productions. It does
not import SML, execute productions, read the current time, or infer the project
from environment variables. Callers supply trusted `now` (finite Unix seconds)
and `project` (default `"default"`), plus the original query. Searcher, legacy
SOAR modules, configuration and default provider profiles remain independent.

```python
from cognitive_castle.prosaic_boosts import apply_shipped_boosts

boosted = apply_shipped_boosts(
    hits, query="decision about storage", project="my-project", now=1792713600.0
)
```

The policy returns deep copies in incoming order. It retains legacy audit
fields `score_pre_soar`, `soar_boost`, and `soar_tags` for comparisons. Their
names do not indicate that Soar executed. `boost_policy_version` is
`castle-shipped-v1`; `boost_rules_sha256` pins the recognized productions.
Duplicate legacy memory identities raise `ValueError` before score processing.
Identity uses `id`, falling back to `wing/room/source_file` exactly as the
retained bridge does. The provider requires unique drawer IDs; rejecting an
ambiguous caller avoids the bridge's lossy tag attribution through a shared key.

| Tag | Condition | Multiplier |
| --- | --- | --- |
| `recency-boost` | Age from `created_at` is strictly less than seven days | 1.25 |
| `same-project` | Hit `wing` exactly matches explicit `project` | 1.15 |
| `entity-match` | Hit `entity_match` is truthy | 1.30 |
| `type-match` | Query intent matches normalized drawer `room` | 1.25 |

Tags compound in table order; the product retains the legacy `[0.1, 10.0]`
clamp. Only the first 50 input hits are eligible. The room aliases are
`decisions` → `decision`, `problems` → `problem`, `preferences` → `preference`,
and `milestones` → `milestone`; singular forms and `emotional` also work.
The existing English-only query classifier and its first-match precedence
are reused.

Missing, invalid and non-string dates are ineligible for recency. Dates at
exactly seven days are ineligible. Future dates clamp to zero age and qualify.
Offsets and `Z` suffixes are honored. **Naive timestamps retain the legacy
host-local timezone interpretation**, despite the old helper's UTC wording.
Use timezone-aware timestamps for portable replay; changing naive timestamps
to UTC requires a future policy version and explicit migration. Tests freeze
UTC, Europe/Prague and America/New_York to cover this compatibility behavior.

When any incoming score is nonpositive and at least one eligible tag fires,
all hits use `rank-base-v1`: incoming rank supplies a positive base from 1 to
`1 / count`, including hits after 50. The original signed score is preserved
as `raw_relevance_score`. Without a firing tag, signed scores remain unchanged.
Tail hits receive neutral audit fields using the retained bridge's
`setdefault` behavior.

`apply_shipped_to_reranked` adapts `(score, row)` tuples without mutating them.
The tuple score is authoritative; missing `created_at` is promoted from
`metadata_json.filed_at`. A non-neutral multiplier triggers descending score
sorting, preserving input order on ties. Without a multiplier it preserves
the incoming order even when scores are not ordered.

## Custom rules are retained and rejected explicitly

The retained `soar_bridge.py`, `.soar` files, custom-rule configuration and
legacy tests remain available. This Python policy does not interpret arbitrary
SOAR, learn productions, or silently ignore custom configuration. `rules_path`
is optional; any supplied file must have the exact shipped bytes. Modified,
missing and unreadable files raise `UnsupportedRulesError`, including for an
empty hit list. Callers with a configured rule path must pass it explicitly;
the policy deliberately does not resolve ambient environment configuration.

The pinned SHA-256 is
`2f733306d6e5464cd2d63a1b639650a9730953b6217469d054fd05ce076821f9`.
An exact copy at another path is accepted. Even a comment or whitespace change
requires a new audited policy or the retained SOAR route. The hash is a local
identity check against reviewed shipped bytes, not an authenticity signature.

Run the read-only local inventory with:

```sh
python scripts/inventory_soar_rules.py
python scripts/inventory_soar_rules.py --root /path/to/one --root /path/to/two
```

Its defaults cover the five authorized workspaces. JSON reports rule paths,
SHA-256 hashes, exact-shipped/custom classifications, and config key locations
without emitting rule contents or configuration values. It scans `.soar` and
common configuration formats, including `.env` files; it excludes repository
metadata, virtual environments, dependency caches, and symlinks. It reports
unreadable paths and absent roots. This is a local discovery aid; it does not
claim to inventory deployment hosts or dynamically generated environment
configuration. It never executes discovered manifests or rules.

## Verification boundary

`tests/prosaic_fork/test_boosts.py` has hand-checked score/date/rank/tail/tie
vectors and compares frozen rule-output strings through the retained bridge's
real input, output parser and score application. The oracle replaces only the
external kernel; it does **not** demonstrate production loading or real Soar
rule firing. It also checks nonmutation, repeated calls, explicit context,
custom rejection, and execution with SML/bridge imports forbidden.

The separate `test_real_sml_gate_matches_shipped_policy_when_installed` loads
the actual retained productions through SML and requires all four tags plus
matching scores. Its skip means the real SML equivalence gate remains unmet.
The local verification run had **53 passed, 11 skipped** across this file,
`test_soar_bridge.py`, `test_soar_bridge_failures.py`, and `test_query_intent.py`;
SML bindings were absent. Native Soar execution, platform qualification and
custom production equivalence are not claimed by that result.
