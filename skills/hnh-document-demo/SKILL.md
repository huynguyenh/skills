---
name: hnh-document-demo
description: >
  Package a build session into a shareable "Build with AI" demo document — markdown + screenshots + optional screen recordings — and push to the zenlbs/build-with-ai GitHub repo. Use this skill whenever the user says "document this demo", "wrap this up", "create a demo doc", "package this session", "write up what we built", or asks to create a sharing document about how they used AI to build something. Also trigger when the user mentions "build-with-ai", "demo-1", "demo-2", or any reference to packaging a session for sharing with the team. Even if the user just says "wrap it up" or "share this" at the end of a build session, this skill applies.
---

# Document Demo

Package a completed build session into a polished, shareable markdown document that showcases how AI was used as a software engineering tool — not just a code generator.

## What This Skill Produces

```
demo-{id}/
├── {slug}.md              ← Main document (the star)
├── {slug}.pdf             ← Branded PDF (optional, if user wants)
├── assets/
│   ├── screenshots/       ← Captured from the built product
│   │   ├── 01-*.png
│   │   ├── 02-*.png
│   │   └── ...
│   └── *.mp4              ← Screen recordings (user-provided)
└── generate-pdf.py        ← PDF generation script (if PDF was created)
```

## Workflow

### Phase 1: Reflect on the Session

Before writing anything, review what happened in this session:

1. **What was built** — the product, features, pages, components
2. **What techniques were used** — prompting patterns, debugging approaches, how problems were solved
3. **What skills were invoked** — which wrapper skills (`hnh-review-pr`, `hnh-design-guideline`, etc.) played a role
4. **What went wrong and how it was fixed** — bugs found, root causes discovered, interesting debugging moments
5. **Where we struggled** — things that took multiple attempts, scope cuts, AI looping on dead-end approaches
6. **What we learned** — both domain knowledge and meta-lessons about the AI collaboration
7. **What to improve for next time** — skills to create, knowledge to capture, process changes (THIS IS THE MOST IMPORTANT — it creates the compounding improvement loop)
8. **What the user explicitly asked to highlight** — they may have called out specific insights during the session

The document should read like a senior engineer sharing hard-won insights with their team, not like a changelog or feature list.

### Phase 2: Write the Markdown

The document structure follows this pattern. Adapt section names and content to what actually happened — don't force sections that don't apply.

```markdown
# {Title}

**{One-line hook}**

---

## Key Takeaways

### 1. {Takeaway Title}

{Expanded paragraph — not a copy of the PDF, but a real explanation
with specific examples from the session. What happened, why it matters,
what the reader should learn from it.}

### 2. {Takeaway Title}
...

(3-5 takeaways, each with its own ### heading and paragraph)

---

## What I Built

{Brief description + stats if applicable}

{Screenshots — inline images with relative paths}

---

## {Technical Deep-Dive Sections}

{These vary by session. Could be:
- "The Foundation: Design System & Skills"
- "Prompting in Practice"
- "The Feedback Loop"
- "Debugging: From Symptom to Root Cause"
- "Shipping: The Automated Pipeline"
- etc.}

---

## Where We Struggled

{Honest account of what went wrong — for BOTH the human and the AI.
Not a blame list. Each struggle should name:
1. The symptom (what we saw)
2. Why it was hard (what made it non-obvious)
3. How many attempts it took
4. What finally fixed it — or if we cut scope

Include things like: AI looping on approaches that couldn't work,
undocumented platform behaviors, tooling gaps that slowed us down,
scope decisions that should have been made earlier.}

---

## What We Learned Along the Way

{Split into two sub-sections:}

### About {Domain/Technology}
{Technical lessons specific to the domain — the kind of thing
you'd tell a colleague starting a similar project.}

### About Working with AI
{Meta-lessons about the collaboration itself — when AI was
effective, when it wasn't, what patterns worked, what to avoid.}

---

## Making the Next Demo Smoother

{THE MOST IMPORTANT SECTION. Every struggle above should map to
a concrete improvement:

- **Skills to create** — new wrapper skills that would have
  prevented wasted time (e.g., native screenshot skill)
- **Knowledge to capture** — domain knowledge to add to
  ~/.claude/knowledge/ so the AI doesn't repeat mistakes
- **Process changes** — rules or conventions to add
  (e.g., "cut scope after 3 failed attempts")
- **Skill updates** — improvements to existing skills based
  on what we hit during this session

Each item should be actionable with a clear "to build", "to add",
or "done" status. This section creates a compounding improvement
loop: each demo identifies what to build for the next one.}

---

**Appendix:** {Screen recordings, additional assets}
```

