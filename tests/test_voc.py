import pytest

from stakes.effects import EffectType
from stakes.probe_agent import parse_verdict
from stakes.voc import VocParams, bucket, fit_p_err


@pytest.mark.parametrize("text, verdict, reason", [
    ("APPROVE", "APPROVE", None),
    ("**APPROVE**", "APPROVE", None),
    ("approve.\nREVISE: later line ignored", "APPROVE", None),
    ("REVISE: no explicit yes from the customer", "REVISE", "no explicit yes from the customer"),
    ("REVISE", "REVISE", "The reviewer flagged this action."),
    ("I think the agent should REVISE: x", "UNPARSED", None),  # only the first line counts
    ("", "UNPARSED", None),
    ("APPROVED", "UNPARSED", None),
])
def test_parse_verdict(text, verdict, reason):
    assert parse_verdict(text) == (verdict, reason)


def test_bucket():
    assert bucket(0.0) == "agree" and bucket(None) == "agree" and bucket(1 / 3) == "disagree"


def _e(effect, p_hat, wrong, **kw):
    return {"effect": effect, "p_hat": p_hat, "erroneous": wrong, "tool_error": False, **kw}


def test_fit_p_err_smooths_toward_pooled_rate():
    entries = (
        [_e("IRREVERSIBLE", 0.0, False)] * 9 + [_e("IRREVERSIBLE", 0.0, True)]
        + [_e("COMPENSABLE", 0.67, True)] * 2
        + [_e("READ", 0.0, True), _e("IRREVERSIBLE", None, True),  # ignored: read, unprobed
           _e("IRREVERSIBLE", 0.0, True, tool_error=True), _e("IRREVERSIBLE", 0.0, True, mutating=False)]
    )
    p_err, pooled, counts = fit_p_err(entries, prior_strength=4.0)
    assert counts["IRREVERSIBLE"]["agree"] == [10, 1]
    assert pooled["agree"] == pytest.approx(2 / 12, abs=1e-4)
    assert p_err["IRREVERSIBLE"]["agree"] == pytest.approx((1 + 4 * 2 / 12) / 14, abs=1e-4)
    # 2/2 wrong is shrunk well below 1
    assert 0.5 < p_err["COMPENSABLE"]["disagree"] < 1.0


def test_voc_value_and_lambda_monotone(tmp_path):
    p = VocParams(p_err={"IRREVERSIBLE": {"agree": 0.2, "disagree": 0.5}},
                  p_err_default={"agree": 0.1, "disagree": 0.4})
    assert p.voc_verify(EffectType.IRREVERSIBLE, 0.0, 0.0) == pytest.approx(0.1)
    assert p.voc_verify(EffectType.COMPENSABLE, 0.5, 0.0) == pytest.approx(0.4 * 0.6 * 0.5)
    assert p.voc_verify(EffectType.READ, 1.0, 0.0) == 0.0
    vals = [p.voc_verify(EffectType.IRREVERSIBLE, 0.0, lam) for lam in (0, 0.05, 0.1, 0.2)]
    assert vals == sorted(vals, reverse=True)
    p.dump(tmp_path / "p.yaml")
    assert VocParams.load(tmp_path / "p.yaml") == p
