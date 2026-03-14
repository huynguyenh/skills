# Skill Usage Rules

When interacting with external services that have a dedicated wrapper skill, ALWAYS use that skill. Never make raw API calls, curl commands, or grep for credentials when a skill already handles it.

## Service → Skill Mapping

| Service | Skill | Trigger |
|---------|-------|---------|
| Google Docs | `hnh-gg-docs` → `~/.claude/skills/hnh-gg-docs/scripts/gdocs.py` | Any docs.google.com URL, reading/creating/editing Google Docs |
| Google Sheets | `hnh-gg-sheets` → `~/.claude/skills/hnh-gg-sheets/scripts/gsheets.py` | Any spreadsheet URL, reading/writing Google Sheets |
| Google Drive | `hnh-gg-drive` → `~/.claude/skills/hnh-gg-drive/scripts/gdrive.py` | Upload, download, search, organize Drive files |
| Notion | `hnh-notion` → `~/.claude/skills/hnh-notion/scripts/notion.py` | Any notion.so URL, reading/creating/querying Notion |
| Dify | `hnh-dify` → `~/.claude/skills/hnh-dify/scripts/dify.py` | Running workflows, managing knowledge bases, Dify apps |
| Discord | `hnh-discord` → `~/.claude/skills/hnh-discord/scripts/discord.py` | Reading/sending Discord messages, managing threads |
| Sentry | `hnh-report-sentry` | Investigating Sentry issues or errors |
| AWS | `hnh-aws` → `aws` CLI | S3, ECR, RDS, CloudWatch, IAM operations |
| Kubernetes/EKS | `hnh-k8s` → `kubectl` | Pod debugging, logs, events, resource monitoring |
| GitHub | `gh` CLI (not curl) | PRs, issues, releases, API calls |

## What NOT to do

- Do NOT `grep ~/.zshrc` for API tokens to make raw `curl` calls when a wrapper skill exists
- Do NOT use `gcloud` CLI directly for Google Docs/Sheets/Drive — the Python scripts handle auth via ADC
- Do NOT write inline Python scripts to call Google/Notion/Dify APIs — use the existing CLI tools
- Do NOT fetch web pages to scrape content from services that have an API skill

## When no skill exists

If the service has no wrapper skill, then raw API calls are acceptable. Check the skills list first.
