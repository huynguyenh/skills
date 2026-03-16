---
name: hnh-add-knowledge
description: "Capture and organize personal knowledge into a structured, searchable knowledge base — with automatic reconciliation against existing entries. Use this skill whenever the user shares a fact, tip, lesson learned, or piece of information they want to remember — even if they don't say 'remember' or 'save'. Also use when the user says 'add knowledge', 'note this', 'I learned that', or shares a standalone insight. Trigger on any statement that looks like the user is teaching Claude something they want retained, not just asking a question. Also trigger when the user wants to refresh, rescan, or audit their knowledge base — phrases like 'rescan Drive', 'update knowledge from Notion', 'audit my knowledge', 'refresh what we know about ZenLabs', or 'sync knowledge'. When the user asks a domain-specific question, check the knowledge base first before relying on general information."
---

# Knowledge Base Manager

Capture knowledge the user shares, classify by scope and domain, store in an organized file structure, and — critically — reconcile new information against existing entries so the knowledge base stays accurate and current.

## Storage layout

```
~/.claude/knowledge/
├── INDEX.md          ← auto-generated, lists all scopes/domains
├── global/           ← applies to user broadly (work + personal)
│   ├── docker.md
│   ├── git.md
│   └── ...
├── work/             ← work-specific knowledge
│   ├── kubernetes.md
│   └── ...
└── personal/         ← personal life + own businesses
    ├── zenlabs.md
    └── ...
```

## Scope classification

