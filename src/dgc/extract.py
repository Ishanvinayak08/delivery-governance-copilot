"""Deterministic (offline) extraction of RAID items from notes and emails.

Offline-first by design: the tool must work without network access or API keys, and
the LLM extractor is an optional enhancement that falls back to this one.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from dgc.dates import find_due
from dgc.models import RaidItem

PREFIX_TYPES = {
    "action": "Action", "ai": "Action", "risk": "Risk", "issue": "Issue",
    "blocker": "Issue", "decision": "Decision", "dependency": "Dependency",
    "assumption": "Assumption",
}
_LINE = re.compile(
    r"^\s*(?:[-*\u2022]\s*)?(?:\*\*)?(action|ai|risk|issue|blocker|decision|dependency|assumption)"
    r"(?:\*\*)?\s*[:\-\u2013]\s*(.+)$", re.IGNORECASE)
_OWNER_EXPLICIT = re.compile(r"\b(?i:owner)\s*[:=]\s*([A-Z][\w'-]*)")
_OWNER_AT = re.compile(r"(?<!\w)@([A-Za-z][\w'-]*)")
_OWNER_TO = re.compile(r"^([A-Z][a-z][\w'-]*)\s+(?:to|will|must|should)\s+")
_SEVERITY = re.compile(
    r"(?:\[|\(|\b(?:severity|priority|impact)\s*[:=]\s*)(critical|high|medium|low)\b", re.IGNORECASE)
_CLOSED = re.compile(r"\b(done|closed|completed|resolved)\b", re.IGNORECASE)
_BLOCKED = re.compile(r"\b(blocker|blocked)\b", re.IGNORECASE)

# Keyword fallback for free-text email sentences (checked in order).
_EMAIL_RULES = [
    ("Issue", re.compile(r"\b(out of scope|scope change|change request)\b", re.I)),
    ("Dependency", re.compile(r"\b(waiting on|waiting for|depends on|dependent on|pending from)\b", re.I)),
    ("Risk", re.compile(r"\b(risk|may not hold|might slip|could slip|at risk)\b", re.I)),
    ("Issue", re.compile(r"\b(delayed|delay|slipped|blocked|unable to|failed|failing)\b", re.I)),
]


def _clean_title(text: str, due_start: Optional[int]) -> str:
    if due_start is not None:
        text = text[:due_start]
    text = _OWNER_EXPLICIT.sub("", text)
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", text)
    text = _OWNER_TO.sub("", text)
    text = re.sub(r"^(?:also|and|so|but),?\s+", "", text.strip(), flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" .;,:-")
    return text[:1].upper() + text[1:] if text else text


def _build(item_type: str, text: str, source: str, kind: str, ref: date) -> RaidItem:
    due, due_start = find_due(text, ref)
    owner = None
    for pat in (_OWNER_EXPLICIT, _OWNER_AT, _OWNER_TO):
        m = pat.search(text.strip())
        if m:
            owner = m.group(1)
            break
    sev_m = _SEVERITY.search(text)
    severity = sev_m.group(1).capitalize() if sev_m else ("Low" if item_type == "Action" else "Medium")
    status = "Closed" if _CLOSED.search(text) else ("Blocked" if _BLOCKED.search(text) else "Open")
    found = sum(x is not None for x in (owner, due)) + (1 if sev_m else 0)
    return RaidItem(
        item_type=item_type, title=_clean_title(text, due_start), source=source,
        source_kind=kind, owner=owner, due=due, severity=severity, status=status,
        raw_text=text.strip(), confidence=round(0.55 + 0.15 * found, 2),
    )


def extract_from_text(text: str, source: str, kind: str, ref: date) -> list[RaidItem]:
    items: list[RaidItem] = []
    for line in text.splitlines():
        m = _LINE.match(line)
        if m:
            items.append(_build(PREFIX_TYPES[m.group(1).lower()], m.group(2), source, kind, ref))
            continue
        if kind != "email":
            continue
        body = line.strip()
        if not body or re.match(r"^(from|to|cc|date|subject)\s*:", body, re.I):
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", body):
            for item_type, pat in _EMAIL_RULES:
                if pat.search(sentence):
                    it = _build(item_type, sentence, source, kind, ref)
                    it.confidence = min(it.confidence, 0.6)  # keyword guess: flag for review
                    items.append(it)
                    break
    return items
