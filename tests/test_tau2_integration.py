"""Offline integration tests against the pinned tau2 checkout. No API calls are made."""

import pytest

import stakes.tau2_setup  # noqa: F401
from stakes.effects import EffectRegistry, EffectType, tau2_base_types


@pytest.mark.parametrize("domain", ["airline", "retail"])
def test_registry_covers_every_state_changing_tool(domain):
    from tau2.runner import build_environment

    env = build_environment(domain)
    reg = EffectRegistry.load(domain, tau2_base_types(env))
    assert reg.unlabeled() == []
    # every labelled tool must exist in the environment (catches typos in the YAML)
    assert set(reg.labels) <= set(reg.base_types)


@pytest.mark.parametrize("domain", ["airline", "retail"])
def test_gold_writes_are_typed(domain):
    from tau2.runner import build_environment, get_tasks

    from stakes.episode import gold_actions

    env = build_environment(domain)
    reg = EffectRegistry.load(domain, tau2_base_types(env))
    for t in get_tasks(domain, task_split_name="train"):
        for g in gold_actions(t):
            if g["requestor"] == "assistant":
                reg.type_of(g["name"])  # raises if any gold action is unlabeled


def test_probe_agent_end_to_end_with_fake_llm(monkeypatch):
    """Runs a real tau2 airline episode, replacing every LLM call with a scripted fake.

    Checks that the probe fires only on writes, that candidates are never executed, and that
    the episode record joins probes to ledger entries.
    """
    import tau2.agent.llm_agent as llm_agent_mod
    import tau2.user.user_simulator as user_mod
    from tau2 import TextRunConfig
    from tau2.data_model.message import AssistantMessage, ToolCall, UserMessage
    from tau2.evaluator.evaluator import EvaluationType
    from tau2.registry import registry
    from tau2.runner import build_environment, build_text_orchestrator, get_tasks, run_simulation

    import stakes.probe_agent as probe_mod
    from stakes.episode import build_record

    tasks = [t for t in get_tasks("airline", task_split_name="train")
             if any(a.name == "cancel_reservation" for a in (t.evaluation_criteria.actions or []))]
    task = tasks[0]
    cancel = next(a for a in task.evaluation_criteria.actions if a.name == "cancel_reservation")
    # Build messages lazily: tau2 orders the transcript by message timestamp, so each fake
    # reply must be created at the moment it is "generated", as a real LLM reply would be.
    script = [
        lambda: AssistantMessage(role="assistant", content=None, tool_calls=[
            ToolCall(id="c1", name="get_reservation_details", arguments=dict(cancel.arguments))]),
        lambda: AssistantMessage(role="assistant", content=None, tool_calls=[
            ToolCall(id="c2", name="cancel_reservation", arguments=dict(cancel.arguments))]),
        lambda: AssistantMessage(role="assistant", content="Done, your reservation is cancelled."),
    ]
    state = {"i": 0, "probe_calls": 0}

    def fake_agent_generate(**kw):
        msg = script[min(state["i"], len(script) - 1)]()
        state["i"] += 1
        return msg

    def fake_probe_generate(**kw):
        state["probe_calls"] += 1
        # one candidate disagrees with the proposal (a different reservation id)
        args = {"reservation_id": "ZZZZZZ"} if state["probe_calls"] == 1 else dict(cancel.arguments)
        return AssistantMessage(role="assistant", content=None, tool_calls=[
            ToolCall(id="p", name="cancel_reservation", arguments=args)], cost=0.001,
            usage={"prompt_tokens": 10, "completion_tokens": 5})

    user_turns = {"n": 0}

    def fake_user_generate(**kw):
        user_turns["n"] += 1
        text = "Please cancel my reservation." if user_turns["n"] == 1 else "###STOP###"
        return UserMessage(role="user", content=text)

    monkeypatch.setattr(llm_agent_mod, "generate", fake_agent_generate)
    monkeypatch.setattr(probe_mod, "generate", fake_probe_generate)
    monkeypatch.setattr(user_mod, "generate", fake_user_generate)

    env = build_environment("airline")
    reg = EffectRegistry.load("airline", tau2_base_types(env))
    holder = {}

    def factory(tools, domain_policy, **kw):
        holder["agent"] = probe_mod.ProbeAgent(tools=tools, domain_policy=domain_policy,
                                               llm="fake", llm_args={}, registry=reg, k0=3)
        return holder["agent"]

    registry.register_agent_factory(factory, "stakes_probe_test")
    cfg = TextRunConfig(domain="airline", agent="stakes_probe_test", llm_agent="fake", llm_user="fake")
    result = run_simulation(build_text_orchestrator(cfg, task, seed=1), evaluation_type=EvaluationType.ENV)

    probes = holder["agent"].probe_dicts()
    effects = [p["effect"] for p in probes]
    assert effects[:2] == [EffectType.READ.value, EffectType.IRREVERSIBLE.value]
    assert probes[0]["probed"] is False  # read step: no probe (probe_reads_frac=0)
    assert probes[1]["probed"] is True and len(probes[1]["candidates"]) == 3
    assert probes[1]["p_hat"] == pytest.approx(1 / 3)
    assert state["probe_calls"] == 3

    # candidates were never executed: exactly one cancel call reached the environment
    rec = build_record(result=result, task=task, trial=0, seed=1, registry=reg, probes=probes, meta={})
    cancels = [e for e in rec["ledger"] if e["name"] == "cancel_reservation"]
    assert len(cancels) == 1 and cancels[0]["p_hat"] == pytest.approx(1 / 3)
    assert rec["probe_join_mismatches"] == 0
    assert rec["probe_cost"] == pytest.approx(0.003)


