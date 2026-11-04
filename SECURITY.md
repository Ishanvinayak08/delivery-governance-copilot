# Security and data handling

- Never commit real project data, credentials or API keys. `.env` and `output/` are git-ignored.
- Offline mode sends nothing off the machine.
- LLM mode redacts emails and phone numbers before sending text, but redaction is pattern-based and not a guarantee. Do not use LLM mode on confidential material without your organisation's approval.
- Report vulnerabilities privately via GitHub Security Advisories on this repository.
