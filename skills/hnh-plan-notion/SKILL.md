---
name: hnh-plan-notion
description: Create a principal-engineer-level implementation plan from a Notion page. Use this skill whenever the user provides a Notion URL (e.g., https://www.notion.so/...), mentions a Notion page or doc, or says "plan this Notion doc". Fetches the page content first, then challenges the approach, interviews the user, launches parallel agents to explore the codebase and gather context, and produces a comprehensive plan with alternative approaches, risk analysis, detailed testing strategy, observability, and deployment steps.
---

# Implementation Planning (Notion)

Create a thorough, principal-engineer-level implementation plan starting from a Notion page.

## Input Parsing

Accept:
- Full URL: `https://www.notion.so/{workspace}/{page-title}-{page_id}` or `https://notion.so/...`
- The page ID is the last 32-character hex string in the URL (with or without dashes)

## Phase 0: Fetch Notion Page

Read `~/.zshrc` for `NOTION_API_TOKEN`. If not configured (placeholder value), tell the user:

> "No Notion token configured. To set this up:
> 1. Go to https://www.notion.so/my-integrations and create an internal integration
> 2. Copy the token (starts with `ntn_` or `secret_`)
> 3. Update `~/.zshrc`: replace `<YOUR_NOTION_TOKEN_HERE>` with your token
> 4. Share the Notion page with your integration (click Share → invite the integration)
> Then try again."

If configured:

```bash
# Page metadata
curl -s -H "Authorization: Bearer <NOTION_API_TOKEN>" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/<PAGE_ID>" | python3 -m json.tool

# Page content (blocks)
curl -s -H "Authorization: Bearer <NOTION_API_TOKEN>" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/blocks/<PAGE_ID>/children?page_size=100" | python3 -m json.tool
```

Parse blocks recursively — extract `rich_text[].plain_text` from each block type. Present in readable format.

## Identifier

Ask for a plan identifier:
> "What identifier should I use? A Jira ticket number if one exists (e.g., APKNOWLEDG-640) or a short label (e.g., `redesign-search`)."

## Workflow

### 1. Challenge the problem
Read `~/.claude/skills/hnh-plan/references/plan-workflow.md` Phase 1. Notion pages tend to be detailed but may describe a solution without justifying it — question the approach.

### 2. Interview
Read `~/.claude/skills/hnh-plan/references/plan-workflow.md` Phase 2. Start by summarizing the Notion page. Help extract concrete acceptance criteria from the prose.

### 3. Deep investigation
Launch two agents in parallel from `~/.claude/skills/hnh-plan/agents/`:

| Agent | File | What it does |
|-------|------|-------------|
| Context Gatherer | `~/.claude/skills/hnh-plan/agents/context-gatherer.md` | Prior attempts, git history, related issues, architecture docs, current state |
| Architecture Analyst | `~/.claude/skills/hnh-plan/agents/architecture-analyst.md` | Full system impact, dependencies, API contracts, DB changes, performance, security, alternative approaches |

### 4. Approach decision
Present alternatives with tradeoffs. Get user sign-off.

### 5. Write the plan
Follow the Plan Template in `~/.claude/skills/hnh-plan/references/plan-workflow.md`.
- Save to `~/.claude/plans/{IDENTIFIER}/{YYYY-MM-DD-description}.md`
- Link back to the Notion page URL in the plan header

### 6. Review
Show the plan. Iterate until satisfied.

## Credential Reference

Tokens in `~/.zshrc` — read and inline literal values. See `~/.claude/memory/credentials.md`.
