"""Governance policy loaded from YAML, with safe defaults."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

DEFAULT_SCOPE_KEYWORDS = [
    "out of scope", "additional scope", "scope change", "scope creep",
    "new requirement", "additional devices", "additional licences",
]


@dataclass
class Config:
    stale_days: int = 14
    overdue_escalate_days: int = 7
    duplicate_similarity: float = 0.85
    red_if_critical_findings: int = 1
    red_if_high_findings: int = 3
    amber_if_high_findings: int = 1
    amber_if_medium_findings: int = 4
    scope_keywords: list = field(default_factory=lambda: list(DEFAULT_SCOPE_KEYWORDS))
    rules_enabled: dict = field(default_factory=dict)

    def enabled(self, rule_id: str) -> bool:
        return bool(self.rules_enabled.get(rule_id, True))

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        cfg = cls()
        if path is None or not Path(path).exists():
            return cfg
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        t, r = data.get("thresholds", {}), data.get("rag", {})
        cfg.stale_days = int(t.get("stale_days", cfg.stale_days))
        cfg.overdue_escalate_days = int(t.get("overdue_escalate_days", cfg.overdue_escalate_days))
        cfg.duplicate_similarity = float(t.get("duplicate_similarity", cfg.duplicate_similarity))
        cfg.red_if_critical_findings = int(r.get("red_if_critical_findings", 1))
        cfg.red_if_high_findings = int(r.get("red_if_high_findings", 3))
        cfg.amber_if_high_findings = int(r.get("amber_if_high_findings", 1))
        cfg.amber_if_medium_findings = int(r.get("amber_if_medium_findings", 4))
        cfg.scope_keywords = list(data.get("scope_keywords", cfg.scope_keywords))
        cfg.rules_enabled = dict(data.get("rules_enabled", {}))
        return cfg
