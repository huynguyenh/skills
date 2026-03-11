#!/usr/bin/env python3
"""
Generate a Work Breakdown Structure (WBS) PDF for a Vietnamese Restaurant
Mobile Ordering App project.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import (
    HexColor, white, black, Color
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from datetime import date
import os

OUTPUT_DIR = "/Users/hnh/.claude/skills/hnh-wbs-workspace/iteration-1/restaurant-app-scope/without_skill/outputs/"
PDF_FILE = os.path.join(OUTPUT_DIR, "wbs_restaurant_app.pdf")

# Color palette
PRIMARY = HexColor("#B22222")       # Dark red (Vietnamese theme)
SECONDARY = HexColor("#D4A017")     # Gold accent
DARK = HexColor("#1A1A2E")          # Near-black
LIGHT_BG = HexColor("#FFF8F0")      # Warm off-white
HEADER_BG = HexColor("#8B0000")     # Dark red header
L1_BG = HexColor("#FFF0E0")         # Level 1 background
L2_BG = HexColor("#FFFFFF")         # Level 2 background
BORDER_COLOR = HexColor("#D4A017")  # Gold border
GRAY = HexColor("#666666")
LIGHT_GRAY = HexColor("#EEEEEE")


# ──────────────────────────────────────────────────────────────
# WBS DATA
# ──────────────────────────────────────────────────────────────

WBS = [
    {
        "id": "1.0",
        "title": "Project Management & Planning",
        "packages": [
            {
                "id": "1.1",
                "title": "Project Initiation",
                "tasks": [
                    "1.1.1 – Define project charter and objectives",
                    "1.1.2 – Stakeholder identification and analysis",
                    "1.1.3 – Establish project governance structure",
                    "1.1.4 – Define success criteria and KPIs",
                ]
            },
            {
                "id": "1.2",
                "title": "Planning & Estimation",
                "tasks": [
                    "1.2.1 – Create detailed project schedule (Gantt)",
                    "1.2.2 – Resource planning and team allocation",
                    "1.2.3 – Budget estimation and approval",
                    "1.2.4 – Risk assessment and mitigation plan",
                    "1.2.5 – Communication plan (stakeholders, team)",
                ]
            },
            {
                "id": "1.3",
                "title": "Vendor & Tool Selection",
                "tasks": [
                    "1.3.1 – Evaluate cross-platform frameworks (React Native / Flutter)",
                    "1.3.2 – Select payment gateway provider",
                    "1.3.3 – Select cloud infrastructure (AWS / GCP / Azure)",
                    "1.3.4 – Select CI/CD and DevOps tooling",
                ]
            },
        ]
    },
    {
        "id": "2.0",
        "title": "Requirements & Design",
        "packages": [
            {
                "id": "2.1",
                "title": "Requirements Gathering",
                "tasks": [
                    "2.1.1 – Customer journey mapping (order, pay, pickup)",
                    "2.1.2 – Staff workflow analysis (order receipt, prep, completion)",
                    "2.1.3 – Menu data structure requirements (5 locations, variations)",
                    "2.1.4 – Loyalty program rules definition",
                    "2.1.5 – Multi-location business rules (hours, pricing, availability)",
                    "2.1.6 – Compliance requirements (PCI-DSS, data privacy)",
                ]
            },
            {
                "id": "2.2",
                "title": "UX/UI Design",
                "tasks": [
                    "2.2.1 – Information architecture and navigation flow",
                    "2.2.2 – Wireframes: Customer app (all screens)",
                    "2.2.3 – Wireframes: Staff tablet dashboard",
                    "2.2.4 – Visual design system (brand colors, typography, icons)",
                    "2.2.5 – High-fidelity mockups: Customer app",
                    "2.2.6 – High-fidelity mockups: Staff dashboard",
                    "2.2.7 – Interactive prototype and usability testing",
                    "2.2.8 – Design review and sign-off",
                ]
            },
            {
                "id": "2.3",
                "title": "Technical Architecture",
                "tasks": [
                    "2.3.1 – System architecture design (client, API, DB, services)",
                    "2.3.2 – API contract definition (OpenAPI / GraphQL schema)",
                    "2.3.3 – Database schema design",
                    "2.3.4 – Real-time communication architecture (WebSocket / SSE)",
                    "2.3.5 – Security architecture (auth, encryption, tokenization)",
                    "2.3.6 – Architecture review and approval",
                ]
            },
        ]
    },
    {
        "id": "3.0",
        "title": "Customer Mobile App (iOS & Android)",
        "packages": [
            {
                "id": "3.1",
                "title": "Authentication & Profile",
                "tasks": [
                    "3.1.1 – User registration (email, phone, social login)",
                    "3.1.2 – Login / logout / session management",
                    "3.1.3 – Profile management (name, phone, addresses)",
                    "3.1.4 – Password reset and account recovery",
                    "3.1.5 – Push notification opt-in and preferences",
                ]
            },
            {
                "id": "3.2",
                "title": "Restaurant & Menu Browsing",
                "tasks": [
                    "3.2.1 – Location selector (map view, list view, GPS auto-detect)",
                    "3.2.2 – Menu display with categories and search",
                    "3.2.3 – Item detail view (photos, description, allergens, spice level)",
                    "3.2.4 – Customization options (add-ons, modifications, notes)",
                    "3.2.5 – Menu availability by location and time of day",
                ]
            },
            {
                "id": "3.3",
                "title": "Cart & Ordering",
                "tasks": [
                    "3.3.1 – Add/remove/edit items in cart",
                    "3.3.2 – Cart summary with subtotal, tax, fees",
                    "3.3.3 – Order type selection (pickup, dine-in)",
                    "3.3.4 – Scheduled order (pick future time slot)",
                    "3.3.5 – Promo code / coupon application",
                    "3.3.6 – Order submission and confirmation",
                ]
            },
            {
                "id": "3.4",
                "title": "Payment Integration",
                "tasks": [
                    "3.4.1 – Credit/debit card payment (Stripe / Braintree)",
                    "3.4.2 – Apple Pay integration",
                    "3.4.3 – Google Pay integration",
                    "3.4.4 – Save payment methods for future use",
                    "3.4.5 – Payment receipt and email confirmation",
                    "3.4.6 – Refund handling (customer-side display)",
                ]
            },
            {
                "id": "3.5",
                "title": "Order Tracking",
                "tasks": [
                    "3.5.1 – Real-time order status updates (placed, preparing, ready)",
                    "3.5.2 – Push notifications for status changes",
                    "3.5.3 – Estimated prep time display",
                    "3.5.4 – Order history with reorder capability",
                ]
            },
            {
                "id": "3.6",
                "title": "Loyalty Program",
                "tasks": [
                    "3.6.1 – Points balance and tier display",
                    "3.6.2 – Points earning on orders",
                    "3.6.3 – Rewards catalog and redemption",
                    "3.6.4 – Points history and transaction log",
                    "3.6.5 – Referral program (invite friends, earn bonus)",
                ]
            },
        ]
    },
    {
        "id": "4.0",
        "title": "Staff Tablet Dashboard",
        "packages": [
            {
                "id": "4.1",
                "title": "Staff Authentication & Setup",
                "tasks": [
                    "4.1.1 – Staff login (PIN or credentials)",
                    "4.1.2 – Role-based access (manager, kitchen, counter)",
                    "4.1.3 – Location binding and shift configuration",
                ]
            },
            {
                "id": "4.2",
                "title": "Real-Time Order Management",
                "tasks": [
                    "4.2.1 – Live order queue (new orders appear in real-time)",
                    "4.2.2 – Order detail view with items, mods, notes",
                    "4.2.3 – Order status update (accept, preparing, ready, completed)",
                    "4.2.4 – Order prioritization and time tracking",
                    "4.2.5 – Audio/visual alerts for new orders",
                    "4.2.6 – Bulk order actions (mark multiple ready)",
                ]
            },
            {
                "id": "4.3",
                "title": "Menu & Operations Management",
                "tasks": [
                    "4.3.1 – Toggle item availability (86'd items)",
                    "4.3.2 – Adjust prep time estimates",
                    "4.3.3 – Pause/resume online ordering",
                    "4.3.4 – Daily order summary and reports",
                ]
            },
        ]
    },
    {
        "id": "5.0",
        "title": "Backend Services & Infrastructure",
        "packages": [
            {
                "id": "5.1",
                "title": "Core API Development",
                "tasks": [
                    "5.1.1 – User service (registration, auth, profile)",
                    "5.1.2 – Menu service (CRUD, categories, availability)",
                    "5.1.3 – Order service (create, update, status, history)",
                    "5.1.4 – Payment service (process, refund, webhook handling)",
                    "5.1.5 – Loyalty service (points calculation, rewards, tiers)",
                    "5.1.6 – Notification service (push, email, SMS)",
                    "5.1.7 – Location service (store info, hours, geo-queries)",
                ]
            },
            {
                "id": "5.2",
                "title": "Real-Time Infrastructure",
                "tasks": [
                    "5.2.1 – WebSocket server for order status streaming",
                    "5.2.2 – Event-driven architecture (order lifecycle events)",
                    "5.2.3 – Message queue setup (RabbitMQ / SQS) for async processing",
                ]
            },
            {
                "id": "5.3",
                "title": "Database & Storage",
                "tasks": [
                    "5.3.1 – Primary database setup (PostgreSQL)",
                    "5.3.2 – Caching layer (Redis) for menus, sessions",
                    "5.3.3 – Image/asset storage (S3 / CDN)",
                    "5.3.4 – Database migration and seed scripts",
                ]
            },
            {
                "id": "5.4",
                "title": "Cloud Infrastructure & DevOps",
                "tasks": [
                    "5.4.1 – Infrastructure as Code (Terraform / CloudFormation)",
                    "5.4.2 – CI/CD pipeline (build, test, deploy automation)",
                    "5.4.3 – Environment setup (dev, staging, production)",
                    "5.4.4 – Auto-scaling and load balancing configuration",
                    "5.4.5 – Logging, monitoring, alerting (Datadog / CloudWatch)",
                    "5.4.6 – Backup and disaster recovery plan",
                ]
            },
        ]
    },
    {
        "id": "6.0",
        "title": "Admin Portal (Web)",
        "packages": [
            {
                "id": "6.1",
                "title": "Menu Management",
                "tasks": [
                    "6.1.1 – CRUD for menu items, categories, modifiers",
                    "6.1.2 – Photo upload and management",
                    "6.1.3 – Pricing management (per-location overrides)",
                    "6.1.4 – Bulk import/export (CSV/Excel)",
                ]
            },
            {
                "id": "6.2",
                "title": "Business Operations",
                "tasks": [
                    "6.2.1 – Multi-location dashboard (orders, revenue, trends)",
                    "6.2.2 – Staff account management",
                    "6.2.3 – Loyalty program configuration (rules, tiers, rewards)",
                    "6.2.4 – Promo code and campaign management",
                    "6.2.5 – Customer data and analytics",
                    "6.2.6 – Revenue reports and export",
                ]
            },
        ]
    },
    {
        "id": "7.0",
        "title": "Quality Assurance & Testing",
        "packages": [
            {
                "id": "7.1",
                "title": "Testing Strategy & Automation",
                "tasks": [
                    "7.1.1 – Test plan creation (scope, approach, environments)",
                    "7.1.2 – Unit test coverage (backend services, frontend components)",
                    "7.1.3 – Integration testing (API, payment, notification flows)",
                    "7.1.4 – End-to-end testing (customer ordering flow, staff flow)",
                    "7.1.5 – Performance and load testing (concurrent orders, peak hours)",
                ]
            },
            {
                "id": "7.2",
                "title": "Specialized Testing",
                "tasks": [
                    "7.2.1 – Security testing and penetration testing",
                    "7.2.2 – Payment flow testing (PCI compliance verification)",
                    "7.2.3 – Multi-device and OS version testing",
                    "7.2.4 – Accessibility testing (WCAG compliance)",
                    "7.2.5 – Offline/poor connectivity behavior testing",
                    "7.2.6 – User acceptance testing (UAT) with restaurant staff",
                ]
            },
        ]
    },
    {
        "id": "8.0",
        "title": "Deployment & Launch",
        "packages": [
            {
                "id": "8.1",
                "title": "App Store Submission",
                "tasks": [
                    "8.1.1 – Apple App Store listing (screenshots, description, metadata)",
                    "8.1.2 – Google Play Store listing",
                    "8.1.3 – App review and approval process",
                    "8.1.4 – Beta testing program (TestFlight / Play Console)",
                ]
            },
            {
                "id": "8.2",
                "title": "Rollout Strategy",
                "tasks": [
                    "8.2.1 – Pilot launch at 1 location",
                    "8.2.2 – Staff training and onboarding materials",
                    "8.2.3 – Feedback collection and iteration",
                    "8.2.4 – Phased rollout to remaining 4 locations",
                    "8.2.5 – Go-live checklist and cutover plan",
                ]
            },
        ]
    },
    {
        "id": "9.0",
        "title": "Post-Launch & Operations",
        "packages": [
            {
                "id": "9.1",
                "title": "Support & Maintenance",
                "tasks": [
                    "9.1.1 – Bug triage and hotfix process",
                    "9.1.2 – Customer support integration (in-app chat / help center)",
                    "9.1.3 – Performance monitoring and optimization",
                    "9.1.4 – Regular dependency and security updates",
                ]
            },
            {
                "id": "9.2",
                "title": "Growth & Iteration",
                "tasks": [
                    "9.2.1 – Analytics review and feature prioritization",
                    "9.2.2 – A/B testing framework for UX improvements",
                    "9.2.3 – App update release cadence (bi-weekly / monthly)",
                    "9.2.4 – Roadmap planning for V2 features (delivery, catering, etc.)",
                ]
            },
        ]
    },
]


# ──────────────────────────────────────────────────────────────
# PDF GENERATION
# ──────────────────────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_FILE,
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=20*mm,
        leftMargin=18*mm,
        rightMargin=18*mm,
        title="WBS - Vietnamese Restaurant Mobile Ordering App",
        author="Project Management Office",
    )

    styles = getSampleStyleSheet()
    page_width = A4[0] - 36*mm  # usable width

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        textColor=HEADER_BG,
        spaceAfter=2*mm,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        textColor=GRAY,
        alignment=TA_CENTER,
        spaceAfter=6*mm,
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        textColor=white,
        spaceBefore=6*mm,
        spaceAfter=0,
    )
    package_title_style = ParagraphStyle(
        "PackageTitle",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=HEADER_BG,
        spaceBefore=0,
        spaceAfter=0,
        leftIndent=4*mm,
    )
    task_style = ParagraphStyle(
        "TaskItem",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=DARK,
        leftIndent=10*mm,
        spaceBefore=0,
        spaceAfter=0,
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=GRAY,
        alignment=TA_CENTER,
    )
    overview_style = ParagraphStyle(
        "Overview",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=DARK,
        spaceAfter=2*mm,
    )
    stats_label_style = ParagraphStyle(
        "StatsLabel",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=GRAY,
        alignment=TA_CENTER,
    )
    stats_value_style = ParagraphStyle(
        "StatsValue",
        parent=styles["Normal"],
        fontSize=18,
        leading=22,
        textColor=HEADER_BG,
        alignment=TA_CENTER,
    )

    story = []

    # ── COVER / HEADER ───────────────────────────────────────
    story.append(Spacer(1, 15*mm))

    # Title block
    story.append(Paragraph("Work Breakdown Structure", title_style))
    story.append(Spacer(1, 2*mm))

    # Decorative line
    line_table = Table(
        [[""]],
        colWidths=[80*mm],
        rowHeights=[0.8*mm],
    )
    line_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SECONDARY),
        ("LINEBELOW", (0, 0), (-1, -1), 0, white),
    ]))
    line_table.hAlign = "CENTER"
    story.append(line_table)
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph(
        "Vietnamese Restaurant Chain<br/>Mobile Ordering Application",
        subtitle_style
    ))

    # Meta info
    today = date.today().strftime("%B %d, %Y")
    meta_data = [
        ["Project", "Vietnamese Restaurant Mobile Ordering App"],
        ["Client", "Vietnamese Restaurant Chain (5 Locations)"],
        ["Date", today],
        ["Version", "1.0"],
        ["Status", "Draft"],
    ]
    meta_table = Table(meta_data, colWidths=[35*mm, 90*mm], rowHeights=[7*mm]*5)
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), HEADER_BG),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("RIGHTPADDING", (0, 0), (0, -1), 4*mm),
        ("LEFTPADDING", (1, 0), (1, -1), 4*mm),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, LIGHT_GRAY),
    ]))
    meta_table.hAlign = "CENTER"
    story.append(meta_table)

    story.append(Spacer(1, 10*mm))

    # ── STATISTICS SUMMARY BOX ────────────────────────────────
    total_phases = len(WBS)
    total_packages = sum(len(phase["packages"]) for phase in WBS)
    total_tasks = sum(
        len(task)
        for phase in WBS
        for pkg in phase["packages"]
        for task in [pkg["tasks"]]
    )

    stats_data = [
        [
            Paragraph("PHASES", stats_label_style),
            Paragraph("WORK PACKAGES", stats_label_style),
            Paragraph("TASKS", stats_label_style),
            Paragraph("PLATFORMS", stats_label_style),
        ],
        [
            Paragraph(str(total_phases), stats_value_style),
            Paragraph(str(total_packages), stats_value_style),
            Paragraph(str(total_tasks), stats_value_style),
            Paragraph("iOS + Android", ParagraphStyle(
                "PlatVal", parent=stats_value_style, fontSize=14, leading=18
            )),
        ],
    ]

    stats_table = Table(stats_data, colWidths=[page_width/4]*4, rowHeights=[6*mm, 12*mm])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), L1_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, SECONDARY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.3, SECONDARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBEFORE", (1, 0), (1, -1), 0.3, SECONDARY),
        ("LINEBEFORE", (2, 0), (2, -1), 0.3, SECONDARY),
        ("LINEBEFORE", (3, 0), (3, -1), 0.3, SECONDARY),
    ]))
    story.append(stats_table)

    story.append(Spacer(1, 8*mm))

    # ── PROJECT OVERVIEW ──────────────────────────────────────
    overview_heading = ParagraphStyle(
        "OverviewHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=HEADER_BG,
        spaceAfter=3*mm,
    )
    story.append(Paragraph("Project Overview", overview_heading))
    story.append(Paragraph(
        "This WBS defines the full scope of work for building a cross-platform mobile ordering "
        "application for a Vietnamese restaurant chain with 5 locations. The system encompasses "
        "a customer-facing app (iOS and Android), a staff-facing tablet dashboard for real-time "
        "order management, backend services, an admin portal, and supporting infrastructure.",
        overview_style
    ))
    story.append(Paragraph(
        "Key capabilities include menu browsing by location, online payment processing, "
        "real-time order tracking, a loyalty points program, and multi-location operations "
        "management. The project follows a phased rollout strategy starting with a single pilot "
        "location before expanding to all 5 sites.",
        overview_style
    ))

    story.append(Spacer(1, 4*mm))

    # ── SCOPE ASSUMPTIONS ─────────────────────────────────────
    story.append(Paragraph("Key Assumptions", overview_heading))
    assumptions = [
        "Cross-platform development using React Native or Flutter (single codebase for iOS and Android).",
        "Pickup and dine-in ordering only; delivery is deferred to a future phase.",
        "Payment processing via Stripe or equivalent PCI-compliant gateway.",
        "Cloud-hosted infrastructure with auto-scaling for peak meal times.",
        "Staff dashboard optimized for tablet form factors (iPad and Android tablets).",
        "Phased rollout: pilot at 1 location, then expand to remaining 4.",
    ]
    for a in assumptions:
        story.append(Paragraph(f"&bull;  {a}", ParagraphStyle(
            "Assumption", parent=overview_style, leftIndent=5*mm, spaceAfter=1*mm,
        )))

    story.append(PageBreak())

    # ── WBS DETAIL PAGES ──────────────────────────────────────
    # Table of Contents style header
    toc_heading = ParagraphStyle(
        "TOCHeading",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=HEADER_BG,
        spaceAfter=6*mm,
    )
    story.append(Paragraph("WBS Detail Breakdown", toc_heading))
    story.append(Spacer(1, 2*mm))

    for phase in WBS:
        # Phase header bar
        phase_header_data = [[
            Paragraph(
                f"<b>{phase['id']}  {phase['title']}</b>",
                ParagraphStyle("PhaseH", parent=section_title_style, spaceBefore=0, spaceAfter=0)
            )
        ]]
        phase_table = Table(phase_header_data, colWidths=[page_width], rowHeights=[9*mm])
        phase_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, -1), white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4*mm),
            ("ROUNDEDCORNERS", [2, 2, 0, 0]),
        ]))

        # Build rows for packages and tasks
        detail_rows = []
        for pkg in phase["packages"]:
            # Package header row
            detail_rows.append([
                Paragraph(f"<b>{pkg['id']}</b>", ParagraphStyle(
                    "PkgID", parent=package_title_style, leftIndent=0, alignment=TA_LEFT
                )),
                Paragraph(f"<b>{pkg['title']}</b>", package_title_style),
            ])
            # Task rows
            for task in pkg["tasks"]:
                detail_rows.append([
                    "",
                    Paragraph(task, task_style),
                ])

        if detail_rows:
            detail_table = Table(
                detail_rows,
                colWidths=[18*mm, page_width - 18*mm],
            )

            # Build style commands
            style_cmds = [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5*mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5*mm),
                ("LEFTPADDING", (0, 0), (0, -1), 4*mm),
                ("BOX", (0, 0), (-1, -1), 0.5, SECONDARY),
            ]

            # Shade package header rows
            row_idx = 0
            for pkg in phase["packages"]:
                style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), L1_BG))
                style_cmds.append(("LINEBELOW", (0, row_idx), (-1, row_idx), 0.3, SECONDARY))
                row_idx += 1  # package header
                task_count = len(pkg["tasks"])
                for t in range(task_count):
                    if t < task_count - 1:
                        style_cmds.append(("LINEBELOW", (1, row_idx), (1, row_idx), 0.15, LIGHT_GRAY))
                    row_idx += 1
                # Line between packages
                if row_idx < len(detail_rows):
                    style_cmds.append(("LINEABOVE", (0, row_idx), (-1, row_idx), 0.3, SECONDARY))

            detail_table.setStyle(TableStyle(style_cmds))

            # Keep phase header + detail together
            story.append(KeepTogether([
                phase_table,
                detail_table,
                Spacer(1, 5*mm),
            ]))
        else:
            story.append(phase_table)
            story.append(Spacer(1, 5*mm))

    # ── SUMMARY TABLE ─────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Phase Summary", toc_heading))

    summary_header = ["WBS ID", "Phase", "Work Packages", "Tasks"]
    summary_rows = [summary_header]
    for phase in WBS:
        pkg_count = len(phase["packages"])
        task_count = sum(len(pkg["tasks"]) for pkg in phase["packages"])
        summary_rows.append([
            phase["id"],
            phase["title"],
            str(pkg_count),
            str(task_count),
        ])
    # Totals row
    summary_rows.append([
        "",
        Paragraph("<b>TOTAL</b>", ParagraphStyle("TotalLabel", fontSize=9, textColor=HEADER_BG)),
        Paragraph(f"<b>{total_packages}</b>", ParagraphStyle("TotalVal", fontSize=9, textColor=HEADER_BG, alignment=TA_CENTER)),
        Paragraph(f"<b>{total_tasks}</b>", ParagraphStyle("TotalVal2", fontSize=9, textColor=HEADER_BG, alignment=TA_CENTER)),
    ])

    summary_table = Table(
        summary_rows,
        colWidths=[16*mm, 80*mm, 30*mm, 30*mm],
        repeatRows=1,
    )
    summary_table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        # Body
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("ALIGN", (2, 1), (3, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [white, L1_BG]),
        ("GRID", (0, 0), (-1, -1), 0.3, SECONDARY),
        ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
        # Totals row
        ("BACKGROUND", (0, -1), (-1, -1), HexColor("#FFF0E0")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, HEADER_BG),
    ]))
    summary_table.hAlign = "CENTER"
    story.append(summary_table)

    story.append(Spacer(1, 10*mm))

    # ── GLOSSARY / NOTES ──────────────────────────────────────
    story.append(Paragraph("Notes", overview_heading))
    notes = [
        "This WBS covers scope definition only. Effort estimates, resource assignments, and "
        "schedule dependencies are maintained in the project plan.",
        "Work packages may be further decomposed during sprint planning as the team refines "
        "acceptance criteria for each item.",
        "The WBS follows a product-oriented decomposition. Cross-cutting concerns (security, "
        "performance, accessibility) are embedded within each phase rather than isolated.",
        "Delivery integration (e.g., DoorDash, UberEats) and catering features are explicitly "
        "excluded from V1 scope and reserved for the V2 roadmap.",
    ]
    for i, n in enumerate(notes, 1):
        story.append(Paragraph(f"{i}. {n}", ParagraphStyle(
            "Note", parent=overview_style, leftIndent=5*mm, spaceAfter=2*mm, fontSize=9,
        )))

    # ── BUILD ─────────────────────────────────────────────────
    doc.build(story)
    print(f"PDF generated: {PDF_FILE}")
    print(f"  Phases:        {total_phases}")
    print(f"  Work Packages: {total_packages}")
    print(f"  Tasks:         {total_tasks}")


if __name__ == "__main__":
    build_pdf()
