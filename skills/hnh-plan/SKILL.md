---
name: hnh-plan
description: Create a principal-engineer-level implementation plan for a task, feature, or bug fix from a plain text description or conversation context. Use this skill whenever the user says "plan this", "create a plan", "how should we implement this", or wants to think through implementation before writing code — even if they don't explicitly say "plan". If the user provides a Jira ticket or Notion page, use /hnh-plan-jira or /hnh-plan-notion instead — those fetch the ticket details automatically.
---

# Implementation Planning (Plain Text)

Create a thorough, principal-engineer-level implementation plan from a plain text description or conversation context.

## Input

The user provides a description of what they want to build or fix. No ticket to fetch — context comes from the user and the codebase.

## Identifier

Every plan needs an identifier for the directory name. Check if the current git branch has a ticket number — if so, use it. Otherwise, ask:

> "What identifier should I use for this plan? A Jira ticket number (e.g., APKNOWLEDG-640) or a short label (e.g., `refactor-auth`)."

## Workflow

### 0. Read Project CLAUDE.md

Before starting, check if the repository (cwd or the target repo) has a `CLAUDE.md` at its root. If it exists, read it — it contains project-specific conventions, architecture context, and patterns that should inform the plan. Pass relevant context to investigation agents.

### 1. Challenge the problem
Read `references/plan-workflow.md` Phase 1. Before planning how, ask whether and why. Present your assessment to the user.

### 2. Interview
Read `references/plan-workflow.md` Phase 2. Ask targeted questions until requirements are completely clear. Do not proceed with ambiguities.

### 3. Deep investigation
Launch two agents in parallel. Read each agent's `.md` file from `agents/` and pass the ticket context + interview answers:

| Agent | File | What it does |
|-------|------|-------------|
| Context Gatherer | `agents/context-gatherer.md` | Prior attempts, git history, related issues, architecture docs, current state |
| Architecture Analyst | `agents/architecture-analyst.md` | Full system impact, dependencies, API contracts, DB changes, performance, security, alternative approaches |

Ask the user which repo/service this relates to if not obvious from the conversation context.

### 4. Approach decision
Present alternative approaches from the Architecture Analyst with tradeoffs. Get user sign-off before writing the plan.

### 5. Write the plan
Follow the Plan Template in `references/plan-workflow.md`. Save to `~/.claude/plans/{IDENTIFIER}/{YYYY-MM-DD-description}.md`.

### 6. Review
Show the plan. Iterate until the user is satisfied.

### 7. QA Verification (during implementation)
After each implementation step, run the QA Verifier agent (`agents/qa-verifier.md`). **Never ship code without verification.**

| Agent | File | What it does |
|-------|------|-------------|
| QA Verifier | `agents/qa-verifier.md` | Build check, mechanism isolation test, integration verification, regression check |

**Critical rule**: For system-level features (event handling, keyboard input, OS APIs, networking), always write and run a standalone test script that verifies the mechanism in isolation BEFORE integrating it into the app.

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
