# Architecture

```
src/dgc/
  ingest.py    Jira CSV reader, file hashing, date-from-filename
  extract.py   Offline RAID extraction (prefix convention + email keyword fallback)
  llm.py       Optional LLM extractor with strict output validation
  privacy.py   Redaction applied before any LLM call
  dates.py     Forgiving date parsing
  rules.py     Governance rules (pure functions) and RAG scoring
  config.py    YAML policy loader
  report.py    Markdown / CSV / JSON writers
  audit.py     Append-only JSONL audit log
  pipeline.py  Orchestration
  cli.py       `dgc run` and `dgc demo`
```

**Data flow:** inputs, then `RaidItem` objects, then `Finding` objects, then report plus audit. Rules are pure functions over items plus an `as_of` date, which makes them deterministic and trivially testable.

**Extension points:** add a rule in `rules.py` with a config toggle; add a source by returning `RaidItem`s from a new reader; swap the extractor behind the same schema.
