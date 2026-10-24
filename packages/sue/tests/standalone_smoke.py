"""Run with a clean installed-wheel interpreter; no test dependencies required."""

import json
import sys


class ImportGuard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {
            "cognitive_castle",
            "lancedb",
            "torch",
            "spacy",
            "soar",
            "requests",
            "httpx",
        }:
            raise AssertionError(f"forbidden import: {fullname}")


def audit(event, args):
    if event.startswith(("subprocess.", "socket.", "os.system", "os.posix_spawn", "os.fork")):
        raise AssertionError(f"forbidden dispatch: {event}")


sys.meta_path.insert(0, ImportGuard())
sys.addaudithook(audit)

import castle_sue  # noqa: E402

SOURCE = "Only administrators may export data."
CLAIM = "Administrators may export data."
SUCCESS = {
    "DEFINE": ("definition", "ESTABLISHED"),
    "DISTINGUISH": ("distinction", "ESTABLISHED"),
    "CAUSE_OR_CRITERION": ("criterion", "ESTABLISHED"),
    "DIVIDE": ("case-split", "ESTABLISHED"),
    "COUNTEREXAMPLE": ("example", "NOT_FOUND"),
    "FOLLOW_CONSEQUENCE": ("consequence", "CONSISTENT"),
    "TEST_OPPOSITE": ("consequence", "EXCLUDED"),
}


def main():
    caps = castle_sue.capabilities()
    assert caps["apiVersion"] == 1
    assert caps["schemaVersion"] == 2
    assert caps["policyVersion"] == "2026-09-24"
    assert set(caps["lenses"]) == {
        "euthyphro",
        "meno",
        "parmenides",
        "cratylus",
        "theaetetus",
        "sophist",
        "gorgias",
        "republic",
        "philebus",
    }
    counts = {}
    for lens in caps["lenses"]:
        state = castle_sue.initial_state(CLAIM, lens=lens)
        for _ in range(14):
            if state["terminal"]:
                break
            assert castle_sue.question(state)
            assert castle_sue.schema(state)
            rejected, error = castle_sue.advance(state, {}, [SOURCE])
            assert rejected == state and error == "invalid_turn"
            op = state["operator"]
            answer_type, result = SUCCESS[op]
            response = {
                "answer": "An attributed interpretation requiring review.",
                "verdict": "SUPPORTED",
                "answer_type": answer_type,
                "evidence_lines": [1],
                "claim": CLAIM if op == "DEFINE" else None,
                "test_result": result,
                "evidence": [{"line": 1, "quote": SOURCE}],
                "premises": [{"statement": SOURCE, "kind": "stated", "evidence_lines": [1]}],
                "witness": None,
                "open_questions": [],
                "addresses": [],
                "revision_reason": None,
            }
            state, error = castle_sue.advance(state, response, [SOURCE])
            assert error is None, (lens, op, error)
        assert state["terminal"] == "RESOLVED", (lens, state["terminal"])
        assert castle_sue.coverage(state)["missing"] == []
        assert castle_sue.question(state) is None and castle_sue.schema(state) is None
        counts[lens] = len(state["turns"])
    print(json.dumps({"capabilities": caps, "resolvedTurns": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
