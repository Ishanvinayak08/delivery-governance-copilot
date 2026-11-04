"""Governance rules engine. Each rule is a small pure function over RAID items."""
from __future__ import annotations

import re
from datetime import date
from difflib import SequenceMatcher

from dgc.config import Config
from dgc.models import SEV_RANK, Finding, RaidItem

_CR_REF = re.compile(r"\bCR-?\d+\b", re.IGNORECASE)


def _norm(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def _f(rule: str, sev: str, it: RaidItem, msg: str, rec: str) -> Finding:
    return Finding(rule, sev, it.item_id, it.title, msg, rec)


def _high_item(it: RaidItem) -> bool:
    return SEV_RANK[it.severity] >= SEV_RANK["High"]


def evaluate(items: list[RaidItem], as_of: date, cfg: Config) -> list[Finding]:
    out: list[Finding] = []
    open_items = [i for i in items if i.is_open]

    for it in open_items:
        if cfg.enabled("GOV-001") and not it.owner and it.item_type != "Decision":
            out.append(_f("GOV-001", "High" if _high_item(it) else "Medium", it,
                          f"{it.item_type} has no accountable owner.",
                          "Assign a single named owner before the next governance meeting."))

        if cfg.enabled("GOV-002") and it.due is None and it.item_type in ("Action", "Risk", "Issue", "Dependency") \
                and it.source_kind != "jira":
            out.append(_f("GOV-002", "Medium", it, f"{it.item_type} has no due date.",
                          "Agree a due date, or a review date for risks."))

        if cfg.enabled("GOV-003") and it.due and it.due < as_of and it.item_type != "Decision":
            days = (as_of - it.due).days
            sev = "High" if days >= cfg.overdue_escalate_days or _high_item(it) else "Medium"
            out.append(_f("GOV-003", sev, it, f"Overdue by {days} day(s) (due {it.due.isoformat()}).",
                          "Re-baseline with the owner or escalate if it threatens a milestone."
                          if sev == "High" else "Confirm a revised date with the owner."))

        if cfg.enabled("GOV-004") and it.status == "In Progress" and it.updated:
            idle = (as_of - it.updated).days
            if idle >= cfg.stale_days:
                out.append(_f("GOV-004", "Medium", it, f"In progress but untouched for {idle} days.",
                              "Check whether work has stalled and update the ticket."))

        if cfg.enabled("GOV-005") and it.status == "Blocked" and it.due is None:
            out.append(_f("GOV-005", "High" if _high_item(it) else "Medium", it,
                          "Blocked with no target unblock date.",
                          "Name the unblock owner and a date; escalate if external."))

        if cfg.enabled("GOV-007"):
            text = f"{it.title} {it.raw_text}".lower()
            if any(k in text for k in cfg.scope_keywords) and not _CR_REF.search(text):
                out.append(_f("GOV-007", "High", it,
                              "Possible scope change with no change request reference.",
                              "Raise a change request (impact on cost, time, quality) before agreeing."))

    if cfg.enabled("GOV-006"):
        seen: set[tuple[str, str]] = set()
        for i, a in enumerate(open_items):
            for b in open_items[i + 1:]:
                if a.source_kind == b.source_kind or a.item_type == "Decision":
                    continue
                ratio = SequenceMatcher(None, _norm(a.title), _norm(b.title)).ratio()
                key = tuple(sorted((a.item_id, b.item_id)))
                if ratio >= cfg.duplicate_similarity and key not in seen:
                    seen.add(key)
                    out.append(_f("GOV-006", "Low", a,
                                  f"Probable duplicate of {b.item_id} ({b.source}).",
                                  "Cross-reference or merge so the item has one source of truth."))
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    return sorted(out, key=lambda f: (order[f.severity], f.rule_id, f.item_id))


def rag_status(findings: list[Finding], cfg: Config) -> tuple[str, str]:
    c = sum(f.severity == "Critical" for f in findings)
    h = sum(f.severity == "High" for f in findings)
    m = sum(f.severity == "Medium" for f in findings)
    if c >= cfg.red_if_critical_findings or h >= cfg.red_if_high_findings:
        return "RED", f"{c} critical and {h} high governance findings (red at {cfg.red_if_high_findings}+ high)."
    if h >= cfg.amber_if_high_findings or m >= cfg.amber_if_medium_findings:
        return "AMBER", f"{h} high and {m} medium governance findings."
    return "GREEN", "No material governance findings."
