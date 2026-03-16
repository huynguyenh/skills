---
name: hnh-add-knowledge
description: Capture and organize personal knowledge into a structured, searchable knowledge base. Use this skill whenever the user shares a fact, tip, lesson learned, or piece of information they want to remember — even if they don't say "remember" or "save". Also use when the user says "add knowledge", "note this", "I learned that", or shares a standalone insight. Trigger on any statement that looks like the user is teaching Claude something they want retained, not just asking a question. When the user asks a domain-specific question, check the knowledge base first before relying on general information.
---

# Knowledge Base Manager

Capture short pieces of knowledge the user shares, classify them by scope and domain, and store them in an organized file structure.

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

Determine which scope the knowledge belongs to:

| Scope | When to use | Examples |
|-------|-------------|---------|
| **Global** | Universally useful — applies to the user as a person across work and personal life | Programming fundamentals, productivity tips, health facts, general tech knowledge |
| **Work** | Specific to the user's current employment | Internal API quirks, team conventions, infrastructure details, work tooling |
| **Personal** | Personal life, side projects, own businesses | ZenLabs (user's company), personal finance, family, hobbies |

**Key context:** The user owns a company called ZenLabs. Anything ZenLabs-related is **Personal** scope, not Work.

When the scope is ambiguous, ask. Don't guess.

## Domain detection

Within each scope, identify the domain or project. This becomes the filename.

- Use lowercase kebab-case: `docker.md`, `google-cloud.md`, `zenlabs-ops.md`
- If a domain file already exists, append to it
- If it's genuinely new, create a new file
- Before creating a new domain, check existing files — the knowledge might fit an existing one

Read `INDEX.md` first to see what domains already exist. This avoids creating duplicates like `docker.md` and `containers.md`.

## Adding an entry

Each entry in a domain file is a bullet point. Group related entries under headings if the file grows. Keep entries concise — this is a reference, not a blog.

**Format:**

```markdown
# Docker

- Containers use bridge network by default; use `--network host` to share host network stack
- Multi-stage builds reduce image size — use `FROM x AS builder` then `COPY --from=builder`
- `docker system prune -a` removes all unused images, not just dangling ones

## Compose
- `depends_on` only waits for container start, not readiness — use healthchecks
```

**Rules:**
- No dates on entries (this is a knowledge base, not a journal)
- Deduplicate — if the knowledge is already captured, skip it or refine the existing entry
- Keep each bullet self-contained and scannable
- Use sub-headings to group within a domain when it gets long (10+ entries)

## Workflow

When the user shares knowledge:

1. **Read INDEX.md** to see existing scopes and domains
2. **Classify** the scope and domain
3. **Confirm briefly** — state the classification in your response: "Added to **personal/zenlabs**" (don't ask for confirmation unless ambiguous)
4. **Read the target file** if it exists — check for duplicates and find the right place to insert
5. **Write the entry** — append to the domain file, or create it if new
6. **Update INDEX.md** if a new domain was created

## Looking up knowledge

When the user asks a question and you suspect there might be relevant stored knowledge:

1. Read `INDEX.md` to scan for relevant domains
2. Read the matching domain file(s)
3. Use the stored knowledge to inform your answer — prefer it over generic information
4. If the stored knowledge contradicts general info, go with the stored knowledge and mention it

This is important: the user builds this knowledge base precisely because they want their specific, verified facts used — not generic web answers.

## INDEX.md format

Auto-generate and maintain this file whenever domains change:

```markdown
# Knowledge Base Index

## Global
| Domain | File | Summary |
|--------|------|---------|
| docker | `global/docker.md` | Container runtime, networking, volumes |
| git | `global/git.md` | Version control patterns |

## Work
| Domain | File | Summary |
|--------|------|---------|
## Personal
| Domain | File | Summary |
|--------|------|---------|
| zenlabs | `personal/zenlabs.md` | ZenLabs company operations |
```

Keep summaries short (under 10 words). Update the summary when the domain content evolves significantly.

