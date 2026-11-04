"""Append-only audit trail: what went in, what came out, and that a human still has to approve."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from dgc import __version__


def write_audit(out_dir: Path, record: dict) -> Path:
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool_version": __version__,
        "human_approval": "PENDING",
        **record,
    }
    path = Path(out_dir) / "audit_log.jsonl"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return path
