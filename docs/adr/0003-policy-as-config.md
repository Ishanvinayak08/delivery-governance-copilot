# ADR-0003: Governance policy as YAML configuration
**Status:** Accepted, 2026-11-04

**Context:** Different projects need different thresholds (stale days, RAG triggers).
**Decision:** Thresholds, keywords and rule toggles live in `config/governance_rules.yaml`; rule logic stays in code.
**Consequences:** Governance leads can tune policy without code changes; config validation is needed (M2).
