import pytest

from stakes.canon import TEXT_REPLY, canon_call, canon_message, disagreement, proposal_disagreement
from stakes.effects import EffectRegistry, EffectType, UnlabeledToolError
from stakes.ledger import build_ledger, decisive_error


def test_canon_ignores_key_order_whitespace_case_and_int_float():
    a = canon_call("f", {"b": 2, "a": "  Hello   World "})
    b = canon_call("f", {"a": "hello world", "b": 2.0})
    assert a == b


def test_canon_distinguishes_values_and_tools():
    assert canon_call("f", {"x": 1}) != canon_call("f", {"x": 2})
    assert canon_call("f", {"x": 1}) != canon_call("g", {"x": 1})


def test_canon_message_order_insensitive_and_text():
    m1 = canon_message([("a", {"x": 1}), ("b", {})])
    m2 = canon_message([("b", {}), ("a", {"x": 1})])
    assert m1 == m2
    assert canon_message([]) == TEXT_REPLY
    assert canon_message(None) == TEXT_REPLY


def test_disagreement_measures():
    assert disagreement(["a", "a", "a"]) == 0.0
    assert disagreement(["a", "a", "b", "c"]) == pytest.approx(0.5)
    assert proposal_disagreement("a", ["a", "b", "b"]) == pytest.approx(2 / 3)
    with pytest.raises(ValueError):
        proposal_disagreement("a", [])


REG = EffectRegistry(
    domain="t",
    labels={
        "cancel": EffectType.IRREVERSIBLE,
        "rename": EffectType.REVERSIBLE,
        "book": EffectType.COMPENSABLE,
    },
    base_types={"get": "read", "cancel": "write", "rename": "write", "book": "write", "mystery": "write"},
)


def test_registry_fallback_and_unlabeled():
    assert REG.type_of("get") is EffectType.READ
    assert REG.type_of("cancel") is EffectType.IRREVERSIBLE
    with pytest.raises(UnlabeledToolError):
        REG.type_of("mystery")
    assert REG.unlabeled() == ["mystery"]
    assert REG.max_type(["get", "rename", "cancel"]) is EffectType.IRREVERSIBLE


def _call(turn, name, args=None, error=False):
    return {"turn": turn, "name": name, "arguments": args or {}, "error": error}


GOLD = [
    {"action_id": "g0", "name": "get", "arguments": {"id": "R1"}, "compare_args": None, "requestor": "assistant"},
    {"action_id": "g1", "name": "cancel", "arguments": {"id": "R1"}, "compare_args": None, "requestor": "assistant"},
]


def test_ledger_correct_episode_has_no_errors():
    led = build_ledger([_call(0, "get", {"id": "R1"}), _call(1, "cancel", {"id": "R1"})], GOLD, REG)
    assert not any(e.erroneous for e in led.entries)
    assert led.unmatched_gold_writes == []
    assert led.entries[1].matched_gold == "g1"


def test_ledger_wrong_write_is_decisive():
    calls = [_call(0, "get", {"id": "R2"}), _call(1, "cancel", {"id": "R2"})]
    led = build_ledger(calls, GOLD, REG)
    assert [e.erroneous for e in led.entries] == [False, True]  # reads are never "erroneous"
    d = decisive_error(led)
    assert (d.kind, d.effect, d.turn, d.tool) == ("wrong_write", "IRREVERSIBLE", 1, "cancel")


def test_ledger_tool_error_is_not_a_commit():
    led = build_ledger([_call(0, "cancel", {"id": "R9"}, error=True)], GOLD, REG)
    assert not led.entries[0].erroneous
    assert decisive_error(led).kind == "missed_write"


def test_duplicate_write_is_erroneous():
    calls = [_call(0, "cancel", {"id": "R1"}), _call(1, "cancel", {"id": "R1"})]
    led = build_ledger(calls, GOLD, REG)
    assert [e.erroneous for e in led.entries] == [False, True]


def test_refusal_task_any_write_is_wrong():
    led = build_ledger([_call(0, "book", {"x": 1})], [], REG)
    assert decisive_error(led).kind == "wrong_write"


def test_no_write_failure_class():
    led = build_ledger([_call(0, "get", {"id": "R1"})], GOLD[:1], REG)
    assert decisive_error(led).kind == "no_write_error"


def test_compare_args_subset():
    gold = [{"action_id": "g", "name": "rename", "arguments": {"id": "A", "note": "x"},
             "compare_args": ["id"], "requestor": "assistant"}]
    led = build_ledger([_call(0, "rename", {"id": "A", "note": "different"})], gold, REG)
    assert not led.entries[0].erroneous


def test_nested_extra_fields_still_match():
    # reference gives flights as {flight_number, date}; the agent adds informational fields
    gold = [{"action_id": "g", "name": "book", "requestor": "assistant", "compare_args": None,
             "arguments": {"id": "A", "flights": [{"n": "HAT1", "d": "2024-05-01"}]}}]
    call = {"id": "A", "flights": [{"n": "HAT1", "d": "2024-05-01", "price": 100, "origin": "LAS"}]}
    assert not build_ledger([_call(0, "book", call)], gold, REG).entries[0].erroneous


def test_nested_value_difference_is_wrong():
    gold = [{"action_id": "g", "name": "book", "requestor": "assistant", "compare_args": None,
             "arguments": {"id": "A", "flights": [{"n": "HAT1", "d": "2024-05-01"}]}}]
    wrong_flight = {"id": "A", "flights": [{"n": "HAT9", "d": "2024-05-01"}]}
    missing_leg = {"id": "A", "flights": []}
    missing_key = {"flights": [{"n": "HAT1", "d": "2024-05-01"}]}
    for call in (wrong_flight, missing_leg, missing_key):
        assert build_ledger([_call(0, "book", call)], gold, REG).entries[0].erroneous
