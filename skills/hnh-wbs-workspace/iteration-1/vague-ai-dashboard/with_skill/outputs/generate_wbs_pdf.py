#!/usr/bin/env python3
"""
WBS PDF Generator — AI-Powered Analytics Dashboard POC
ZenLabs branded output using ReportLab
"""

import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors

# ── ZenLabs Brand Colors ─────────────────────────────────────────────
PRIMARY_BLACK  = HexColor("#09242E")
EMERALD_900    = HexColor("#04563E")
EMERALD_500    = HexColor("#43CE81")
EMERALD_300    = HexColor("#98D5AB")
EMERALD_100    = HexColor("#C8E6B7")
FIREFLY_200    = HexColor("#C0E0EF")
FIREFLY_100    = HexColor("#D8EDF5")
ECRU_100       = HexColor("#F6F6E8")
ECRU_300       = HexColor("#E3E2BC")
ECRU_700       = HexColor("#636230")
WHITE          = HexColor("#FFFFFF")

# ── Paths ─────────────────────────────────────────────────────────────
LOGO_PATH = os.path.expanduser(
    "~/.claude/skills/hnh-design-guideline/assets/logos/logo-dark-on-light.png"
)
OUTPUT_DIR = os.path.expanduser(
    "~/.claude/skills/hnh-wbs-workspace/iteration-1/vague-ai-dashboard/with_skill/outputs"
)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"wbs-ai-analytics-dashboard-{date.today().isoformat()}.pdf")

# ── Page Dimensions ───────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN = 20 * mm


# ── Styles ────────────────────────────────────────────────────────────
def get_styles():
    return {
        "title": ParagraphStyle(
            "Title",
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=PRIMARY_BLACK,
            alignment=TA_LEFT,
        ),
        "h1": ParagraphStyle(
            "H1",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=EMERALD_900,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=EMERALD_900,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=PRIMARY_BLACK,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
        ),
        "body_bold": ParagraphStyle(
            "BodyBold",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=13,
            textColor=PRIMARY_BLACK,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=PRIMARY_BLACK,
            leftIndent=12,
            bulletIndent=0,
            spaceAfter=2,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=WHITE,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=PRIMARY_BLACK,
        ),
        "table_cell_bold": ParagraphStyle(
            "TableCellBold",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=PRIMARY_BLACK,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=HexColor("#478FB4"),
        ),
    }


# ── Risk badge helper ─────────────────────────────────────────────────
def risk_badge(level, style):
    """Return a Paragraph with brand-colored risk text."""
    color_map = {
        "Low": ("#04563E", "#C8E6B7"),
        "Medium": ("#636230", "#E3E2BC"),
        "High": ("#09242E", "#D8EDF5"),
    }
    text_c, bg_c = color_map.get(level, ("#09242E", "#FFFFFF"))
    return Paragraph(
        f'<font color="{text_c}"><b>{level}</b></font>',
        style,
    )


def risk_bg(level):
    color_map = {
        "Low": EMERALD_100,
        "Medium": ECRU_300,
        "High": FIREFLY_100,
    }
    return color_map.get(level, WHITE)


# ── Table builder ─────────────────────────────────────────────────────
def build_table(headers, rows, col_widths=None, risk_col=None):
    """Build a branded table. risk_col index triggers row-level risk coloring."""
    s = get_styles()
    # Build data
    header_row = [Paragraph(h, s["table_header"]) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(c), s["table_cell"]) for c in row])

    if col_widths is None:
        available = PAGE_W - 2 * MARGIN
        col_widths = [available / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), EMERALD_900),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, FIREFLY_200),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]

    # Alternating rows OR risk-based coloring
    for i in range(1, len(data)):
        if risk_col is not None and risk_col < len(rows[i - 1]):
            risk_val = str(rows[i - 1][risk_col]).strip()
            bg = risk_bg(risk_val)
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
        else:
            bg = ECRU_100 if i % 2 == 0 else WHITE
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

    t.setStyle(TableStyle(style_cmds))
    return t


