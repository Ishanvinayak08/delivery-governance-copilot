# Roadmap and Milestones

| Milestone | Target | Scope | Exit criteria |
|---|---|---|---|
| **M1: MVP** | 2026-11-04 | Ingest, offline extraction, 7 rules, report, audit, CLI, CI | Demo runs; tests green; docs complete (done: v0.1.0) |
| **M2: Hardening** | 2026-11-22 | Config validation, richer CLI errors, input format docs, dedupe tuning | No unhandled exceptions on malformed input; 90% line coverage on rules |
| **M3: Evaluation** | 2026-12-13 | Labelled sample set, precision/recall harness, timed before/after comparison | Metrics published in `docs/evaluation.md` against charter targets |
| **M4: Integrations** | 2027-01-31 | Jira Cloud API read connector; Confluence publish of approved reports; Power BI dataset export | Sandbox end-to-end run recorded |

Change requests that move a milestone are logged as issues labelled `change-request`.
