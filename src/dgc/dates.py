"""Forgiving date parsing for phrases found in real meeting notes and emails."""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_DAY_MON = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b")
_MON_DAY = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})(?:st|nd|rd|th)?\b")
_WEEKDAY = re.compile(
    r"\b(mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)(?:day|sday|nesday|rsday|urday)?\b")
_TRIGGER = re.compile(r"\b(by|due|before|until)\b\s*:?\s*(.+)$", re.IGNORECASE)


def _resolve_year(month: int, day: int, ref: date) -> Optional[date]:
    try:
        candidate = date(ref.year, month, day)
    except ValueError:
        return None
    # A date more than ~6 months in the past most likely means next year.
    if (ref - candidate).days > 180:
        try:
            return date(ref.year + 1, month, day)
        except ValueError:
            return None
    return candidate


def parse_date(text: str, ref: date) -> Optional[date]:
    """Parse ISO dates, '6 Nov', 'Nov 6' or a weekday (next occurrence on/after ref)."""
    low = text.lower()
    m = _ISO.search(low)
    if m:
        try:
            return date(int(m[1]), int(m[2]), int(m[3]))
        except ValueError:
            return None
    m = _DAY_MON.search(low)
    if m:
        return _resolve_year(MONTHS[m[2]], int(m[1]), ref)
    m = _MON_DAY.search(low)
    if m:
        return _resolve_year(MONTHS[m[1]], int(m[2]), ref)
    m = _WEEKDAY.search(low)
    if m:
        target = WEEKDAYS[m[1][:3]]
        return ref + timedelta(days=(target - ref.weekday()) % 7)
    return None


def find_due(text: str, ref: date) -> tuple[Optional[date], Optional[int]]:
    """Return (due_date, index where the due phrase starts) for 'by/due/before/until ...'."""
    for m in _TRIGGER.finditer(text):
        d = parse_date(m.group(2), ref)
        if d:
            return d, m.start()
    return None, None
