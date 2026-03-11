# Chat Summary: WBS for AI-Powered Analytics Dashboard

## Task

Create a Work Breakdown Structure (WBS) for a vaguely-specified client project: an AI-powered analytics dashboard that lets users upload spreadsheet data and query it with natural language. Constraints mentioned: "should be fast" and "budget is tight."

## Approach

### Handling Vagueness

The brief was intentionally vague. Rather than blocking on missing information, I:

1. **Documented 7 explicit assumptions** covering data format, LLM approach, performance targets, team size, MVP scope, deployment model, and platform (web-only).
2. **Listed 6 open questions / unknowns** that would need client clarification: data schemas, budget ceiling, save/share features, authentication, compliance, and concurrency.
3. **Proceeded with reasonable MVP defaults** -- single-tenant, no enterprise auth, open-source stack, managed LLM API, responsive web UI.

### WBS Structure

Decomposed the project into **8 top-level phases** with **40 work packages** total:

| # | Phase | Work Packages | Effort |
|---|-------|--------------|--------|
| 1 | Project Management | 5 | 4.5d + 2 ongoing |
| 2 | Data Ingestion & Storage | 5 | 9.0d |
| 3 | Natural Language Query Engine | 6 | 13.0d |
| 4 | Frontend / Dashboard UI | 7 | 14.0d |
| 5 | Backend API & Infrastructure | 5 | 5.5d |
| 6 | Testing & Quality Assurance | 5 | 9.0d |
| 7 | Deployment & DevOps | 4 | 3.5d |
| 8 | Documentation & Handoff | 3 | 2.5d |
| **TOTAL** | | **40** | **61.0 person-days + ongoing PM** |

### Key Design Decisions

- **Text-to-SQL via LLM**: The natural language engine converts questions to SQL using schema-aware prompt engineering. This is the most pragmatic approach for a budget-constrained project compared to training custom models.
- **Budget-conscious stack**: Next.js + Tailwind (free), PostgreSQL on Supabase/Railway ($5/mo), OpenAI gpt-4o-mini for cost-efficient inference, Vercel for hosting. Estimated monthly run cost: $10-50/mo.
- **Performance target**: Interpreted "fast" as sub-3-second query response, with caching layer for repeated queries.
- **Timeline estimate**: 14-17 weeks for a solo developer, 8-11 weeks for a two-person team.

## Output

- **PDF file**: `wbs_ai_analytics_dashboard.pdf` (6 pages, A4 format)
  - Page 1: Title page with summary
  - Page 2-3: Assumptions/unknowns + WBS tables (phases 1-4)
  - Page 4-5: WBS tables (phases 4-8)
  - Page 6: Effort summary table, timeline estimate, stack recommendation

## PDF Generation Method

Used Python `reportlab` library to generate the PDF programmatically. The script (`generate_wbs_pdf.py`) is included in the outputs directory and is fully self-contained / re-runnable.

### Visual Design Choices

- Dark navy / blue color palette for headers and accents
- Gold accent lines for visual hierarchy on the title page
- Alternating row colors in tables for readability
- Consistent typography using Helvetica family
- Blue table headers with white text
- Grey summary box on the title page

## What Was NOT Done (Out of Scope)

- No Gantt chart or timeline visualization (could be a follow-up)
- No RACI matrix (would need team role definitions from client)
- No cost breakdown beyond stack recommendations (would need hourly rates)
- No risk register (noted as a work package in phase 1, but not elaborated in this document)
- No dependency mapping between work packages

## Observations on the Brief's Vagueness

The brief leaves several critical dimensions undefined:

1. **"Some data in spreadsheets"** -- Could mean anything from a single sales report to dozens of interconnected datasets. The WBS assumes simple, independent tables.
2. **"Ask questions in natural language"** -- The accuracy bar is undefined. Text-to-SQL works well for structured queries but struggles with ambiguous or complex multi-join questions. The WBS includes an LLM output validation phase to establish a quality baseline.
3. **"Should be fast"** -- No quantified SLA. Assumed sub-3-second for typical queries. If the client means "instant" (< 500ms), the architecture would need pre-computation or a different approach.
4. **"Budget is tight"** -- No actual number. The stack recommendation targets $10-50/mo in run costs, but developer time (the main cost) is unaddressed. A solo developer at 61 person-days is the minimum viable team.
