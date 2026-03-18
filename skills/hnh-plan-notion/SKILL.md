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

## Phase 0a: Read Project CLAUDE.md

Before starting, check if the repository (cwd or the target repo) has a `CLAUDE.md` at its root. If it exists, read it — it contains project-specific conventions, architecture context, and patterns that should inform the plan. Pass relevant context to investigation agents.

## Phase 0b: Fetch Notion Page

Use the `hnh-notion` skill's CLI tool to fetch the page. Read `~/.zshrc` for `NOTION_API_TOKEN`, then:

```bash
NOTION_TOKEN="<value from ~/.zshrc>"
python3 ~/.claude/skills/hnh-notion/scripts/notion.py --token "$NOTION_TOKEN" read <PAGE_ID>
```

This returns the page title, properties, and all content rendered as readable text — no need to parse blocks manually.

If the token is missing or a placeholder, tell the user:

> "No Notion token configured. See the hnh-notion skill for setup instructions, or:
> 1. Go to https://www.notion.so/my-integrations and create an internal integration
> 2. Add the token to `~/.zshrc` as `NOTION_API_TOKEN`
> 3. Share the Notion page with the integration"

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

### 7. QA Verification (during implementation)
After each implementation step, run the QA Verifier agent (`~/.claude/skills/hnh-plan/agents/qa-verifier.md`). **Never ship code without verification.** For system-level features, always write and run a standalone test script to verify the mechanism in isolation first.

### 8. PR creation
After implementation is complete, ask the user: **"Should I create a PR?"** If yes:
1. Create the PR
2. Run `/hnh-review-pr` on the PR
3. Fix all findings from the review
4. Report back with the final PR link

## Implementation Discipline

**The approved plan is a contract.** Implement it exactly as written — do not simplify, flatten, or skip parts of the plan during implementation. If you realize a change would be better mid-implementation, STOP and ask the user before deviating. Never silently change the approach.

## Credential Reference

Tokens in `~/.zshrc` — read and inline literal values. See `~/.claude/rules/global-credentials.md`.
