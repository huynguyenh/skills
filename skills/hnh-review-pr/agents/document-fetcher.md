# Agent A: Document Fetcher

Fetch linked documents from the PR body and branch name to understand the intent behind the change. This is a **blocking dependency** — the final report quality depends heavily on understanding *why* the change was made.

## What to look for

Parse the PR body and branch name for links to:
- **Jira**: URLs matching `atlassian.net/browse/TICKET-123` or ticket IDs like `PROJ-123`
- **esa.io**: URLs matching `*.esa.io/posts/12345`
- **Confluence**: URLs containing `atlassian.net/wiki`
- **Branch name**: ticket IDs embedded in the branch (e.g., `feat/PROJ-590-description`)

## How to fetch

Read `~/.zshrc` for credentials — inline literal values in commands, never use `$ENV_VAR` syntax.

### Jira

```bash
curl -s -u "<JIRA_EMAIL>:<JIRA_API_TOKEN>" \
  "<JIRA_BASE_URL>/rest/api/3/issue/<TICKET-ID>?fields=summary,description,status,issuetype,priority,assignee,comment" \
  | python3 -m json.tool
```

Env vars: `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`

### esa.io

```bash
curl -s -H "Authorization: Bearer <ESA_ACCESS_TOKEN>" \
  "https://api.esa.io/v1/teams/<ESA_TEAM>/posts/<POST_NUMBER>"
```

Env vars: `ESA_ACCESS_TOKEN`, `ESA_TEAM`

### Confluence

Not currently configured. If a Confluence link is found, note it in the report as "could not fetch — no credentials configured."

## Output

Return a summary of:
1. Ticket title/summary
2. Description (what the ticket asks for)
3. Status and priority
4. Any relevant comments providing implementation context

If no links are found anywhere (body + branch name), note "No linked documents found" — the main report will flag this as a suggestion.
