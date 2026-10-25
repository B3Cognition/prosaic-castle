"""Frozen hand vectors and retained-bridge comparisons; no simulated SML claim."""

import builtins
from copy import deepcopy
from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest


NOW = datetime(2026, 10, 23, tzinfo=timezone.utc).timestamp()
RULES = Path(__file__).parents[2] / "cognitive_castle/rules/castle-boost.soar"


def api():
    # Keep missing implementation as an ordinary assertion failure for watched RED.
    from cognitive_castle import __path__

    assert (Path(next(iter(__path__))) / "prosaic_boosts.py").exists(), "shipped policy absent"
    return importlib.import_module("cognitive_castle.prosaic_boosts")


def test_four_shipped_rules_compound_without_mutation_or_environment(monkeypatch):
    boost = api()
    monkeypatch.setenv("CASTLE_PROJECT", "untrusted")
    hits = [
        {
            "id": "all",
            "score": 0.8,
            "wing": "trusted",
            "room": "decisions",
            "created_at": "2026-10-22T00:00:00Z",
            "entity_match": True,
            "nested": {"x": []},
        }
    ]
    frozen = deepcopy(hits)
    result = boost.apply_shipped_boosts(
        hits, query="decision about storage", project="trusted", now=NOW
    )
    assert result[0]["score"] == pytest.approx(1.86875)
    assert result[0]["soar_tags"] == ["recency-boost", "same-project", "entity-match", "type-match"]
    assert result[0]["score_pre_soar"] == 0.8
    assert result[0]["boost_policy_version"] == "castle-shipped-v1"
    assert len(result[0]["boost_rules_sha256"]) == 64
    result[0]["nested"]["x"].append("changed")
    assert hits == frozen
    assert boost.apply_shipped_boosts(
        hits, query="decision about storage", project="trusted", now=NOW
    )[0]["score"] == pytest.approx(1.86875)


@pytest.mark.parametrize(
    "date,want",
    [
        (None, 1.0),
        ("bad", 1.0),
        (42, 1.0),
        ("2026-10-16T00:00:00Z", 1.0),
        ("2026-10-16T00:00:01Z", 1.25),
        ("2026-10-24T00:00:00Z", 1.25),
        ("2026-10-16T02:00:00+02:00", 1.0),
    ],
)
def test_recency_boundary_invalid_future_and_offset(date, want):
    result = api().apply_shipped_boosts([{"score": 1.0, "created_at": date}], now=NOW)
    assert result[0]["score"] == want


@pytest.mark.parametrize(
    "room,query",
    [
        ("decisions", "decision about x"),
        ("preferences", "preferred choice"),
        ("milestones", "shipped feature"),
        ("problems", "bug"),
        ("emotional", "feeling"),
    ],
)
def test_room_aliases(room, query):
    assert (
        api().apply_shipped_boosts([{"score": 1.0, "room": room}], query=query, now=NOW)[0]["score"]
        == 1.25
    )


def test_signed_rank_basis_includes_unboosted_tail_and_only_first_fifty_are_eligible():
    hits = [{"id": str(i), "score": -i, "entity_match": True} for i in range(52)]
    result = api().apply_shipped_boosts(hits, now=NOW)
    assert result[0]["score"] == 1.3
    assert result[49]["score"] == pytest.approx(3 / 52 * 1.3)
    assert result[50]["score"] == 2 / 52
    assert result[51]["score"] == 1 / 52
    assert result[51]["soar_tags"] == []
    assert result[51]["raw_relevance_score"] == -51
    assert result[51]["adjustment_basis"] == "rank-base-v1"
    assert hits[0]["score"] == 0


def test_signed_scores_untouched_when_only_tail_matches():
    result = api().apply_shipped_boosts(
        [{"id": str(i), "score": -1.0} for i in range(50)]
        + [{"id": "tail", "score": -2.0, "entity_match": True}],
        now=NOW,
    )
    assert [h["score"] for h in result] == [-1.0] * 50 + [-2.0]


