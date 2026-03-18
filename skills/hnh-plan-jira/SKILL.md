---
name: hnh-plan-jira
description: Create a principal-engineer-level implementation plan from a Jira ticket. Use this skill whenever the user provides a Jira ticket URL (e.g., https://your-org.atlassian.net/browse/TICKET-123), a bare ticket ID (e.g., APKNOWLEDG-640), or says "plan this Jira ticket". Fetches the ticket details first (summary, description, acceptance criteria, comments, linked issues), then challenges the approach, interviews the user, launches parallel agents to explore the codebase and gather context, and produces a comprehensive plan with alternative approaches, risk analysis, detailed testing strategy, observability, and deployment steps.
---

# Implementation Planning (Jira)

Create a thorough, principal-engineer-level implementation plan starting from a Jira ticket.

## Input Parsing

Accept:
- Full URL: `https://{host}/browse/TICKET-123`
- Bare ID: `APKNOWLEDG-640`, `TICKET-123`
- From branch: extract ticket ID from current git branch if it matches `{type}/{TICKET}-description`

## Phase 0a: Read Project CLAUDE.md

Before starting, check if the repository (cwd or the target repo) has a `CLAUDE.md` at its root. If it exists, read it — it contains project-specific conventions, architecture context, and patterns that should inform the plan. Pass relevant context to investigation agents.

## Phase 0b: Fetch Jira Ticket

Read `~/.zshrc` for `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, then:

```bash
curl -s -u "<JIRA_EMAIL>:<JIRA_API_TOKEN>" \
  "<JIRA_BASE_URL>/rest/api/3/issue/<TICKET-ID>?fields=summary,description,status,issuetype,priority,assignee,comment,attachment,issuelinks,subtasks" \
  | python3 -m json.tool
```

Extract and present:
- **Summary** and **description** (parse ADF — extract text nodes recursively)
- **Acceptance criteria** (often in description or a custom field)
- **Status**, **priority**, **assignee**
- **Comments** — especially from the reporter or PM (clarifications that didn't make it into the description)
- **Linked issues** — blockers, parent epics, related work
- **Subtasks** — if this is a parent ticket
- **Attachments** — note them (can't fetch binary, but user should know they exist)

## Workflow

### 1. Challenge the problem
Read `~/.claude/skills/hnh-plan/references/plan-workflow.md` Phase 1. Critically evaluate the ticket — is this the right solution to the right problem?

### 2. Interview
Read `~/.claude/skills/hnh-plan/references/plan-workflow.md` Phase 2. Start by summarizing the Jira ticket, then ask targeted questions. Tickets are often incomplete — surface the hidden context.

### 3. Deep investigation
Launch two agents in parallel. Read each agent's `.md` file from `~/.claude/skills/hnh-plan/agents/` and pass the ticket context + interview answers:

| Agent | File | What it does |
|-------|------|-------------|
| Context Gatherer | `~/.claude/skills/hnh-plan/agents/context-gatherer.md` | Prior attempts, git history, related issues, architecture docs, current state |
| Architecture Analyst | `~/.claude/skills/hnh-plan/agents/architecture-analyst.md` | Full system impact, dependencies, API contracts, DB changes, performance, security, alternative approaches |

Ask the user which repo/service this relates to if not obvious from the Jira project key.

### 4. Approach decision
Present alternatives with tradeoffs. Get user sign-off.

### 5. Write the plan
Follow the Plan Template in `~/.claude/skills/hnh-plan/references/plan-workflow.md`.
- Identifier = Jira ticket ID
- Save to `~/.claude/plans/{TICKET-ID}/{YYYY-MM-DD-description}.md`
- Link back to the Jira ticket URL in the plan header

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
