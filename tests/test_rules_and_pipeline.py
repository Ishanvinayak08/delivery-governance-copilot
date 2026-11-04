import json
import tempfile
from datetime import date
from pathlib import Path

from dgc.config import Config
from dgc.llm import parse_llm_json
from dgc.models import RaidItem
from dgc.pipeline import run_pipeline
from dgc.privacy import redact
from dgc.rules import evaluate, rag_status

AS_OF = date(2026, 11, 4)
SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample"


def item(**kw):
    base = dict(item_type="Action", title="Do thing", source="s", source_kind="notes",
                owner="Ann", due=date(2026, 11, 10), item_id="T-001")
    base.update(kw)
    return RaidItem(**base)


def rules(items):
    return {f.rule_id for f in evaluate(items, AS_OF, Config())}


def test_clean_item_has_no_findings_and_green():
    f = evaluate([item()], AS_OF, Config())
    assert f == [] and rag_status(f, Config())[0] == "GREEN"


def test_decisions_do_not_need_owner():
    assert "GOV-001" not in rules([item(item_type="Decision", owner=None)])


def test_extra_alone_is_not_scope_change():
    assert "GOV-007" not in rules([item(title="Pricing for the extra devices may rise")])


def test_missing_owner_and_closed_items_ignored():
    assert "GOV-001" in rules([item(owner=None)])
    assert rules([item(owner=None, status="Closed")]) == set()


def test_overdue_escalates_after_threshold():
    f = evaluate([item(due=date(2026, 10, 20))], AS_OF, Config())
    assert f[0].rule_id == "GOV-003" and f[0].severity == "High"
    f = evaluate([item(due=date(2026, 11, 2))], AS_OF, Config())
    assert f[0].severity == "Medium"


def test_stale_and_blocked_rules():
    assert "GOV-004" in rules([item(status="In Progress", updated=date(2026, 10, 1))])
    assert "GOV-005" in rules([item(status="Blocked", due=None, source_kind="jira")])


def test_scope_change_needs_change_request_reference():
    assert "GOV-007" in rules([item(title="Request additional devices")])
    assert "GOV-007" not in rules([item(title="Request additional devices under CR-12")])


def test_duplicate_detection_across_sources_only():
    a = item(title="Imaging build fails on 2023 laptop", item_id="I-001")
    b = item(title="Imaging build fails on 2023 laptop", source_kind="jira", item_id="I-002")
    assert "GOV-006" in rules([a, b])
    assert "GOV-006" not in rules([a, item(title=a.title, item_id="I-003")])


def test_rag_thresholds():
    cfg = Config()
    high = evaluate([item(owner=None, severity="High", item_id=f"T-{n}") for n in range(3)], AS_OF, cfg)
    assert rag_status(high, cfg)[0] == "RED"
    one = evaluate([item(owner=None, severity="High")], AS_OF, cfg)
    assert rag_status(one, cfg)[0] == "AMBER"


def test_redaction_removes_contact_details():
    out = redact("Mail raj@vendor.example or call +61 412 345 678 today")
    assert "vendor.example" not in out and "412" not in out


def test_llm_output_is_validated_not_trusted():
    good = '```json\n[{"type":"Risk","title":"X","owner":null,"due":"2026-11-09","severity":"High"}]\n```'
    assert parse_llm_json(good, "f", "notes")[0].due == date(2026, 11, 9)
    for bad in ('{"a":1}', '[{"type":"Wish","title":"X"}]', '[{"type":"Risk","title":"X","severity":"Huge"}]'):
        try:
            parse_llm_json(bad, "f", "notes")
        except ValueError:
            continue
        raise AssertionError(f"accepted invalid output: {bad}")


def test_end_to_end_demo_is_deterministic_and_traceable():
    cfg = Config.load(Path(__file__).resolve().parents[1] / "config" / "governance_rules.yaml")
    with tempfile.TemporaryDirectory() as tmp:
        res = run_pipeline("Atlas", AS_OF, Path(tmp), sorted(SAMPLE.glob("meeting_notes_*.md")),
                           sorted(SAMPLE.glob("email_*.txt")), sorted(SAMPLE.glob("jira_*.csv")), cfg)
        report = Path(res.paths["report"]).read_text(encoding="utf-8")
        assert "DRAFT" in report and res.rag == "RED"
        ids = [i.item_id for i in res.items]
        assert len(ids) == len(set(ids))
        audit = json.loads(Path(res.paths["audit"]).read_text().splitlines()[-1])
        assert audit["human_approval"] == "PENDING" and len(audit["inputs"]) == 3
        assert all(len(s["sha256"]) == 64 for s in audit["inputs"])
        assert {"GOV-001", "GOV-003", "GOV-004", "GOV-005", "GOV-006", "GOV-007"} <= {
            f.rule_id for f in res.findings}
