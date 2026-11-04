"""Orchestration: ingest -> extract -> assign IDs -> evaluate rules -> report -> audit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from dgc.audit import write_audit
from dgc.config import Config
from dgc.extract import extract_from_text
from dgc.ingest import file_date, read_jira_csv, sha256_of
from dgc.llm import LLMUnavailable, extract_with_llm
from dgc.models import RaidItem
from dgc.report import build_report, write_outputs
from dgc.rules import evaluate, rag_status

_PREFIX = {"Risk": "R", "Assumption": "A", "Issue": "I", "Dependency": "D", "Action": "T", "Decision": "DEC"}


@dataclass
class Result:
    items: list
    findings: list
    rag: str
    paths: dict


def _assign_ids(items: list[RaidItem]) -> None:
    counters: dict[str, int] = {}
    for it in items:
        counters[it.item_type] = counters.get(it.item_type, 0) + 1
        it.item_id = f"{_PREFIX[it.item_type]}-{counters[it.item_type]:03d}"


def run_pipeline(project: str, as_of: date, out_dir: Path, notes: list[Path], emails: list[Path],
                 jira: list[Path], cfg: Optional[Config] = None, mode: str = "offline") -> Result:
    cfg = cfg or Config()
    items: list[RaidItem] = []
    sources: list[dict] = []
    fallbacks: list[str] = []

    for kind, paths in (("notes", notes), ("email", emails)):
        for p in paths:
            p = Path(p)
            text = p.read_text(encoding="utf-8")
            sources.append({"path": p.name, "kind": kind, "sha256": sha256_of(p)})
            extracted = None
            if mode == "llm":
                try:
                    extracted = extract_with_llm(text, p.name, kind)
                except (LLMUnavailable, ValueError, KeyError) as exc:
                    fallbacks.append(f"{p.name}: {type(exc).__name__}: {exc}")
                except Exception as exc:  # network/API errors must never break the pipeline
                    fallbacks.append(f"{p.name}: {type(exc).__name__}")
            if extracted is None:
                extracted = extract_from_text(text, p.name, kind, file_date(p, as_of))
            items.extend(extracted)
    for p in jira:
        p = Path(p)
        sources.append({"path": p.name, "kind": "jira", "sha256": sha256_of(p)})
        items.extend(read_jira_csv(p))

    _assign_ids(items)
    findings = evaluate(items, as_of, cfg)
    rag, reason = rag_status(findings, cfg)

    mode_note = "offline rules-based extraction" if mode == "offline" else (
        "LLM-assisted extraction" + (f" (fell back to offline for {len(fallbacks)} file(s))" if fallbacks else ""))
    report_md = build_report(project, as_of, items, findings, rag, reason, sources, mode_note)
    paths = write_outputs(out_dir, report_md, items, findings)
    audit = write_audit(Path(out_dir), {
        "project": project, "as_of": as_of.isoformat(), "mode": mode, "inputs": sources,
        "items_extracted": len(items), "findings": len(findings), "rag": rag, "fallbacks": fallbacks,
    })
    paths["audit"] = audit
    return Result(items, findings, rag, paths)
