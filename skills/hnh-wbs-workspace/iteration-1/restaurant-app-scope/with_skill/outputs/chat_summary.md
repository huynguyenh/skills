# WBS Chat Summary: Vietnamese Restaurant Mobile Ordering App

**Date:** 2026-03-10
**Mode:** Scope (no estimates)
**Skill used:** hnh-wbs

---

## Phase 1: Brief Analysis

**Project:** Cross-platform mobile ordering app for a Vietnamese restaurant chain (5 locations).

**Core requirements extracted:**
- Customer-facing mobile app (iOS + Android): menu browsing, ordering, online payment, loyalty points
- Staff-facing tablet dashboard: real-time order management
- Multi-location support (5 restaurants)

**Gaps identified:** Security requirements, POS integration details, menu management workflow, order fulfillment lifecycle, analytics/reporting, scalability targets, PCI-DSS compliance, localization, offline capability.

---

## Phase 2: CTO Challenge

Three categories of pushback were raised:

### Technical Feasibility Concerns
- Real-time WebSocket reliability in restaurant WiFi environments (spotty connections, tablet sleep, kitchen chaos)
- PCI-DSS compliance not mentioned in brief -- non-negotiable for payment processing
- Multi-location data model implications (per-location menus, pricing, hours, loyalty cross-location behavior)

### Missing from the Brief
- Menu management ownership and update workflow
- Order fulfillment lifecycle (confirmation, prep time, status tracking, out-of-stock handling)
- POS integration requirements (existing system? standalone?)
- Analytics and reporting expectations
- Offline resilience for staff tablets
- Localization requirements (English + Vietnamese?)

### Hidden Complexities
- "Earn loyalty points" implies: calculation rules, tiers, redemption, expiry, history, promotional bonuses, possibly referrals
- "Pay online" implies: multiple payment methods, refunds, partial refunds, tips, tax calculation, receipts, failure recovery
- "Both iOS and Android" is a major architecture decision (native vs cross-platform)
- Multi-location ordering implies: geolocation, per-location availability, location-specific hours

**User response:** Acknowledged all points, agreed to proceed with these considerations in mind.

---

## Phase 3: Approach Analysis

### Decisions Made

| Decision | Chosen Approach | Rationale |
|---|---|---|
| Mobile Framework | **React Native** | Mature ecosystem, strong Stripe/push SDKs, single codebase, large talent pool, Claude Code generates RN boilerplate efficiently |
| Backend Architecture | **NestJS Modular Monolith** | Clean module boundaries, built-in WebSocket support, single deployment, TypeScript shared with frontend. Microservices overkill for 5 locations. |
| Database | **PostgreSQL + Redis** | ACID transactions for payments/orders, Redis for caching and real-time pub/sub |
| Payment Processing | **Stripe** | PCI compliance via tokenization, Apple Pay/Google Pay, React Native SDK, refund handling |
| Real-Time Updates | **Socket.IO via NestJS** | Native NestJS support, Redis adapter for scaling, robust reconnection |
| Loyalty Program | **Custom-built** | Simple enough, deeply tied to order flow, avoids third-party dependency |
| Push Notifications | **Firebase Cloud Messaging** | Free tier sufficient, cross-platform, mature React Native libraries |

### AI Acceleration Identified
- Claude Code: NestJS module scaffolding, RN screen boilerplate, API contracts, DB migrations, test stubs
- Dify Workflows: Order notification flows, customer re-engagement, loyalty milestone alerts
- AI-Assisted QA: Test case generation from OpenAPI specs, automated accessibility audits

**User response:** Accepted all recommendations.

---

## Phase 4: WBS Structure

Full WBS built across 6 SDLC phases, 32 modules total:

1. **Discovery & Requirements** (4 modules): Requirements doc, user story mapping, menu data model spike, POS integration spike
2. **System Design & Architecture** (5 modules): High-level architecture, data model, API contracts, security architecture, infrastructure blueprint
3. **Development** (15 modules):
   - Backend (8): Auth, Location, Menu Management, Order, Payment, Loyalty, Real-Time Notifications, Admin
   - Frontend (7): Customer Onboarding, Menu Browsing, Cart & Checkout, Order Tracking, Loyalty, Staff Order Dashboard, Staff Management
4. **Quality Assurance** (5 modules): Unit/integration testing, E2E testing, payment testing, performance/load testing, UAT & accessibility
5. **Deployment & DevOps** (4 modules): CI/CD pipeline, environment setup, app store submission, monitoring & alerting
6. **Post-Launch & Maintenance** (4 modules): Launch support, post-launch monitoring, knowledge transfer, Phase 2 roadmap

---

## Phase 5: PDF Generation

- Generated using ReportLab with ZenLabs brand guidelines
- Design guideline skill consulted for colors, typography, layout
- Logo placed on cover page from `~/.claude/skills/hnh-design-guideline/assets/logos/logo-dark-on-light.png`

---

## Phase 6: PDF QA

### QA Round 1 (Failed)
Issues found:
1. **Page 4 blank** (critical) -- unnecessary PageBreak after Approach Analysis
2. **Page 10 blank** (critical) -- unnecessary PageBreak before Assumptions section
3. **"Likelihood" column word-wrapped** (major) -- Risk Register column too narrow, rendered as "Likelihoo d"

### QA Round 2 (Passed)
All three issues fixed:
- Removed unnecessary PageBreak calls (11 pages reduced to 8 with no empty pages)
- Widened Likelihood column in Risk Register

Final QA: **PASS** -- zero issues across all checklist categories (layout, typography, colors, content, tables, logo, spelling).

---

## Output

**PDF saved to:** `~/.claude/skills/hnh-wbs-workspace/iteration-1/restaurant-app-scope/with_skill/outputs/wbs-vietnamese-restaurant-app-2026-03-10.pdf`

**PDF specs:** 8 pages, A4, ZenLabs branded, ~66KB