def test_wrapper_uses_tuple_score_filed_at_and_stable_conditional_sort():
    boost = api()
    rows = [
        (1.0, {"id": "a", "score": 99}),
        (1.25, {"id": "b", "score": 99}),
        (1.0, {"id": "c", "metadata_json": json.dumps({"filed_at": "2026-10-22T00:00:00Z"})}),
    ]
    frozen = deepcopy(rows)
    result = boost.apply_shipped_to_reranked(rows, now=NOW)
    assert [row["id"] for _, row in result] == ["b", "c", "a"]
    assert [score for score, _ in result] == [1.25, 1.25, 1.0]
    assert rows == frozen
    # Without tags, incoming order survives even if scores aren't ordered.
    assert [
        score
        for score, _ in boost.apply_shipped_to_reranked(
            [(0.1, {"id": "a"}), (0.9, {"id": "b"})], now=NOW
        )
    ] == [0.1, 0.9]


@pytest.mark.parametrize(
    "hits",
    [
        [{"id": "same", "score": 1.0}, {"id": "same", "score": 0.9, "entity_match": True}],
        [
            {"wing": "w", "room": "r", "source_file": "f", "score": 1.0},
            {"wing": "w", "room": "r", "source_file": "f", "score": 0.9},
        ],
    ],
)
def test_duplicate_legacy_identities_are_rejected_before_ambiguous_rule_attribution(hits):
    with pytest.raises(ValueError, match="duplicate"):
        api().apply_shipped_boosts(hits, now=NOW)


def test_custom_rules_rejected_even_empty_input_and_exact_shipped_copy_allowed(tmp_path):
    boost = api()
    custom = tmp_path / "custom.soar"
    custom.write_bytes(RULES.read_bytes() + b"\n")
    with pytest.raises(boost.UnsupportedRulesError, match="custom"):
        boost.apply_shipped_boosts([], now=NOW, rules_path=custom)
    custom.write_bytes(RULES.read_bytes())
    assert boost.apply_shipped_boosts([], now=NOW, rules_path=custom) == []
    with pytest.raises(boost.UnsupportedRulesError):
        boost.apply_shipped_boosts([], now=NOW, rules_path=tmp_path / "missing")


def test_now_is_explicit_and_finite():
    boost = api()
    with pytest.raises(TypeError):
        boost.apply_shipped_boosts([])
    with pytest.raises(ValueError):
        boost.apply_shipped_boosts([], now=float("nan"))


def test_no_sml_import_or_legacy_dependency(monkeypatch):
    boost = api()
    real_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        assert "sml" not in name.lower() and "soar_bridge" not in name
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    importlib.reload(boost)
    assert (
        boost.apply_shipped_boosts([{"score": 1.0, "entity_match": True}], now=NOW)[0]["score"]
        == 1.3
    )


class OracleWME:
    """Input WME sink; output below is a frozen rule-output oracle, not Soar."""

    def CreateIdWME(self, _):
        return OracleWME()

    def CreateStringWME(self, *args):
        pass

    CreateFloatWME = CreateStringWME
    CreateIntWME = CreateStringWME


class OracleAgent:
    def GetInputLink(self):
        return OracleWME()

    def Commit(self):
        pass

    def RunSelf(self, _):
        pass

    def DestroyWME(self, _):
        pass

    def ExecuteCommandLine(self, _):
        return """(M1 ^id all ^boost-tag recency-boost ^boost-tag same-project
 ^boost-tag entity-match ^boost-tag type-match)
(M2 ^id recent ^boost-tag recency-boost)
(M3 ^id none)
"""


@pytest.mark.parametrize("scores", [[0.8, 0.7, 0.6], [0, -0.1, -0.2]])
def test_frozen_rule_output_oracle_matches_retained_bridge(monkeypatch, scores):
    from cognitive_castle import soar_bridge as legacy

    boost = api()
    legacy._reset_for_test()
    monkeypatch.setenv("CASTLE_PROJECT", "trusted")
    monkeypatch.setattr(legacy.time, "time", lambda: NOW)
    monkeypatch.setattr(legacy, "_load_sml", lambda: object())
    monkeypatch.setattr(legacy, "_get_agent", lambda *args: OracleAgent())
    hits = [
        {
            "id": "all",
            "score": scores[0],
            "wing": "trusted",
            "room": "decisions",
            "entity_match": True,
            "created_at": "2026-10-22T00:00:00Z",
        },
        {"id": "recent", "score": scores[1], "created_at": "2026-10-24T00:00:00Z"},
        {"id": "none", "score": scores[2], "created_at": "bad"},
    ]
    cfg = SimpleNamespace(palace_path="oracle", soar_rules_path=str(RULES))
    old = legacy.apply_soar_boosts(deepcopy(hits), cfg, query="decision about x")
    new = boost.apply_shipped_boosts(hits, query="decision about x", project="trusted", now=NOW)
    for expected, actual in zip(old, new):
        for key in (
            "score",
            "score_pre_soar",
            "soar_boost",
            "soar_tags",
            "raw_relevance_score",
            "adjustment_basis",
        ):
            assert actual.get(key) == expected.get(key)
    legacy._reset_for_test()


