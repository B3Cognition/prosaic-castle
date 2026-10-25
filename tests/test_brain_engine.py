"""Differential adapter tests use scripted answers, never an answering model."""

from dataclasses import asdict
from types import SimpleNamespace

import pytest

from cognitive_castle._vendor.sue import sue_dialectic as vendor

SOURCE = "Only administrators may export data.\nConsent must be current.\n"
CLAIM = "Administrators export with current consent."
TYPES = dict(
    DEFINE="definition",
    DISTINGUISH="distinction",
    CAUSE_OR_CRITERION="criterion",
    DIVIDE="case-split",
    COUNTEREXAMPLE="example",
    FOLLOW_CONSEQUENCE="consequence",
    TEST_OPPOSITE="consequence",
    REVISE="revision",
)


def answer(op, result=None, **changes):
    result = result or vendor.SUCCESS_RESULT[op]
    silent = result == "UNKNOWN"
    p = dict(
        answer="An attributed interpretation, requiring review.",
        verdict={"UNKNOWN": "SILENT", "INCOMPLETE": "PARTIAL", "CONFLICT": "CONTRADICTED"}.get(
            result, "SUPPORTED"
        ),
        answer_type=TYPES[op],
        evidence_lines=[] if silent else [1],
        claim=CLAIM if op in ("DEFINE", "REVISE") and not silent else None,
        test_result=result,
        evidence=[] if silent else [{"line": 1, "quote": SOURCE.splitlines()[0]}],
        premises=[]
        if silent
        else [{"statement": SOURCE.splitlines()[0], "kind": "stated", "evidence_lines": [1]}],
        witness=None,
        open_questions=[],
        addresses=[],
        revision_reason=None,
    )
    if result in ("FOUND", "POSSIBLE", "CONFLICT"):
        p["witness"] = dict(
            situation="An export request.",
            reading_a="Export allowed.",
            reading_b="Export forbidden.",
            why_incompatible="Opposite decisions for the same request.",
            lines_a=[1],
            lines_b=[1],
        )
    p.update(changes)
    return p


@pytest.mark.parametrize("lens", list(vendor.LENSES))
@pytest.mark.parametrize("scenario", ["success", "silence", "partial", "revision", "exhaustion"])
def test_reducer_matches_unchanged_vendor(monkeypatch, tmp_path, lens, scenario):
    from cognitive_castle import brain_engine as engine

    path = vendor.LENSES[lens]["path"]
    replies = [answer(op) for op in path]
    cap = 14
    if scenario == "silence":
        replies = [answer("DEFINE", "UNKNOWN")]
    elif scenario == "partial":
        replies = [answer("DEFINE", "INCOMPLETE"), answer("DISTINGUISH", "UNKNOWN")]
    elif scenario == "exhaustion":
        cap = 2
    elif scenario == "revision":
        prefix = list(path[: path.index("COUNTEREXAMPLE")])
        replies = [answer(op) for op in prefix] + [answer("COUNTEREXAMPLE", "FOUND")]
        replies += [
            answer(
                "REVISE",
                addresses=list(range(1, len(replies) + 1)),
                revision_reason="Retain role and consent.",
            )
        ]
        replies += [answer(op) for op in path if op != "DEFINE"]
    queue = iter(replies)

    def execute(_config, _prompt, validator, **_kw):
        validated = validator(next(queue))
        assert not isinstance(validated, vendor.v1.ParseFailure)
        return validated

    monkeypatch.setattr(vendor.v1, "execute_round", execute)
    spec = SimpleNamespace(lines=SOURCE.splitlines())
    turns, terminal, error = vendor.run_dialogue(None, spec, tmp_path, lens, CLAIM, cap)
    assert error is None
    state = engine.initial_state(CLAIM, lens=lens, max_turns=cap)
    for reply in replies:
        if state["terminal"]:
            break
        state, failure = engine.advance(state, reply, spec.lines)
        assert failure is None
    assert state["turns"] == [asdict(t) for t in turns]
    assert state["terminal"] == terminal
    assert engine.coverage(state) == vendor.depth_profile(turns, lens)


def test_invalid_reducer_does_not_mutate_input():
    from cognitive_castle import brain_engine as engine

    state = engine.initial_state(CLAIM)
    other, failure = engine.advance(state, {}, SOURCE.splitlines())
    assert failure and other == state and state["turns"] == []


def test_repeated_cycle_stops_without_claiming_missing_dimensions():
    from cognitive_castle import brain_engine as engine

    state = engine.initial_state(CLAIM, cycle_guard=True)
    for op, result in [('DEFINE','ESTABLISHED'), ('DISTINGUISH','INCOMPLETE'),
                       ('DIVIDE','ESTABLISHED'), ('DISTINGUISH','INCOMPLETE'),
                       ('DIVIDE','ESTABLISHED')]:
        assert state['operator'] == op
        state, error = engine.advance(state, answer(op, result), SOURCE.splitlines())
        assert error is None
    assert state['terminal'] == 'BOUNDED_STOP'
    assert state['turns'][-1]['stop_reason'] == 'repeated_cycle_no_progress'
    assert engine.coverage(state)['missing'] == [
        'DISTINGUISH','CAUSE_OR_CRITERION','COUNTEREXAMPLE',
        'FOLLOW_CONSEQUENCE','TEST_OPPOSITE']
    assert len(engine.coverage(state)['open_issues']) == 2
    assert engine.advance(state, {}, SOURCE.splitlines()) == (state, 'engine_terminal')


def test_cycle_guard_retains_legacy_and_new_information():
    from cognitive_castle import brain_engine as engine

    legacy = engine.initial_state(CLAIM)
    guarded = engine.initial_state(CLAIM, cycle_guard=True)
    assert 'cycle_guard' not in legacy
    for i, (op,result) in enumerate([
        ('DEFINE','ESTABLISHED'), ('DISTINGUISH','INCOMPLETE'),
        ('DIVIDE','ESTABLISHED'), ('DISTINGUISH','INCOMPLETE'),
        ('DIVIDE','ESTABLISHED')]):
        value = answer(op,result,answer=f'A distinct examined case {i}.')
        legacy, error = engine.advance(legacy,value,SOURCE.splitlines())
        guarded, other = engine.advance(guarded,value,SOURCE.splitlines())
        assert error is other is None
    assert guarded['terminal'] is legacy['terminal'] is None
    before = __import__('copy').deepcopy(guarded)
    invalid = answer('DISTINGUISH','INCOMPLETE',evidence=[{'line':1,'quote':'invented'}])
    assert engine.advance(guarded,invalid,SOURCE.splitlines()) == (before,'invalid_turn')


def test_cycle_guard_allows_addressing_a_previously_open_issue():
    from cognitive_castle import brain_engine as engine

    state = engine.initial_state(CLAIM, cycle_guard=True)
    for op,result,refs in [('DEFINE','ESTABLISHED',[]),('DISTINGUISH','INCOMPLETE',[]),
                           ('DIVIDE','ESTABLISHED',[]),('DISTINGUISH','INCOMPLETE',[]),
                           ('DIVIDE','ESTABLISHED',[2,4])]:
        state,error = engine.advance(state,answer(op,result,addresses=refs),SOURCE.splitlines())
        assert error is None
    assert state['terminal'] is None
    assert engine.coverage(state)['open_issues'] == []
