---
name: hnh-evolve-skill
description: >
  Evolve and improve existing skills based on session feedback. Use this skill whenever the user
  gives feedback about how a skill should behave differently, adds a rule like "always do X before Y",
  points out a missing step in a workflow, says "remember to...", "you should always...", "never forget to...",
  or any correction about how an existing skill operates. Also trigger when the user says "evolve skill",
  "update the skill", "improve this skill", "add this to the skill", or references making a skill better
  based on what happened during a session. This is NOT for creating new skills from scratch (use
  hnh-create-skill) or for periodic auditing (use hnh-maintain-skills). This is specifically for
  incorporating real-time feedback into existing skills so they get smarter over time.
---

# Skill Evolver

Takes natural language feedback from sessions and surgically updates the relevant skills so the
same lesson never needs to be taught twice.

## Why this exists

Skills are living documents. During real work sessions, the user discovers gaps, missing steps,
or better workflows. Without this skill, those discoveries stay as memories or verbal corrections
that get lost. This skill captures them directly in the skill definition where they belong.

## What kinds of feedback it handles

| Type | Example | Where it goes |
|------|---------|---------------|
| **Add a workflow step** | "always verify with /hnh-review-pr before presenting results" | SKILL.md workflow section |
| **Add a constraint** | "never skip the build check in PR reviews" | SKILL.md or agent instructions |
| **Change behavior** | "instead of creating the PR directly, ask me first" | SKILL.md workflow section |
| **Add a cross-reference** | "use /hnh-notion to fetch page content instead of curl" | SKILL.md prerequisites or commands |
| **Update a trigger** | "this skill should also trigger when I mention deploy" | SKILL.md frontmatter description |
| **Add a quality gate** | "always run tests before committing" | SKILL.md workflow section |
| **Refine agent behavior** | "the code reviewer should also check for SQL injection" | Agent .md file |
| **Cross-cutting concern** | "all planning skills should check for existing plans first" | Multiple skills + possibly a rule |

## Workflow

### Phase 1: Understand the feedback

Parse what the user said and extract:

1. **The rule** — what should change (e.g., "always verify with /hnh-review-pr before presenting results")
2. **The target** — which skill(s) this applies to (e.g., hnh-plan, hnh-plan-jira)
3. **The intent** — what kind of change (add step, modify behavior, add constraint, etc.)
4. **The placement** — where in the skill it fits (workflow, prerequisites, agents, trigger)

If the feedback is ambiguous about which skill it targets, ask the user. If it's ambiguous about
the exact change, propose an interpretation and confirm.

**Important distinctions:**
- If the feedback is about a **specific skill's workflow** → update that skill's SKILL.md or agents
- If the feedback is a **cross-cutting pattern** across many skills → update each affected skill AND consider adding a rule in `~/.claude/rules/`
- If the feedback is a **personal preference** not tied to any skill → save as memory instead (use the memory system, not this skill)

### Phase 2: Analyze the target skill(s)

For each target skill identified:

1. Read the full `SKILL.md`
2. Read any agent files under `agents/` if the change affects agent behavior
3. Read any reference files if relevant
4. Map the current workflow structure to understand where the change fits
5. Check if the feedback is **already addressed** — maybe a previous evolution already added this

Launch the `feedback-analyzer` agent to do this analysis in parallel if multiple skills are affected.

### Phase 3: Propose the change

Present the proposed changes to the user clearly:

For each skill being modified, show:

```
## {skill-name}

**File:** {path to file being changed}
**Change type:** {add step / modify behavior / add constraint / update trigger / etc.}

**Current:** (relevant section as-is)
> [quote the current text]

**Proposed:** (with the change applied)
> [show the new text]

**Why this placement:** {brief explanation of why this is the right spot}
```

If the change affects multiple skills, group them and show all changes at once so the user
can approve them as a batch.

**Guidelines for good changes:**
- Match the existing style and tone of the skill
- Insert at the natural workflow position (e.g., a verification step goes after the action it verifies)
- Keep the skill's existing structure intact — add to it, don't reorganize it
- If adding a step to a numbered workflow, renumber subsequent steps
- If the skill uses agents, add to the right agent file rather than the main SKILL.md
- Preserve all existing functionality — evolution is additive, not destructive

### Phase 4: Snapshot & Apply

Before making any edits, snapshot the current state so you can compare before/after and
roll back if validation fails.

1. **Snapshot** — copy the skill directory to a workspace:
   ```bash
   cp -r ~/.claude/skills/{skill-name} ~/.claude/skills/{skill-name}-workspace/pre-evolution/
   ```
