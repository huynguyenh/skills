# Agent: Feedback Analyzer

Analyze a target skill to understand its structure and determine exactly where and how to
integrate a piece of user feedback.

## Inputs

- **Feedback rule**: The extracted rule/improvement from the user's feedback
- **Target skill name**: Which skill to analyze (e.g., `hnh-plan`)
- **Change intent**: What kind of change (add step, modify behavior, add constraint, etc.)

## What to investigate

### 1. Read the full skill

```bash
cat ~/.claude/skills/{skill-name}/SKILL.md
```

Understand:
- The overall structure (sections, headings, workflow phases)
- The current workflow steps (numbered or described)
- Any existing constraints or quality gates
- Prerequisites and dependencies on other skills
- The tone and style of writing

### 2. Check for agent files

```bash
ls ~/.claude/skills/{skill-name}/agents/ 2>/dev/null
```

If agents exist, read each one to understand:
- What each agent is responsible for
- Whether the feedback applies to an agent rather than the main SKILL.md
- The agent's checklist and output format

### 3. Check for existing coverage

Determine if the feedback is already addressed:
- Is there already a step that does what the feedback asks for?
- Is there a partial implementation that needs extending?
- Is there a conflicting instruction?

### 4. Find the insertion point

Identify the exact location where the change should go:
- For workflow steps: which phase/step number
- For constraints: which section
- For trigger updates: the frontmatter description field
- For agent changes: which agent file and which section

## Output

Return a structured analysis:

```markdown
## Skill Analysis: {skill-name}

### Structure
- Total sections: {N}
- Workflow phases: {list of phase names}
- Agent files: {list or "none"}
- Related skills referenced: {list}

### Existing Coverage
- Already addressed: {yes/no/partially}
- If partially: {what's already there and what's missing}
- Conflicts: {any conflicting instructions}

### Recommended Change
- **File**: {path to file to modify}
- **Location**: {section name, after line X, or "new section"}
- **Type**: {insert / replace / append}
- **Context**: {the surrounding text where the change goes}

### Draft Change
{The actual text to insert/replace, written in the skill's existing style}
```

## Red flags

- If the skill doesn't exist, report it immediately — don't try to create it
- If the feedback would fundamentally change the skill's purpose, flag it
- If the change would break an existing workflow step, flag the conflict
- If the same feedback should apply to multiple agent files, list all of them
