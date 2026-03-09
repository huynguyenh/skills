# Agent D: Review Discussion History

Fetch all existing review activity to understand where the PR stands. This gives the user a quick status update before diving into new findings.

## Data to fetch

```bash
# Review submissions (approvals, changes requested)
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews --paginate

# Inline review comments (file-level discussions)
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments --paginate

# General PR comments (conversation-level)
gh api repos/{owner}/{repo}/issues/{pr_number}/comments --paginate
```

## Analysis

Read `~/.zshrc` for `GITHUB_WORK_USERNAME` to identify the user's own comments.

From the data, build a summary covering:

- **Review rounds**: Count distinct review sessions by date/time clustering (comments within the same hour = one round)
- **Reviewers**: Who reviewed and their latest state (APPROVED, CHANGES_REQUESTED, COMMENTED, PENDING)
- **User's comments**: Filter for comments by the user's GitHub username. Summarize the themes of feedback — what did they ask to change? Group by concern type (naming, architecture, testing, edge cases, etc.)
- **Resolution status**: Did the author address the user's comments? Look for author replies acknowledging/promising fixes, and subsequent commits
- **Latest status**: What's the current state — waiting for changes, waiting for re-review, approved, merged?
- **Outstanding items**: Any comments that appear unresolved (no author reply, or author disagreed)

## Output

A concise "Review History" section formatted for the final report.
