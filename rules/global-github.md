# GitHub Rules

Always use the `gh` CLI for GitHub operations — never raw `curl` to the GitHub API or manual git remote manipulation when `gh` can handle it.

This includes:
- Creating/viewing PRs: `gh pr create`, `gh pr view`
- Cloning repos: `gh repo clone`
- Checking auth: `gh auth status`
- API calls: `gh api` (handles auth automatically)
- Issues and releases: `gh issue`, `gh release`

The `gh` CLI manages authentication, handles multiple accounts, and produces consistent output. Using it avoids token leaks in command history and simplifies multi-account setups.
