"""Optional LLM extractor. Everything here is advisory: output is validated against the
same schema as offline extraction and anything malformed is rejected, not trusted."""
from __future__ import annotations

import json
import os
import re
from datetime import date

from dgc.models import ITEM_TYPES, SEVERITIES, RaidItem
from dgc.privacy import redact

SYSTEM_PROMPT = (
    "You extract RAID items (Risk, Assumption, Issue, Dependency, Action, Decision) from "
    "project delivery text. Return ONLY a JSON array. Each element: "
    '{"type": one of %s, "title": str, "owner": str|null, "due": "YYYY-MM-DD"|null, '
    '"severity": one of %s}. Never invent owners or dates; use null when not stated.'
) % (list(ITEM_TYPES), list(SEVERITIES))


class LLMUnavailable(RuntimeError):
    pass


def parse_llm_json(raw: str, source: str, kind: str) -> list[RaidItem]:
    """Validate model output strictly. Raises ValueError on anything unexpected."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    data = json.loads(cleaned)
    if not isinstance(data, list):
        raise ValueError("expected a JSON array")
    items = []
    for row in data:
        if not isinstance(row, dict) or row.get("type") not in ITEM_TYPES or not row.get("title"):
            raise ValueError(f"invalid item: {row!r}")
        severity = row.get("severity") or "Medium"
        if severity not in SEVERITIES:
            raise ValueError(f"invalid severity: {severity!r}")
        due = None
        if row.get("due"):
            due = date.fromisoformat(row["due"])
        items.append(RaidItem(
            item_type=row["type"], title=str(row["title"]).strip(), source=source,
            source_kind=kind, owner=row.get("owner") or None, due=due, severity=severity,
            confidence=0.8,
        ))
    return items


def extract_with_llm(text: str, source: str, kind: str) -> list[RaidItem]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise LLMUnavailable("ANTHROPIC_API_KEY not set")
    try:
        import anthropic
    except ImportError as exc:
        raise LLMUnavailable("install the 'llm' extra: pip install -e '.[llm]'") from exc
    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(
        model=os.environ.get("DGC_MODEL", "claude-sonnet-5-5"),
        max_tokens=2000, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": redact(text)[:20000]}],
    )
    raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    return parse_llm_json(raw, source, kind)