| Scope | When to use | Examples |
|-------|-------------|---------|
| **Global** | Universally useful — applies across work and personal life | Programming fundamentals, productivity tips, general tech |
| **Work** | Specific to the user's current employment | Internal API quirks, team conventions, infrastructure |
| **Personal** | Personal life, side projects, own businesses | ZenLabs (user's company), personal finance, hobbies |

**Key context:** The user owns a company called ZenLabs. Anything ZenLabs-related is **Personal** scope, not Work.

When the scope is ambiguous, ask. Don't guess.

## Domain detection

Within each scope, identify the domain or project. This becomes the filename.

- Use lowercase kebab-case: `docker.md`, `google-cloud.md`, `zenlabs-ops.md`
- If a domain file already exists, append to it
- If it's genuinely new, create a new file
- Before creating a new domain, check existing files — the knowledge might fit an existing one

Read `INDEX.md` first to see what domains already exist.

## Entry format

Each entry is a bullet point. Group related entries under headings if the file grows. Keep entries concise.

```markdown
# Docker

- Containers use bridge network by default; use `--network host` to share host network stack
- Multi-stage builds reduce image size — use `FROM x AS builder` then `COPY --from=builder`

## Compose
- `depends_on` only waits for container start, not readiness — use healthchecks
```

**Rules:**
- No dates on entries
- Keep each bullet self-contained and scannable
- Use sub-headings to group within a domain when it gets long (10+ entries)

---

## Two operating modes

This skill operates in two modes depending on the user's intent:

### Mode 1: Add Knowledge (default)

When the user shares a fact or insight to remember.

**Workflow:**

1. **Read INDEX.md** to see existing scopes and domains
2. **Classify** the scope and domain
3. **Read the target file** if it exists
4. **Reconcile** the new knowledge against the existing file (see Reconciliation below)
5. **Write** — apply the reconciled changes (add new, update existing, or merge)
6. **Update INDEX.md** if a new domain was created
7. **Confirm** — tell the user what was done: "Added to **personal/zenlabs** (also updated the Drive folder ID which had changed)"

### Mode 2: Rescan & Refresh

When the user asks to refresh knowledge from external sources or audit existing knowledge for accuracy.

Trigger phrases: "rescan Drive", "update knowledge from Notion", "refresh ZenLabs knowledge", "audit my knowledge base", "sync knowledge", "check if our knowledge is still accurate"

**Workflow:**

1. **Read INDEX.md** and all knowledge files to understand current state
2. **Identify sources to scan** — parse the user's request for which sources:
   - "rescan Drive" → use `/hnh-gg-drive` to list current Drive structure
   - "rescan Notion" → use `/hnh-notion` to search/read relevant pages
   - "rescan everything" → all available sources
   - No source specified → scan all, but focus on the scopes/domains the user mentioned
3. **Launch parallel fetch agents** (one per source) to gather current state
4. **Reconcile** fetched data against every relevant knowledge file
5. **Present a diff report** to the user before applying changes
6. **Apply** approved changes

**Parallel fetch strategy for Rescan mode:**

Launch one agent per external source. Each agent's job is to gather current facts and return them as structured output. These run simultaneously to save time.

| Agent | Source | What it fetches |
|-------|--------|----------------|
| Drive Scanner | Google Drive | Current folder structure, file names, folder IDs (via `/hnh-gg-drive`) |
| Notion Scanner | Notion | Page titles, database schemas, key content from relevant pages (via `/hnh-notion`) |

Each agent should:
- Read the agent instructions from `agents/source-scanner.md`
- Receive the current knowledge file content as context (so it knows what to compare against)
- Return a structured list of findings: `{fact, status, evidence}` where status is one of: `new`, `changed`, `unchanged`, `outdated`

After all agents return, reconcile their combined findings against the knowledge base (see below).

---

## Reconciliation

Reconciliation is the process of comparing new information against existing knowledge entries and deciding what to do. This happens in both modes — it's the core intelligence of this skill.

### How it works

When you have new information (whether from the user directly or from a rescan), compare it against every entry in the relevant knowledge file(s):

**For each new piece of information, classify it as:**

| Classification | What it means | Action |
|---------------|---------------|--------|
| **New** | No existing entry covers this topic | Add as a new bullet point |
| **Update** | An existing entry covers the same topic but the details have changed | Replace the old entry with updated information |
| **Merge** | The new info enriches an existing entry without contradicting it | Combine into a single, richer entry |
| **Conflict** | The new info contradicts an existing entry | Flag to the user — present both versions and ask which is correct |
| **Redundant** | Already captured accurately | Skip — don't add a duplicate |

### What makes a good reconciliation

The goal is to keep the knowledge base as a single source of truth. A few principles:

- **Prefer updating over appending.** If a Drive folder ID changed, update the existing entry rather than adding a new bullet saying "folder ID is now X" below the old one. The old value shouldn't linger.
- **Detect semantic duplicates.** Two entries might use different wording but describe the same fact. Merge them into one clear entry.
- **Be conservative with deletions.** Don't remove entries just because a rescan didn't find them — the absence of evidence isn't evidence of absence. Only mark something as outdated if you have positive evidence it's wrong (e.g., a folder no longer exists, a person left the company).
- **Conflicts get flagged, not auto-resolved.** When new info contradicts existing knowledge, show both to the user and let them decide. This is important because the existing entry might have been manually verified and the new scan might be wrong.

### Reconciliation in Add mode (lightweight)

When the user shares a single fact, you don't need to scan the entire knowledge base — just read the target domain file and reconcile the new entry against it. Also check related files for cascading references (e.g., if updating a name in `zenlabs.md`, check if `zenlabs-employees.md` references the old name too). This adds minimal overhead but catches the most common issues: duplicates, outdated entries, cascading references, and conflicts.

### Reconciliation in Rescan mode (thorough)

When doing a full rescan, read ALL knowledge files and reconcile against ALL fetched data. For a large knowledge base, you can parallelize this by scope — spawn one reconciliation agent per scope (global, work, personal) processing simultaneously.

Present the results as a structured diff report before applying. Use tables with status columns so the user can quickly scan what changed:

```
## Knowledge Base Reconciliation Report

**Source:** Google Drive / Notion  |  **Scan date:** 2026-03-10
**KB files examined:** personal/zenlabs.md, personal/zenlabs-employees.md, INDEX.md

### personal/zenlabs.md — Drive Structure

| Item | KB Value | Source Value | Status |
|------|----------|-------------|--------|
| Folder 0: Operations | ID `abc...` | ID `abc...` | UNCHANGED |
| Folder 5: Branding | ID `old_id` | ID `new_id` | CHANGED |
| Folder 7: Templates | (not in KB) | ID `xxx` | NEW |
| Notion workspace name | "Zen Labs" | "ZenLabs" | CONFLICT |

### personal/zenlabs-employees.md
- NEW: Found new team member "Linh" in Notion HR database
- UNCHANGED: Hào's info matches current records

### Summary
| Category | Count |
|----------|-------|
| Unchanged | 6 |
| New | 2 |
| Changed | 1 |
| Conflicts | 1 |
```

Wait for user approval before applying changes. The user might say "apply all", "skip the conflict", or "actually, let me clarify that one".

---

## Looking up knowledge

When the user asks a question and you suspect there might be relevant stored knowledge:

1. Read `INDEX.md` to scan for relevant domains
2. Read the matching domain file(s)
3. Use the stored knowledge to inform your answer — prefer it over generic information
4. If the stored knowledge contradicts general info, go with the stored knowledge and mention it

The user builds this knowledge base precisely because they want their specific, verified facts used — not generic web answers.

## INDEX.md format

Auto-generate and maintain this file whenever domains change:

```markdown
# Knowledge Base Index

## Global
| Domain | File | Summary |
|--------|------|---------|
| docker | `global/docker.md` | Container runtime, networking, volumes |

## Work
| Domain | File | Summary |
|--------|------|---------|
## Personal
| Domain | File | Summary |
|--------|------|---------|
| zenlabs | `personal/zenlabs.md` | ZenLabs company operations |
```

Keep summaries short (under 10 words). Update the summary when the domain content evolves significantly.
