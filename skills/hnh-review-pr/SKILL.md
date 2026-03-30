---
name: hnh-review-pr
description: Deep PR review with context gathering, build verification, and principal-engineer-level code review. Use this skill whenever the user shares a GitHub PR URL, mentions reviewing a PR, asks to check/review/audit a pull request, or says "review this PR". Triggers on PR URLs from github.com, PR numbers with repo context, or any request to review code changes in a pull request — even if the user doesn't explicitly say "review".
---

# PR Review

A comprehensive PR review skill that gathers full context, verifies the build, and delivers a principal-engineer-level code review with categorized, actionable findings.

## Input Parsing

Accept any of these formats:
- Full URL: `https://github.com/{owner}/{repo}/pull/1234`
- Short: `owner/repo#123` or `repo#123`
- Just a number: `#123` or `1234` (only if repo context is clear from cwd or conversation)

Extract: `owner`, `repo`, `pr_number`. You'll need these throughout.

## Execution Flow

The review has four phases. Phase 2 launches review agents in parallel. Phase 3 verifies review findings before the final report.

### Phase 0: Read Project CLAUDE.md

Before starting the review, check if the repository has a `CLAUDE.md` file at its root. If it exists, read it — it contains project-specific conventions, patterns, and architecture context that directly inform what counts as a valid finding vs. a false positive. Pass relevant conventions to all review and verification agents so they don't flag established patterns as issues.

### Phase 1: Fetch PR Metadata

Run these `gh` commands to gather everything:

```bash
# PR title, body, head branch, base branch, state, author
gh pr view {pr_number} --repo {owner}/{repo} --json title,body,headRefName,baseRefName,state,author,url,number

# Full diff
gh pr diff {pr_number} --repo {owner}/{repo}

# List of changed files
gh pr view {pr_number} --repo {owner}/{repo} --json files
```

Save the PR URL, title, body, head branch, and diff for use in later phases.

### Phase 2: Parallel Work

Launch all 6 agents in parallel (all in a single tool-call turn). Each agent's detailed instructions are in its own file under `agents/` — read the file and pass its contents as the agent prompt.

| Agent | File | What it does |
|-------|------|-------------|
| A: Document Fetcher | `agents/document-fetcher.md` | Fetch linked Jira/esa/Confluence docs — **blocking dependency** for report context |
| B: Build Verifier | `agents/build-verifier.md` | Checkout PR branch, build, run tests, report pass/fail |
| C: Architecture Review | `agents/architecture-review.md` | Correctness, security, performance, architecture — the serious bugs |
| D: Discussion History | `agents/discussion-history.md` | Fetch review comments, summarize rounds, resolution status |
| E: Clean Code Review | `agents/clean-code-review.md` | Naming, control flow, complexity, early returns — code quality |
| F: DRY Check | `agents/dry-check.md` | Duplicate/near-duplicate code detection — identical blocks, structural twins, reimplemented utilities |

**How to launch each agent:**
1. Read the agent's `.md` file from this skill's `agents/` directory
2. Launch a general-purpose agent with the file contents as instructions, plus the PR-specific context (diff, title, body, owner, repo, pr_number)
3. For agents C and E, also pass the full diff (save to a temp file and reference it)
4. All 5 agents launch in the same tool-call turn for maximum parallelism

### Phase 3: Verification

Review agents sometimes produce findings that sound convincing but are factually wrong — referencing outdated API behavior, misreading logic, or suggesting patterns that contradict the codebase. This phase catches those errors before they reach the final report.

Once Agents C, E, and F complete, collect their findings and launch 3 verification agents in parallel (single tool-call turn):

| Agent | File | What it verifies |
|-------|------|-----------------|
| V1: Fact Checker | `agents/verify-facts.md` | Version numbers, API behavior, library features, deprecation claims, default values |
| V2: Logic Verifier | `agents/verify-logic.md` | Re-reads actual source code to confirm bugs/issues actually exist |
| V3: Pattern Verifier | `agents/verify-codebase.md` | Checks suggestions match the project's actual conventions and patterns |

**How to launch each verification agent:**
1. Read the agent's `.md` file from this skill's `agents/` directory
2. Pass the collected findings from Agents C and E as input
3. Also pass: owner, repo, pr_number, and the list of changed files so they can read source
4. All 3 agents launch in the same tool-call turn

