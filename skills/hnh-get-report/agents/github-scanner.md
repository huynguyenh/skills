# GitHub Scanner Agent

You are scanning GitHub repositories for recent development activity on a ZenLabs project.

## Inputs

You will receive:
- **Repo URLs**: List of GitHub repo URLs (e.g., `https://github.com/zenlbs/gmd-tms-backend`)
- **Since date**: The date of the last report (for filtering recent activity). If no previous
  report, use yesterday's date.

## Task

For each repository, extract the org/repo from the URL (e.g., `zenlbs/gmd-tms-backend`),
then gather:

### 1. Recent commits on the default branch

```bash
gh api repos/{owner}/{repo}/commits --jq '.[0:15] | .[] | {sha: .sha[0:7], message: .commit.message | split("\n")[0], author: .commit.author.name, date: .commit.author.date}'
```

Filter to commits since the `since_date`. Count total and list the most recent 10.

### 2. Open PRs

```bash
gh pr list --repo {owner}/{repo} --state open --json number,title,author,createdAt,labels
```

### 3. Recently merged PRs

```bash
gh pr list --repo {owner}/{repo} --state merged --json number,title,author,mergedAt --limit 10
```

Filter to PRs merged since `since_date`.

### 4. Branch activity (optional)

If useful for understanding what features are in flight:

```bash
gh api repos/{owner}/{repo}/branches --jq '.[].name' | head -20
```

## Output

Return a structured summary for each repo:

```json
{
  "repos": {
    "gmd-tms-backend": {
      "commits_since": 5,
      "recent_commits": [
        {"sha": "abc1234", "message": "feat: add vehicle API", "author": "Hao", "date": "2026-03-11"}
      ],
      "open_prs": [
        {"number": 42, "title": "feat: dispatch order CRUD", "author": "dev-name"}
      ],
      "merged_prs": [
        {"number": 40, "title": "fix: auth token refresh", "author": "dev-name", "merged": "2026-03-11"}
      ],
      "active_branches": ["main", "develop", "feature/dispatch-orders"]
    }
  }
}
```

Focus on summarizing the activity concisely. The main skill will format this into the report.