@pytest.mark.parametrize(
    "zone,want", [("UTC", 1.0), ("Europe/Prague", 1.0), ("America/New_York", 1.25)]
)
def test_naive_timestamp_preserves_legacy_local_timezone(monkeypatch, zone, want):
    from cognitive_castle import soar_bridge as legacy

    boost = api()
    monkeypatch.setenv("TZ", zone)
    time.tzset()
    try:
        result = boost.apply_shipped_boosts(
            [{"score": 1.0, "created_at": "2026-10-16T00:00:00"}], now=NOW
        )
        assert result[0]["score"] == want
        assert (legacy._compute_age_seconds("2026-10-16T00:00:00", NOW) < 604800) == (want == 1.25)
    finally:
        monkeypatch.undo()
        time.tzset()


def test_inventory_reports_rule_hashes_and_config_locations_without_values(tmp_path):
    script = Path(__file__).parents[2] / "scripts/inventory_soar_rules.py"
    assert script.exists(), "read-only inventory absent"
    custom = tmp_path / "custom.soar"
    custom.write_text("sp {secret-production}\n")
    (tmp_path / "shipped.soar").write_bytes(RULES.read_bytes())
    (tmp_path / "settings.toml").write_text('soar_rules_path = "TOP-SECRET-PRIVATE-PATH"\n')
    (tmp_path / "notes.md").write_text("soar_rules_path discussion\n")
    ignored = tmp_path / ".git"
    ignored.mkdir()
    (ignored / "hidden.soar").write_text("ignored")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(completed.stdout)
    assert [(Path(row["path"]).name, row["kind"]) for row in report["rules"]] == [
        ("custom.soar", "custom"),
        ("shipped.soar", "shipped-exact"),
    ]
    assert [
        (Path(row["path"]).name, row["line"], row["key"]) for row in report["config_occurrences"]
    ] == [("settings.toml", 1, "soar_rules_path")]
    assert "TOP-SECRET" not in completed.stdout and "secret-production" not in completed.stdout
    assert {p: p.read_bytes() for p in before} == before


@pytest.mark.soar
def test_real_sml_gate_matches_shipped_policy_when_installed(monkeypatch):
    """Qualifies native SML only when this test executes rather than skips."""
    pytest.importorskip("Python_sml_ClientInterface", reason="real SML gate unavailable")
    from cognitive_castle import soar_bridge as legacy

    boost = api()
    legacy._reset_for_test()
    monkeypatch.delenv("CASTLE_SML_DISABLED", raising=False)
    monkeypatch.setenv("CASTLE_PROJECT", "trusted")
    monkeypatch.setattr(legacy.time, "time", lambda: NOW)
    hits = [
        {
            "id": "all",
            "score": 0.8,
            "wing": "trusted",
            "room": "decisions",
            "entity_match": True,
            "created_at": "2026-10-22T00:00:00Z",
        },
        {"id": "none", "score": 0.7},
    ]
    cfg = SimpleNamespace(palace_path="real-sml-policy-gate", soar_rules_path=str(RULES))
    try:
        old = legacy.apply_soar_boosts(deepcopy(hits), cfg, query="decision about x")
        new = boost.apply_shipped_boosts(hits, query="decision about x", project="trusted", now=NOW)
        assert set(old[0]["soar_tags"]) == {
            "recency-boost",
            "same-project",
            "entity-match",
            "type-match",
        }
        for expected, actual in zip(old, new):
            assert actual["score"] == pytest.approx(expected["score"])
            assert set(actual["soar_tags"]) == set(expected["soar_tags"])
    finally:
        legacy._reset_for_test()