def _run_fake_episode(monkeypatch, mode, probe_fn, verifier_fn=None, **agent_kwargs):
    """Shared harness: scripted agent proposes read -> cancel -> text, fake user, fake probes."""
    import tau2.agent.llm_agent as llm_agent_mod
    import tau2.user.user_simulator as user_mod
    from tau2 import TextRunConfig
    from tau2.data_model.message import AssistantMessage, ToolCall, UserMessage
    from tau2.evaluator.evaluator import EvaluationType
    from tau2.registry import registry
    from tau2.runner import build_environment, build_text_orchestrator, get_tasks, run_simulation

    import stakes.probe_agent as probe_mod
    from stakes.episode import build_record

    task = next(t for t in get_tasks("airline", task_split_name="train")
                if any(a.name == "cancel_reservation" for a in (t.evaluation_criteria.actions or [])))
    cancel = next(a for a in task.evaluation_criteria.actions if a.name == "cancel_reservation")
    script = [
        lambda: AssistantMessage(role="assistant", content=None, tool_calls=[
            ToolCall(id="c1", name="get_reservation_details", arguments=dict(cancel.arguments))]),
        lambda: AssistantMessage(role="assistant", content=None, tool_calls=[
            ToolCall(id="c2", name="cancel_reservation", arguments=dict(cancel.arguments))]),
        lambda: AssistantMessage(role="assistant", content="Done."),
    ]
    st = {"i": 0, "calls": []}

    def fake_agent(**kw):
        m = script[min(st["i"], len(script) - 1)]()
        st["i"] += 1
        return m

    def fake_probe_module_generate(**kw):
        st["calls"].append(kw.get("call_name"))
        if kw.get("call_name") == "stakes_verifier":
            return verifier_fn(kw)
        current = script[min(st["i"], len(script)) - 1]()  # what the agent just proposed
        return probe_fn(kw, cancel, current)

    turns = {"n": 0}

    def fake_user(**kw):
        turns["n"] += 1
        return UserMessage(role="user", content="Cancel it please." if turns["n"] == 1 else "###STOP###")

    monkeypatch.setattr(llm_agent_mod, "generate", fake_agent)
    monkeypatch.setattr(probe_mod, "generate", fake_probe_module_generate)
    monkeypatch.setattr(user_mod, "generate", fake_user)

    env = build_environment("airline")
    reg = EffectRegistry.from_env("airline", env)
    holder = {}

    def factory(tools, domain_policy, **kw):
        holder["a"] = probe_mod.ProbeAgent(tools=tools, domain_policy=domain_policy, llm="fake",
                                           llm_args={}, registry=reg, k0=3, mode=mode,
                                           **agent_kwargs)
        return holder["a"]

    import time
    name = f"stakes_test_{mode}_{time.time_ns()}"
    registry.register_agent_factory(factory, name)
    cfg = TextRunConfig(domain="airline", agent=name, llm_agent="fake", llm_user="fake")
    result = run_simulation(build_text_orchestrator(cfg, task, seed=1), evaluation_type=EvaluationType.ENV)
    probes = holder["a"].probe_dicts()
    rec = build_record(result=result, task=task, trial=0, seed=1, registry=reg, probes=probes, meta={})
    return rec, probes, st


def _msg(calls=None, content=None):
    from tau2.data_model.message import AssistantMessage, ToolCall
    return AssistantMessage(role="assistant", content=content, cost=0.001,
                            usage={"prompt_tokens": 10, "completion_tokens": 2},
                            tool_calls=[ToolCall(id=f"p{i}", name=n, arguments=a)
                                        for i, (n, a) in enumerate(calls)] if calls else None)


def test_stakes_vote_switches_to_majority(monkeypatch):
    # all 3 samples propose a different reservation -> majority (3) beats the proposal (1)
    def probe(kw, cancel, current):
        return _msg([("cancel_reservation", {"reservation_id": "ZZZZZZ"})])

    def approve(kw):
        return _msg(content="APPROVE")

    rec, probes, _st = _run_fake_episode(monkeypatch, "stakes", probe, approve)
    cancel_step = next(p for p in probes if p["effect"] == "IRREVERSIBLE")
    assert cancel_step["switched_by_vote"] is True
    assert '"zzzzzz"' in cancel_step["executed"]
    assert cancel_step["verified"] is True and cancel_step["revised"] is False
    # reads get no deliberation in stakes mode
    assert all(not p["probed"] for p in probes if p["effect"] == "READ")
    assert rec["probe_join_mismatches"] == 0


