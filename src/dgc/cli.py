"""Command-line interface."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from dgc import __version__
from dgc.config import Config
from dgc.pipeline import run_pipeline


def _run(args: argparse.Namespace) -> int:
    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    res = run_pipeline(args.project, as_of, Path(args.out), [Path(p) for p in args.notes or []],
                       [Path(p) for p in args.emails or []], [Path(p) for p in args.jira or []],
                       Config.load(Path(args.config)), args.mode)
    print(f"RAG: {res.rag} | items: {len(res.items)} | findings: {len(res.findings)}")
    for name, path in res.paths.items():
        print(f"  {name}: {path}")
    print("Outputs are DRAFT. A project manager must review and approve before sharing.")
    return 0


def _demo(args: argparse.Namespace) -> int:
    d = Path(args.data)
    args.notes = sorted(str(p) for p in d.glob("meeting_notes_*.md"))
    args.emails = sorted(str(p) for p in d.glob("email_*.txt"))
    args.jira = sorted(str(p) for p in d.glob("jira_*.csv"))
    return _run(args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dgc", description="Delivery Governance Copilot")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--project", default="Project Atlas (sample)")
        p.add_argument("--as-of", default=None, help="ISO date; defaults to today")
        p.add_argument("--out", default="output")
        p.add_argument("--config", default="config/governance_rules.yaml")
        p.add_argument("--mode", choices=["offline", "llm"], default="offline")

    run = sub.add_parser("run", help="Process your own inputs")
    common(run)
    run.add_argument("--notes", nargs="*")
    run.add_argument("--emails", nargs="*")
    run.add_argument("--jira", nargs="*")
    run.set_defaults(func=_run)

    demo = sub.add_parser("demo", help="Run on the bundled fictional sample data")
    common(demo)
    demo.add_argument("--data", default="data/sample")
    demo.set_defaults(func=_demo, as_of="2026-11-04")

    args = parser.parse_args(argv)
    return args.func(args)
