from datetime import date

from dgc.extract import extract_from_text

REF = date(2026, 10, 28)


def one(line, kind="notes"):
    items = extract_from_text(line, "t", kind, REF)
    assert len(items) == 1, items
    return items[0]


def test_action_owner_due_severity():
    it = one("- Action: Marcus to confirm imaging build sign-off by 2026-10-30 [high]")
    assert (it.item_type, it.owner, it.due, it.severity) == ("Action", "Marcus", date(2026, 10, 30), "High")
    assert it.title == "Confirm imaging build sign-off"


def test_explicit_owner_and_due_phrase():
    it = one("- Dependency: Client to approve MDM policy before Wave 3. Owner: Daniel. Due 6 Nov")
    assert it.item_type == "Dependency" and it.owner == "Daniel" and it.due == date(2026, 11, 6)


def test_missing_owner_stays_none():
    it = one("- Action: Update the cutover runbook (no owner agreed yet)")
    assert it.owner is None and it.title == "Update the cutover runbook"


def test_blocker_marks_blocked_status():
    it = one("- Issue: Imaging build fails (blocker) owner: Marcus [critical]")
    assert it.status == "Blocked" and it.severity == "Critical"


def test_email_keyword_fallback_is_low_confidence():
    items = extract_from_text("The shipment is delayed by a week.", "e.txt", "email", REF)
    assert items and items[0].item_type == "Issue" and items[0].confidence <= 0.6


def test_notes_ignore_unprefixed_lines():
    assert extract_from_text("Wave 2 is delayed.", "n.md", "notes", REF) == []