def test_stakes_verifier_revises_confident_irreversible(monkeypatch):
    # All samples agree (p_hat = 0), but the verifier objects -> regenerate (ask the user instead)
    def probe(kw, cancel, current):
        if any(getattr(m, "role", "") == "system" and "reviewer note" in (m.content or "")
               for m in kw["messages"]):
            return _msg(content="Before I cancel, can you confirm the reservation id?")
        return _msg([("cancel_reservation", dict(cancel.arguments))])

    def revise(kw):
        return _msg(content="REVISE: the customer never confirmed the cancellation with yes.")

    rec, probes, _st = _run_fake_episode(monkeypatch, "stakes", probe, revise)
    step = next(p for p in probes if p["effect"] == "IRREVERSIBLE")
    assert step["p_hat"] == 0.0 and step["revised"] is True
    assert step["executed"] == "<text>"  # the irreversible call was NOT executed
    assert not any(e["name"] == "cancel_reservation" for e in rec["ledger"])


def test_unc_only_skips_verifier_when_confident(monkeypatch):
    def probe(kw, cancel, current):  # every sample agrees with the current proposal
        calls = [(tc.name, dict(tc.arguments)) for tc in (current.tool_calls or [])]
        return _msg(calls or None, content=current.content)

    _rec, probes, st = _run_fake_episode(
        monkeypatch, "unc_only", probe, lambda kw: _msg(content="REVISE: x")
    )
    assert "stakes_verifier" not in st["calls"]  # p_hat = 0 everywhere -> no verification
    assert all(p["probed"] for p in probes if p["proposal"] != "<text>")  # samples at reads too


def test_transfer_is_not_a_wrong_write_and_summary_ignored():
    from tau2.runner import build_environment

    from stakes.ledger import build_ledger

    reg = EffectRegistry.from_env("airline", build_environment("airline"))
    assert not reg.mutates("transfer_to_human_agents") and reg.mutates("cancel_reservation")
    a = reg.canon([("transfer_to_human_agents", {"summary": "user wants refund"})])
    b = reg.canon([("transfer_to_human_agents", {"summary": "customer asks to cancel"})])
    assert a == b
    led = build_ledger([{"turn": 0, "name": "transfer_to_human_agents", "arguments": {}, "error": False}], [], reg)
    assert not led.entries[0].erroneous


def _agreeing_probe(kw, cancel, current):
    calls = [(tc.name, dict(tc.arguments)) for tc in (current.tool_calls or [])]
    return _msg(calls or None, content=current.content)


def _voc_params():
    from stakes.voc import VocParams
    return VocParams(p_err={"IRREVERSIBLE": {"agree": 0.2, "disagree": 0.5}},
                     p_err_default={"agree": 0.2, "disagree": 0.5}, phi_verify=0.5)


@pytest.mark.parametrize("lam, expect_verify", [(0.05, True), (0.2, False)])
def test_voc_verifies_confident_irreversible_only_when_worth_it(monkeypatch, lam, expect_verify):
    # confident (p_hat = 0) irreversible write: VOC = 0.2 * 1.0 * 0.5 - lam * 1 = 0.1 - lam
    _rec, probes, st = _run_fake_episode(
        monkeypatch, "voc", _agreeing_probe, lambda kw: _msg(content="APPROVE"),
        voc_params=_voc_params(), lam=lam,
    )
    step = next(p for p in probes if p["effect"] == "IRREVERSIBLE")
    assert step["probed"] and step["p_hat"] == 0.0
    assert step["voc"] == pytest.approx(0.1 - lam)
    assert step["verified"] is expect_verify
    assert ("stakes_verifier" in st["calls"]) is expect_verify
    assert all(not p["probed"] for p in probes if p["effect"] == "READ")


def test_voc_mode_requires_params():
    with pytest.raises(ValueError, match="voc_params"):
        import stakes.probe_agent as probe_mod
        probe_mod.ProbeAgent(tools=[], domain_policy="", llm="fake", llm_args={},
                             registry=None, mode="voc")


def test_verifier_is_told_the_effect_type(monkeypatch):
    seen = []

    def probe(kw, cancel, current):  # one sample disagrees everywhere -> unc_only verifies all
        calls = [(tc.name, dict(tc.arguments)) for tc in (current.tool_calls or [])]
        if calls and len([c for c in seen if c == "s"]) % 3 == 0:
            calls = [(calls[0][0], {"reservation_id": "ZZZZZZ"})]
        seen.append("s")
        return _msg(calls or None, content=current.content)

    prompts = []

    def verifier(kw):
        prompts.append(kw["messages"][-1].content)
        return _msg(content="APPROVE")

    _run_fake_episode(monkeypatch, "unc_only", probe, verifier)
    assert any("read-only lookup" in p for p in prompts)
    assert any("cannot be undone" in p for p in prompts)
