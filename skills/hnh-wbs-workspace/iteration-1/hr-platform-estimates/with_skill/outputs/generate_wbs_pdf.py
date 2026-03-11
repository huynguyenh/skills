#!/usr/bin/env python3
"""
WBS PDF Generator — HR Management Platform
ZenLabs branded document using ReportLab
"""

import os
from datetime import date
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─── Brand Colors ────────────────────────────────────────────────────────────
PRIMARY_BLACK = HexColor("#09242E")
EMERALD_900 = HexColor("#04563E")
EMERALD_500 = HexColor("#43CE81")
EMERALD_300 = HexColor("#98D5AB")
EMERALD_100 = HexColor("#C8E6B7")
FIREFLY_200 = HexColor("#C0E0EF")
FIREFLY_100 = HexColor("#D8EDF5")
FIREFLY_300 = HexColor("#478FB4")
ECRU_100 = HexColor("#F6F6E8")
ECRU_300 = HexColor("#E3E2BC")
ECRU_700 = HexColor("#636230")
WHITE = HexColor("#FFFFFF")

# ─── Paths ───────────────────────────────────────────────────────────────────
LOGO_PATH = os.path.expanduser(
    "~/.claude/skills/hnh-design-guideline/assets/logos/logo-dark-on-light.png"
)
OUTPUT_DIR = os.path.expanduser(
    "~/.claude/skills/hnh-wbs-workspace/iteration-1/hr-platform-estimates/with_skill/outputs/"
)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "wbs-hr-management-platform-2026-03-10.pdf")

# ─── Page dimensions ─────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

# ─── Try to register fonts ───────────────────────────────────────────────────
HEADING_FONT = "Helvetica-Bold"
HEADING_FONT_NORMAL = "Helvetica"
BODY_FONT = "Helvetica"
BODY_FONT_BOLD = "Helvetica-Bold"

# Try to find and register Rubik and Inter
def try_register_fonts():
    global HEADING_FONT, HEADING_FONT_NORMAL, BODY_FONT, BODY_FONT_BOLD
    font_dirs = [
        os.path.expanduser("~/Library/Fonts"),
        "/Library/Fonts",
        "/System/Library/Fonts",
    ]
    for d in font_dirs:
        rubik_bold = os.path.join(d, "Rubik-Bold.ttf")
        rubik_reg = os.path.join(d, "Rubik-Regular.ttf")
        inter_reg = os.path.join(d, "Inter-Regular.ttf")
        inter_bold = os.path.join(d, "Inter-Bold.ttf")
        if os.path.exists(rubik_bold):
            try:
                pdfmetrics.registerFont(TTFont("Rubik-Bold", rubik_bold))
                HEADING_FONT = "Rubik-Bold"
            except:
                pass
        if os.path.exists(rubik_reg):
            try:
                pdfmetrics.registerFont(TTFont("Rubik", rubik_reg))
                HEADING_FONT_NORMAL = "Rubik"
            except:
                pass
        if os.path.exists(inter_reg):
            try:
                pdfmetrics.registerFont(TTFont("Inter", inter_reg))
                BODY_FONT = "Inter"
            except:
                pass
        if os.path.exists(inter_bold):
            try:
                pdfmetrics.registerFont(TTFont("Inter-Bold", inter_bold))
                BODY_FONT_BOLD = "Inter-Bold"
            except:
                pass

try_register_fonts()


# ─── Styles ──────────────────────────────────────────────────────────────────
def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName=HEADING_FONT,
        fontSize=28,
        textColor=WHITE,
        leading=34,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName=BODY_FONT,
        fontSize=14,
        textColor=WHITE,
        leading=20,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="CoverDate",
        fontName=BODY_FONT,
        fontSize=11,
        textColor=WHITE,
        leading=16,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName=HEADING_FONT,
        fontSize=14,
        textColor=EMERALD_900,
        leading=20,
        spaceBefore=16,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="SubHeading",
        fontName=HEADING_FONT,
        fontSize=11,
        textColor=PRIMARY_BLACK,
        leading=16,
        spaceBefore=10,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName=BODY_FONT,
        fontSize=9,
        textColor=PRIMARY_BLACK,
        leading=13,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        name="BodyBold",
        fontName=BODY_FONT_BOLD,
        fontSize=9,
        textColor=PRIMARY_BLACK,
        leading=13,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName=BODY_FONT,
        fontSize=8,
        textColor=PRIMARY_BLACK,
        leading=11,
    ))
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName=BODY_FONT_BOLD,
        fontSize=8,
        textColor=PRIMARY_BLACK,
        leading=11,
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName=BODY_FONT_BOLD,
        fontSize=8,
        textColor=WHITE,
        leading=11,
    ))
    styles.add(ParagraphStyle(
        name="SmallNote",
        fontName=BODY_FONT,
        fontSize=7,
        textColor=FIREFLY_300,
        leading=10,
    ))
    styles.add(ParagraphStyle(
        name="RiskLow",
        fontName=BODY_FONT_BOLD,
        fontSize=8,
        textColor=EMERALD_900,
        leading=11,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="RiskMedium",
        fontName=BODY_FONT_BOLD,
        fontSize=8,
        textColor=ECRU_700,
        leading=11,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="RiskHigh",
        fontName=BODY_FONT_BOLD,
        fontSize=8,
        textColor=PRIMARY_BLACK,
        leading=11,
        alignment=TA_CENTER,
    ))
    return styles