# ── Footer callback ───────────────────────────────────────────────────
def footer_callback(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(HexColor("#478FB4"))
    canvas.drawCentredString(PAGE_W / 2, 12 * mm, f"Page {doc.page}")
    canvas.drawString(MARGIN, 12 * mm, "ZenLabs — Confidential")
    canvas.restoreState()


def first_page_callback(canvas, doc):
    """No footer on cover page."""
    pass


# ── Build Document ────────────────────────────────────────────────────
def build_pdf():
    s = get_styles()
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    elements = []
    available_w = PAGE_W - 2 * MARGIN

    # ═══════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Spacer(1, 20 * mm))

    # Logo
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=50 * mm, height=12 * mm)
        elements.append(logo)
    elements.append(Spacer(1, 20 * mm))

    # Header bar
    header_data = [[Paragraph(
        "AI-Powered Analytics<br/>Dashboard",
        s["title"]
    )]]
    header_table = Table(header_data, colWidths=[available_w])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), EMERALD_900),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6 * mm))

    # Subtitle bar
    sub_data = [[Paragraph("Work Breakdown Structure", s["subtitle"])]]
    sub_table = Table(sub_data, colWidths=[available_w])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), EMERALD_500),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 30 * mm))

    # Meta info
    meta_lines = [
        f"<b>Date:</b> {date.today().strftime('%B %d, %Y')}",
        "<b>Version:</b> 1.0",
        "<b>Mode:</b> Scope (no estimates)",
        "<b>Prepared by:</b> ZenLabs",
        "<b>Client:</b> Confidential",
    ]
    for line in meta_lines:
        elements.append(Paragraph(line, s["cover_meta"]))
        elements.append(Spacer(1, 2 * mm))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Paragraph("Executive Summary", s["h1"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=EMERALD_900,
        spaceAfter=6, spaceBefore=2
    ))
    exec_summary = (
        "This document defines the Work Breakdown Structure for an AI-powered analytics dashboard "
        "proof of concept. The system enables 5-10 internal users to query approximately 50 sales and "
        "inventory spreadsheets using natural language, receiving instant visual answers via a web dashboard. "
        "The recommended approach is a lightweight custom build using Next.js, Python FastAPI, PostgreSQL, "
        "and the OpenAI API, deployed on managed cloud services. The project is scoped as a CEO demo/POC "
        "within a $15K budget constraint. Key risks include LLM query accuracy on financial data and "
        "spreadsheet format inconsistency across the 50-file dataset. The architecture prioritizes demo "
        "impact and future extensibility over production hardening."
    )
    elements.append(Paragraph(exec_summary, s["body"]))
    elements.append(Spacer(1, 6 * mm))

    # ═══════════════════════════════════════════════════════════════════
    # TECHNICAL FEASIBILITY
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Paragraph("Technical Feasibility", s["h1"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=EMERALD_900,
        spaceAfter=6, spaceBefore=2
    ))
    elements.append(Paragraph(
        "Each major requirement was assessed for technical feasibility. The overall project is viable "
        "with known technology, though the NL query accuracy requires careful prompt engineering and validation.",
        s["body"]
    ))
    elements.append(Spacer(1, 3 * mm))

    feas_headers = ["Requirement", "Feasibility", "Notes"]
    feas_rows = [
        ["Natural language query over structured data",
         "Viable",
         "OpenAI GPT-4 with structured prompting can generate SQL from natural language. Accuracy depends on schema clarity and prompt engineering. Technical spike recommended."],
        ["Spreadsheet data ingestion (50 files)",
         "Viable",
         "Python pandas/openpyxl can parse Excel/CSV. Main risk is format inconsistency across files. Requires a normalization layer."],
        ["Real-time query responses",
         "Viable",
         "PostgreSQL queries on normalized data return sub-second. LLM API latency adds 1-3 seconds. Acceptable for demo."],
        ["Dashboard with charts and KPIs",
         "Viable",
         "Standard web development with mature charting libraries (Recharts, Chart.js). No technical risk."],
        ["5-10 concurrent users",
         "Viable",
         "Trivial load. Managed hosting (Vercel + Railway) handles this without special scaling."],
        ["$15K budget constraint",
         "Viable with constraints",
         "Feasible as a POC with AI-augmented development. Not sufficient for production-grade system. Scope must stay disciplined."],
    ]
    feas_col_widths = [available_w * 0.25, available_w * 0.15, available_w * 0.60]
    elements.append(build_table(feas_headers, feas_rows, feas_col_widths))
    elements.append(Spacer(1, 6 * mm))

    # ═══════════════════════════════════════════════════════════════════
    # APPROACH ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Paragraph("Approach Analysis", s["h1"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=EMERALD_900,
        spaceAfter=6, spaceBefore=2
    ))
    elements.append(Paragraph(
        "Three architectural approaches were evaluated against the project constraints. "
        "Approach B (Lightweight Custom Build) was selected as the recommended path forward.",
        s["body"]
    ))
    elements.append(Spacer(1, 3 * mm))

    approach_headers = ["Factor", "A: No-Code (Retool)", "B: Custom Build (Recommended)", "C: AI Platform (Dify)"]
    approach_rows = [
        ["Stack",
         "Retool + OpenAI API + Airtable",
         "Next.js + FastAPI + PostgreSQL + OpenAI",
         "Dify + React + PostgreSQL"],
        ["Quality",
         "Limited customization, generic look",
         "Full control over UX, polished demo",
         "Good AI pipeline, platform dependency"],
        ["Speed",
         "1-2 weeks",
         "3-4 weeks (AI-augmented)",
         "2-3 weeks"],
        ["Budget Fit",
         "Low dev cost, ongoing licensing",
         "Fits $15K, minimal ongoing cost",
         "$10-13K dev, Dify dependency"],
        ["Demo Impact",
         "Medium — looks like a tool",
         "High — looks like a product",
         "High — if frontend is polished"],
        ["NL Capability",
         "Basic — limited control",
         "Strong — full prompt engineering control",
         "Excellent — Dify handles RAG natively"],
        ["Path to Prod",
         "Locked in Retool ecosystem",
         "Real codebase to evolve",
         "Tied to Dify ecosystem"],
    ]
    approach_col_widths = [available_w * 0.15, available_w * 0.25, available_w * 0.35, available_w * 0.25]
    t = build_table(approach_headers, approach_rows, approach_col_widths)
    elements.append(t)
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        "<b>Decision:</b> Approach B selected. Best balance of demo impact, budget fit, NL query control, "
        "and future extensibility. AI-augmented development (Claude Code) compresses the timeline to fit "
        "within the $15K budget.",
        s["body"]
    ))
    elements.append(Spacer(1, 6 * mm))

    # ═══════════════════════════════════════════════════════════════════
    # WBS BY PHASE
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Paragraph("Work Breakdown Structure", s["h1"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=EMERALD_900,
        spaceAfter=6, spaceBefore=2
    ))
    elements.append(Paragraph(
        "The WBS is organized by SDLC phase at module level. Each module represents a deliverable "
        "unit of work with defined scope, dependencies, and risk assessment. This is scope mode — "
        "no time estimates are included.",
        s["body"]
    ))
    elements.append(Spacer(1, 4 * mm))

    wbs_col_widths = [
        available_w * 0.06,   # ID
        available_w * 0.14,   # Module
        available_w * 0.38,   # Scope
        available_w * 0.18,   # Key Deliverables
        available_w * 0.14,   # Dependencies
        available_w * 0.10,   # Risk
    ]
    wbs_headers = ["ID", "Module", "Scope", "Key Deliverables", "Dependencies", "Risk"]

    # ── Phase 1: Discovery ────────────────────────────────────────────
    elements.append(Paragraph("Phase 1: Discovery &amp; Requirements", s["h2"]))
    phase1_rows = [
        ["1.1", "Requirements Documentation",
         "Formalize the brief into structured requirements. Define user personas (CEO, analyst, data admin), map user stories for the NL query flow, dashboard views, and data management.",
         "Requirements doc, user story map, acceptance criteria",
         "None", "Low"],
        ["1.2", "Data Audit &amp; Schema Definition",
         "Audit all 50 spreadsheets for format consistency, common columns, and data quality issues. Define a normalized target schema for sales and inventory data.",
         "Data audit report, normalized schema, quality assessment",
         "None", "Medium"],
        ["1.3", "NL Query Technical Spike",
         "Validate that OpenAI GPT-4 can translate natural language questions into accurate SQL against the defined schema. Test 10-15 representative queries.",
         "Working spike, accuracy benchmarks, prompt patterns",
         "1.2", "Medium"],
    ]
    elements.append(build_table(wbs_headers, phase1_rows, wbs_col_widths, risk_col=5))
    elements.append(Spacer(1, 5 * mm))

    # ── Phase 2: System Design ────────────────────────────────────────
    elements.append(Paragraph("Phase 2: System Design &amp; Architecture", s["h2"]))
    phase2_rows = [
        ["2.1", "Architecture Design",
         "Define high-level architecture: Next.js frontend (Vercel), Python FastAPI backend (Railway), PostgreSQL, OpenAI API. Define API contracts and NL query pipeline.",
         "Architecture diagram, API contracts, infra blueprint",
         "1.1, 1.2, 1.3", "Low"],
        ["2.2", "Data Model &amp; Pipeline Design",
         "Design the ingestion pipeline (spreadsheet parsing, normalization, PostgreSQL loading), schema migrations, and weekly update workflow.",
         "Data model ERD, pipeline design, ingestion workflow spec",
         "1.2, 2.1", "Low"],
        ["2.3", "Security &amp; Auth Design",
         "Design simple authentication (NextAuth email login), basic roles (admin vs viewer), API key management for OpenAI.",
         "Auth flow design, role definitions, key management",
         "2.1", "Low"],
    ]
    elements.append(build_table(wbs_headers, phase2_rows, wbs_col_widths, risk_col=5))
    elements.append(Spacer(1, 5 * mm))

    # ── Phase 3: Development ──────────────────────────────────────────
    elements.append(Paragraph("Phase 3: Development", s["h2"]))
    phase3_rows = [
        ["3.1", "Data Ingestion Pipeline",
         "Build Python pipeline to parse Excel/CSV, normalize data, load into PostgreSQL. Include validation, error reporting, support for weekly incremental updates.",
         "Ingestion service, validator, error reporter, upload UI",
         "2.2", "Medium"],
        ["3.2", "NL Query Engine",
         "Build the core NL query engine: user question to SQL generation via OpenAI GPT-4, query execution, result formatting. Include SQL validation, result sanity checks, conversation context.",
         "Query engine, prompt templates, SQL validator, formatter",
         "3.1, 1.3", "High"],
        ["3.3", "Dashboard Frontend",
         "Build Next.js dashboard: KPI cards and charts, NL query chat interface, data management view (upload, ingestion status). Responsive, polished for CEO demo.",
         "Dashboard UI, chart components, NL chat interface, upload page",
         "2.1, 3.2", "Low"],
        ["3.4", "Authentication Module",
         "Implement NextAuth email login, simple role system (admin: upload data; viewer: query only), session management, protected routes.",
         "Auth implementation, role-based routing, user management",
         "2.3", "Low"],
        ["3.5", "API Layer",
         "Build FastAPI backend: NL query endpoint, data upload/ingestion trigger, dashboard data (KPIs, aggregations), user session proxy.",
         "REST API, documented endpoints, Pydantic schemas, error handling",
         "3.1, 3.2, 3.4", "Low"],
    ]
    elements.append(build_table(wbs_headers, phase3_rows, wbs_col_widths, risk_col=5))
    elements.append(Spacer(1, 5 * mm))

    # ── Phase 4: Quality Assurance ────────────────────────────────────
    elements.append(Paragraph("Phase 4: Quality Assurance", s["h2"]))
    phase4_rows = [
        ["4.1", "NL Query Accuracy Testing",
         "Build test suite of 30-50 representative NL questions. Verify query engine accuracy (target 85%+). Include edge cases: ambiguous queries, out-of-scope, empty results.",
         "Test suite, accuracy benchmarks, edge case report",
         "3.2", "Medium"],
        ["4.2", "Integration &amp; E2E Testing",
         "End-to-end testing: login, upload spreadsheet, ask question, receive answer, view dashboard. Cover happy paths and error scenarios with real data.",
         "E2E test suite (Playwright), integration coverage, bug report",
         "3.1-3.5", "Low"],
        ["4.3", "Demo Rehearsal &amp; UAT",
         "Conduct demo rehearsal with stakeholders. Prepare scripted CEO questions. Verify all demo scenarios work smoothly. Fix surfaced issues.",
         "Demo script, rehearsal sign-off, final bug fixes",
         "4.1, 4.2", "Low"],
    ]
    elements.append(build_table(wbs_headers, phase4_rows, wbs_col_widths, risk_col=5))
    elements.append(Spacer(1, 5 * mm))

    # ── Phase 5: Deployment ───────────────────────────────────────────
    elements.append(Paragraph("Phase 5: Deployment &amp; DevOps", s["h2"]))
    phase5_rows = [
        ["5.1", "Infrastructure &amp; CI/CD",
         "Set up Vercel (frontend), Railway/Render (backend), managed PostgreSQL. GitHub Actions CI/CD (lint, test, deploy). Environment configs (dev, staging, prod).",
         "Deployed environments, CI/CD pipeline, env configs",
         "3.3, 3.5", "Low"],
        ["5.2", "Data Migration &amp; Seeding",
         "Run initial ingestion of all 50 spreadsheets into production DB. Verify data integrity. Document weekly update workflow.",
         "Seeded production DB, verification report, update workflow doc",
         "3.1, 5.1", "Medium"],
    ]
    elements.append(build_table(wbs_headers, phase5_rows, wbs_col_widths, risk_col=5))
    elements.append(Spacer(1, 5 * mm))

    # ── Phase 6: Post-Launch ──────────────────────────────────────────
    elements.append(Paragraph("Phase 6: Post-Launch &amp; Maintenance", s["h2"]))
    phase6_rows = [
        ["6.1", "Monitoring &amp; Observability",
         "Set up uptime monitoring, error tracking (Sentry free tier), LLM API cost tracking, basic logging and alerting.",
         "Monitoring dashboard, alert config, cost tracking",
         "5.1", "Low"],
        ["6.2", "Knowledge Transfer",
         "Document system architecture, data pipeline, NL prompt engineering approach, weekly update process. Hand off to maintainer.",
         "Technical docs, admin guide, NL tuning guide",
         "All prior", "Low"],
        ["6.3", "Phase 2 Roadmap",
         "Define Phase 2 based on CEO demo feedback: production hardening, additional data sources, advanced analytics, mobile support.",
         "Phase 2 scope doc, prioritized backlog",
         "Demo feedback", "Low"],
    ]
    elements.append(build_table(wbs_headers, phase6_rows, wbs_col_widths, risk_col=5))
    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════
    # DEPENDENCY MAP
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Paragraph("Dependency Map", s["h1"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=EMERALD_900,
        spaceAfter=6, spaceBefore=2
    ))
    elements.append(Paragraph(
        "The table below shows upstream dependencies for each module. Modules cannot begin "
        "until all listed dependencies are complete. The critical path runs through: "
        "1.2 &rarr; 1.3 &rarr; 2.1 &rarr; 2.2 &rarr; 3.1 &rarr; 3.2 &rarr; 3.3/3.5 &rarr; 4.1/4.2 &rarr; 4.3.",
        s["body"]
    ))
    elements.append(Spacer(1, 3 * mm))

    dep_headers = ["Module", "Name", "Blocked By", "Blocks"]
    dep_rows = [
        ["1.1", "Requirements Documentation", "None", "2.1"],
        ["1.2", "Data Audit &amp; Schema", "None", "1.3, 2.1, 2.2"],
        ["1.3", "NL Query Spike", "1.2", "2.1, 3.2"],
        ["2.1", "Architecture Design", "1.1, 1.2, 1.3", "2.2, 2.3, 3.3, 3.5"],
        ["2.2", "Data Model &amp; Pipeline", "1.2, 2.1", "3.1"],
        ["2.3", "Security &amp; Auth Design", "2.1", "3.4"],
        ["3.1", "Data Ingestion Pipeline", "2.2", "3.2, 3.5, 5.2"],
        ["3.2", "NL Query Engine", "3.1, 1.3", "3.3, 3.5, 4.1"],
        ["3.3", "Dashboard Frontend", "2.1, 3.2", "4.2, 5.1"],
        ["3.4", "Authentication Module", "2.3", "3.5"],
        ["3.5", "API Layer", "3.1, 3.2, 3.4", "4.2, 5.1"],
        ["4.1", "NL Query Accuracy Testing", "3.2", "4.3"],
        ["4.2", "Integration &amp; E2E Testing", "3.1-3.5", "4.3"],
        ["4.3", "Demo Rehearsal &amp; UAT", "4.1, 4.2", "5.2"],
        ["5.1", "Infrastructure &amp; CI/CD", "3.3, 3.5", "5.2, 6.1"],
        ["5.2", "Data Migration &amp; Seeding", "3.1, 5.1", "6.2"],
        ["6.1", "Monitoring", "5.1", "6.2"],
        ["6.2", "Knowledge Transfer", "All prior", "6.3"],
        ["6.3", "Phase 2 Roadmap", "Demo feedback", "None"],
    ]
    dep_col_widths = [available_w * 0.08, available_w * 0.28, available_w * 0.32, available_w * 0.32]
    elements.append(build_table(dep_headers, dep_rows, dep_col_widths))
    elements.append(Spacer(1, 6 * mm))

    # ═══════════════════════════════════════════════════════════════════
    # RISK REGISTER
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Paragraph("Risk Register", s["h1"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=EMERALD_900,
        spaceAfter=6, spaceBefore=2
    ))

    risk_headers = ["ID", "Risk", "Likelihood", "Impact", "Severity", "Mitigation"]
    risk_rows = [
        ["R1",
         "LLM generates incorrect SQL leading to wrong financial answers in CEO demo",
         "Medium", "High", "High",
         "Technical spike (1.3) validates accuracy early. Build SQL validation layer. Pre-test all demo questions. Add confidence indicators to answers."],
        ["R2",
         "Spreadsheet format inconsistency across 50 files breaks ingestion pipeline",
         "High", "Medium", "High",
         "Data audit (1.2) identifies issues upfront. Build robust error handling and skip-on-failure logic. Prioritize cleanest files for demo."],
        ["R3",
         "Budget overrun due to scope expansion during development",
         "Medium", "Medium", "Medium",
         "Strict scope discipline: POC only, no production features. Weekly budget check. Cut scope before adding cost."],
        ["R4",
         "OpenAI API latency causes slow query responses during demo",
         "Low", "Medium", "Medium",
         "Cache common queries. Pre-warm the API connection. Have fallback pre-computed answers for demo script questions."],
        ["R5",
         "CEO asks questions outside the supported domain, revealing system limitations",
         "Medium", "Low", "Medium",
         "Define supported query types. Add graceful fallback messages. Rehearse demo script to control question flow."],
        ["R6",
         "Data contains PII or sensitive financial information requiring compliance measures",
         "Low", "High", "Medium",
         "Data audit (1.2) checks for PII. If found, add data masking. For POC, use anonymized subset if needed."],
    ]
    risk_col_widths = [
        available_w * 0.04,   # ID
        available_w * 0.20,   # Risk
        available_w * 0.11,   # Likelihood
        available_w * 0.09,   # Impact
        available_w * 0.10,   # Severity
        available_w * 0.46,   # Mitigation
    ]
    elements.append(build_table(risk_headers, risk_rows, risk_col_widths, risk_col=4))
    elements.append(Spacer(1, 6 * mm))

    # ═══════════════════════════════════════════════════════════════════
    # ASSUMPTIONS & CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════════
    elements.append(Paragraph("Assumptions &amp; Constraints", s["h1"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=EMERALD_900,
        spaceAfter=6, spaceBefore=2
    ))

    elements.append(Paragraph("Assumptions", s["h2"]))
    assumptions = [
        "The 50 spreadsheets are primarily in Excel (.xlsx) or CSV format with tabular structure (headers + rows).",
        "Sales and inventory data has a reasonably consistent schema across files (e.g., common columns like date, product, quantity, revenue).",
        "Weekly data updates are manual (user uploads new files). No real-time sync required.",
        "5-10 users are internal team members. No public access or external authentication required.",
        "The CEO demo is the primary success criteria. Production readiness is out of scope for this phase.",
        "OpenAI GPT-4 API is available and within acceptable cost range for the query volume (~100-500 queries/week).",
        "The client has no existing infrastructure preferences or constraints (greenfield deployment).",
        "No regulatory compliance requirements (SOC 2, HIPAA, GDPR) apply to this POC phase.",
        "The development team has access to AI tooling (Claude Code) to accelerate development.",
    ]
    for a in assumptions:
        elements.append(Paragraph(f"\u2022  {a}", s["bullet"]))
    elements.append(Spacer(1, 5 * mm))

    elements.append(Paragraph("Constraints", s["h2"]))
    constraints = [
        "Budget is fixed at $15K for the initial build. Scope will be cut before budget is exceeded.",
        "This is a POC/demo build. Production hardening, HA, auto-scaling, and advanced security are Phase 2.",
        "NL query accuracy target is 85%+ for common sales/inventory questions. Edge cases and complex multi-step queries may not be supported.",
        "The system is designed for 5-10 concurrent users. It will not scale beyond this without infrastructure changes.",
        "Data freshness is weekly. Sub-daily updates require pipeline rearchitecture (Phase 2).",
        "The NL query engine depends on the OpenAI API. Service outages or API changes are outside our control.",
    ]
    for c in constraints:
        elements.append(Paragraph(f"\u2022  {c}", s["bullet"]))

    # ── Build ─────────────────────────────────────────────────────────
    doc.build(elements, onFirstPage=first_page_callback, onLaterPages=footer_callback)
    return OUTPUT_FILE


if __name__ == "__main__":
    path = build_pdf()
    print(f"PDF generated: {path}")
