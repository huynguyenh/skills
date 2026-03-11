# WBS Chat Summary: HR Management Platform

**Date:** 2026-03-10
**Mode:** Estimate Mode (man-day estimates, critical path, timeline)
**Skill:** hnh-wbs

---

## Phase 1: Brief Intake

**Input:** Text brief in chat describing an HR management platform for mid-size Vietnamese companies (50-500 employees).

**Core features identified:**
1. Employee Directory
2. Leave Management
3. Payroll Integration (Vietnamese providers)
4. Performance Reviews
5. Org Chart

**Platforms:** Web app + Mobile app
**Team:** 3 developers + 1 designer

**Gaps noted:** No specific payroll providers named, no auth/authz model, no compliance requirements, no i18n mention, no data migration scope, no notification requirements, no reporting/analytics.

---

## Phase 2: CTO Challenge

Three categories of pushback were raised:

### Technical Feasibility Concerns
- **Vietnamese Payroll Integration** flagged as highest-risk item. Most VN providers lack public APIs; could require CSV import/export or screen scraping. Requires technical spike before estimates are reliable.
- **Mobile App** for a 3-dev team is ambitious. Cross-platform (React Native) is the only viable path.

### Missing from the Brief
- Authentication & authorization (SSO, RBAC for HR admin/manager/employee/payroll admin)
- Vietnam labor law compliance (mandated leave types, specific rules for each)
- PDPD compliance (Vietnam's Personal Data Protection Decree)
- Multi-language support (Vietnamese + English, date/currency formats)
- Data migration from existing systems
- Notification system (email/push for approval workflows)
- Reporting & analytics dashboards

### Hidden Complexities
- Leave Management: approval chains, carryover rules, half-day leaves, VN public holidays, retroactive adjustments
- Performance Reviews: goals management, 360 feedback, review cycles, calibration -- practically its own product
- Org Chart: must stay in sync with Employee Directory, handle reorgs
- Payroll Integration: bidirectional data flow with reconciliation

**User response:** "Good points, let's proceed with those considerations in mind."

---

## Phase 3: Approach Analysis

Three approaches evaluated:

### Option A: Modular Monolith + React Native (RECOMMENDED)
- **Stack:** NestJS backend, Next.js web, React Native mobile, PostgreSQL, Auth0, AWS
- **Pros:** Fastest path (~22-24 weeks), single codebase, shared React ecosystem, excellent AI acceleration potential, perfect team fit for 3 devs
- **Cons:** Scaling individual modules harder later (irrelevant at 500 employees)

### Option B: Microservices + Flutter
- **Pros:** Clean domain boundaries, independent scaling
- **Cons:** 1.5-2x longer (~35-40 weeks), massive DevOps overhead, two separate frontend stacks, team too small
- **Verdict:** Not recommended for this team size

### Option C: SaaS Platform + Customization (OrangeHRM/Odoo)
- **Pros:** Fastest MVP, proven workflows
- **Cons:** Customization ceiling, vendor lock-in, VN payroll integration still needs custom work
- **Verdict:** Not recommended due to customization ceiling

### AI Acceleration Plan
- Claude Code for ~40% boilerplate generation (CRUD modules, API endpoints, DB migrations, tests)
- Dify workflows for notification pipelines
- AI-assisted test generation per module
- Claude Code for React component scaffolding

### Phased Delivery
- Phase 1 (MVP): Employee Directory + Leave Management + Auth + Org Chart (web only)
- Phase 2: Performance Reviews + Mobile App
- Phase 3: Payroll Integration (after vendor evaluation spike)

**User response:** Accepted the recommendation (Option A).

---

## Phase 4: WBS Summary

### Effort by SDLC Phase

| Phase | Man-Days | Calendar Weeks |
|---|---|---|
| Discovery & Requirements | 15 | 2 |
| System Design & Architecture | 12 | 1.5 |
| Development Phase 1 (MVP) | 95 | 8 |
| Development Phase 2 | 55 | 5 |
| Development Phase 3 (Payroll) | 30 | 3 |
| Quality Assurance | 30 | 3 (overlaps) |
| Deployment & DevOps | 12 | 1.5 |
| Post-Launch & Maintenance | 10 | 1.5 |
| **Total** | **259** | **22-24 weeks** |

### Critical Path
Discovery -> Architecture -> Auth Module -> Employee Directory -> Leave Management -> QA -> Deployment

### Top Risks
1. Vietnamese payroll providers lack stable APIs (High likelihood, High impact)
2. Vietnam labor law leave rules more complex than anticipated (Medium likelihood, High impact)
3. PDPD compliance requires data localization (Medium likelihood, Medium impact)
4. Scope creep from client (High likelihood, Medium impact)

---

## Phase 5: PDF Generation

- Generated using ReportLab with ZenLabs brand guidelines
- A4, 20mm margins, Emerald 900 header bars, Ecru 100 alternating rows
- Helvetica-Bold (Rubik fallback) for headings, Helvetica (Inter fallback) for body
- Logo placed on cover page from design guideline assets
- 10 pages total

---

## Phase 6: PDF QA

### QA Round 1 - Issues Found: 3
1. **Major (Layout):** Development Phase 1 MVP table split poorly between pages 4-5, leaving page 5 with only 3 rows and excessive whitespace
2. **Major (Layout):** Dependency Map table split poorly between pages 7-8, similar excessive whitespace issue
3. **Minor (Tables):** "Recommendation" text truncated in Approach Analysis table due to narrow first column

### Fixes Applied
- Added PageBreak before Development Phase 1 MVP section
- Added PageBreak before Dependency Map section
- Added PageBreak before System Design & Architecture section
- Widened first column of Approach Analysis table from 25mm to 30mm
- Moved Approach Analysis table to start on a new page with WBS section following on same page

### QA Round 2 - Issues Found: 0
All pages pass clean. Layout correct, colors match brand, all sections present with complete content, no text overflow or truncation.

---

## Output

**PDF:** `wbs-hr-management-platform-2026-03-10.pdf`
**Location:** `~/.claude/skills/hnh-wbs-workspace/iteration-1/hr-platform-estimates/with_skill/outputs/`
