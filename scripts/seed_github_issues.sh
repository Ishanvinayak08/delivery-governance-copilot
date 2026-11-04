#!/usr/bin/env bash
# Creates labels, milestones and starter issues so the repo is run like a real project.
# Prerequisites: GitHub CLI (https://cli.github.com), `gh auth login`, run from the repo root
# after you have pushed the repo to GitHub.
set -euo pipefail

gh label create change-request --color D93F0B --description "Scope, date or policy change" 2>/dev/null || true
gh label create governance-rule --color 0E8A16 --description "New or changed governance rule" 2>/dev/null || true
gh label create integration --color 1D76DB --description "External system connector" 2>/dev/null || true
gh label create evaluation --color 5319E7 --description "Measuring accuracy and benefit" 2>/dev/null || true

gh api "repos/{owner}/{repo}/milestones" -f title="M2: Hardening" -f due_on="2026-11-22T00:00:00Z" -f description="Validation, errors, dedupe tuning" >/dev/null || true
gh api "repos/{owner}/{repo}/milestones" -f title="M3: Evaluation" -f due_on="2026-12-13T00:00:00Z" -f description="Labelled set, precision/recall, timed comparison" >/dev/null || true
gh api "repos/{owner}/{repo}/milestones" -f title="M4: Integrations" -f due_on="2027-01-31T00:00:00Z" -f description="Jira API, Confluence, Power BI" >/dev/null || true

gh issue create --milestone "M2: Hardening" --label enhancement --title "Validate governance_rules.yaml and fail with clear messages" --body "Unknown keys, wrong types and out-of-range thresholds should produce actionable errors. See ADR-0003."
gh issue create --milestone "M2: Hardening" --label bug --title "Graceful handling of malformed Jira CSV (missing columns, odd encodings)" --body "Document required columns; add column-mapping config."
gh issue create --milestone "M2: Hardening" --label governance-rule --title "GOV-008: High risk with no mitigation action linked" --body "Flag High/Critical risks that have no related action."
gh issue create --milestone "M3: Evaluation" --label evaluation --title "Build labelled sample set (20 notes/emails) and precision/recall harness" --body "Targets in charter section 2. Publish results in docs/evaluation.md."
gh issue create --milestone "M3: Evaluation" --label evaluation --title "Timed before/after comparison of weekly report effort" --body "4 sample weeks; record method and raw timings."
gh issue create --milestone "M4: Integrations" --label integration --title "Jira Cloud API read-only connector" --body "Replace CSV export for ingestion; use a free sandbox."
gh issue create --milestone "M4: Integrations" --label integration --title "Publish approved report to Confluence" --body "Only after human approval is recorded."
gh issue create --milestone "M4: Integrations" --label integration --title "Power BI-ready dataset export" --body "Flat CSV/Parquet of RAID items and findings with run metadata."
echo "Seeded labels, milestones and issues."
