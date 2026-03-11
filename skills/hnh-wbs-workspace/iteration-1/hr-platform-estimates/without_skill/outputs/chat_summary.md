# HR Management Platform - WBS & Effort Estimates

## Task Summary

**Request:** Create a Work Breakdown Structure (WBS) with effort estimates for an HR Management Platform targeting mid-size Vietnamese companies (50-500 employees).

**Approach:** Built a comprehensive WBS from general project management and software engineering knowledge, without referencing any skill files. Used Python with reportlab to generate a professionally formatted PDF.

---

## Project Overview

| Attribute | Value |
|---|---|
| **Total Effort** | 531 person-days |
| **Team** | 3 Developers + 1 Designer |
| **Calendar Duration** | ~8-9 months |
| **Platforms** | Web (React) + Mobile (React Native, iOS & Android) |
| **Tech Stack** | React, React Native, Node.js/NestJS, PostgreSQL, AWS |

## WBS Structure (7 Phases, 20 Work Packages, 102 Tasks)

### Phase 1: Discovery & Planning (80 PD)
- **1.1 Requirements Analysis** (17 PD) - Stakeholder interviews, persona development, feasibility, payroll provider research
- **1.2 UX/UI Design** (41 PD) - IA, wireframes, design system, hi-fi mockups (web + mobile), prototyping
- **1.3 Architecture & Tech Setup** (22 PD) - System architecture, DB schema, API contracts, CI/CD, security design

### Phase 2: Foundation - Backend & Auth (56 PD)
- **2.1 Backend Core** (13 PD) - Project scaffolding, DB setup, base API, file storage
- **2.2 Authentication & Authorization** (22 PD) - JWT auth, RBAC, SSO, password recovery, audit logging
- **2.3 Web App Foundation** (21 PD) - React setup, design system implementation, layout, auth screens

### Phase 3: Core Modules - Web (161 PD) - Largest phase
- **3.1 Employee Directory** (25 PD) - CRUD, profiles, search, bulk import/export, documents
- **3.2 Organization Chart** (23 PD) - Interactive visualization, drag-and-drop, department management
- **3.3 Leave Management** (33 PD) - Policy engine, approval workflows, balance tracking, team calendar, Vietnam holidays
- **3.4 Payroll Integration** (46 PD) - Adapter layer, MISA & Bravo integration, tax (PIT), social insurance (BHXH/BHYT/BHTN), payslips
- **3.5 Performance Reviews** (34 PD) - Review cycles, OKRs, self-assessment, 360 feedback, calibration, analytics

### Phase 4: Advanced Features (54 PD)
- **4.1 Admin & Settings** (17 PD) - Company settings, role management, configuration panel
- **4.2 Dashboard & Reporting** (23 PD) - Executive dashboard, HR analytics, custom report builder, export
- **4.3 Notifications & Communication** (14 PD) - Email, in-app, push notifications, announcement board

### Phase 5: Mobile Application (60 PD)
- **5.1 Mobile Foundation** (19 PD) - React Native setup, mobile design system, offline caching
- **5.2 Mobile Core Features** (27 PD) - Directory, leave, payslips, org chart, performance, notifications
- **5.3 Mobile Platform-Specific** (14 PD) - iOS/Android optimizations, biometric auth, deep linking, app store prep

### Phase 6: Testing & Quality Assurance (80 PD)
- **6.1 Testing** (48 PD) - Unit, integration, E2E, mobile, performance, security, UAT
- **6.2 Bug Fixing & Polish** (32 PD) - Bug triage, UI polish, performance optimization, accessibility

### Phase 7: Deployment & Launch (40 PD)
- **7.1 Infrastructure & DevOps** (16 PD) - AWS setup, migrations, SSL/DNS, monitoring, backup/DR
- **7.2 Launch Activities** (24 PD) - App store submission, documentation, training, data migration, go-live

## Recommended Timeline

| Period | Phase | Milestone |
|---|---|---|
| Month 1-2 | Discovery & Planning | Requirements locked, designs approved |
| Month 2-3 | Foundation | Backend running, auth working, web shell ready |
| Month 3-5 | Core Modules (Web) | Web MVP with all 5 core modules |
| Month 5-6 | Advanced Features | Admin, dashboards, notifications |
| Month 5-7 | Mobile App | Parallel track alongside advanced features |
| Month 7-8 | Testing & QA | Full test cycle, UAT complete |
| Month 8-9 | Deployment & Launch | Production go-live |

## Effort Distribution by Role

| Role | Person-Days | % of Total |
|---|---|---|
| Developers (3) | 444 | 83.6% |
| Designer (1) | 44 | 8.3% |
| Dev + Designer (shared) | 16 | 3.0% |
| All Team | 27 | 5.1% |

## Cost Estimation (Vietnamese Market Rates)

| Role | Qty | Monthly Rate (USD) | Duration | Cost Range |
|---|---|---|---|---|
| Senior Developer | 2 | $2,500 - $4,000 | 9 months | $45,000 - $72,000 |
| Mid-level Developer | 1 | $1,500 - $2,500 | 9 months | $13,500 - $22,500 |
| UI/UX Designer | 1 | $1,500 - $3,000 | 6 months | $9,000 - $18,000 |
| Infrastructure (AWS) | - | $500 - $1,500/mo | 12 months | $6,000 - $18,000 |
| **Total** | | | | **$73,500 - $130,500** |

## Key Risks

1. **Vietnamese payroll API instability (High)** - Providers may have limited/undocumented APIs. Mitigate with adapter layer and fallback modes.
2. **Team capacity - 3 devs is lean (High)** - Limited parallel workstreams. Consider contractor for payroll integration.
3. **Scope creep on performance module (Medium)** - Lock scope to defined review types.
4. **React Native on low-end devices (Medium)** - Vietnamese market includes budget Android phones. Profile early.
5. **Regulatory changes (Medium)** - Vietnamese labor law changes frequently. Build configurable rule engine.
6. **Data privacy compliance (Medium)** - Vietnam Cybersecurity Law requirements for data residency.

## Key Recommendations

1. **Phased delivery** - Ship Web MVP (directory + leave + org chart) by month 5 for early feedback
2. **Payroll first** - Start with one provider (MISA), add Bravo later. Highest risk module.
3. **Mobile parallel track** - Begin mobile in month 3 to avoid bottleneck
4. **Contractor for payroll** - Consider specialized contractor given team size constraints
5. **Design lead time** - Designer should be 2-4 weeks ahead of development
6. **Automated testing early** - Invest in E2E tests from Phase 2; manual QA critical for payroll/tax
7. **Security audit** - External review before launch for payroll/PII data
8. **Localization from day one** - Build i18n infrastructure early (Vietnamese primary, English secondary)

## Outputs Generated

| File | Description |
|---|---|
| `HR_Platform_WBS.pdf` | Full WBS document (29 KB, multi-page PDF with tables, risk register, cost estimates) |
| `chat_summary.md` | This analysis summary |
| `generate_wbs_pdf.py` | Python script used to generate the PDF (for reproducibility) |

## Methodology Notes

- Estimates are in **person-days (PD)** assuming 8-hour workdays, 5-day weeks
- Calendar duration accounts for parallelism (3 devs) but sequential phase dependencies
- A 15-20% contingency buffer is recommended on top of these estimates for unknowns
- Mobile effort is reduced (~60% of web) due to shared API layer and React Native code reuse
- Payroll integration (46 PD) is the single largest and highest-risk work package, warranting dedicated attention
