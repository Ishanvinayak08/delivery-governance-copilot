# ADR-0002: Offline-first extraction, LLM optional
**Status:** Accepted, 2026-11-04

**Context:** Project data is often confidential; the tool must be demoable, testable and deterministic.
**Decision:** Default to rules-based extraction. LLM mode is opt-in, redacts contact details, validates output against the item schema, and falls back to offline on any failure.
**Consequences:** Deterministic CI; lower recall on free prose; LLM benefits available without making them a dependency.
