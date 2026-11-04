# Project Charter: Delivery Governance Copilot

| | |
|---|---|
| **Project manager / sponsor** | Ishan Vinayak |
| **Version / date** | 1.0, 2026-11-04 |
| **Status** | Approved for MVP |

## 1. Purpose and business case
Weekly governance reporting on concurrent technology projects is manual, inconsistent and often late. This project builds a small, auditable tool that consolidates delivery inputs into a RAID log and draft status report, applying a consistent governance policy, while keeping a human accountable for every output.

## 2. Objectives and success measures
Targets below are **hypotheses to validate**, not claimed results.

| Objective | Measure | Target |
|---|---|---|
| Reduce effort of weekly governance consolidation | PM time per weekly report (before/after, timed on 4 sample weeks) | 50% reduction |
| Improve governance hygiene | % open items with owner and due date | 95%+ |
| Trustworthy extraction | Precision/recall of RAID extraction on a labelled sample set | Precision 0.85+, recall 0.75+ (offline), measured in M3 |
| Safe by design | Outputs without a human-approval gate | 0 |

## 3. Scope
**In scope:** CSV/text ingestion, extraction, governance rules, report/RAID/audit outputs, CLI, docs, CI.
**Out of scope (MVP):** live Jira/Confluence APIs, web UI, auto-sending of reports, storing data in the cloud.

## 4. Deliverables
Working CLI (`dgc`), governance policy file, sample data and example outputs, test suite, ADRs, project governance pack (this folder).

## 5. Milestones
See [05-roadmap.md](05-roadmap.md).

## 6. Assumptions
- Teams are willing to use a light note-taking convention.
- Jira data can be exported as CSV.
- Offline heuristics are good enough to be useful as a first pass with human review.

## 7. Constraints
Solo-maintained, evenings and weekends; no budget beyond optional LLM API usage; no real client data may be used.

## 8. Key risks
Tracked in [03-raid-log.md](03-raid-log.md).

## 9. Stakeholders
See [02-raci.md](02-raci.md).

## 10. Approval
Sponsor approval: Ishan Vinayak, 2026-11-04.
