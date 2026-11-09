"""Value-of-computation (VOC) allocator for STAKES (proposal §6.4, Algorithms 1 and 3).

At a write step, after k0 samples give the disagreement p_hat, run operator o iff

    VOC(o) = p_err(effect, p_hat) * C(effect) * phi_o  -  lam * kappa_o  >  0

  p_err   calibrated error probability. p_hat alone says nothing about *confident* errors
          (p_hat = 0), so p_err is an empirical table P(write is wrong | effect, agree/disagree),
          fitted on dev-split baseline rollouts (Algorithm 3, `fit_p_err`).
  C       harm of an uncorrected error of this effect type (ordinal table, A-006). tau2 fails a
          task on any wrong DB write, so an empirical C would be flat; C encodes reversibility.
  phi_o   probability operator o fixes a wrong action; kappa_o its cost in LLM calls.
  lam     price of one LLM call in harm units. Sweeping lam traces the cost-reliability frontier:
          lam = 0 verifies every write, large lam verifies nothing.

The vote operator is free once samples exist (kappa = 0), so it is always applied.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from stakes.effects import EffectType

AGREE, DISAGREE = "agree", "disagree"

# A-006: ordinal harm by policy-compliant reversibility. Only the ratios matter (lam rescales).
DEFAULT_HARM = {
    "READ": 0.0,
    "IDEMPOTENT": 0.1,
    "REVERSIBLE": 0.25,
    "COMPENSABLE": 0.6,
    "IRREVERSIBLE": 1.0,
}


def bucket(p_hat: float | None) -> str:
    return AGREE if not p_hat else DISAGREE


@dataclass
class VocParams:
    p_err: dict[str, dict[str, float]]  # effect -> {agree|disagree -> P(wrong)}
    p_err_default: dict[str, float]  # pooled over effects, for effects with no data
    harm: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_HARM))
    phi_verify: float = 0.5  # A-007: placeholder until fitted from verifier replays
    kappa_verify: float = 1.0  # one verifier call (+ an occasional revision)
    source: str = ""

    def error_prob(self, effect: EffectType, p_hat: float | None) -> float:
        b = bucket(p_hat)
        return self.p_err.get(effect.value, {}).get(b, self.p_err_default[b])

    def voc_verify(self, effect: EffectType, p_hat: float | None, lam: float) -> float:
        gain = self.error_prob(effect, p_hat) * self.harm.get(effect.value, 0.0) * self.phi_verify
        return gain - lam * self.kappa_verify

    @classmethod
    def load(cls, path: str | Path) -> VocParams:
        d = yaml.safe_load(Path(path).read_text())
        return cls(**d)

    def dump(self, path: str | Path) -> None:
        Path(path).write_text(yaml.safe_dump(self.__dict__, sort_keys=False))


def fit_p_err(entries: list[dict], prior_strength: float = 4.0) -> tuple[dict, dict, dict]:
    """Algorithm 3 (error base rates). entries: ledger dicts from *measure*-mode dev runs.

    Counts executed DB-mutating writes per (effect, agree/disagree) and smooths each cell
    toward the pooled rate of its bucket with a Beta prior of `prior_strength` pseudo-counts,
    so sparse cells (e.g. 2 observations) do not produce 0 or 1.
    Returns (p_err, pooled, counts).
    """
    counts: dict[str, dict[str, list[int]]] = {}
    pooled_n = {AGREE: [0, 0], DISAGREE: [0, 0]}
    for e in entries:
        # skip reads, rejected calls, non-mutating tools, and writes that were never probed
        if e["effect"] == "READ" or e.get("tool_error") or e.get("p_hat") is None:
            continue
        if not e.get("mutating", True):
            continue
        b = bucket(e["p_hat"])
        cell = counts.setdefault(e["effect"], {AGREE: [0, 0], DISAGREE: [0, 0]})[b]
        cell[0] += 1
        cell[1] += int(bool(e["erroneous"]))
        pooled_n[b][0] += 1
        pooled_n[b][1] += int(bool(e["erroneous"]))
    pooled = {b: (w + 1) / (n + 2) for b, (n, w) in pooled_n.items()}  # Laplace
    p_err = {
        eff: {
            b: round((w + prior_strength * pooled[b]) / (n + prior_strength), 4)
            for b, (n, w) in cells.items()
        }
        for eff, cells in counts.items()
    }
    return p_err, {b: round(v, 4) for b, v in pooled.items()}, {
        eff: {b: list(v) for b, v in cells.items()} for eff, cells in counts.items()
    }


def main(argv=None) -> int:
    """Fit p_err from measure-mode runs:  python -m stakes.voc RUN_DIR... --out params/X.yaml"""
    import argparse

    p = argparse.ArgumentParser(prog="stakes.voc")
    p.add_argument("run_dirs", nargs="+")
    p.add_argument("--out", required=True)
    p.add_argument("--prior-strength", type=float, default=4.0)
    args = p.parse_args(argv)

    from tau2.runner import build_environment

    from stakes.effects import EffectRegistry

    entries = []
    registries: dict[str, EffectRegistry] = {}
    for d in args.run_dirs:
        cfg = json.loads((Path(d) / "run_config.json").read_text())
        if cfg["mode"] != "measure" or cfg.get("split") == "test":
            raise SystemExit(f"{d}: fit only on measure-mode dev (train) runs, got {cfg}")
        dom = cfg["domain"]
        if dom not in registries:
            registries[dom] = EffectRegistry.from_env(dom, build_environment(dom))
        for f in sorted((Path(d) / "episodes").glob("*.json")):
            rec = json.loads(f.read_text())
            for e in rec["ledger"]:
                entries.append({**e, "mutating": registries[dom].mutates(e["name"])})
    p_err, pooled, counts = fit_p_err(entries, args.prior_strength)
    params = VocParams(p_err=p_err, p_err_default=pooled,
                       source=f"fit_p_err on {args.run_dirs}; counts [n, wrong]={counts}")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    params.dump(args.out)
    print(yaml.safe_dump({"p_err": p_err, "pooled": pooled, "counts": counts}, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
