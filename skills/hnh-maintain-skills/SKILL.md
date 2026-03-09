---
name: hnh-maintain-skills
description: >
  Retrospective skill maintenance — scan all custom skills for improvement opportunities,
  detect outdated patterns, find where newer skills can replace raw API calls in older skills,
  and keep the skill ecosystem consistent and up to date.
  Use this skill whenever the user says "maintain skills", "review skills", "skill audit",
  "skill hygiene", "improve our skills", "check skills for updates", or after adding a new
  skill that wraps an API already used by other skills. Also trigger when the user asks about
  skill quality, consistency, or cross-references between skills.
---

# Skill Maintenance

Periodically review all custom skills (`hnh-*`) and find improvements — especially places where
older skills do things the hard way when a newer, dedicated skill already handles it better.

## Why this matters

As the skill collection grows, earlier skills can become stale. A typical example: `hnh-plan-notion`
was written before `hnh-notion` existed, so it uses raw `curl` calls to the Notion API. Now that
`hnh-notion` wraps the entire Notion API in a CLI tool, `hnh-plan-notion` should use that instead —
it's more reliable, handles errors better, and stays in sync if the API changes.

This skill catches those opportunities systematically rather than relying on memory.

## What it detects

| Category | Severity | Example |
|----------|----------|---------|
| **Raw API calls** | High | A skill uses `curl` to an API that another skill already wraps (e.g., Notion, Google Sheets) |
| **Missing cross-references** | Medium | A skill talks about Notion extensively but doesn't know `hnh-notion` exists |
| **Stale file references** | Medium | A skill references a path (`~/.claude/...`) that no longer exists |
| **Credential anti-patterns** | Low | Using `$ENV_VAR` syntax or `source ~/.zshrc` instead of inline tokens |
| **Duplicated logic** | Low | Multiple skills implement the same helper or agent pattern independently |

## Workflow

### Step 1: Run the scanner

```bash
python3 ~/.claude/skills/hnh-maintain-skills/scripts/scan_skills.py --verbose
```

This scans all `hnh-*` skills and outputs a JSON report with categorized findings.

### Step 2: Present the findings

Summarize the report for the user in a readable format. Group findings by skill, starting with
high-severity items. For each finding, explain:

- **What's happening** — the specific pattern detected
- **Why it matters** — what could go wrong or what's being missed
- **Suggested fix** — concrete change to make (which file, what to replace with what)

Example presentation:

```
## hnh-plan-notion

🔴 **Raw Notion API call** (SKILL.md, line 42)
   Currently uses `curl -s -H "Authorization: Bearer <TOKEN>" https://api.notion.com/v1/pages/...`
   → Use `python3 ~/.claude/skills/hnh-notion/scripts/notion.py --token "$TOKEN" read PAGE_ID` instead.
   This handles error codes, pagination, and content parsing automatically.

🟡 **Missing cross-reference** (SKILL.md)
   Mentions Notion 12 times but never references hnh-notion's CLI tool.
   → Add a note in the Prerequisites section pointing to hnh-notion.
```

### Step 3: Propose changes

For each finding the user wants to fix, draft the specific edit:
- Show the old code/text
- Show the proposed replacement
- Explain what changes in behavior (if any)

Group related changes per skill so the user can approve them as a batch.

### Step 4: Apply with user approval

Only apply changes after the user confirms. For each skill being modified:

1. Read the current file
2. Apply the edit
3. Do a quick sanity check — make sure the skill still looks correct
4. Tell the user what was changed

After all changes, suggest running `/hnh-backup` to sync the updated skills to GitHub.

## Extending the scanner

The scanner script (`scripts/scan_skills.py`) has a registry of known API wrapper skills. When a new
wrapper skill is added (e.g., a future `hnh-jira` skill), update the `build_capability_registry()`
function to include it. The scanner will then automatically detect older skills that use raw calls
to that API.

The registry currently tracks:
- **hnh-notion** → Notion API (`api.notion.com`)
- **hnh-gg-sheets** → Google Sheets & Drive API (`googleapis.com`)

To add a new wrapper, add an entry to `api_wrappers` in the script with:
- `service`: Human-readable API name
- `cli_tool`: Path to the CLI tool
- `api_patterns`: Regex patterns that match raw API calls
- `capabilities`: List of what the wrapper can do

## When to run this

Good times to run a maintenance scan:
- After adding a new skill that wraps an API (like after creating `hnh-notion`)
- After a major refactor of any skill
- Periodically (monthly or quarterly) as a hygiene check
- When something breaks and you suspect a stale reference
