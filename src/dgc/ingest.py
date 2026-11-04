"""Readers for each input type."""
from __future__ import annotations

import csv
import hashlib
import re
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from dgc.models import RaidItem

_PRIORITY = {"highest": "Critical", "critical": "Critical", "high": "High", "medium": "Medium",
             "low": "Low", "lowest": "Low"}
_CLOSED = {"done", "closed", "resolved", "complete", "completed"}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_date(path: Path, fallback: date) -> date:
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", Path(path).name)
    if m:
        try:
            return date(int(m[1]), int(m[2]), int(m[3]))
        except ValueError:
            pass
    return fallback


def _parse_any(value: str) -> Optional[date]:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%b/%y", "%d/%b/%y %I:%M %p", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def read_jira_csv(path: Path) -> list[RaidItem]:
    items: list[RaidItem] = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            r = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            status_raw = r.get("status", "")
            low_status = status_raw.lower()
            issue_type = r.get("issue type", "").lower()
            if low_status in _CLOSED:
                status = "Closed"
            elif low_status == "blocked":
                status = "Blocked"
            elif low_status in ("in progress", "in review"):
                status = "In Progress"
            else:
                status = "Open"
            if issue_type == "risk":
                item_type = "Risk"
            elif issue_type == "dependency":
                item_type = "Dependency"
            elif issue_type == "bug" or status == "Blocked":
                item_type = "Issue"
            else:
                item_type = "Action"
            items.append(RaidItem(
                item_type=item_type, title=r.get("summary", ""), source=Path(path).name,
                source_kind="jira", owner=r.get("assignee") or None,
                due=_parse_any(r.get("due date", "")),
                severity=_PRIORITY.get(r.get("priority", "").lower(), "Medium"),
                status=status, raw_text=r.get("summary", ""),
                updated=_parse_any(r.get("updated", "")),
                external_key=r.get("issue key") or None, confidence=1.0,
            ))
    return items
