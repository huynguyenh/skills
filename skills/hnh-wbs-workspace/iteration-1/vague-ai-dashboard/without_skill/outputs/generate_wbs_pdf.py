#!/usr/bin/env python3
"""
Generate a Work Breakdown Structure (WBS) PDF for the
AI-Powered Analytics Dashboard project.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import (
    HexColor, white, black, Color
)
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import KeepTogether
import os
from datetime import date

# ── Colour palette ──────────────────────────────────────────
DARK_NAVY   = HexColor("#1B2A4A")
MID_BLUE    = HexColor("#2E5090")
LIGHT_BLUE  = HexColor("#4A90D9")
ACCENT_GOLD = HexColor("#D4A843")
SOFT_GREY   = HexColor("#F5F6FA")
BORDER_GREY = HexColor("#D0D5DD")
TEXT_DARK    = HexColor("#1A1A2E")
TEXT_MID     = HexColor("#4A4A5A")
ROW_ALT     = HexColor("#EDF2FA")
WHITE       = white

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(OUTPUT_DIR, "wbs_ai_analytics_dashboard.pdf")

# ── WBS data ────────────────────────────────────────────────
PROJECT_TITLE = "AI-Powered Analytics Dashboard"
PROJECT_DATE = date.today().strftime("%B %d, %Y")

# Assumptions noted in the brief
ASSUMPTIONS = [
    "Data is in CSV/Excel format (spreadsheets), volume under 100 MB.",
    "Natural language querying uses an LLM API (e.g. OpenAI) rather than a custom-trained model.",
    "\"Fast\" means sub-3-second query response for typical questions.",
    "\"Tight budget\" implies a small team (1-2 developers), open-source stack, and cloud-managed LLM API.",
    "MVP scope: upload data, ask questions, see chart/table answers. No multi-tenant auth or enterprise SSO.",
    "Target deployment: single cloud instance or serverless (e.g. Vercel + managed DB).",
    "No mobile-native app; responsive web UI is sufficient.",
]

UNKNOWNS = [
    "Exact data schemas and number of distinct spreadsheet types.",
    "Acceptable monthly cloud/API spend ceiling.",
    "Whether users need to save/share dashboards or just ad-hoc queries.",
    "Authentication requirements (open access vs. login-protected).",
    "Data sensitivity / compliance requirements (GDPR, HIPAA, etc.).",
    "Expected concurrent user count.",
]

# WBS hierarchy: (id, title, description, effort_days)
WBS = [
    {
        "id": "1",
        "title": "Project Management",
        "children": [
            ("1.1", "Project Kickoff & Planning", "Define scope, timeline, and roles. Align with client on MVP features.", "2d"),
            ("1.2", "Requirements Gathering", "Collect sample data, document question patterns, define acceptance criteria.", "2d"),
            ("1.3", "Risk & Assumption Log", "Document assumptions, unknowns, and mitigation plans.", "0.5d"),
            ("1.4", "Sprint Planning & Tracking", "Ongoing backlog grooming, standups, retrospectives.", "Ongoing"),
            ("1.5", "Client Demos & Feedback Loops", "Bi-weekly demos to gather feedback and adjust priorities.", "Ongoing"),
        ],
    },
    {
        "id": "2",
        "title": "Data Ingestion & Storage",
        "children": [
            ("2.1", "File Upload Interface", "Drag-and-drop UI for CSV/Excel uploads with validation and error feedback.", "2d"),
            ("2.2", "Data Parsing & Normalization", "Parse spreadsheets, infer column types, handle edge cases (dates, nulls).", "3d"),
            ("2.3", "Database Schema Design", "Design schema to store uploaded datasets; support multiple tables.", "1d"),
            ("2.4", "Data Storage Layer", "Implement storage using PostgreSQL or DuckDB for analytical queries.", "2d"),
            ("2.5", "Data Preview & Metadata", "Show column names, types, row counts, and sample rows after upload.", "1d"),
        ],
    },
    {
        "id": "3",
        "title": "Natural Language Query Engine",
        "children": [
            ("3.1", "LLM Integration Layer", "Connect to OpenAI (or similar) API; manage keys, retries, rate limits.", "2d"),
            ("3.2", "Schema-Aware Prompt Engineering", "Build prompts that include table schema so the LLM generates accurate SQL.", "3d"),
            ("3.3", "Text-to-SQL Pipeline", "Convert natural language to SQL, execute against DB, return results.", "3d"),
            ("3.4", "Query Validation & Safety", "Sanitise generated SQL; prevent destructive operations; handle errors.", "2d"),
            ("3.5", "Response Formatting", "Return results as structured data (table rows, aggregates) for the frontend.", "1d"),
            ("3.6", "Caching & Performance", "Cache frequent queries; optimise for sub-3-second response times.", "2d"),
        ],
    },
    {
        "id": "4",
        "title": "Frontend / Dashboard UI",
        "children": [
            ("4.1", "UI Framework Setup", "Scaffold React/Next.js project; configure Tailwind CSS and component library.", "1d"),
            ("4.2", "Data Upload Page", "Page for uploading, listing, and managing datasets.", "2d"),
            ("4.3", "Query Interface", "Chat-style input bar for natural language questions with autocomplete hints.", "3d"),
            ("4.4", "Results Display (Tables)", "Render query results as sortable, paginated data tables.", "2d"),
            ("4.5", "Results Display (Charts)", "Auto-select chart type (bar, line, pie) based on result shape; use Chart.js or Recharts.", "3d"),
            ("4.6", "Dashboard Layout & Navigation", "Top nav, sidebar for datasets, responsive layout.", "2d"),
            ("4.7", "Loading States & Error Handling", "Skeleton loaders, friendly error messages, retry prompts.", "1d"),
        ],
    },
    {
        "id": "5",
        "title": "Backend API & Infrastructure",
        "children": [
            ("5.1", "API Framework Setup", "Set up FastAPI (Python) or Next.js API routes; configure CORS.", "1d"),
            ("5.2", "File Upload Endpoint", "Handle multipart uploads, validate file types and size limits.", "1d"),
            ("5.3", "Query Endpoint", "Accept NL question, orchestrate LLM call, return results.", "2d"),
            ("5.4", "Environment & Config Management", "Manage API keys, DB credentials, and feature flags securely.", "0.5d"),
            ("5.5", "Logging & Monitoring", "Structured logging; basic health-check endpoint; error alerting.", "1d"),
        ],
    },
    {
        "id": "6",
        "title": "Testing & Quality Assurance",
        "children": [
            ("6.1", "Unit Tests (Backend)", "Test parsing, SQL generation, response formatting.", "2d"),
            ("6.2", "Integration Tests", "End-to-end tests: upload file, ask question, verify response.", "2d"),
            ("6.3", "Frontend Tests", "Component tests and basic E2E tests with Playwright or Cypress.", "2d"),
            ("6.4", "LLM Output Validation", "Evaluate accuracy of generated SQL against a golden-question set.", "2d"),
            ("6.5", "Performance Testing", "Verify sub-3-second response for datasets up to 100 MB.", "1d"),
        ],
    },
    {
        "id": "7",
        "title": "Deployment & DevOps",
        "children": [
            ("7.1", "CI/CD Pipeline", "GitHub Actions (or similar) for lint, test, build, deploy.", "1d"),
            ("7.2", "Infrastructure Provisioning", "Set up cloud resources (Vercel/Railway + managed Postgres).", "1d"),
            ("7.3", "Domain & SSL Setup", "Configure custom domain, HTTPS, DNS.", "0.5d"),
            ("7.4", "Production Deploy & Smoke Test", "Deploy to production, verify all flows end-to-end.", "1d"),
        ],
    },
    {
        "id": "8",
        "title": "Documentation & Handoff",
        "children": [
            ("8.1", "User Guide", "Short guide showing how to upload data and ask questions.", "1d"),
            ("8.2", "Developer Documentation", "README, architecture diagram, environment setup instructions.", "1d"),
            ("8.3", "Client Handoff & Training", "Walkthrough session with client; hand over credentials and repos.", "0.5d"),
        ],
    },
]


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title="WBS - AI-Powered Analytics Dashboard",
        author="Project Team",
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ───────────────────────────────────────
    s_title = ParagraphStyle(
        "WBSTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        textColor=DARK_NAVY,
        spaceAfter=4 * mm,
        alignment=TA_CENTER,
    )
    s_subtitle = ParagraphStyle(
        "WBSSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=TEXT_MID,
        alignment=TA_CENTER,
        spaceAfter=6 * mm,
    )
    s_section = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=MID_BLUE,
        spaceBefore=8 * mm,
        spaceAfter=3 * mm,
    )
    s_subsection = ParagraphStyle(
        "SubSection",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=DARK_NAVY,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
    )
    s_body = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=2 * mm,
    )
    s_bullet = ParagraphStyle(
        "BulletCustom",
        parent=s_body,
        leftIndent=12,
        bulletIndent=4,
        spaceBefore=1 * mm,
        spaceAfter=1 * mm,
    )
    s_table_header = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=WHITE,
    )
    s_table_cell = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
    )
    s_table_cell_bold = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=DARK_NAVY,
    )
    s_footer_note = ParagraphStyle(
        "FooterNote",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        textColor=TEXT_MID,
        alignment=TA_CENTER,
        spaceBefore=6 * mm,
    )

    story = []

    # ── Title page ──────────────────────────────────────────
    story.append(Spacer(1, 30 * mm))
    story.append(HRFlowable(width="60%", thickness=2, color=ACCENT_GOLD, spaceAfter=6 * mm))
    story.append(Paragraph("Work Breakdown Structure", s_title))
    story.append(Paragraph(PROJECT_TITLE, ParagraphStyle(
        "ProjectName", parent=s_title, fontSize=16, leading=22, textColor=LIGHT_BLUE,
        spaceAfter=6 * mm,
    )))
    story.append(HRFlowable(width="60%", thickness=2, color=ACCENT_GOLD, spaceBefore=2 * mm, spaceAfter=8 * mm))
    story.append(Paragraph(f"Date: {PROJECT_DATE}", s_subtitle))
    story.append(Paragraph("Document Type: WBS / Project Planning", s_subtitle))
    story.append(Paragraph("Status: Draft", s_subtitle))

    story.append(Spacer(1, 20 * mm))

    # Summary box
    summary_text = (
        "This document presents the Work Breakdown Structure for an AI-powered analytics "
        "dashboard that enables users to upload spreadsheet data and query it using natural "
        "language. The WBS covers all phases from planning through deployment and handoff."
    )
    summary_table = Table(
        [[Paragraph(summary_text, ParagraphStyle(
            "SummaryText", parent=s_body, textColor=DARK_NAVY, fontSize=10, leading=14
        ))]],
        colWidths=[doc.width * 0.85],
    )
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_GREY),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(summary_table)

    story.append(PageBreak())

    # ── Table of Contents ───────────────────────────────────
    story.append(Paragraph("Table of Contents", s_section))
    story.append(Spacer(1, 2 * mm))
    toc_items = [
        "1. Assumptions & Unknowns",
        "2. Work Breakdown Structure",
        "3. Effort Summary",
    ]
    for item in toc_items:
        story.append(Paragraph(item, ParagraphStyle(
            "TOCItem", parent=s_body, fontSize=11, leading=16, leftIndent=10,
            textColor=MID_BLUE, spaceAfter=2 * mm
        )))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY, spaceAfter=4 * mm))

    # ── Section 1: Assumptions & Unknowns ───────────────────
    story.append(Paragraph("1. Assumptions & Unknowns", s_section))

    story.append(Paragraph("Assumptions", s_subsection))
    for a in ASSUMPTIONS:
        story.append(Paragraph(f"\u2022  {a}", s_bullet))

    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Open Questions / Unknowns", s_subsection))
    for u in UNKNOWNS:
        story.append(Paragraph(f"\u2022  {u}", s_bullet))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY, spaceAfter=4 * mm))

    # ── Section 2: WBS Table ────────────────────────────────
    story.append(Paragraph("2. Work Breakdown Structure", s_section))

    col_widths = [
        doc.width * 0.08,   # ID
        doc.width * 0.22,   # Task
        doc.width * 0.58,   # Description
        doc.width * 0.12,   # Effort
    ]

    for phase in WBS:
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(f"{phase['id']}. {phase['title']}", s_subsection))

        header = [
            Paragraph("ID", s_table_header),
            Paragraph("Task", s_table_header),
            Paragraph("Description", s_table_header),
            Paragraph("Effort", s_table_header),
        ]
        rows = [header]
        for child in phase["children"]:
            wbs_id, task, desc, effort = child
            rows.append([
                Paragraph(wbs_id, s_table_cell),
                Paragraph(task, s_table_cell_bold),
                Paragraph(desc, s_table_cell),
                Paragraph(effort, s_table_cell),
            ])

        t = Table(rows, colWidths=col_widths, repeatRows=1)

        # Build style commands
        style_cmds = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), MID_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GREY),
            ("BOX", (0, 0), (-1, -1), 1, MID_BLUE),
            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            # Alignment
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (3, 0), (3, -1), "CENTER"),
        ]
        # Alternating row colours
        for i in range(1, len(rows)):
            if i % 2 == 0:
                style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))

        t.setStyle(TableStyle(style_cmds))
        story.append(t)

    story.append(PageBreak())

    # ── Section 3: Effort Summary ───────────────────────────
    story.append(Paragraph("3. Effort Summary", s_section))

    summary_header = [
        Paragraph("Phase", s_table_header),
        Paragraph("Work Packages", s_table_header),
        Paragraph("Estimated Effort", s_table_header),
    ]
    summary_rows = [summary_header]
    total_days = 0.0

    for phase in WBS:
        phase_days = 0.0
        ongoing_count = 0
        for child in phase["children"]:
            effort_str = child[3]
            if effort_str.lower() == "ongoing":
                ongoing_count += 1
            else:
                val = float(effort_str.replace("d", ""))
                phase_days += val
        total_days += phase_days
        effort_label = f"{phase_days:.1f} days"
        if ongoing_count > 0:
            effort_label += f" + {ongoing_count} ongoing"

        summary_rows.append([
            Paragraph(f"{phase['id']}. {phase['title']}", s_table_cell_bold),
            Paragraph(str(len(phase["children"])), s_table_cell),
            Paragraph(effort_label, s_table_cell),
        ])

    # Total row
    summary_rows.append([
        Paragraph("TOTAL", ParagraphStyle("TotalCell", parent=s_table_cell_bold, textColor=MID_BLUE)),
        Paragraph(str(sum(len(p["children"]) for p in WBS)), ParagraphStyle("TotalCell2", parent=s_table_cell_bold, textColor=MID_BLUE)),
        Paragraph(f"{total_days:.1f} days + ongoing PM", ParagraphStyle("TotalCell3", parent=s_table_cell_bold, textColor=MID_BLUE)),
    ])

    summary_col_widths = [
        doc.width * 0.45,
        doc.width * 0.20,
        doc.width * 0.35,
    ]
    st = Table(summary_rows, colWidths=summary_col_widths, repeatRows=1)
    st_style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), MID_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ("BOX", (0, 0), (-1, -1), 1, MID_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
        # Total row highlight
        ("BACKGROUND", (0, -1), (-1, -1), SOFT_GREY),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, MID_BLUE),
    ]
    for i in range(1, len(summary_rows) - 1):
        if i % 2 == 0:
            st_style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    st.setStyle(TableStyle(st_style_cmds))
    story.append(st)

    story.append(Spacer(1, 8 * mm))

    # Timeline estimate
    story.append(Paragraph("Estimated Timeline", s_subsection))
    timeline_text = (
        f"With a total of approximately <b>{total_days:.0f} person-days</b> of discrete work plus ongoing "
        "project management, a single full-stack developer can deliver the MVP in roughly "
        f"<b>{int(total_days / 5) + 2}\u2013{int(total_days / 4) + 2} weeks</b>, "
        "accounting for context-switching, client feedback cycles, and integration time. "
        "A two-person team could compress this to approximately "
        f"<b>{int(total_days / 8) + 1}\u2013{int(total_days / 6) + 1} weeks</b>."
    )
    story.append(Paragraph(timeline_text, s_body))

    # Budget note
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Budget-Conscious Stack Recommendation", s_subsection))
    stack_items = [
        "<b>Frontend:</b> Next.js + Tailwind CSS (free, open source)",
        "<b>Backend:</b> Next.js API routes or FastAPI (free, open source)",
        "<b>Database:</b> PostgreSQL on Supabase free tier or Railway ($5/mo)",
        "<b>LLM API:</b> OpenAI gpt-4o-mini for cost efficiency (~$0.15 per 1M input tokens)",
        "<b>Hosting:</b> Vercel free/hobby tier or Railway starter ($5/mo)",
        "<b>Estimated monthly run cost:</b> $10\u201350/mo depending on query volume",
    ]
    for item in stack_items:
        story.append(Paragraph(f"\u2022  {item}", s_bullet))

    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="40%", thickness=1, color=ACCENT_GOLD, spaceAfter=4 * mm))
    story.append(Paragraph("End of Document", s_footer_note))

    # ── Build ───────────────────────────────────────────────
    doc.build(story)
    print(f"PDF generated: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
