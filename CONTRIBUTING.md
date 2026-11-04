# Contributing

1. Open or pick a GitHub Issue; link your PR to it.
2. Branch from `main`: `feature/<short-name>` or `fix/<short-name>`.
3. `pip install -e ".[dev]"`, then run `ruff check src tests` and `pytest -q` before pushing.
4. New governance rules need: an ID (`GOV-0NN`), a config toggle, a test for the positive and negative case, and a row in the README rule table.
5. Keep sample data fictional. Never commit real client, vendor or personal data.
6. Open a PR using the template. One approving review and green CI are required to merge.
7. Material design choices are recorded as an ADR in `docs/adr/`.

Commit style: short imperative subject (`Add stale-ticket rule`), reference the issue (`Refs #12`).