# ─── Footer callback ─────────────────────────────────────────────────────────
def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(BODY_FONT, 7)
    canvas.setFillColor(FIREFLY_300)
    canvas.drawString(MARGIN, 12 * mm, "ZenLabs  |  Work Breakdown Structure  |  HR Management Platform")
    canvas.drawRightString(PAGE_W - MARGIN, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def add_footer_cover(canvas, doc):
    """No footer on cover page"""
    pass


# ─── Helper: branded table ───────────────────────────────────────────────────
def make_table(data, col_widths=None, has_risk_col=False, risk_col_idx=None):
    """Create a branded table with Emerald 900 header, alternating rows."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_commands = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), EMERALD_900),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), BODY_FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        # Body
        ("FONTNAME", (0, 1), (-1, -1), BODY_FONT),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (-1, -1), PRIMARY_BLACK),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, FIREFLY_200),
        # Alignment
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    # Alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), ECRU_100))
        else:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), WHITE))

    # Risk column coloring
    if has_risk_col and risk_col_idx is not None:
        for i in range(1, len(data)):
            cell_val = data[i][risk_col_idx]
            if isinstance(cell_val, Paragraph):
                text = cell_val.text if hasattr(cell_val, 'text') else str(cell_val)
            else:
                text = str(cell_val)
            text_lower = text.lower()
            if "low" in text_lower:
                style_commands.append(("BACKGROUND", (risk_col_idx, i), (risk_col_idx, i), EMERALD_100))
            elif "medium" in text_lower:
                style_commands.append(("BACKGROUND", (risk_col_idx, i), (risk_col_idx, i), ECRU_300))
            elif "high" in text_lower:
                style_commands.append(("BACKGROUND", (risk_col_idx, i), (risk_col_idx, i), FIREFLY_100))

    t.setStyle(TableStyle(style_commands))
    return t


def p(text, style_name="BodyText2", styles=None):
    """Shortcut to create a Paragraph."""
    return Paragraph(text, styles[style_name])


def risk_cell(level, styles):
    """Create a styled risk cell."""
    style_map = {"Low": "RiskLow", "Medium": "RiskMedium", "High": "RiskHigh"}
    return Paragraph(level, styles[style_map.get(level, "TableCell")])


# ─── Build Document ──────────────────────────────────────────────────────────
def build_pdf():
    styles = get_styles()
    story = []

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # COVER PAGE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # We build the cover as a table with a colored background
    # Logo first (on white background above the green bar)
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=50 * mm, height=12 * mm)
        logo.hAlign = "LEFT"
        story.append(Spacer(1, 20 * mm))
        story.append(logo)
        story.append(Spacer(1, 20 * mm))

    # Green header block as a table
    cover_data = [[
        Paragraph("HR Management Platform", styles["CoverTitle"]),
    ], [
        Paragraph("Work Breakdown Structure", styles["CoverSubtitle"]),
    ], [
        Paragraph("March 10, 2026  |  Version 1.0", styles["CoverDate"]),
    ], [
        Paragraph("Prepared by ZenLabs", styles["CoverDate"]),
    ]]

    cover_table = Table(cover_data, colWidths=[CONTENT_W])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), EMERALD_900),
        ("TOPPADDING", (0, 0), (0, 0), 20),
        ("BOTTOMPADDING", (0, -1), (0, -1), 20),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(cover_table)

    story.append(Spacer(1, 30 * mm))

    # Cover summary info
    cover_info = [
        ["Project", "HR Management Platform for Mid-Size Companies (Vietnam)"],
        ["Client", "Mid-size companies (50-500 employees)"],
        ["Team", "3 Developers + 1 Designer"],
        ["Total Effort", "259 man-days"],
        ["Timeline", "22-24 weeks (~5.5-6 months)"],
        ["Mode", "Estimate Mode (includes man-day estimates)"],
    ]
    cover_info_data = [[
        Paragraph(row[0], styles["TableCellBold"]),
        Paragraph(row[1], styles["TableCell"]),
    ] for row in cover_info]

    cover_info_table = Table(cover_info_data, colWidths=[35 * mm, CONTENT_W - 35 * mm])
    cover_info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, FIREFLY_200),
        ("BACKGROUND", (0, 0), (0, -1), ECRU_100),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(cover_info_table)

    story.append(PageBreak())

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EXECUTIVE SUMMARY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(p("Executive Summary", "SectionHeading", styles))
    story.append(p(
        "This document presents the Work Breakdown Structure for an HR Management Platform "
        "targeting mid-size Vietnamese companies with 50 to 500 employees. The platform comprises "
        "five core modules: Employee Directory, Leave Management (compliant with Vietnam labor law), "
        "Payroll Integration with local Vietnamese providers, Performance Reviews, and Org Chart. "
        "The recommended approach is a modular monolith architecture using NestJS (backend), "
        "Next.js (web frontend), and React Native (mobile), with Auth0 for authentication and "
        "PostgreSQL for data persistence. Development is phased across three delivery milestones: "
        "MVP (Employee Directory, Leave Management, Org Chart, web only), Phase 2 (Performance Reviews, "
        "Mobile App), and Phase 3 (Payroll Integration). Total estimated effort is 259 man-days with "
        "a critical path timeline of 22-24 weeks for a team of 3 developers and 1 designer. "
        "The highest-risk item is payroll integration due to uncertain API availability from Vietnamese providers.",
        "BodyText2", styles
    ))

    story.append(Spacer(1, 6 * mm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TECHNICAL FEASIBILITY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(p("Technical Feasibility", "SectionHeading", styles))
    story.append(p(
        "Each major requirement has been assessed for technical feasibility. Items marked as "
        "needing a POC should be validated during the Discovery phase before committing to estimates.",
        "BodyText2", styles
    ))

    feasibility_data = [
        [
            Paragraph("Requirement", styles["TableHeader"]),
            Paragraph("Feasibility", styles["TableHeader"]),
            Paragraph("Assessment", styles["TableHeader"]),
        ],
        [
            Paragraph("Employee Directory", styles["TableCell"]),
            Paragraph("Viable", styles["RiskLow"]),
            Paragraph("Standard CRUD with search. Well-understood pattern, highly automatable with Claude Code.", styles["TableCell"]),
        ],
        [
            Paragraph("Leave Management", styles["TableCell"]),
            Paragraph("Viable", styles["RiskLow"]),
            Paragraph("Core workflow is standard. Complexity lies in Vietnam labor law compliance (leave types, accrual rules). Requires legal review during discovery.", styles["TableCell"]),
        ],
        [
            Paragraph("Payroll Integration", styles["TableCell"]),
            Paragraph("Needs POC", styles["RiskHigh"]),
            Paragraph("Vietnamese payroll providers vary widely in API maturity. Some may only support CSV import/export. A technical spike is required to evaluate top 3 providers before committing to integration approach.", styles["TableCell"]),
        ],
        [
            Paragraph("Performance Reviews", styles["TableCell"]),
            Paragraph("Viable", styles["RiskLow"]),
            Paragraph("Review cycles, goal tracking, and feedback collection are well-understood. Calibration views add moderate complexity but are not blocking.", styles["TableCell"]),
        ],
        [
            Paragraph("Org Chart", styles["TableCell"]),
            Paragraph("Viable", styles["RiskLow"]),
            Paragraph("Tree visualization libraries are mature. Drag-and-drop editing and real-time sync with directory are moderate effort.", styles["TableCell"]),
        ],
        [
            Paragraph("Web Application", styles["TableCell"]),
            Paragraph("Viable", styles["RiskLow"]),
            Paragraph("Next.js is a proven framework. Standard SPA with server-side rendering. No feasibility concerns.", styles["TableCell"]),
        ],
        [
            Paragraph("Mobile Application", styles["TableCell"]),
            Paragraph("Viable", styles["RiskLow"]),
            Paragraph("React Native enables code sharing with web. Team of 3 devs can manage if mobile scope is limited to core flows (directory, leave, notifications).", styles["TableCell"]),
        ],
        [
            Paragraph("Vietnam Compliance (PDPD)", styles["TableCell"]),
            Paragraph("Needs POC", styles["RiskMedium"]),
            Paragraph("Vietnam's Personal Data Protection Decree has specific requirements for employee data handling, consent, and storage locality. Needs legal review.", styles["TableCell"]),
        ],
    ]

    feasibility_table = make_table(feasibility_data, col_widths=[30 * mm, 22 * mm, CONTENT_W - 52 * mm], has_risk_col=True, risk_col_idx=1)
    story.append(feasibility_table)

    story.append(Spacer(1, 6 * mm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # APPROACH ANALYSIS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(p("Approach Analysis", "SectionHeading", styles))
    story.append(p(
        "Three architectural approaches were evaluated based on quality, time, and budget impact "
        "for a team of 3 developers and 1 designer building a multi-platform HR solution.",
        "BodyText2", styles
    ))

    story.append(PageBreak())

    approach_data = [
        [
            Paragraph("Criteria", styles["TableHeader"]),
            Paragraph("A: Modular Monolith + React Native", styles["TableHeader"]),
            Paragraph("B: Microservices + Flutter", styles["TableHeader"]),
            Paragraph("C: SaaS + Customization", styles["TableHeader"]),
        ],
        [
            Paragraph("Architecture", styles["TableCellBold"]),
            Paragraph("NestJS modular monolith, Next.js web, React Native mobile, PostgreSQL", styles["TableCell"]),
            Paragraph("Separate NestJS services per domain, Flutter mobile, PostgreSQL per service", styles["TableCell"]),
            Paragraph("OrangeHRM/Odoo base, custom modules for VN-specific features", styles["TableCell"]),
        ],
        [
            Paragraph("Quality", styles["TableCellBold"]),
            Paragraph("High. Single codebase simplifies testing and consistency. Shared logic between web and mobile.", styles["TableCell"]),
            Paragraph("High long-term, but inter-service complexity introduces integration risks for a small team.", styles["TableCell"]),
            Paragraph("Medium. Constrained by upstream platform decisions and customization limits.", styles["TableCell"]),
        ],
        [
            Paragraph("Time Impact", styles["TableCellBold"]),
            Paragraph("Fastest. ~22-24 weeks. One backend to maintain, shared React ecosystem.", styles["TableCell"]),
            Paragraph("Slowest. ~35-40 weeks. DevOps overhead, two frontend stacks, service coordination.", styles["TableCell"]),
            Paragraph("Fast initially (~12 weeks for basic), but customization grows exponentially. ~30+ weeks total.", styles["TableCell"]),
        ],
        [
            Paragraph("Budget Impact", styles["TableCellBold"]),
            Paragraph("Moderate. Auth0 licensing, AWS hosting. Predictable costs.", styles["TableCell"]),
            Paragraph("Highest. Multiple services = more infra, monitoring, and operational overhead.", styles["TableCell"]),
            Paragraph("Low initially, but licensing fees for SaaS platform + custom development on top.", styles["TableCell"]),
        ],
        [
            Paragraph("Team Fit", styles["TableCellBold"]),
            Paragraph("Excellent. 3 devs can own the full stack. TypeScript throughout.", styles["TableCell"]),
            Paragraph("Poor. 3 devs cannot effectively manage multiple services + Flutter.", styles["TableCell"]),
            Paragraph("Fair. Less custom code, but requires platform expertise the team may not have.", styles["TableCell"]),
        ],
        [
            Paragraph("AI Acceleration", styles["TableCellBold"]),
            Paragraph("Excellent. Claude Code for NestJS modules, React components, Prisma schemas, test generation.", styles["TableCell"]),
            Paragraph("Good. AI helps per-service, but coordination logic is harder to generate.", styles["TableCell"]),
            Paragraph("Limited. AI can help with custom modules but not with platform internals.", styles["TableCell"]),
        ],
        [
            Paragraph("Recommendation", styles["TableCellBold"]),
            Paragraph("RECOMMENDED", styles["RiskLow"]),
            Paragraph("Not recommended for this team size", styles["TableCell"]),
            Paragraph("Not recommended due to customization ceiling", styles["TableCell"]),
        ],
    ]

    approach_table = make_table(approach_data, col_widths=[30 * mm, (CONTENT_W - 30 * mm) / 3, (CONTENT_W - 30 * mm) / 3, (CONTENT_W - 30 * mm) / 3])
    story.append(approach_table)

    story.append(Spacer(1, 6 * mm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WBS BY PHASE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(p("WBS by SDLC Phase", "SectionHeading", styles))

    # --- Phase 1: Discovery ---
    story.append(p("1. Discovery &amp; Requirements", "SubHeading", styles))
    story.append(p("Estimated effort: 15 man-days | Calendar: ~2 weeks", "SmallNote", styles))

    disc_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("Requirements Documentation", styles["TableCellBold"]),
            Paragraph("Detailed functional specs and user stories for all 5 core modules. Acceptance criteria definition.", styles["TableCell"]),
            Paragraph("None", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("5", styles["TableCell"]),
        ],
        [
            Paragraph("Vietnam Labor Law Research", styles["TableCellBold"]),
            Paragraph("Research and document VN-specific leave policies, payroll rules, PDPD data handling requirements.", styles["TableCell"]),
            Paragraph("None", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("4", styles["TableCell"]),
        ],
        [
            Paragraph("Payroll Provider Evaluation", styles["TableCellBold"]),
            Paragraph("Technical spike: identify top 3 VN payroll providers, assess API availability and integration feasibility.", styles["TableCell"]),
            Paragraph("None", styles["TableCell"]),
            risk_cell("High", styles),
            Paragraph("4", styles["TableCell"]),
        ],
        [
            Paragraph("UX Research &amp; Wireframing", styles["TableCellBold"]),
            Paragraph("User flows, wireframes for all modules. Designer-led with stakeholder input.", styles["TableCell"]),
            Paragraph("Requirements Doc", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("2", styles["TableCell"]),
        ],
    ]
    story.append(make_table(disc_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))
    story.append(Spacer(1, 4 * mm))

    # --- Phase 2: System Design ---
    story.append(PageBreak())
    story.append(p("2. System Design &amp; Architecture", "SubHeading", styles))
    story.append(p("Estimated effort: 12 man-days | Calendar: ~1.5 weeks", "SmallNote", styles))

    arch_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("High-Level Architecture", styles["TableCellBold"]),
            Paragraph("System architecture diagram, service boundaries, deployment topology for NestJS modular monolith.", styles["TableCell"]),
            Paragraph("Discovery complete", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("2", styles["TableCell"]),
        ],
        [
            Paragraph("Data Model Design", styles["TableCellBold"]),
            Paragraph("PostgreSQL schema (Prisma) for employees, leave, reviews, org structure. Migration strategy.", styles["TableCell"]),
            Paragraph("Architecture", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("3", styles["TableCell"]),
        ],
        [
            Paragraph("API Contract Design", styles["TableCellBold"]),
            Paragraph("OpenAPI specs for all endpoints. Shared TypeScript types between web and mobile.", styles["TableCell"]),
            Paragraph("Data Model", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("3", styles["TableCell"]),
        ],
        [
            Paragraph("Security &amp; Auth Architecture", styles["TableCellBold"]),
            Paragraph("Auth0 setup, RBAC design (Admin/HR/Manager/Employee roles), SSO integration plan.", styles["TableCell"]),
            Paragraph("Architecture", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("2", styles["TableCell"]),
        ],
        [
            Paragraph("Infrastructure Blueprint", styles["TableCellBold"]),
            Paragraph("AWS infrastructure (ECS, RDS, S3, CloudFront), CI/CD pipeline design, environments.", styles["TableCell"]),
            Paragraph("Architecture", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("2", styles["TableCell"]),
        ],
    ]
    story.append(make_table(arch_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))
    story.append(Spacer(1, 4 * mm))

    # --- Phase 3: Development Phase 1 (MVP) ---
    story.append(PageBreak())
    story.append(p("3. Development \u2014 Phase 1 (MVP)", "SubHeading", styles))
    story.append(p("Estimated effort: 95 man-days | Calendar: ~8 weeks (3 devs parallel)", "SmallNote", styles))

    dev1_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("Auth &amp; User Management", styles["TableCellBold"]),
            Paragraph("Auth0 integration, login/signup, RBAC middleware, session management, SSO.", styles["TableCell"]),
            Paragraph("Security Arch", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("10", styles["TableCell"]),
        ],
        [
            Paragraph("Employee Directory", styles["TableCellBold"]),
            Paragraph("Employee profiles (CRUD), search/filter, profile photos, bulk import (CSV), i18n (VN/EN).", styles["TableCell"]),
            Paragraph("Auth Module", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("12", styles["TableCell"]),
        ],
        [
            Paragraph("Leave Management", styles["TableCellBold"]),
            Paragraph("VN labor law compliant leave types, request/approval workflows, balance tracking, calendar view, half-day support, public holidays.", styles["TableCell"]),
            Paragraph("Auth, Employee Dir", styles["TableCell"]),
            risk_cell("High", styles),
            Paragraph("20", styles["TableCell"]),
        ],
        [
            Paragraph("Org Chart", styles["TableCellBold"]),
            Paragraph("Visual hierarchy rendering, drag-and-drop editing, auto-sync with employee directory.", styles["TableCell"]),
            Paragraph("Employee Dir", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("10", styles["TableCell"]),
        ],
        [
            Paragraph("Web Frontend (Core)", styles["TableCellBold"]),
            Paragraph("Next.js app shell, layout, navigation, dashboard, i18n framework, responsive design.", styles["TableCell"]),
            Paragraph("API Contracts", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("15", styles["TableCell"]),
        ],
        [
            Paragraph("Notification System", styles["TableCellBold"]),
            Paragraph("Email (SendGrid) + push (FCM) notifications for leave approvals and system alerts.", styles["TableCell"]),
            Paragraph("Auth Module", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("5", styles["TableCell"]),
        ],
        [
            Paragraph("Admin Panel", styles["TableCellBold"]),
            Paragraph("Company settings, user management, leave policy config, public holiday management.", styles["TableCell"]),
            Paragraph("Auth Module", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("8", styles["TableCell"]),
        ],
        [
            Paragraph("UI/UX Design (Full)", styles["TableCellBold"]),
            Paragraph("Complete design system, all screens, component library, design tokens. Designer-led.", styles["TableCell"]),
            Paragraph("Wireframes", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("15", styles["TableCell"]),
        ],
    ]
    story.append(make_table(dev1_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))

    story.append(PageBreak())

    # --- Phase 4: Development Phase 2 ---
    story.append(p("4. Development \u2014 Phase 2", "SubHeading", styles))
    story.append(p("Estimated effort: 55 man-days | Calendar: ~5 weeks", "SmallNote", styles))

    dev2_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("Performance Reviews", styles["TableCellBold"]),
            Paragraph("Review cycles, goal setting, self/peer/manager reviews, rating scales, templates, calibration view.", styles["TableCell"]),
            Paragraph("Employee Dir", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("20", styles["TableCell"]),
        ],
        [
            Paragraph("Mobile App (React Native)", styles["TableCellBold"]),
            Paragraph("Core flows: employee directory, leave request/approval, notifications, profile. Shared logic with web.", styles["TableCell"]),
            Paragraph("Web Frontend, APIs", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("25", styles["TableCell"]),
        ],
        [
            Paragraph("Reporting &amp; Analytics", styles["TableCellBold"]),
            Paragraph("HR dashboards (headcount, leave utilization, review completion), CSV/PDF export.", styles["TableCell"]),
            Paragraph("All core modules", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("10", styles["TableCell"]),
        ],
    ]
    story.append(make_table(dev2_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))
    story.append(Spacer(1, 4 * mm))

    # --- Phase 5: Development Phase 3 ---
    story.append(p("5. Development \u2014 Phase 3 (Payroll)", "SubHeading", styles))
    story.append(p("Estimated effort: 30 man-days | Calendar: ~3 weeks", "SmallNote", styles))

    dev3_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("Payroll Integration", styles["TableCellBold"]),
            Paragraph("Integration with VN payroll providers, bidirectional data sync, reconciliation, error handling.", styles["TableCell"]),
            Paragraph("Payroll Spike, Leave Mgmt", styles["TableCell"]),
            risk_cell("High", styles),
            Paragraph("25", styles["TableCell"]),
        ],
        [
            Paragraph("Data Migration Tools", styles["TableCellBold"]),
            Paragraph("Import from Excel/CSV, data validation, dry-run mode, rollback capability.", styles["TableCell"]),
            Paragraph("Employee Dir", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("5", styles["TableCell"]),
        ],
    ]
    story.append(make_table(dev3_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))
    story.append(Spacer(1, 4 * mm))

    # --- Phase 6: QA ---
    story.append(p("6. Quality Assurance", "SubHeading", styles))
    story.append(p("Estimated effort: 30 man-days | Calendar: ~3 weeks (overlaps with development)", "SmallNote", styles))

    qa_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("Test Strategy &amp; Setup", styles["TableCellBold"]),
            Paragraph("Jest + Playwright setup, CI integration, code coverage targets, AI-generated test boilerplate.", styles["TableCell"]),
            Paragraph("Dev start", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("3", styles["TableCell"]),
        ],
        [
            Paragraph("Unit &amp; Integration Testing", styles["TableCellBold"]),
            Paragraph("Per-module testing (AI-assisted generation, human review), API contract tests.", styles["TableCell"]),
            Paragraph("Each module", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("10", styles["TableCell"]),
        ],
        [
            Paragraph("E2E Testing", styles["TableCellBold"]),
            Paragraph("Critical user journeys: leave request flow, review cycle, employee onboarding, payroll sync.", styles["TableCell"]),
            Paragraph("Feature complete", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("7", styles["TableCell"]),
        ],
        [
            Paragraph("UAT &amp; Compliance Testing", styles["TableCellBold"]),
            Paragraph("User acceptance testing with VN HR stakeholders, Vietnam labor law compliance verification.", styles["TableCell"]),
            Paragraph("Feature complete", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("5", styles["TableCell"]),
        ],
        [
            Paragraph("Security &amp; Performance Testing", styles["TableCellBold"]),
            Paragraph("Penetration testing, load testing (500 concurrent users), PDPD compliance audit.", styles["TableCell"]),
            Paragraph("Feature complete", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("5", styles["TableCell"]),
        ],
    ]
    story.append(make_table(qa_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))

    story.append(PageBreak())

    # --- Phase 7: Deployment ---
    story.append(p("7. Deployment &amp; DevOps", "SubHeading", styles))
    story.append(p("Estimated effort: 12 man-days | Calendar: ~1.5 weeks", "SmallNote", styles))

    deploy_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("CI/CD Pipeline", styles["TableCellBold"]),
            Paragraph("GitHub Actions, automated testing, staging/production deployment, Docker containerization.", styles["TableCell"]),
            Paragraph("Infra Blueprint", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("3", styles["TableCell"]),
        ],
        [
            Paragraph("Environment Setup", styles["TableCellBold"]),
            Paragraph("Staging + production environments on AWS, database provisioning, SSL, domain setup.", styles["TableCell"]),
            Paragraph("CI/CD", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("3", styles["TableCell"]),
        ],
        [
            Paragraph("Monitoring &amp; Alerting", styles["TableCellBold"]),
            Paragraph("Application monitoring (CloudWatch/Datadog), error tracking (Sentry), uptime monitoring.", styles["TableCell"]),
            Paragraph("Deployment", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("3", styles["TableCell"]),
        ],
        [
            Paragraph("App Store Deployment", styles["TableCellBold"]),
            Paragraph("iOS App Store + Google Play Store submissions, certificates, review process.", styles["TableCell"]),
            Paragraph("Mobile App", styles["TableCell"]),
            risk_cell("Medium", styles),
            Paragraph("3", styles["TableCell"]),
        ],
    ]
    story.append(make_table(deploy_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))
    story.append(Spacer(1, 4 * mm))

    # --- Phase 8: Post-Launch ---
    story.append(p("8. Post-Launch &amp; Maintenance", "SubHeading", styles))
    story.append(p("Estimated effort: 10 man-days | Calendar: ~1.5 weeks", "SmallNote", styles))

    post_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Scope", styles["TableHeader"]),
            Paragraph("Dependencies", styles["TableHeader"]),
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Days", styles["TableHeader"]),
        ],
        [
            Paragraph("Knowledge Transfer", styles["TableCellBold"]),
            Paragraph("Documentation, runbooks, training materials for client team.", styles["TableCell"]),
            Paragraph("All complete", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("4", styles["TableCell"]),
        ],
        [
            Paragraph("Bug Triage &amp; Stabilization", styles["TableCellBold"]),
            Paragraph("Post-launch bug fixes, performance tuning during first 2 weeks.", styles["TableCell"]),
            Paragraph("Launch", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("4", styles["TableCell"]),
        ],
        [
            Paragraph("Phase 2+ Roadmap", styles["TableCellBold"]),
            Paragraph("Technical debt assessment, feature prioritization for next iteration.", styles["TableCell"]),
            Paragraph("Stabilization", styles["TableCell"]),
            risk_cell("Low", styles),
            Paragraph("2", styles["TableCell"]),
        ],
    ]
    story.append(make_table(post_data, col_widths=[30 * mm, 65 * mm, 28 * mm, 18 * mm, 14 * mm], has_risk_col=True, risk_col_idx=3))
    story.append(Spacer(1, 6 * mm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DEPENDENCY MAP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(PageBreak())
    story.append(p("Dependency Map &amp; Critical Path", "SectionHeading", styles))
    story.append(p(
        "The critical path determines the minimum timeline. Modules on the critical path cannot be parallelized "
        "and directly affect the total project duration.",
        "BodyText2", styles
    ))

    dep_data = [
        [
            Paragraph("Module", styles["TableHeader"]),
            Paragraph("Depends On", styles["TableHeader"]),
            Paragraph("Blocks", styles["TableHeader"]),
            Paragraph("Critical Path", styles["TableHeader"]),
        ],
        [
            Paragraph("Requirements Documentation", styles["TableCellBold"]),
            Paragraph("\u2014", styles["TableCell"]),
            Paragraph("Architecture, Wireframes", styles["TableCell"]),
            Paragraph("Yes", styles["RiskHigh"]),
        ],
        [
            Paragraph("VN Labor Law Research", styles["TableCellBold"]),
            Paragraph("\u2014", styles["TableCell"]),
            Paragraph("Leave Management", styles["TableCell"]),
            Paragraph("Yes", styles["RiskHigh"]),
        ],
        [
            Paragraph("Payroll Provider Spike", styles["TableCellBold"]),
            Paragraph("\u2014", styles["TableCell"]),
            Paragraph("Payroll Integration", styles["TableCell"]),
            Paragraph("No (parallel)", styles["TableCell"]),
        ],
        [
            Paragraph("Architecture Design", styles["TableCellBold"]),
            Paragraph("Discovery", styles["TableCell"]),
            Paragraph("All development modules", styles["TableCell"]),
            Paragraph("Yes", styles["RiskHigh"]),
        ],
        [
            Paragraph("Auth &amp; User Management", styles["TableCellBold"]),
            Paragraph("Security Architecture", styles["TableCell"]),
            Paragraph("Employee Dir, Leave, Admin, Notifications", styles["TableCell"]),
            Paragraph("Yes", styles["RiskHigh"]),
        ],
        [
            Paragraph("Employee Directory", styles["TableCellBold"]),
            Paragraph("Auth Module", styles["TableCell"]),
            Paragraph("Leave Mgmt, Org Chart, Reviews, Data Migration", styles["TableCell"]),
            Paragraph("Yes", styles["RiskHigh"]),
        ],
        [
            Paragraph("Leave Management", styles["TableCellBold"]),
            Paragraph("Auth, Employee Dir, VN Law Research", styles["TableCell"]),
            Paragraph("Payroll Integration", styles["TableCell"]),
            Paragraph("Yes", styles["RiskHigh"]),
        ],
        [
            Paragraph("Org Chart", styles["TableCellBold"]),
            Paragraph("Employee Directory", styles["TableCell"]),
            Paragraph("\u2014", styles["TableCell"]),
            Paragraph("No", styles["TableCell"]),
        ],
        [
            Paragraph("Performance Reviews", styles["TableCellBold"]),
            Paragraph("Employee Directory", styles["TableCell"]),
            Paragraph("\u2014", styles["TableCell"]),
            Paragraph("No (Phase 2)", styles["TableCell"]),
        ],
        [
            Paragraph("Mobile App", styles["TableCellBold"]),
            Paragraph("Web Frontend, APIs stable", styles["TableCell"]),
            Paragraph("App Store Deploy", styles["TableCell"]),
            Paragraph("No (Phase 2)", styles["TableCell"]),
        ],
        [
            Paragraph("Payroll Integration", styles["TableCellBold"]),
            Paragraph("Payroll Spike, Leave Mgmt", styles["TableCell"]),
            Paragraph("\u2014", styles["TableCell"]),
            Paragraph("No (Phase 3)", styles["TableCell"]),
        ],
    ]
    story.append(make_table(dep_data, col_widths=[32 * mm, 40 * mm, 50 * mm, 33 * mm], has_risk_col=True, risk_col_idx=3))

    story.append(Spacer(1, 4 * mm))
    story.append(p(
        "<b>Critical path:</b> Discovery \u2192 Architecture \u2192 Auth Module \u2192 Employee Directory \u2192 "
        "Leave Management \u2192 QA \u2192 Deployment. This sequence defines the minimum project duration of ~22 weeks.",
        "BodyText2", styles
    ))

    story.append(PageBreak())

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RISK REGISTER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(p("Risk Register", "SectionHeading", styles))

    risk_data = [
        [
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Likelihood", styles["TableHeader"]),
            Paragraph("Impact", styles["TableHeader"]),
            Paragraph("Mitigation", styles["TableHeader"]),
        ],
        [
            Paragraph("Vietnamese payroll providers lack stable APIs, forcing CSV-based integration or custom adapters", styles["TableCell"]),
            Paragraph("High", styles["RiskHigh"]),
            Paragraph("High", styles["RiskHigh"]),
            Paragraph("Conduct payroll provider spike in Discovery. Design an adapter pattern that supports both API and CSV modes. Phase payroll integration last.", styles["TableCell"]),
        ],
        [
            Paragraph("Vietnam labor law leave rules are more complex than anticipated, requiring rework", styles["TableCell"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("High", styles["RiskHigh"]),
            Paragraph("Engage a VN labor law consultant during Discovery. Build leave rules as configurable policies, not hardcoded logic.", styles["TableCell"]),
        ],
        [
            Paragraph("PDPD compliance requires data localization or consent mechanisms not initially scoped", styles["TableCell"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Include PDPD review in Discovery phase. Choose AWS ap-southeast-1 (Singapore) or VN-local hosting. Build consent flows into onboarding.", styles["TableCell"]),
        ],
        [
            Paragraph("React Native mobile app has platform-specific bugs that delay release", styles["TableCell"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Limit mobile MVP scope to core flows only. Use Expo for faster iteration. Build mobile in Phase 2 after web APIs stabilize.", styles["TableCell"]),
        ],
        [
            Paragraph("Scope creep from client requesting additional features during development", styles["TableCell"]),
            Paragraph("High", styles["RiskHigh"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Lock Phase 1 scope with signed-off requirements. Use phased delivery to defer additions to future phases.", styles["TableCell"]),
        ],
        [
            Paragraph("Team capacity: 3 devs insufficient for parallel web + mobile development", styles["TableCell"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Phase mobile after web MVP. Use AI tooling aggressively for boilerplate. Consider contract developer for mobile if timeline is rigid.", styles["TableCell"]),
        ],
        [
            Paragraph("SSO integration complexity exceeds estimate due to varied client identity providers", styles["TableCell"]),
            Paragraph("Low", styles["TableCell"]),
            Paragraph("Medium", styles["RiskMedium"]),
            Paragraph("Use Auth0 which supports 30+ IdP integrations out of the box. Limit initial SSO to Google Workspace and Azure AD.", styles["TableCell"]),
        ],
    ]
    story.append(make_table(risk_data, col_widths=[40 * mm, 20 * mm, 20 * mm, CONTENT_W - 80 * mm]))
    story.append(Spacer(1, 6 * mm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TIMELINE (Estimate Mode)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(p("Timeline &amp; Effort Summary", "SectionHeading", styles))
    story.append(p(
        "All estimates assume an AI-augmented team using Claude Code for boilerplate generation, "
        "AI-assisted test writing, and Dify workflow automation where applicable. "
        "Calendar weeks assume 3 developers working in parallel with overlapping phases.",
        "BodyText2", styles
    ))

    timeline_data = [
        [
            Paragraph("Phase", styles["TableHeader"]),
            Paragraph("Man-Days", styles["TableHeader"]),
            Paragraph("Calendar Weeks", styles["TableHeader"]),
            Paragraph("Start", styles["TableHeader"]),
            Paragraph("End", styles["TableHeader"]),
        ],
        [
            Paragraph("Discovery &amp; Requirements", styles["TableCellBold"]),
            Paragraph("15", styles["TableCell"]),
            Paragraph("2", styles["TableCell"]),
            Paragraph("Week 1", styles["TableCell"]),
            Paragraph("Week 2", styles["TableCell"]),
        ],
        [
            Paragraph("System Design &amp; Architecture", styles["TableCellBold"]),
            Paragraph("12", styles["TableCell"]),
            Paragraph("1.5", styles["TableCell"]),
            Paragraph("Week 3", styles["TableCell"]),
            Paragraph("Week 4", styles["TableCell"]),
        ],
        [
            Paragraph("Development Phase 1 (MVP)", styles["TableCellBold"]),
            Paragraph("95", styles["TableCell"]),
            Paragraph("8", styles["TableCell"]),
            Paragraph("Week 5", styles["TableCell"]),
            Paragraph("Week 12", styles["TableCell"]),
        ],
        [
            Paragraph("Development Phase 2", styles["TableCellBold"]),
            Paragraph("55", styles["TableCell"]),
            Paragraph("5", styles["TableCell"]),
            Paragraph("Week 13", styles["TableCell"]),
            Paragraph("Week 17", styles["TableCell"]),
        ],
        [
            Paragraph("Development Phase 3 (Payroll)", styles["TableCellBold"]),
            Paragraph("30", styles["TableCell"]),
            Paragraph("3", styles["TableCell"]),
            Paragraph("Week 18", styles["TableCell"]),
            Paragraph("Week 20", styles["TableCell"]),
        ],
        [
            Paragraph("Quality Assurance", styles["TableCellBold"]),
            Paragraph("30", styles["TableCell"]),
            Paragraph("3", styles["TableCell"]),
            Paragraph("Week 18", styles["TableCell"]),
            Paragraph("Week 20", styles["TableCell"]),
        ],
        [
            Paragraph("Deployment &amp; DevOps", styles["TableCellBold"]),
            Paragraph("12", styles["TableCell"]),
            Paragraph("1.5", styles["TableCell"]),
            Paragraph("Week 21", styles["TableCell"]),
            Paragraph("Week 22", styles["TableCell"]),
        ],
        [
            Paragraph("Post-Launch &amp; Maintenance", styles["TableCellBold"]),
            Paragraph("10", styles["TableCell"]),
            Paragraph("1.5", styles["TableCell"]),
            Paragraph("Week 23", styles["TableCell"]),
            Paragraph("Week 24", styles["TableCell"]),
        ],
    ]
    story.append(make_table(timeline_data, col_widths=[40 * mm, 22 * mm, 28 * mm, 25 * mm, 25 * mm]))
    story.append(Spacer(1, 4 * mm))

    # Summary box
    summary_box_data = [
        [Paragraph("<b>Total Effort</b>", styles["TableCellBold"]), Paragraph("259 man-days", styles["TableCellBold"])],
        [Paragraph("<b>Team</b>", styles["TableCellBold"]), Paragraph("3 developers + 1 designer", styles["TableCell"])],
        [Paragraph("<b>Critical Path Duration</b>", styles["TableCellBold"]), Paragraph("22-24 weeks (~5.5-6 months)", styles["TableCellBold"])],
        [Paragraph("<b>MVP Delivery</b>", styles["TableCellBold"]), Paragraph("Week 12 (web app with Employee Dir, Leave Mgmt, Org Chart)", styles["TableCell"])],
        [Paragraph("<b>Full Platform Delivery</b>", styles["TableCellBold"]), Paragraph("Week 22-24 (all modules, web + mobile)", styles["TableCell"])],
    ]
    summary_box = Table(summary_box_data, colWidths=[40 * mm, CONTENT_W - 40 * mm])
    summary_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ECRU_100),
        ("GRID", (0, 0), (-1, -1), 0.5, FIREFLY_200),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_box)

    story.append(Spacer(1, 6 * mm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ASSUMPTIONS & CONSTRAINTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(p("Assumptions &amp; Constraints", "SectionHeading", styles))

    story.append(p("<b>Assumptions</b>", "BodyBold", styles))
    assumptions = [
        "The team has access to AI tooling (Claude Code, Dify) and is proficient in their use, resulting in ~30-40% acceleration on boilerplate and testing tasks.",
        "Auth0 (or equivalent) is approved for authentication; the team will not build a custom auth system.",
        "Vietnamese payroll providers will cooperate during the evaluation spike and provide technical documentation.",
        "The client will provide timely feedback during UAT and requirements validation (max 3 business days turnaround).",
        "A Vietnam labor law consultant or HR domain expert is available during the Discovery phase.",
        "The designer works full-time on this project during Phases 1-2 and transitions out after the design system is delivered.",
        "AWS is the approved cloud provider; no on-premises hosting requirement.",
        "The mobile app scope is limited to core flows (directory, leave, notifications) and does not replicate the full web experience.",
    ]
    for a in assumptions:
        story.append(p(f"\u2022  {a}", "BodyText2", styles))

    story.append(Spacer(1, 4 * mm))
    story.append(p("<b>Constraints</b>", "BodyBold", styles))
    constraints = [
        "Team size is fixed at 3 developers + 1 designer. No additional hires are planned.",
        "Budget for third-party services (Auth0, SendGrid, AWS) must be approved separately.",
        "Payroll integration scope depends on the outcome of the provider evaluation spike; estimates may change.",
        "The platform must comply with Vietnam's Personal Data Protection Decree (PDPD), which may require data localization.",
        "All UI must support Vietnamese and English from launch; additional languages are out of scope.",
        "Performance targets: system must handle 500 concurrent users with sub-2-second page load times.",
    ]
    for c in constraints:
        story.append(p(f"\u2022  {c}", "BodyText2", styles))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BUILD THE PDF
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    # Build with footer
    doc.build(story, onFirstPage=add_footer_cover, onLaterPages=add_footer)
    print(f"PDF generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_pdf()
