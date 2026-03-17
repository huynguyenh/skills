# Principal Engineer Planning Workflow

This is the shared planning process used by all three plan skills. It's designed to produce plans that a principal engineer would be proud of — plans that anticipate problems, consider alternatives, and don't leave testing or deployment as afterthoughts.

The philosophy: **spend more time thinking, less time fixing.** A thorough plan saves 10x the time it takes to create.

## Phase 1: Challenge the Problem

Before planning *how* to implement something, a principal engineer asks *whether* and *why*.

After reading the ticket/description, critically evaluate it:

- **Is this solving the right problem?** Sometimes tickets describe a solution when the actual problem is different. If the ticket says "add a cache for X" but the real issue is an N+1 query, flag it.
- **Is this the right scope?** Too big = risky, too small = misses the point. Should it be split? Should it be expanded to include a related fix?
- **Is the timing right?** Are there dependencies that should land first? Is there related work in flight that this should coordinate with?
- **What happens if we do nothing?** Understanding the cost of inaction helps prioritize.

Present your assessment to the user. If you have concerns about the approach, raise them now — not after spending hours on a detailed plan. Be direct: "I think we should consider X instead because Y."

## Phase 2: Interview

The interview fills the gaps between what the ticket says and what you need to know. Tickets are written by humans who assume context — your job is to surface that hidden context.

### What to ask about

**Requirements:**
- What does "done" look like? (Concrete acceptance criteria, not "it works")
- What are the non-functional requirements? (Performance targets, latency SLAs, data volume expectations)
- Who are the users/consumers of this change?

**Scope:**
- What's explicitly out of scope? (Prevents scope creep during implementation)
- Are there follow-up tickets planned? (Affects how much abstraction/extensibility to build in)

**Technical:**
- Are there specific patterns, libraries, or approaches that must be used?
- Are there things that have been tried before and failed? Why?
- Is there a preference between the approaches you identified in Phase 1?

**Risk:**
- What's the worst case if this breaks in production?
- Is there a deadline or event driving the timeline?
- Do we need to coordinate with other teams or services?

**Testing:**
- What level of confidence do we need? (Quick fix vs. critical path change)
- Are there existing test suites that cover this area?
- Do we need load testing or security review?

Keep asking until there are no ambiguities. Short, focused questions > long lists. Follow up on anything that feels hand-wavy.

## Phase 3: Deep Investigation

This is where a principal engineer's plan diverges from a junior's. Launch two agents in parallel to gather comprehensive context:

| Agent | File | What it does |
|-------|------|-------------|
| Context Gatherer | `agents/context-gatherer.md` | Prior attempts, git history, related issues, architecture docs, current system state |
| Architecture Analyst | `agents/architecture-analyst.md` | Full system impact, dependency mapping, API contracts, DB changes, performance, security, alternative approaches |

Read each agent's `.md` file and launch them with the ticket context + interview answers.

**What you get back:**
- Whether anyone has tried this before (and what happened)
- The full impact radius of the change
- Database migration requirements
- API backward compatibility assessment
- 2-3 alternative approaches with tradeoffs
- Security and performance considerations
- Red flags and risks

Review the agent results carefully. If they found prior failed attempts, understand why they failed. If they identified risks you hadn't considered, add them to your mental model.

## Phase 4: Approach Decision

Before writing the plan, commit to an approach. The Architecture Analyst proposed alternatives — now decide:

1. Present the options to the user with clear tradeoffs
2. Make a recommendation and explain your reasoning
3. Get the user's sign-off before proceeding

Document the decision and the reasoning — future you (or someone else reading the plan) needs to understand *why* this approach was chosen.

## Phase 5: Write the Plan

Save to: `~/.claude/plans/{IDENTIFIER}/{YYYY-MM-DD-short-description}.md`

Check if `~/.claude/plans/{IDENTIFIER}/` already has plans — read them first.

### Plan Template

```markdown
# {Identifier}: {Title}

**Ticket**: {link to Jira/Notion, or "N/A"}
**Date**: {YYYY-MM-DD}
**Status**: Draft
**Branch**: `{type}/{IDENTIFIER}-short-description` (suggested)

## Context

{2-4 sentences: what this change does, why it matters, and the business impact if it doesn't get done}

## Decision

**Chosen approach**: {name of the approach}

**Why this approach**: {2-3 sentences explaining the reasoning}

**Alternatives considered**:
- {Option B}: Rejected because {reason}
- {Option C}: Rejected because {reason}

## Acceptance Criteria

- [ ] {Concrete, testable criterion 1}
- [ ] {Concrete, testable criterion 2}
- [ ] ...

## Scope

**In scope:**
- {bullet points}

**Out of scope:**
- {bullet points — explicitly documenting what we're NOT doing}

**Follow-up work** (separate tickets):
- {Things we identified but deferred}

## System Impact

### Files Changed
| File | Change type | Description |
|------|------------|-------------|
| `path/to/file.go` | Modify | {what changes and why} |
| `path/to/new_file.go` | Create | {what it does} |
| ... | ... | ... |

### Database Changes
{Migration details, or "None"}
- Migration: {description}
- Downtime risk: {none/low/high — explain}
- Data backfill: {needed/not needed}
- Rollback: {how to reverse the migration}

### API Changes
{Contract changes, or "None"}
- {Endpoint}: {what changes}
- Backward compatible: {yes/no — explain}
- Client updates needed: {list affected clients}

### Dependencies
- {Upstream}: {what this depends on}
- {Downstream}: {what depends on this — verify it still works}

## Implementation Steps

Order these for safety — things that are easy to revert go first, risky changes go last. Each step should be independently reviewable and ideally independently deployable.

### Step 1: {description}
**Files**: `path/to/file.go`
**Why this first**: {sequencing rationale}

{What to change and why. Include current code state and intended change.}

```
// Current
{relevant code snippet}

