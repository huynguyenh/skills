---
name: hnh-create-pr
description: >
  Wrap up a coding session into a pull request — commit changes, create a branch, push, open a PR
  with a human-readable description, self-review with /hnh-review-pr, fix findings, and post the
  outcome. Use this skill whenever the user says "create a PR", "wrap this up", "open a PR",
  "submit a PR", "make a pull request", "send this for review", or wants to turn their current
  work into a PR. Also trigger when the user finishes implementing a feature/fix and says something
  like "let's get this merged", "ready for review", or "push this up". This skill handles the entire
  PR lifecycle from uncommitted changes to a review-ready pull request.
---

# Create PR

Wraps up the current session's work into a clean, review-ready pull request. Handles everything:
branch creation, committing, pushing, PR description, self-review, fixing findings, and posting
the final review as PR comments.

## Prerequisites

- Must be inside a git repository
- Must have changes to commit (staged, unstaged, or untracked)
- `gh` CLI must be authenticated (`gh auth status`)
- Git identity must be configured (see `~/.claude/rules/global-github.md`)

## Workflow

### Step 1: Gather context

Before doing anything, collect what you need. Ask the user for anything not already clear
from the session context:

1. **Base branch** — which branch to target (e.g., `main`, `develop`). If unclear, ask.
2. **Jira ticket number** — needed for branch naming. If the user is already on a feature
   branch with a ticket number, extract it. Otherwise, ask.
3. **Branch name** — if the user is already on a feature branch, use it. If on `main` or
   `develop`, create one using the format: `{type}/{TICKET-NUMBER}-short-description`
   - Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`
   - Example: `feat/APKNOWLEDG-640-add-search-endpoint`
   - Ask the user for the type if not obvious from context.

Don't ask questions you can answer from context. If the user just spent the session fixing
a bug on branch `fix/PROJ-123-null-pointer`, you already know everything.

### Step 2: Stage and commit

1. Verify git identity is configured:
   ```bash
   git config user.name && git config user.email
   ```
   If not set, configure it per `~/.claude/rules/global-github.md`.

2. Review what needs to be committed:
   ```bash
   git status
   git diff
   ```

3. Stage relevant files — be specific, don't blindly `git add -A`. Exclude:
   - `.env`, credentials, secrets
   - Large binaries or generated files that shouldn't be tracked
   - Temporary/debug files

4. Commit with a clear message. Keep it concise — what changed and why. No AI attribution.

If there are already commits on the branch that cover the work, skip this step.

### Step 3: Push the branch

```bash
git push -u origin {branch-name}
```

If the branch already tracks a remote and is up to date, skip.

### Step 4: Write the PR description

Write the PR description in plain, simple English. Write for a human reviewer — short
sentences, no jargon walls, no AI-generated fluff.

**Before writing**, check if the repo has a PR template:
```bash
# Check common template locations
ls .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
ls .github/pull_request_template.md 2>/dev/null
ls docs/pull_request_template.md 2>/dev/null
ls PULL_REQUEST_TEMPLATE.md 2>/dev/null
# Also check for multiple templates
ls .github/PULL_REQUEST_TEMPLATE/ 2>/dev/null
```

**If a template exists**: read it and fill in each section. Respect the structure — don't
skip sections or rearrange. If a section doesn't apply, write "N/A" or "None" rather than
deleting it.

**If no template exists**, use this simple format:
```
## What
{1-2 sentences: what this PR does}

## Why
{1-2 sentences: why this change is needed}

## How
{bullet points: key implementation decisions, if any are non-obvious}

## Testing
{what was tested and how}
```

**Writing style guidelines:**
- Short sentences. Say what changed, not what you thought about changing.
- No "This PR implements..." — just say what it does.
- No bullet-point walls. If you need more than 5 bullets, you probably need a smaller PR.
- Link the Jira ticket if there is one.
- No AI attribution of any kind.

### Step 5: Create the PR

```bash
gh pr create \
  --base {base-branch} \
  --title "{concise title}" \
  --body "$(cat <<'EOF'
{PR description from Step 4}
EOF
)"
```

Keep the title under 70 characters. Use imperative mood: "Add search endpoint" not
"Added search endpoint" or "This PR adds a search endpoint".

Save the PR number and URL — you'll need them for the review step.

### Step 6: Self-review with /hnh-review-pr

Run `/hnh-review-pr` on the PR you just created. This is not optional — every PR gets
reviewed before the user sees it.

Pass the PR URL to the review skill and let it run the full review workflow (all agents
in parallel, verification phase, final report).

### Step 7: Fix findings

Go through the review report and fix everything that's clearly correct:

- **CRITICAL**: Fix all of them. These are merge blockers.
- **WARNING**: Fix all of them unless you have a good reason not to.
- **SUGGESTION**: Fix the ones that make sense. Skip if it's purely stylistic and debatable.
- **CLEAN CODE**: Fix the clear wins (bad naming, unnecessary complexity). Skip subjective ones.
- **DRY VIOLATIONS**: Fix if there's a genuine duplicate. Skip if the "duplication" is intentional.

For each fix:
1. Make the code change
2. Commit with a descriptive message referencing the finding (e.g., "fix: handle nil case in search handler")
3. Push

Don't batch all fixes into one giant commit — group logically related fixes together.

### Step 8: Post outcome as PR comment

After fixing everything, post a summary comment on the PR:

```bash
gh pr comment {pr-number} --body "$(cat <<'EOF'
## Self-review complete

**Findings fixed:**
- {C1: description — fixed in commit abc123}
- {W1: description — fixed in commit def456}
- ...

**Findings skipped (with reason):**
- {S3: description — skipped because ...}

**Review status:** Ready for human review.
EOF
)"
```

Then tell the user: here's the PR link, here's what was found and fixed, it's ready for
review.

## Important rules

- **Always use `gh` CLI** for all GitHub operations. Never use raw `curl` to the GitHub API.
- **Never add AI attribution** — no "Generated with Claude Code", no co-author trailers.
- **Ask before acting** when context is ambiguous. Don't guess the base branch or ticket number.
- **Respect the repo's conventions** — if you see a PR template, use it. If you see a commit
  message convention in recent history, follow it.
- **Don't create empty PRs** — if there are no changes to commit, tell the user and stop.
