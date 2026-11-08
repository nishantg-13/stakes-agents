"""Effect typing: map a tool call to its policy-compliant, agent-relative reversibility class."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml

REGISTRY_DIR = Path(__file__).resolve().parents[2] / "registries"


class EffectType(str, Enum):
    READ = "READ"
    IDEMPOTENT = "IDEMPOTENT"
    REVERSIBLE = "REVERSIBLE"
    COMPENSABLE = "COMPENSABLE"
    IRREVERSIBLE = "IRREVERSIBLE"

    @property
    def is_write(self) -> bool:
        return self is not EffectType.READ

    @property
    def severity(self) -> int:
        """Ordinal stakes rank, used for sorting and coarse analysis. Not a cost table."""
        return _SEVERITY[self]


_SEVERITY = {
    EffectType.READ: 0,
    EffectType.IDEMPOTENT: 1,
    EffectType.REVERSIBLE: 2,
    EffectType.COMPENSABLE: 3,
    EffectType.IRREVERSIBLE: 4,
}


class UnlabeledToolError(KeyError):
    """Raised for a state-changing tool the registry does not label."""


@dataclass(frozen=True)
class EffectRegistry:
    domain: str
    labels: dict[str, EffectType]
    # tau2's own ToolType annotation ("read"/"write"/"generic"/"think"); fallback for READ only.
    base_types: dict[str, str]
    # Tools that change the database (tau2's mutates_state). None = assume every write mutates.
    mutating: frozenset[str] | None = None
    # Free-text arguments ignored when comparing sampled actions (e.g. a transfer summary).
    canon_ignore: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def mutates(self, tool_name: str) -> bool:
        """Can a wrong call change the DB state that success is judged on?"""
        if self.mutating is None:
            return self.type_of(tool_name).is_write
        return tool_name in self.mutating

    def canon(self, calls) -> str:
        """Canonical key for a message's tool calls, dropping free-text arguments."""
        from stakes.canon import canon_message

        cleaned = [
            (n, {k: v for k, v in (a or {}).items() if k not in self.canon_ignore.get(n, ())})
            for n, a in (calls or [])
        ]
        return canon_message(cleaned)

    def type_of(self, tool_name: str) -> EffectType:
        if tool_name in self.labels:
            return self.labels[tool_name]
        if self.base_types.get(tool_name) == "read":
            return EffectType.READ
        raise UnlabeledToolError(
            f"{self.domain}: tool '{tool_name}' is not READ in tau2 and has no effect label"
        )

    def max_type(self, tool_names: list[str]) -> EffectType:
        """Highest-stakes effect among the tool calls in one assistant message."""
        types = [self.type_of(n) for n in tool_names]
        return max(types, key=lambda t: t.severity) if types else EffectType.READ

    def unlabeled(self) -> list[str]:
        missing = []
        for name in self.base_types:
            try:
                self.type_of(name)
            except UnlabeledToolError:
                missing.append(name)
        return missing

    @classmethod
    def load(
        cls,
        domain: str,
        base_types: dict[str, str],
        path: Path | None = None,
        mutating: set[str] | None = None,
    ):
        path = path or REGISTRY_DIR / f"tau2_{domain}.yaml"
        raw = yaml.safe_load(path.read_text())
        labels = {name: EffectType(spec["type"]) for name, spec in raw["tools"].items()}
        ignore = {
            name: tuple(spec.get("canon_ignore", ()))
            for name, spec in raw["tools"].items()
            if spec.get("canon_ignore")
        }
        return cls(
            domain=domain,
            labels=labels,
            base_types=dict(base_types),
            mutating=frozenset(mutating) if mutating is not None else None,
            canon_ignore=ignore,
        )

    @classmethod
    def from_env(cls, domain: str, environment):
        return cls.load(domain, tau2_base_types(environment), mutating=tau2_mutating(environment))


def tau2_base_types(environment) -> dict[str, str]:
    """tau2's ToolType annotation for every agent tool in an environment."""
    from tau2.environment.toolkit import TOOL_TYPE_ATTR

    out = {}
    for name, fn in environment.tools.tools.items():
        tool_type = getattr(fn, TOOL_TYPE_ATTR, None)
        out[name] = getattr(tool_type, "value", str(tool_type))
    return out


def tau2_mutating(environment) -> set[str]:
    """Agent tools that tau2 marks as mutating the DB (re-executed during evaluation replay)."""
    from tau2.environment.toolkit import MUTATES_STATE_ATTR

    return {
        name
        for name, fn in environment.tools.tools.items()
        if getattr(fn, MUTATES_STATE_ATTR, False)
    }
