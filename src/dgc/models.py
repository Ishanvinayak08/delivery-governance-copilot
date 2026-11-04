"""Core domain models."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Optional

ITEM_TYPES = ("Risk", "Assumption", "Issue", "Dependency", "Action", "Decision")
SEVERITIES = ("Low", "Medium", "High", "Critical")
SEV_RANK = {s: i for i, s in enumerate(SEVERITIES)}
STATUSES = ("Open", "In Progress", "Blocked", "Closed")


@dataclass
class RaidItem:
    item_type: str
    title: str
    source: str
    source_kind: str  # notes | email | jira
    owner: Optional[str] = None
    due: Optional[date] = None
    severity: str = "Medium"
    status: str = "Open"
    raw_text: str = ""
    updated: Optional[date] = None
    external_key: Optional[str] = None
    confidence: float = 1.0
    item_id: str = ""

    @property
    def is_open(self) -> bool:
        return self.status != "Closed"

    def to_row(self) -> dict:
        d = asdict(self)
        d["due"] = self.due.isoformat() if self.due else ""
        d["updated"] = self.updated.isoformat() if self.updated else ""
        d["owner"] = self.owner or ""
        d["external_key"] = self.external_key or ""
        d["confidence"] = round(self.confidence, 2)
        return d


@dataclass
class Finding:
    rule_id: str
    severity: str
    item_id: str
    item_title: str
    message: str
    recommendation: str

    def to_dict(self) -> dict:
        return asdict(self)