// After
{what it should look like}
```

### Step 2: {description}
...

### Step N: {description}
...

## Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| {what could go wrong} | Low/Med/High | Low/Med/High | {how we prevent or handle it} |
| ... | ... | ... | ... |

### Rollback Plan
{If this change causes problems in production, here's how to revert:}
1. {Step 1}
2. {Step 2}

### Feature Flag
{Do we need a feature flag? If yes, describe the flag and the rollout strategy. If no, explain why not.}

## Testing Strategy

### Testing Pyramid
{Describe the overall testing approach — where does the confidence come from?}

### Unit Tests

| Test file | Test case | What it verifies | Priority |
|-----------|-----------|-----------------|----------|
| `path/to/file_test.go` | `TestX_WhenY_ExpectZ` | {behavior} | Must have |
| ... | ... | ... | ... |

**Edge cases to cover:**
- {Empty input}
- {Nil values}
- {Concurrent access}
- {Boundary values}
- {Error conditions}

### Integration Tests

| Scenario | Setup | Action | Expected Result |
|----------|-------|--------|----------------|
| Happy path | {preconditions} | {trigger} | {outcome} |
| Error path | {preconditions} | {trigger} | {error handling} |
| ... | ... | ... | ... |

### Automation / E2E Tests
{If the project has E2E tests:}
- {What scenarios to automate}
- {Which test framework/tool to use}
- {Or: "No E2E framework — manual testing covers this"}

### Performance Testing
{If the change affects performance-sensitive code:}
- Benchmark: {what to measure}
- Expected: {target numbers}
- Tool: {how to measure — e.g., `go test -bench`, k6, etc.}
- {Or: "Not performance-sensitive — skip"}

### Security Testing
{If the change touches auth, user input, or data:}
- {What to verify — e.g., "auth bypass not possible", "input sanitized"}
- {Or: "No new security surface"}

### Manual Verification
{Step-by-step instructions anyone can follow:}
1. {Setup step}
2. {Action}
3. {Expected result — be specific}
4. ...

### Test Checklist
- [ ] All new code paths have unit tests
- [ ] Edge cases covered (listed above)
- [ ] Existing tests still pass
- [ ] Integration test covers happy + error paths
- [ ] Performance acceptable (if applicable)
- [ ] Security reviewed (if applicable)
- [ ] Manual verification completed

## Observability

{How will we know this is working correctly in production?}

### Logging
- {New log lines to add and their purpose}
- {Log level choices (info for business events, warn for recoverable errors, error for failures)}

### Metrics
- {New metrics to track — e.g., request count, latency, error rate}
- {Or: "Existing metrics cover this"}

### Alerts
- {New alerts needed — e.g., "error rate > X for 5 min"}
- {Or: "Existing alerts cover this"}

### Monitoring
- {Dashboard changes}
- {What to watch during the first 24h after deploy}

## Deployment

### Pre-deployment
- [ ] All tests pass in CI
- [ ] PR reviewed and approved
- [ ] Database migration tested in staging (if applicable)
- [ ] Feature flag configured (if applicable)

### Deployment Steps
1. {If there's a specific order — e.g., "deploy migration first, then service"}
2. {Or: "Standard deploy — no special steps"}

### Post-deployment Verification
1. {Check X endpoint returns expected response}
2. {Verify metrics look normal}
3. {Check logs for errors}
4. {Monitor for 30 min / 24h depending on risk}

### Rollback Trigger
{Under what conditions do we rollback? Be specific:}
- Error rate exceeds {X}%
- Latency exceeds {X}ms p99
- {Business metric} drops below {threshold}

## Report

Update this section when implementation is complete:

### What We Did
- {Summary of changes — approach taken, deviations from plan, surprises}

### What We Tested
- Unit tests: {X added/modified — all passing}
- Integration tests: {Y scenarios — results}
- Manual verification: {what was checked, results}
- Performance: {benchmark results, or "N/A"}

### What We Observed After Deploy
- {Metrics, logs, any anomalies}
- {Or: "Not yet deployed"}

### What's Left
- {Follow-up work, tech debt, cleanup}
- {Or: "Nothing — all acceptance criteria met, monitoring clean"}
```

## Phase 6: QA Verification (During Implementation)

**This phase runs during implementation, not during planning.** But the plan must account for it.

Every implementation step must be verified before moving to the next step or shipping to the user. Read `agents/qa-verifier.md` for the full process.

### Key Rule: Verify the Mechanism First

For system-level features (event handling, keyboard input, networking, filesystem, OS APIs), **always write a minimal standalone test** that exercises the specific mechanism in isolation before integrating it into the app.

This prevents the pattern of: "it should work in theory" → build → ship → broken → rebuild → ship → broken × 5.

Examples:
- Implementing keyboard shortcut capture? Write a 30-line script that captures keys and prints them. Run it. See it work. Then integrate.
- Adding a CGEvent tap? Write a standalone tap that logs events. Run it. Verify. Then integrate.
- Using a new API? Call it from a test script first. Confirm the response. Then use it in the app.

### Verification Checklist (include in every plan)

Add this to each Implementation Step:

```markdown
**Verification:**
- [ ] Build passes with no new warnings
- [ ] Core mechanism verified in isolation (standalone test script)
- [ ] Integration verified (app runs correctly with this change)
- [ ] Existing tests still pass
- [ ] Confidence: High/Medium — never ship at Low
```

## After Writing

1. Show the full plan to the user
2. Ask for feedback — iterate until they're satisfied
3. Confirm: "Ready to start implementing? I'll follow this plan step by step, verify each step with the QA agent, and update the Report section as we go."