**Processing verification results:**
- **INCORRECT / INCONSISTENT findings** → Remove from the final report entirely, or revise with the corrected information
- **PARTIALLY_CORRECT findings** → Revise the finding to reflect what's actually true, drop the incorrect parts
- **UNVERIFIED factual claims** → Add a caveat note like "(verify: could not confirm version behavior)" so the user knows to double-check
- **VERIFIED / CONFIRMED / CONSISTENT findings** → Keep as-is

This step is not optional — every review must go through verification. The goal is zero false positives in the final report. A shorter, accurate report is far more valuable than a longer one with wrong claims.

### Phase 4: Alignment Check & Report

Once all agents (including verification) complete, synthesize the results.

**Alignment check**: Compare what the PR title/description says the change does vs. what the diff actually does. Flag mismatches — missing changes, undocumented side effects, scope creep, or misleading descriptions.

**Build status**: Include build/test results at the top of the report.

## Report Format

Present the final report in this exact structure:

```
## PR Review: {PR title}
**PR**: {clickable PR URL}
**Author**: {author} | **Branch**: `{head}` → `{base}`
**Linked ticket**: {ticket title + link, or "None found"}

### Review History
{Review round count, reviewers, your comment themes, resolution status, latest state}

### Build Status
{PASS/FAIL with details if failed}

### Alignment
{Does the diff match the PR description? Any scope issues?}

### CRITICAL
None — or list of merge-blocking issues

- **C1.** [{short description}]({github_link}) `{filepath}:{line}`
  {1-2 sentence explanation}
  ```
  // current
  {brief code snippet showing the problem}
  // suggested
  {concrete fix}
  ```

### Warning
None — or list of things that should be fixed but aren't blockers

- **W1.** [{short description}]({github_link}) `{filepath}:{line}`
  {explanation}
  ```
  // current → suggested fix
  ```

### Suggestion
None — or list of improvements worth considering

- **S1.** [{short description}]({github_link}) `{filepath}:{line}`
  {explanation}
  ```
  // current → suggested fix
  ```

### Clean Code
None — or naming, control flow, complexity, early returns findings from Agent E

- **CC1.** [{short description}]({github_link}) `{filepath}:{line}`
  {explanation}
  ```
  // current
  {code snippet}
  // suggested
  {concrete rewrite}
  ```

### DRY Violations
None — or duplicate/near-duplicate code found in the codebase

- **D1.** [{short description}]({github_link}) `{filepath}:{line}`
  Duplicates `{existing_filepath}:{line}` — {explanation}
  ```
  // suggested: extract to shared function or reuse existing
  {concrete fix}
  ```

### Nice to Have
None — or optional polish items

- **N1.** [{short description}]({github_link}) `{filepath}:{line}`
  {explanation}

### What Looks Good
Highlight the positive aspects of the PR — things the author did well that should be recognized and continued.

- {bullet point for each positive aspect — e.g., good test coverage, clean architecture, clear naming, good error handling, thorough documentation, etc.}
```

**GitHub link format** — link directly into the PR file view so the user can jump to the line and leave a comment:

```
https://github.com/{owner}/{repo}/pull/{pr_number}/files#diff-{sha256_hex(filepath)}R{line}
```

The anchor is `diff-` + SHA256 hex digest of the file path (from project root) + `R` + line number (right side = new code). Generate it inline with Python:

```python
import hashlib
anchor = hashlib.sha256(filepath.encode()).hexdigest()
url = f"https://github.com/{owner}/{repo}/pull/{pr_number}/files#diff-{anchor}R{line}"
```

Or use the helper script bundled with this skill:
```bash
python3 ~/.claude/skills/hnh-review-pr/scripts/gh_link.py {owner} {repo} {pr_number} {filepath} {line}
```

Never skip any section. If a category has no findings, show the heading with "None" — this confirms the area was reviewed and nothing was found. This is important for the user to know that every area was checked.

For every finding that involves code, include a brief `// current` and `// suggested` snippet so the user can see exactly what to change without having to open the file.

Keep each finding to 1-2 sentences. The goal is a report you can scan in 60 seconds and know exactly what needs attention.

## Credential Reference

Tokens are in `~/.zshrc` — read the file and inline literal values in commands. Never use `$ENV_VAR` syntax or `source ~/.zshrc`.

| Service | Env vars |
|---------|----------|
| GitHub (work) | `GITHUB_WORK_USERNAME` |
| Jira | `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |
| esa.io | `ESA_ACCESS_TOKEN`, `ESA_TEAM` |
| Sentry | `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_URL` |
| Confluence | Not configured — ask user to set up if needed |
