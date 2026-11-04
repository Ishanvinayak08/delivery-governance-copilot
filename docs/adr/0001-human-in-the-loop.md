# ADR-0001: Human-in-the-loop for all outputs
**Status:** Accepted, 2026-11-04

**Context:** Governance reports influence escalations and stakeholder confidence. Extraction is imperfect.
**Decision:** All outputs are stamped DRAFT; the audit log records `human_approval: PENDING`; the tool never sends or publishes.
**Consequences:** Slightly more PM effort per report; far lower risk of an automated error reaching stakeholders; clear accountability.