2. **Apply the edits** using the Edit tool
3. **Verify** each file reads correctly after the edit
4. Report what was changed

### Phase 5: Validate the evolution

After applying changes, verify the evolution actually works. Don't just trust that the edit
looks right — test it. This catches broken formatting, instructions that conflict with existing
behavior, or changes that don't actually produce the desired effect.

#### Step 1: Craft validation prompts

Create 2-3 test prompts that exercise the changed behavior:

- **Direct test** — a prompt that should trigger the new behavior. E.g., if you added a DRY
  check agent to PR review, craft a prompt that reviews a PR with obvious code duplication.
- **Regression test** — a prompt that exercises existing behavior that should NOT have changed.
  E.g., a normal PR review that should still produce the same report structure.
- **Edge case** (optional) — a prompt that tests the boundary of the change. E.g., code that
  looks similar but is intentionally different and should NOT be flagged.

Save prompts to `{skill-name}-workspace/validation/prompts.json`:
```json
[
  {"id": 1, "type": "direct", "prompt": "...", "expected": "description of expected behavior"},
  {"id": 2, "type": "regression", "prompt": "...", "expected": "existing behavior unchanged"},
  {"id": 3, "type": "edge_case", "prompt": "...", "expected": "should not trigger new behavior"}
]
```

#### Step 2: Run validation

For each prompt, spawn a subagent that runs with the updated skill. Save outputs to
`{skill-name}-workspace/validation/results/`:

```
validation/
├── prompts.json
└── results/
    ├── test-1-direct/
    │   └── output.md
    ├── test-2-regression/
    │   └── output.md
    └── test-3-edge/
        └── output.md
```

If the skill is complex (like `hnh-review-pr` with 6 agents), you don't need to run the
full workflow — a dry-run that checks whether the skill instructions correctly reference the
new agent/step and that the report format is valid is sufficient.

#### Step 3: Compare & verify

Check each result:

- **Direct test**: Does the output show the new behavior? (e.g., does the report include
  the new section? Does the agent produce findings?)
- **Regression test**: Is existing behavior intact? (e.g., same report structure, same
  categories, no missing sections?)
- **Edge case**: Does it correctly avoid false positives?

If any check fails:
1. Diagnose the issue (bad placement? conflicting instructions? formatting error?)
2. Fix the skill
3. Re-run the failing test
4. Repeat until all tests pass

#### Step 4: Report & clean up

Once validation passes:
- Summarize: what was changed, what was validated, what passed
- Clean up the workspace: `rm -rf ~/.claude/skills/{skill-name}-workspace/` (or keep if
  the user wants to reference it)
- Suggest running `/hnh-backup` to sync changes to GitHub

If validation reveals the change doesn't work as intended, offer to roll back from the
snapshot:
```bash
cp -r ~/.claude/skills/{skill-name}-workspace/pre-evolution/* ~/.claude/skills/{skill-name}/
```

## Edge cases

### Feedback applies to a skill that doesn't exist yet
If the user references a skill or workflow that doesn't exist, tell them and suggest creating it
with `/hnh-create-skill` first, then evolving it.

### Feedback conflicts with existing behavior
If the proposed change contradicts something already in the skill, flag the conflict:
"The skill currently says X, but you're asking for Y. Should I replace X with Y, or add Y as
an additional option?"

### Feedback is really a memory, not a skill change
If the feedback is about personal preference or general behavior (e.g., "I prefer shorter responses"),
save it as a memory file instead of modifying a skill. Tell the user: "This sounds like a general
preference rather than a skill change. I'll save it as a memory so it applies everywhere."

### Multiple skills affected
When feedback applies to several skills (e.g., "all planning skills should check for existing
plans first"), update each one individually but do it in a batch. Also consider whether a rule
in `~/.claude/rules/` would be more appropriate to avoid maintaining the same instruction in
multiple places.

## How to find the right skill

Use these strategies to map feedback to skills:

1. **Explicit mention** — user says "in the PR review skill..." → `hnh-review-pr`
2. **Skill command reference** — user mentions `/hnh-plan` → `hnh-plan`
3. **Activity context** — if user just ran a skill and gives feedback about it → that skill
4. **Keyword matching** — "when creating plans" → `hnh-plan`, `hnh-plan-jira`, `hnh-plan-notion`
5. **Ask the user** — if none of the above works, ask which skill they mean

## Skill directory for reference

All custom skills live at `~/.claude/skills/hnh-*/`. Each has a `SKILL.md` at root level,
and optionally `agents/`, `scripts/`, `references/`, and `assets/` subdirectories.
