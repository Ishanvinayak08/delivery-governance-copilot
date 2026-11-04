# GitHub setup checklist

1. Create an empty public repo named `delivery-governance-copilot` (no README/licence; they already exist).
2. Push the code (see README or the steps given with the project).
3. Replace `<your-username>` in `README.md` with your GitHub username.
4. Run `./scripts/seed_github_issues.sh` to create labels, milestones and starter issues.
5. Settings, Branches: protect `main` (require PR, require CI to pass).
6. Settings, General: add description and topics: `project-management`, `governance`, `raid`, `delivery`, `python`, `llm`.
7. Create a release: tag `v0.1.0`, paste the CHANGELOG entry.
8. Optional: create a GitHub Project (board) and add the milestone issues.
