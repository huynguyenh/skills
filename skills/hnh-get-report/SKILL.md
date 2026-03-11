---
name: hnh-get-report
description: >
  Generate a CEO-level project status report for ZenLabs projects by scanning all project
  data sources in parallel — backlog spreadsheets, GitHub repos, Google Drive, and Notion.
  Use this skill whenever the user asks for a project report, status update, progress check,
  daily standup summary, or asks "how's [project] going?". Also trigger on "report",
  "update me on", "progress", "what did the team do", "standup", "how are things going with",
  or any request to summarize project activity — even if they don't say "report" explicitly.
  Works only with ZenLabs projects that have entries in the knowledge base.
---

# Project Status Report

Generate a concise, CEO-level project status report by scanning all configured data sources
for a ZenLabs project in parallel, then comparing against the previous report to highlight
what changed.

## Prerequisites

- Project must exist in the knowledge base (`~/.claude/knowledge/personal/`)
- Relevant skills installed: `hnh-gg-sheets`, `hnh-gg-drive`, `hnh-notion`, `gh` CLI

## Workflow

### Phase 1: Discover Sources

1. Read `~/.claude/knowledge/INDEX.md` to find the project's knowledge file
2. Read the project knowledge file (e.g., `personal/gmd-tms.md`)
3. Extract all configured sources:
   - **Backlog spreadsheet** — spreadsheet ID, key tabs
   - **GitHub repos** — repo URLs
   - **Drive folders** — folder IDs
   - **Notion pages** — page IDs or search terms (if configured)
4. Read previous report snapshot from `~/.claude/memory/reports/{project-slug}/latest.json`
   - If no snapshot exists, this is the first report — skip delta computation

### Phase 2: Parallel Data Collection

Launch one subagent per data source. Read each agent's instructions from the corresponding
file under `agents/` and pass it the project context + previous snapshot.

| Agent | File | What it scans |
|-------|------|---------------|
| Backlog Scanner | `agents/backlog-scanner.md` | Reads backlog spreadsheet, computes pipeline metrics, identifies UC status changes |
| GitHub Scanner | `agents/github-scanner.md` | Checks recent commits, PRs, and merges across all project repos |
| Drive Scanner | `agents/drive-scanner.md` | Looks for new or recently modified files in project Drive folders |
| Notion Scanner | `agents/notion-scanner.md` | Checks Notion pages for updates (if configured) |

Only launch agents for sources that exist in the knowledge file. If no Notion pages are
configured, skip the Notion scanner. If no Drive folders, skip Drive. At minimum, the
backlog spreadsheet and GitHub repos should be present.

**How to launch each agent:**
1. Read the agent instructions file (e.g., `agents/backlog-scanner.md`)
2. Spawn a general-purpose Agent with a prompt that includes:
   - The agent instructions (from the file)
   - The project-specific parameters (spreadsheet ID, repo URLs, etc.)
   - The previous snapshot data (or "no previous snapshot" if first run)
   - The report period (default: "since last report" or "today" if first run)

### Phase 3: Aggregate & Report

Once all agents return, compile their findings into a structured report.

**Report template:**

```
# {Project Name} — Status Report

**Date:** {today}  |  **Sprint:** {N} (Week {W})  |  **Type:** {Daily/Weekly}

---

## Executive Summary

2-3 sentences: overall project health, key milestone reached, biggest risk or blocker.
This should be genuinely interpretive — not just restating numbers, but telling the CEO
what they need to know in 10 seconds.

## Key Metrics

| Metric | Current | Change |
|--------|---------|--------|
| Total Use Cases | X | — |
| Completed (all stages done) | X | +N |
| In Development (BE + FE active) | X | +N |
| Ready for QA | X | +N |
| Estimation (total hours) | X | — |

## Pipeline Status

BA ({n}) → Design ({n}) → BE ({n}) → FE ({n}) → QA ({n}) → Pilot ({n}) → Launch ({n})

Show count at each stage. Use the most relevant status (e.g., "WIP" counts at that stage,
"Ready for X" counts at the next stage's queue).

## Changes Since Last Report

Group by movement type:

### Completed
- UC-XXX "Name" — now done through [stage]

### Progressed
- UC-XXX "Name" — moved from [old] → [new]

### Newly Added
- UC-XXX "Name" — added to backlog

### Blocked / No Movement
- Note any UCs that have been stuck for multiple reports

## Development Activity

### Backend ({repo-name})
- {N} commits since last report
- PRs merged: {list}
- PRs open: {list}

### Frontend ({repo-name})
- {N} commits since last report
- PRs merged: {list}
- PRs open: {list}

## Documents & Artifacts

New or updated files in Drive/Notion since last report. Skip this section if nothing changed.

## Risks & Attention Items

Items that need CEO awareness — blockers, resource concerns, timeline risks.

## Next Sprint Preview

What's planned for the upcoming sprint based on the backlog's planned sprint column.
```

### Phase 4: Save Snapshot

After generating the report, save a metrics snapshot so the next report can compute deltas.

```bash
mkdir -p ~/.claude/memory/reports/{project-slug}/
```

Save to `~/.claude/memory/reports/{project-slug}/latest.json`:

```json
{
  "date": "2026-03-11",
  "sprint": 3,
  "pipeline": {
    "ba": {"Ready for Dev": 44, "UC WIP": 13, "To Do": 76},
    "be": {"Ready for FE": 28, "To Do": 18, "BE WIP": 8},
    "fe": {"To Do": 29, "Ready for QA": 17, "FE WIP": 7},
    "qa": {},
    "pilot": {"To Do": 55},
    "launch": {"To Do": 55}
  },
  "estimation_hours": {"ba": 86.5, "design": 201, "fe": 196, "be": 290, "qa": 0},
  "uc_statuses": {
    "TP-M01_UC-001": {"ba": "Ready for Dev", "be": "Ready for FE", "fe": "N/a"},
    "...": "..."
  },
  "github": {
    "gmd-tms-backend": {"latest_commit_sha": "abc1234", "open_prs": 2},
    "gmd-tms-frontend": {"latest_commit_sha": "def5678", "open_prs": 1}
  }
}
```

The `uc_statuses` field stores per-UC status so the next report can identify exactly which
UCs moved between stages.

## Report Cadence

- **Daily** (default): What changed today, short and focused. ~1 page.
- **Weekly**: Broader view, sprint summary, velocity observations. ~2 pages.
- **Custom**: User specifies period ("since Monday", "last 3 days", "this week").

Adjust depth based on cadence. Daily reports highlight changes. Weekly reports include
trends and patterns.

## Parsing the Backlog

Use the bundled `scripts/parse_backlog.py` for reliable metrics extraction:

```bash
python3 <sheets-skill>/scripts/sheets.py read SPREADSHEET_ID \
  --sheet-name "Backlog" 2>/dev/null | \
  python3 <skill-path>/scripts/parse_backlog.py \
  [--previous ~/.claude/memory/reports/{project}/latest.json]
```

The script dynamically detects column layout from headers, computes all pipeline metrics,
and diffs against the previous snapshot if provided. Output is structured JSON that the
report can directly use.

## Tips

- The first report for a project has no deltas — that's fine, it establishes the baseline
- If a source is temporarily unavailable (API error), note it in the report and continue
- Use Vietnamese UC names as they appear in the backlog, but write the report in English
- Keep the executive summary genuinely useful — interpret the data, don't just restate it
- The sprint number can be derived: Sprint = Week number - 7 (started Sprint 0 at Week 8)
