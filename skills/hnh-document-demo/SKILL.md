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
5. **What the user explicitly asked to highlight** — they may have called out specific insights during the session

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
