# RAID Log (project's own)

| ID | Type | Description | Likelihood / Impact | Mitigation / Action | Owner | Status |
|---|---|---|---|---|---|---|
| R-01 | Risk | Offline heuristics miss items written in free prose | High / Medium | Surface low-confidence items; build labelled eval set (M3); LLM mode as option | Maintainer | Open |
| R-02 | Risk | Single maintainer means no independent review | High / Low | CI quality gates; PR checklist; invite peer reviewer | Maintainer | Open |
| R-03 | Risk | Sensitive project data sent to an LLM | Low / High | Offline default; redaction; SECURITY.md guidance; no real data in repo | Maintainer | Mitigated |
| R-04 | Risk | Over-trusting automated RAG | Medium / High | DRAFT stamp, human-approval field in audit log, ADR-0001 | Maintainer | Mitigated |
| A-01 | Assumption | Jira can be exported to CSV with standard columns | n/a | Document required columns; add mapping config in M3 | Maintainer | Open |
| I-01 | Issue | Duplicate detection is title-based only | n/a | Semantic matching on roadmap | Maintainer | Open |
| D-01 | Dependency | Jira Cloud API access for M4 connector | n/a | Use a free Jira sandbox | Maintainer | Open |
| DEC-01 | Decision | Offline-first with optional LLM | n/a | ADR-0002 | Maintainer | Closed |
| DEC-02 | Decision | Policy in YAML | n/a | ADR-0003 | Maintainer | Closed |
