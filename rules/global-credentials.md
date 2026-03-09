# Credentials Rules

All credentials and API tokens live in `~/.zshrc` as environment variables with clear prefixes:

```
GITHUB_PAT_TOKEN=...
JIRA_API_TOKEN=...
JIRA_EMAIL=...
SENTRY_AUTH_TOKEN=...
ESA_ACCESS_TOKEN=...
```

## How Claude uses credentials

Claude runs commands in a subshell, so `source ~/.zshrc` does not work reliably. Instead:

1. Read `~/.zshrc` to find the token value
2. Inline it directly in the command: `GITHUB_PAT_TOKEN=xxx gh api ...`

This keeps credentials out of config files and ensures they work regardless of shell initialization.

## What NOT to do
- Do not `source ~/.zshrc` or `export` in Bash tool calls — subshells don't persist state
- Do not hardcode credentials in skills, memory, plans, or any file that gets backed up
- Do not use `$ENV_VAR` syntax in Bash tool calls expecting it to resolve — read the value first, then inline it