#### Writing Rules

- **Key Takeaways go first.** Readers should get the main insights before scrolling.
- **Use plain markdown.** Headings, paragraphs, bullet lists, blockquotes, tables. No HTML tables for content that works as regular markdown.
- **HTML tables are OK** for stats/metrics boxes and side-by-side image layouts only.
- **Write in first person.** This is the user sharing their experience, not a third-party report.
- **Be specific.** Name the actual bugs found, the exact prompting technique, the real skill that was used. Generic advice is worthless.
- **Include real examples.** Actual prompts the user sent, actual issues that were found, actual code patterns.
- **The system setup is a MUST.** Every document must cover the skills infrastructure, design guidelines, automation workflows — this is the core differentiator of how the user works.
- **Screenshots use relative paths:** `assets/screenshots/01-name.png`
- **Screen recordings referenced in appendix:** `assets/workflow-demo.mp4`

### Phase 3: Capture Screenshots

Take screenshots of the built product to include in the document. Use the preview server if one is running, or Playwright for headless capture.

**Desktop screenshots:** Full viewport at 1440x900 or similar
**Mobile screenshots:** 390x844 viewport for responsive layouts
**Naming:** Sequential numbering — `01-keywords.png`, `02-reports-list.png`, etc.

If the user provides screen recordings (.mov, .mp4), convert/optimize them and place in `assets/`.

### Phase 4: Ask for Demo ID

After the document is written, ask the user:

> "What demo ID should I use? (e.g., 1, 1.a, 2, 3)"

This becomes the directory name: `demo-{id}`

### Phase 5: Package and Push

1. **Create the output directory** at `~/ws/docs/zenlabs/ai-experience-sharing/` (or wherever the source docs live) — this is the working copy
2. **Copy to the repo** — clone or pull `zenlbs/build-with-ai` to `~/ws/code/github.com/zenlbs/build-with-ai/`, then copy the package into `demo-{id}/`
3. **Configure git** before committing:
   ```
   git config user.name "huynguyenh"
   git config user.email "<email>"
   ```
4. **Commit and push:**
   ```
   git add demo-{id}/
   git commit -m "Add demo-{id}: {short description}"
   git push
   ```
5. **Report the URL:** `https://github.com/zenlbs/build-with-ai/tree/main/demo-{id}`

Keep the source docs directory intact — always copy, never move.

### Phase 6: Optional PDF

If the user wants a branded PDF, use the `/hnh-design-guideline` skill for brand specs and generate with ReportLab. Save the generation script as `generate-pdf.py` alongside the output so it can be re-run later.

## Key Principles

**This is not a feature showcase.** The document exists to share how AI is used as a software engineering tool. Every section should teach the reader something about the process — the skills infrastructure, the prompting patterns, the feedback loop, the automated review pipeline. The product screenshots are evidence, not the point.

**Adapt to what actually happened.** If the session was about debugging a nasty CSS issue, the document should go deep on the debugging process. If it was about building a full app from scratch, focus on the architecture decisions and iteration speed. Don't force a template.

**The user's voice matters.** When the user explicitly states insights during the session (like "the biggest win is the feedback loop speed"), those become the lead takeaways — expanded with specifics, but preserving their original framing.

**The improvement loop is mandatory.** Every document MUST end with "Making the Next Demo Smoother" — concrete, actionable items (skills to create, knowledge to capture, process changes). This is the compounding mechanism: each demo makes the next one better. If the session had no struggles, the section should say so explicitly (that's a signal the system is working).
