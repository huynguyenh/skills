#!/usr/bin/env python3
"""
Generate a WBS PDF for the HR Management Platform project.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

# --- Color Palette ---
PRIMARY = HexColor("#1a3a5c")       # Dark navy
SECONDARY = HexColor("#2980b9")     # Blue
ACCENT = HexColor("#27ae60")        # Green
WARNING = HexColor("#e67e22")       # Orange
LIGHT_BG = HexColor("#f0f4f8")     # Light blue-gray
HEADER_BG = HexColor("#1a3a5c")    # Dark navy
SUBHEADER_BG = HexColor("#2c5282") # Medium blue
ROW_ALT = HexColor("#edf2f7")      # Alternating row
BORDER_COLOR = HexColor("#cbd5e0") # Border
TEXT_DARK = HexColor("#2d3748")    # Dark text
TEXT_MUTED = HexColor("#718096")   # Muted text
RISK_HIGH = HexColor("#e53e3e")
RISK_MED = HexColor("#dd6b20")
RISK_LOW = HexColor("#38a169")
PHASE_COLORS = {
    "discovery": HexColor("#6b46c1"),
    "foundation": HexColor("#2b6cb0"),
    "core": HexColor("#2f855a"),
    "advanced": HexColor("#c05621"),
    "mobile": HexColor("#b83280"),
    "testing": HexColor("#e53e3e"),
    "launch": HexColor("#1a3a5c"),
}


OUTPUT_DIR = "/Users/hnh/.claude/skills/hnh-wbs-workspace/iteration-1/hr-platform-estimates/without_skill/outputs/"


# ============================================================
# WBS DATA MODEL
# ============================================================

PROJECT_META = {
    "title": "HR Management Platform",
    "subtitle": "Work Breakdown Structure & Effort Estimates",
    "client": "Mid-size Companies (50-500 employees)",
    "version": "1.0",
    "date": "March 10, 2026",
    "team": "3 Developers + 1 Designer",
    "platforms": "Web Application + Mobile Application (iOS & Android)",
}

ASSUMPTIONS = [
    "Team composition: 3 full-stack developers (2 senior, 1 mid-level) + 1 UI/UX designer.",
    "Working hours: 8 hours/day, 5 days/week. Estimates in person-days (PD).",
    "Tech stack: React (web), React Native (mobile), Node.js/NestJS (backend), PostgreSQL.",
    "Vietnamese payroll providers: integration via API with at least 2 providers (e.g., Misa, Bravo).",
    "Authentication via SSO/OAuth 2.0 with role-based access control (RBAC).",
    "Hosting on AWS (Vietnam region or Singapore for low latency).",
    "Mobile app shares ~60% of business logic with web via shared API layer.",
    "Agile methodology with 2-week sprints. Estimates include buffer for code review and QA.",
    "No legacy system migration in initial scope (can be added as Phase 2).",
    "Localization: Vietnamese (primary) + English.",
]

# WBS structure: list of phases, each with work packages
WBS_PHASES = [
    {
        "id": "1",
        "name": "Discovery & Planning",
        "color": "discovery",
        "packages": [
            {
                "id": "1.1",
                "name": "Requirements Analysis",
                "tasks": [
                    ("1.1.1", "Stakeholder interviews & workshops", 5, "All"),
                    ("1.1.2", "User persona development", 3, "Designer"),
                    ("1.1.3", "Feature prioritization (MoSCoW)", 2, "All"),
                    ("1.1.4", "Technical feasibility assessment", 3, "Dev Lead"),
                    ("1.1.5", "Vietnamese payroll provider API research", 4, "Dev"),
                ],
            },
            {
                "id": "1.2",
                "name": "UX/UI Design",
                "tasks": [
                    ("1.2.1", "Information architecture & user flows", 5, "Designer"),
                    ("1.2.2", "Wireframes (all core modules)", 8, "Designer"),
                    ("1.2.3", "Design system / component library", 6, "Designer"),
                    ("1.2.4", "Hi-fi mockups (web)", 10, "Designer"),
                    ("1.2.5", "Hi-fi mockups (mobile)", 7, "Designer"),
                    ("1.2.6", "Prototype & usability testing", 5, "Designer"),
                ],
            },
            {
                "id": "1.3",
                "name": "Architecture & Tech Setup",
                "tasks": [
                    ("1.3.1", "System architecture design", 4, "Dev Lead"),
                    ("1.3.2", "Database schema design", 5, "Dev Lead"),
                    ("1.3.3", "API contract definition (OpenAPI)", 4, "Dev"),
                    ("1.3.4", "CI/CD pipeline setup", 3, "Dev"),
                    ("1.3.5", "Dev environment & tooling", 3, "Dev"),
                    ("1.3.6", "Security architecture (RBAC, encryption)", 3, "Dev Lead"),
                ],
            },
        ],
    },
    {
        "id": "2",
        "name": "Foundation (Backend & Auth)",
        "color": "foundation",
        "packages": [
            {
                "id": "2.1",
                "name": "Backend Core",
                "tasks": [
                    ("2.1.1", "Project scaffolding (NestJS)", 2, "Dev"),
                    ("2.1.2", "Database setup & ORM config", 3, "Dev"),
                    ("2.1.3", "Base API structure & middleware", 3, "Dev"),
                    ("2.1.4", "Error handling & logging framework", 2, "Dev"),
                    ("2.1.5", "File upload/storage service (S3)", 3, "Dev"),
                ],
            },
            {
                "id": "2.2",
                "name": "Authentication & Authorization",
                "tasks": [
                    ("2.2.1", "User registration & login (JWT)", 4, "Dev"),
                    ("2.2.2", "Role-based access control (RBAC)", 5, "Dev"),
                    ("2.2.3", "SSO / OAuth integration", 4, "Dev"),
                    ("2.2.4", "Password reset & account recovery", 3, "Dev"),
                    ("2.2.5", "Session management & security", 3, "Dev"),
                    ("2.2.6", "Audit logging", 3, "Dev"),
                ],
            },
            {
                "id": "2.3",
                "name": "Web App Foundation",
                "tasks": [
                    ("2.3.1", "React project setup & config", 2, "Dev"),
                    ("2.3.2", "Design system implementation", 6, "Dev + Designer"),
                    ("2.3.3", "Layout & navigation shell", 4, "Dev"),
                    ("2.3.4", "Auth screens (login, register, forgot pw)", 4, "Dev"),
                    ("2.3.5", "State management setup", 2, "Dev"),
                    ("2.3.6", "API client & error handling", 3, "Dev"),
                ],
            },
        ],
    },
    {
        "id": "3",
        "name": "Core Modules (Web)",
        "color": "core",
        "packages": [
            {
                "id": "3.1",
                "name": "Employee Directory",
                "tasks": [
                    ("3.1.1", "Employee CRUD API", 5, "Dev"),
                    ("3.1.2", "Employee profile pages", 5, "Dev"),
                    ("3.1.3", "Search, filter & pagination", 4, "Dev"),
                    ("3.1.4", "Bulk import/export (CSV/Excel)", 5, "Dev"),
                    ("3.1.5", "Employee document management", 4, "Dev"),
                    ("3.1.6", "Profile photo upload & cropping", 2, "Dev"),
                ],
            },
            {
                "id": "3.2",
                "name": "Organization Chart",
                "tasks": [
                    ("3.2.1", "Org structure data model", 3, "Dev"),
                    ("3.2.2", "Interactive org chart visualization", 8, "Dev"),
                    ("3.2.3", "Department & team management", 4, "Dev"),
                    ("3.2.4", "Drag-and-drop reorganization", 5, "Dev"),
                    ("3.2.5", "Reporting line management", 3, "Dev"),
                ],
            },
            {
                "id": "3.3",
                "name": "Leave Management",
                "tasks": [
                    ("3.3.1", "Leave policy configuration engine", 6, "Dev"),
                    ("3.3.2", "Leave request & approval workflow", 6, "Dev"),
                    ("3.3.3", "Leave balance tracking & accrual", 5, "Dev"),
                    ("3.3.4", "Team calendar view", 5, "Dev"),
                    ("3.3.5", "Leave reports & analytics", 4, "Dev"),
                    ("3.3.6", "Public holiday calendar (Vietnam)", 3, "Dev"),
                    ("3.3.7", "Email/push notifications", 4, "Dev"),
                ],
            },
            {
                "id": "3.4",
                "name": "Payroll Integration",
                "tasks": [
                    ("3.4.1", "Payroll provider API adapter layer", 6, "Dev"),
                    ("3.4.2", "MISA payroll integration", 8, "Dev"),
                    ("3.4.3", "Bravo payroll integration", 7, "Dev"),
                    ("3.4.4", "Salary structure management", 5, "Dev"),
                    ("3.4.5", "Tax calculation (Vietnamese PIT)", 6, "Dev"),
                    ("3.4.6", "Social insurance (BHXH/BHYT/BHTN)", 5, "Dev"),
                    ("3.4.7", "Payslip generation & distribution", 5, "Dev"),
                    ("3.4.8", "Payroll reports & compliance", 4, "Dev"),
                ],
            },
            {
                "id": "3.5",
                "name": "Performance Reviews",
                "tasks": [
                    ("3.5.1", "Review cycle configuration", 5, "Dev"),
                    ("3.5.2", "Goal setting & OKR tracking", 6, "Dev"),
                    ("3.5.3", "Self-assessment forms", 4, "Dev"),
                    ("3.5.4", "360-degree feedback collection", 6, "Dev"),
                    ("3.5.5", "Manager review & calibration", 5, "Dev"),
                    ("3.5.6", "Performance analytics & dashboards", 5, "Dev"),
                    ("3.5.7", "Review history & trends", 3, "Dev"),
                ],
            },
        ],
    },
    {
        "id": "4",
        "name": "Advanced Features",
        "color": "advanced",
        "packages": [
            {
                "id": "4.1",
                "name": "Admin & Settings",
                "tasks": [
                    ("4.1.1", "Company settings & branding", 3, "Dev"),
                    ("4.1.2", "User role management UI", 4, "Dev"),
                    ("4.1.3", "Notification preferences", 3, "Dev"),
                    ("4.1.4", "System configuration panel", 4, "Dev"),
                    ("4.1.5", "Data backup & export tools", 3, "Dev"),
                ],
            },
            {
                "id": "4.2",
                "name": "Dashboard & Reporting",
                "tasks": [
                    ("4.2.1", "Executive dashboard", 5, "Dev"),
                    ("4.2.2", "HR analytics & KPIs", 5, "Dev"),
                    ("4.2.3", "Custom report builder", 6, "Dev"),
                    ("4.2.4", "Export to PDF/Excel", 4, "Dev"),
                    ("4.2.5", "Scheduled report delivery", 3, "Dev"),
                ],
            },
            {
                "id": "4.3",
                "name": "Notifications & Communication",
                "tasks": [
                    ("4.3.1", "Email notification engine", 4, "Dev"),
                    ("4.3.2", "In-app notification center", 4, "Dev"),
                    ("4.3.3", "Push notification service", 3, "Dev"),
                    ("4.3.4", "Announcement board", 3, "Dev"),
                ],
            },
        ],
    },
    {
        "id": "5",
        "name": "Mobile Application",
        "color": "mobile",
        "packages": [
            {
                "id": "5.1",
                "name": "Mobile Foundation",
                "tasks": [
                    ("5.1.1", "React Native project setup", 3, "Dev"),
                    ("5.1.2", "Mobile design system implementation", 5, "Dev + Designer"),
                    ("5.1.3", "Navigation & auth flow", 4, "Dev"),
                    ("5.1.4", "Offline data caching strategy", 4, "Dev"),
                    ("5.1.5", "Push notification integration", 3, "Dev"),
                ],
            },
            {
                "id": "5.2",
                "name": "Mobile Core Features",
                "tasks": [
                    ("5.2.1", "Employee directory (mobile)", 5, "Dev"),
                    ("5.2.2", "Leave request & approval (mobile)", 5, "Dev"),
                    ("5.2.3", "Payslip viewer (mobile)", 3, "Dev"),
                    ("5.2.4", "Org chart viewer (mobile)", 4, "Dev"),
                    ("5.2.5", "Performance review (mobile)", 4, "Dev"),
                    ("5.2.6", "Notification center (mobile)", 3, "Dev"),
                    ("5.2.7", "Profile management (mobile)", 3, "Dev"),
                ],
            },
            {
                "id": "5.3",
                "name": "Mobile Platform-Specific",
                "tasks": [
                    ("5.3.1", "iOS-specific optimizations", 3, "Dev"),
                    ("5.3.2", "Android-specific optimizations", 3, "Dev"),
                    ("5.3.3", "Biometric authentication", 3, "Dev"),
                    ("5.3.4", "Deep linking", 2, "Dev"),
                    ("5.3.5", "App store preparation", 3, "Dev"),
                ],
            },
        ],
    },
    {
        "id": "6",
        "name": "Testing & Quality Assurance",
        "color": "testing",
        "packages": [
            {
                "id": "6.1",
                "name": "Testing",
                "tasks": [
                    ("6.1.1", "Unit test coverage (backend)", 8, "Dev"),
                    ("6.1.2", "Unit test coverage (frontend)", 6, "Dev"),
                    ("6.1.3", "Integration testing (API)", 6, "Dev"),
                    ("6.1.4", "End-to-end testing (Cypress/Playwright)", 8, "Dev"),
                    ("6.1.5", "Mobile testing (both platforms)", 6, "Dev"),
                    ("6.1.6", "Performance & load testing", 4, "Dev"),
                    ("6.1.7", "Security testing & penetration test", 5, "Dev"),
                    ("6.1.8", "UAT preparation & support", 5, "All"),
                ],
            },
            {
                "id": "6.2",
                "name": "Bug Fixing & Polish",
                "tasks": [
                    ("6.2.1", "Bug triage & fixing (web)", 10, "Dev"),
                    ("6.2.2", "Bug triage & fixing (mobile)", 8, "Dev"),
                    ("6.2.3", "UI polish & design QA", 5, "Dev + Designer"),
                    ("6.2.4", "Performance optimization", 5, "Dev"),
                    ("6.2.5", "Accessibility audit & fixes", 4, "Dev + Designer"),
                ],
            },
        ],
    },
    {
        "id": "7",
        "name": "Deployment & Launch",
        "color": "launch",
        "packages": [
            {
                "id": "7.1",
                "name": "Infrastructure & DevOps",
                "tasks": [
                    ("7.1.1", "Production infrastructure setup (AWS)", 5, "Dev"),
                    ("7.1.2", "Database migration & seeding", 3, "Dev"),
                    ("7.1.3", "SSL, DNS & domain config", 2, "Dev"),
                    ("7.1.4", "Monitoring & alerting (Datadog/CloudWatch)", 3, "Dev"),
                    ("7.1.5", "Backup & disaster recovery", 3, "Dev"),
                ],
            },
            {
                "id": "7.2",
                "name": "Launch Activities",
                "tasks": [
                    ("7.2.1", "App store submission (iOS + Android)", 3, "Dev"),
                    ("7.2.2", "User documentation & help center", 5, "All"),
                    ("7.2.3", "Admin training materials", 3, "All"),
                    ("7.2.4", "Data migration tooling", 5, "Dev"),
                    ("7.2.5", "Go-live checklist & execution", 3, "All"),
                    ("7.2.6", "Post-launch monitoring & hotfixes", 5, "Dev"),
                ],
            },
        ],
    },
]

# Risk register
RISKS = [
    ("Vietnamese payroll API instability", "High", "Payroll providers may have limited/undocumented APIs. Build adapter layer with fallback modes.", "3.4"),
    ("Scope creep on performance module", "Medium", "Performance reviews can expand indefinitely. Lock scope to defined review types.", "3.5"),
    ("React Native performance on low-end devices", "Medium", "Vietnamese market includes budget Android phones. Profile early and set device baseline.", "5.x"),
    ("Regulatory changes (tax/insurance)", "Medium", "Vietnamese labor law changes frequently. Build configurable rule engine, not hardcoded.", "3.4"),
    ("Team capacity (3 devs is lean)", "High", "Parallel workstreams limited. Sequence phases carefully. Consider contractor for payroll.", "All"),
    ("Data privacy compliance", "Medium", "Vietnam Cybersecurity Law requirements. Engage legal counsel early for data residency.", "2.2"),
]


# ============================================================
# PDF GENERATION
# ============================================================

def compute_phase_totals(phases):
    """Compute totals per phase and per package."""
    results = []
    grand_total = 0
    for phase in phases:
        phase_total = 0
        pkg_results = []
        for pkg in phase["packages"]:
            pkg_total = sum(t[2] for t in pkg["tasks"])
            phase_total += pkg_total
            pkg_results.append((pkg, pkg_total))
        grand_total += phase_total
        results.append((phase, phase_total, pkg_results))
    return results, grand_total


def build_pdf():
    filepath = os.path.join(OUTPUT_DIR, "HR_Platform_WBS.pdf")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=20*mm,
        leftMargin=18*mm,
        rightMargin=18*mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    s_title = ParagraphStyle(
        "WBSTitle", parent=styles["Title"],
        fontSize=22, leading=28,
        textColor=PRIMARY, spaceAfter=4*mm,
        alignment=TA_CENTER,
    )
    s_subtitle = ParagraphStyle(
        "WBSSubtitle", parent=styles["Normal"],
        fontSize=12, leading=16,
        textColor=TEXT_MUTED, alignment=TA_CENTER,
        spaceAfter=8*mm,
    )
    s_section = ParagraphStyle(
        "WBSSection", parent=styles["Heading1"],
        fontSize=15, leading=20,
        textColor=PRIMARY, spaceBefore=6*mm, spaceAfter=3*mm,
        borderWidth=0,
    )
    s_subsection = ParagraphStyle(
        "WBSSubsection", parent=styles["Heading2"],
        fontSize=12, leading=16,
        textColor=SECONDARY, spaceBefore=4*mm, spaceAfter=2*mm,
    )
    s_body = ParagraphStyle(
        "WBSBody", parent=styles["Normal"],
        fontSize=9, leading=13,
        textColor=TEXT_DARK,
    )
    s_body_bold = ParagraphStyle(
        "WBSBodyBold", parent=s_body,
        fontName="Helvetica-Bold",
    )
    s_bullet = ParagraphStyle(
        "WBSBullet", parent=s_body,
        leftIndent=12, bulletIndent=4,
        spaceBefore=1*mm,
    )
    s_small = ParagraphStyle(
        "WBSSmall", parent=styles["Normal"],
        fontSize=7.5, leading=10,
        textColor=TEXT_MUTED,
    )
    s_table_header = ParagraphStyle(
        "WBSTableHeader", parent=styles["Normal"],
        fontSize=8.5, leading=11,
        textColor=white, fontName="Helvetica-Bold",
    )
    s_table_cell = ParagraphStyle(
        "WBSTableCell", parent=styles["Normal"],
        fontSize=8.5, leading=11,
        textColor=TEXT_DARK,
    )
    s_table_cell_bold = ParagraphStyle(
        "WBSTableCellBold", parent=s_table_cell,
        fontName="Helvetica-Bold",
    )
    s_table_cell_center = ParagraphStyle(
        "WBSTableCellCenter", parent=s_table_cell,
        alignment=TA_CENTER,
    )

    elements = []
    page_width = A4[0] - 36*mm  # available width

    # ---- COVER / HEADER ----
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph(PROJECT_META["title"], s_title))
    elements.append(Paragraph(PROJECT_META["subtitle"], s_subtitle))
    elements.append(HRFlowable(width="60%", thickness=1.5, color=SECONDARY, spaceAfter=6*mm))

    # Meta table
    meta_data = [
        ["Client Segment", PROJECT_META["client"]],
        ["Platforms", PROJECT_META["platforms"]],
        ["Team", PROJECT_META["team"]],
        ["Document Version", PROJECT_META["version"]],
        ["Date", PROJECT_META["date"]],
    ]
    meta_table = Table(meta_data, colWidths=[page_width * 0.3, page_width * 0.7])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
        ("TEXTCOLOR", (1, 0), (1, -1), TEXT_DARK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, BORDER_COLOR),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8*mm))

    # ---- ASSUMPTIONS ----
    elements.append(Paragraph("Key Assumptions", s_section))
    for i, a in enumerate(ASSUMPTIONS, 1):
        elements.append(Paragraph(f"<bullet>&bull;</bullet> {a}", s_bullet))
    elements.append(Spacer(1, 4*mm))

    # ---- EXECUTIVE SUMMARY ----
    phase_results, grand_total = compute_phase_totals(WBS_PHASES)

    # Calculate weeks (team of 4, but designer not full-time on dev)
    # Effective dev capacity: 3 devs * 5 days = 15 PD/week
    # Designer overlaps with dev phases partially
    # Rough calendar: grand_total / 15 (dev parallelism) + design lead time
    dev_weeks = round(grand_total / 15, 1)
    calendar_months = round(dev_weeks / 4.33, 1)

    elements.append(Paragraph("Executive Summary", s_section))
    summary_text = (
        f"This project encompasses <b>{grand_total} person-days</b> of effort across "
        f"<b>7 phases</b> and <b>{sum(len(p['packages']) for p in WBS_PHASES)} work packages</b>. "
        f"With a team of 3 developers working in parallel (plus 1 designer), the estimated "
        f"calendar duration is approximately <b>{calendar_months} months</b> "
        f"({dev_weeks} dev-weeks). "
        f"This includes a 2-week design lead time and accounts for sequential dependencies "
        f"between phases. A phased delivery approach is recommended, with the web MVP "
        f"(Phases 1-3) targeting month 5, mobile app by month 7, and full launch by month 8-9."
    )
    elements.append(Paragraph(summary_text, s_body))
    elements.append(Spacer(1, 4*mm))

    # Summary table by phase
    summary_header = [
        Paragraph("Phase", s_table_header),
        Paragraph("Work Packages", s_table_header),
        Paragraph("Tasks", s_table_header),
        Paragraph("Effort (PD)", s_table_header),
        Paragraph("% of Total", s_table_header),
    ]
    summary_rows = [summary_header]
    for phase, phase_total, pkg_results in phase_results:
        task_count = sum(len(pkg["tasks"]) for pkg in phase["packages"])
        pct = round(phase_total / grand_total * 100, 1)
        summary_rows.append([
            Paragraph(f"<b>{phase['id']}. {phase['name']}</b>", s_table_cell),
            Paragraph(str(len(phase["packages"])), s_table_cell_center),
            Paragraph(str(task_count), s_table_cell_center),
            Paragraph(f"<b>{phase_total}</b>", s_table_cell_center),
            Paragraph(f"{pct}%", s_table_cell_center),
        ])
    # Grand total row
    total_tasks = sum(len(pkg["tasks"]) for p in WBS_PHASES for pkg in p["packages"])
    total_pkgs = sum(len(p["packages"]) for p in WBS_PHASES)
    summary_rows.append([
        Paragraph("<b>TOTAL</b>", s_table_cell_bold),
        Paragraph(f"<b>{total_pkgs}</b>", s_table_cell_center),
        Paragraph(f"<b>{total_tasks}</b>", s_table_cell_center),
        Paragraph(f"<b>{grand_total}</b>", s_table_cell_center),
        Paragraph("<b>100%</b>", s_table_cell_center),
    ])

    col_widths_summary = [page_width*0.38, page_width*0.15, page_width*0.12, page_width*0.17, page_width*0.18]
    summary_table = Table(summary_rows, colWidths=col_widths_summary, repeatRows=1)
    summary_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BG),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ])
    # Alternating rows
    for i in range(1, len(summary_rows) - 1):
        if i % 2 == 0:
            summary_style.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
    summary_table.setStyle(summary_style)
    elements.append(summary_table)
    elements.append(Spacer(1, 6*mm))

    # ---- TIMELINE OVERVIEW ----
    elements.append(Paragraph("Recommended Timeline", s_section))
    timeline_data = [
        ["Month 1-2", "Discovery & Planning", "Requirements, UX/UI design, architecture"],
        ["Month 2-3", "Foundation", "Backend core, auth, web app shell"],
        ["Month 3-5", "Core Modules (Web)", "Employee directory, org chart, leave, payroll, performance"],
        ["Month 5-6", "Advanced Features", "Admin, dashboards, reporting, notifications"],
        ["Month 5-7", "Mobile App", "Parallel track: React Native app development"],
        ["Month 7-8", "Testing & QA", "Full testing cycle, UAT, bug fixes"],
        ["Month 8-9", "Deployment & Launch", "Infrastructure, app store, go-live"],
    ]
    timeline_header = [
        Paragraph("Period", s_table_header),
        Paragraph("Phase", s_table_header),
        Paragraph("Key Deliverables", s_table_header),
    ]
    timeline_rows = [timeline_header] + [
        [Paragraph(f"<b>{r[0]}</b>", s_table_cell),
         Paragraph(r[1], s_table_cell),
         Paragraph(r[2], s_table_cell)]
        for r in timeline_data
    ]
    timeline_table = Table(timeline_rows, colWidths=[page_width*0.18, page_width*0.27, page_width*0.55], repeatRows=1)
    tl_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])
    for i in range(1, len(timeline_rows)):
        if i % 2 == 0:
            tl_style.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
    timeline_table.setStyle(tl_style)
    elements.append(timeline_table)

    elements.append(PageBreak())

    # ---- DETAILED WBS ----
    elements.append(Paragraph("Detailed Work Breakdown Structure", s_title))
    elements.append(Spacer(1, 4*mm))

    for phase, phase_total, pkg_results in phase_results:
        color = PHASE_COLORS.get(phase["color"], PRIMARY)

        # Phase header
        phase_header_style = ParagraphStyle(
            f"PhaseHeader_{phase['id']}", parent=s_section,
            textColor=color,
        )
        elements.append(Paragraph(
            f"Phase {phase['id']}: {phase['name']}  "
            f"<font size='10' color='#{TEXT_MUTED.hexval()[2:]}'>"
            f"({phase_total} person-days)</font>",
            phase_header_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1, color=color, spaceAfter=3*mm))

        for pkg, pkg_total in pkg_results:
            elements.append(Paragraph(
                f"{pkg['id']} {pkg['name']}  "
                f"<font size='9' color='#{TEXT_MUTED.hexval()[2:]}'>"
                f"[{pkg_total} PD]</font>",
                s_subsection
            ))

            # Task table
            task_header = [
                Paragraph("WBS ID", s_table_header),
                Paragraph("Task", s_table_header),
                Paragraph("Effort (PD)", s_table_header),
                Paragraph("Owner", s_table_header),
            ]
            task_rows = [task_header]
            for task in pkg["tasks"]:
                task_rows.append([
                    Paragraph(task[0], s_table_cell_center),
                    Paragraph(task[1], s_table_cell),
                    Paragraph(str(task[2]), s_table_cell_center),
                    Paragraph(task[3], s_table_cell_center),
                ])
            # Subtotal
            task_rows.append([
                Paragraph("", s_table_cell),
                Paragraph(f"<b>Subtotal: {pkg['name']}</b>", s_table_cell_bold),
                Paragraph(f"<b>{pkg_total}</b>", s_table_cell_center),
                Paragraph("", s_table_cell),
            ])

            col_widths_task = [page_width*0.1, page_width*0.52, page_width*0.15, page_width*0.23]
            task_table = Table(task_rows, colWidths=col_widths_task, repeatRows=1)
            t_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), SUBHEADER_BG),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -2), 0.4, BORDER_COLOR),
                ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BG),
                ("LINEABOVE", (0, -1), (-1, -1), 1, color),
                ("BOX", (0, -1), (-1, -1), 0.6, color),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
            for i in range(1, len(task_rows) - 1):
                if i % 2 == 0:
                    t_style.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
            task_table.setStyle(t_style)
            elements.append(KeepTogether([task_table, Spacer(1, 3*mm)]))

        # Phase total bar
        phase_total_data = [[
            Paragraph(f"<b>Phase {phase['id']} Total: {phase['name']}</b>",
                      ParagraphStyle("pt", parent=s_table_cell_bold, textColor=white)),
            Paragraph(f"<b>{phase_total} person-days</b>",
                      ParagraphStyle("pt2", parent=s_table_cell_bold, textColor=white, alignment=TA_RIGHT)),
        ]]
        phase_total_table = Table(phase_total_data, colWidths=[page_width*0.7, page_width*0.3])
        phase_total_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("TEXTCOLOR", (0, 0), (-1, -1), white),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOX", (0, 0), (-1, -1), 1, color),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(phase_total_table)
        elements.append(Spacer(1, 6*mm))

    elements.append(PageBreak())

    # ---- EFFORT DISTRIBUTION ----
    elements.append(Paragraph("Effort Distribution by Role", s_section))

    # Compute rough role distribution
    dev_tasks = 0
    designer_tasks = 0
    shared_tasks = 0
    all_tasks = 0
    for phase in WBS_PHASES:
        for pkg in phase["packages"]:
            for task in pkg["tasks"]:
                effort = task[2]
                owner = task[3].lower()
                if "all" in owner:
                    all_tasks += effort
                elif "designer" in owner and "dev" in owner:
                    shared_tasks += effort
                elif "designer" in owner:
                    designer_tasks += effort
                else:
                    dev_tasks += effort

    role_data = [
        [Paragraph("Role", s_table_header),
         Paragraph("Person-Days", s_table_header),
         Paragraph("Percentage", s_table_header),
         Paragraph("Notes", s_table_header)],
        [Paragraph("Developers (3)", s_table_cell),
         Paragraph(str(dev_tasks), s_table_cell_center),
         Paragraph(f"{round(dev_tasks/grand_total*100,1)}%", s_table_cell_center),
         Paragraph("Split across 3 devs for parallelism", s_table_cell)],
        [Paragraph("Designer (1)", s_table_cell),
         Paragraph(str(designer_tasks), s_table_cell_center),
         Paragraph(f"{round(designer_tasks/grand_total*100,1)}%", s_table_cell_center),
         Paragraph("Front-loaded in Phase 1, advisory later", s_table_cell)],
        [Paragraph("Dev + Designer (shared)", s_table_cell),
         Paragraph(str(shared_tasks), s_table_cell_center),
         Paragraph(f"{round(shared_tasks/grand_total*100,1)}%", s_table_cell_center),
         Paragraph("Collaborative tasks (design system, QA)", s_table_cell)],
        [Paragraph("All Team", s_table_cell),
         Paragraph(str(all_tasks), s_table_cell_center),
         Paragraph(f"{round(all_tasks/grand_total*100,1)}%", s_table_cell_center),
         Paragraph("Workshops, UAT, launch activities", s_table_cell)],
        [Paragraph("<b>Total</b>", s_table_cell_bold),
         Paragraph(f"<b>{grand_total}</b>", s_table_cell_center),
         Paragraph("<b>100%</b>", s_table_cell_center),
         Paragraph("", s_table_cell)],
    ]
    role_table = Table(role_data, colWidths=[page_width*0.25, page_width*0.15, page_width*0.15, page_width*0.45], repeatRows=1)
    role_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BG),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
    for i in range(1, len(role_data) - 1):
        if i % 2 == 0:
            role_style.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
    role_table.setStyle(role_style)
    elements.append(role_table)
    elements.append(Spacer(1, 6*mm))

    # ---- RISK REGISTER ----
    elements.append(Paragraph("Risk Register", s_section))

    risk_header = [
        Paragraph("Risk", s_table_header),
        Paragraph("Impact", s_table_header),
        Paragraph("Mitigation", s_table_header),
        Paragraph("Phase", s_table_header),
    ]
    risk_rows = [risk_header]
    for risk in RISKS:
        impact_color = RISK_HIGH if risk[1] == "High" else RISK_MED if risk[1] == "Medium" else RISK_LOW
        risk_rows.append([
            Paragraph(risk[0], s_table_cell),
            Paragraph(f'<font color="#{impact_color.hexval()[2:]}">{risk[1]}</font>',
                      ParagraphStyle("rc", parent=s_table_cell, alignment=TA_CENTER)),
            Paragraph(risk[2], s_table_cell),
            Paragraph(risk[3], s_table_cell_center),
        ])
    risk_table = Table(risk_rows, colWidths=[page_width*0.22, page_width*0.1, page_width*0.55, page_width*0.13], repeatRows=1)
    risk_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])
    for i in range(1, len(risk_rows)):
        if i % 2 == 0:
            risk_style.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
    risk_table.setStyle(risk_style)
    elements.append(risk_table)
    elements.append(Spacer(1, 6*mm))

    # ---- COST ESTIMATION GUIDANCE ----
    elements.append(Paragraph("Cost Estimation Guidance", s_section))
    cost_text = (
        "The following table provides indicative cost ranges based on Vietnamese market rates "
        "for the team composition specified. Actual costs will vary based on seniority, "
        "location (HCMC/Hanoi vs. other cities), and engagement model."
    )
    elements.append(Paragraph(cost_text, s_body))
    elements.append(Spacer(1, 2*mm))

    cost_data = [
        [Paragraph("Role", s_table_header),
         Paragraph("Qty", s_table_header),
         Paragraph("Rate Range (USD/month)", s_table_header),
         Paragraph("Duration", s_table_header),
         Paragraph("Est. Cost Range", s_table_header)],
        [Paragraph("Senior Developer", s_table_cell),
         Paragraph("2", s_table_cell_center),
         Paragraph("$2,500 - $4,000", s_table_cell_center),
         Paragraph("9 months", s_table_cell_center),
         Paragraph("$45,000 - $72,000", s_table_cell_center)],
        [Paragraph("Mid-level Developer", s_table_cell),
         Paragraph("1", s_table_cell_center),
         Paragraph("$1,500 - $2,500", s_table_cell_center),
         Paragraph("9 months", s_table_cell_center),
         Paragraph("$13,500 - $22,500", s_table_cell_center)],
        [Paragraph("UI/UX Designer", s_table_cell),
         Paragraph("1", s_table_cell_center),
         Paragraph("$1,500 - $3,000", s_table_cell_center),
         Paragraph("6 months*", s_table_cell_center),
         Paragraph("$9,000 - $18,000", s_table_cell_center)],
        [Paragraph("Infrastructure (AWS)", s_table_cell),
         Paragraph("-", s_table_cell_center),
         Paragraph("$500 - $1,500/mo", s_table_cell_center),
         Paragraph("12 months", s_table_cell_center),
         Paragraph("$6,000 - $18,000", s_table_cell_center)],
        [Paragraph("<b>Estimated Total</b>", s_table_cell_bold),
         Paragraph("", s_table_cell_center),
         Paragraph("", s_table_cell_center),
         Paragraph("", s_table_cell_center),
         Paragraph("<b>$73,500 - $130,500</b>", s_table_cell_center)],
    ]
    cost_table = Table(cost_data, colWidths=[page_width*0.22, page_width*0.08, page_width*0.25, page_width*0.17, page_width*0.28], repeatRows=1)
    cost_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BG),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
    for i in range(1, len(cost_data) - 1):
        if i % 2 == 0:
            cost_style.add("BACKGROUND", (0, i), (-1, i), ROW_ALT)
    cost_table.setStyle(cost_style)
    elements.append(cost_table)
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph("* Designer full-time for Phase 1, part-time advisory for remaining phases.", s_small))

    elements.append(Spacer(1, 8*mm))

    # ---- RECOMMENDATIONS ----
    elements.append(Paragraph("Recommendations", s_section))
    recommendations = [
        "<b>Phased delivery:</b> Ship Web MVP (directory + leave + org chart) by month 5 for early feedback, then iterate.",
        "<b>Payroll integration:</b> Start with one provider (MISA) first; add Bravo in a subsequent sprint. This is the highest-risk module.",
        "<b>Mobile priority:</b> Begin mobile development in parallel with Phase 3 (month 3) to avoid becoming a bottleneck.",
        "<b>Contractor consideration:</b> With 3 developers, parallel capacity is limited. Consider a contract developer for payroll integration specifically.",
        "<b>Design lead time:</b> Designer should be 2-4 weeks ahead of development. Wireframes and mockups should be approved before sprint planning.",
        "<b>Testing strategy:</b> Invest in automated E2E tests early (Phase 2). Manual QA for payroll calculations is critical given Vietnamese tax complexity.",
        "<b>Security audit:</b> Schedule an external security review before launch, especially for payroll/PII data handling.",
        "<b>Localization:</b> Build i18n infrastructure from day one. Vietnamese primary, English secondary. Content translation is a parallel workstream.",
    ]
    for rec in recommendations:
        elements.append(Paragraph(f"<bullet>&bull;</bullet> {rec}", s_bullet))

    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="40%", thickness=0.5, color=BORDER_COLOR, spaceAfter=3*mm))
    elements.append(Paragraph(
        f"Document generated on {PROJECT_META['date']}. "
        f"Estimates are indicative and subject to refinement during the Discovery phase.",
        s_small
    ))

    # Build PDF
    doc.build(elements)
    print(f"PDF generated: {filepath}")
    return filepath, grand_total, phase_results


if __name__ == "__main__":
    filepath, grand_total, phase_results = build_pdf()
    print(f"Total effort: {grand_total} person-days")
    print(f"Phases: {len(phase_results)}")
    for phase, total, _ in phase_results:
        print(f"  {phase['id']}. {phase['name']}: {total} PD")
