---
name: hnh-profile-watch
description: "Deep-research a person's online presence and produce a signal-driven intelligence brief through a VC lens — deal flow, funding rounds, M&A, portfolio signals, market thesis, competitive intelligence. Maintains an extensible source registry per profile. Use this skill whenever the user mentions watching someone's profile, tracking a person online, researching someone's social presence, wants to know what someone has been up to, asks 'what is [person] doing lately', or provides a person's name with context suggesting they want a profile deep-dive. Also triggers for 'profile watch', 'track [person]', 'research [person]', 'what has [person] been saying', or 'add source to [person]'."
---

# Profile Watch

Research a person's public online presence and produce a **signal-driven intelligence brief** through a venture capital lens.

## Signal, not report

This skill exists to surface **signals** — not write a news summary. Every piece of information should be filtered through: **"So what? What does this mean for where money is moving?"**

A signal is a data point that implies a future action, thesis shift, or market move. Examples:
- A VC posts 3 times about "AI agents for healthcare" in one week → **signal**: they're likely looking at or about to lead a deal in that space
- A portfolio company quietly hires a CFO and VP of IR → **signal**: IPO prep
- An investor starts engaging with a founder's posts who they've never interacted with before → **signal**: possible deal in progress
- Fund announces new hire from a specific sector → **signal**: expanding thesis into that area
- Sudden silence on a topic they used to champion → **signal**: thesis may have shifted or a deal went sour

The brief should be organized around signal strength, not just chronological activity. Rate each signal:
- **🔴 Strong signal** — direct evidence of deals, exits, fund moves, or thesis shifts
- **🟡 Moderate signal** — public statements, sector interest, hiring patterns that suggest direction
- **🟢 Weak signal / noise** — interesting but no clear implication yet (still worth noting for pattern tracking across briefs)

## Extensible source registry

Each profile maintains a `sources.md` file that lists all known sources to check for that person. This file grows over time — when the user asks to add a source, or when you discover a new one during research, add it to the registry.

### Source registry format (`~/profile/{slug}/sources.md`):

```markdown
# {Name} — Source Registry
**Last updated:** {date}

## How to use
This file lists all sources to check when gathering activity for this person.
Add new sources with: "add source {url/description} to {person}"
Sources are checked during every profile watch run.

## Social & Content
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| X/Twitter | https://x.com/{handle} | High | Primary public channel |
| LinkedIn | https://linkedin.com/in/{slug} | Medium | Low activity but job changes matter |
| Substack | https://pmarca.substack.com | Medium | Long-form thesis posts |

## Investment & Deal Data
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| Crunchbase | site:crunchbase.com "{person}" | High | Deal history |
| PitchBook | site:pitchbook.com "{person}" | High | Fund data |
| SEC/EDGAR | site:sec.gov "{fund name}" | Medium | Filings, Form D, 13F |

## News & Media
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| TechCrunch | site:techcrunch.com "{person}" | High | Deal announcements |
| The Information | site:theinformation.com "{person}" | High | Scoops |
| Bloomberg | site:bloomberg.com "{person}" | Medium | Market context |

## Podcasts & Interviews
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| a16z Show | ... | High | Home podcast |
| Latent Space | ... | Medium | AI deep dives |

## Custom Sources
{User-added sources go here. Each entry added via "add source X to {person}"}
```

### Adding sources

When the user says something like "add {source} to {person}'s profile" or "also check {source} for {person}", update their `sources.md` accordingly. If the person doesn't have a profile yet, create it.

When the user says "add {source type} to all profiles" or "update the skill to also check {source}", update the **default source template** in this skill so all future profiles include it. To do this, update the `references/default-sources.md` file.

### During gathering

At the start of Step 3, read `sources.md` and use it as your checklist. Search every source marked High priority, and Medium priority if time allows. This means the gathering step automatically expands as the user adds more sources over time.

## Input format

The user provides:
- **Name** and optionally an **affiliation** (e.g., "Marc Andreessen from a16z")
- **Time range** (optional, default 7 days) — e.g., "last 2 weeks", "past month"
- **Focus areas** (optional) — e.g., "AI investments", "crypto portfolio"

**Source management commands:**
- "add source {url/description} to {person}" — adds to that person's sources.md
- "add source {url/description} to default" — adds to default template for all future profiles
- "show sources for {person}" — displays their source registry

## Workflow

### Step 1: Check for existing profile

Check if `~/profile/{slug}/` exists (slug = lowercased, hyphenated name, e.g., `marc-andreessen`).

- **If exists**: Read `profiles.md` and `sources.md` to get known links and source checklist. Skip to Step 3.
- **If not exists**: Proceed to Step 2.

### Step 2: Deep discovery

Launch a search agent to find the person's public presence. Read `agents/discover.md` for the full agent instructions and launch it as a subagent.

The discovery agent will search broadly and return a structured list of profiles. Save results to:
- `~/profile/{slug}/profiles.md` — verified profile links
- `~/profile/{slug}/sources.md` — initialized from `references/default-sources.md`, populated with discovered sources

### Step 3: Gather recent activity

Read `sources.md` as your gathering checklist. For each source, search for recent activity within the time range.

**Social & Content** — search each platform listed in sources.md:
- X/Twitter: `from:{handle}` posts, replies, threads, and mentions
- LinkedIn: `site:linkedin.com "{person name}"` posts and articles
- YouTube/Podcasts: recent interviews, appearances, talks
- Blog/Substack/Newsletter: recent articles

**Investment & Deal Signals** — this is the highest-value category:
- Funding rounds: `"{person}" OR "{fund}" funding round series {year}`
- M&A activity: `"{person}" OR "{fund}" acquisition merger {year}`
- SEC filings: `"{fund name}" SEC filing Form D 13F {year}`
- Portfolio company news: `"{fund}" portfolio company {year}` — layoffs, pivots, products, follow-on rounds
- LP/fundraising: `"{fund}" fundraise LP {year}`
- Crunchbase/PitchBook: `site:crunchbase.com "{person}"`, `site:pitchbook.com "{person}"`
- Board moves: `"{person}" board director appointed {year}`

**News & Market Context** — from sources listed in sources.md:
- Tech press (TechCrunch, The Information, Bloomberg, etc.)
- Conference appearances, panels, fireside chats
- Regulatory/policy positions, government advisory roles

Use WebSearch and WebFetch aggressively. For each High-priority source, do 2-3 query variations. The investment signals are the highest-value output.

### Step 4: Produce the brief

Write a structured brief to `~/profile/{slug}/brief-{date}.md`. The brief is **signal-first** — lead with what matters, not a chronological dump.

```markdown
# {Name} — Signal Brief
**Period:** {start_date} to {end_date}
**Generated:** {today}
**Sources checked:** {count from sources.md}

## Top Signals

{The 3-5 most important signals from this period, each rated by strength.
Each signal should answer: "What does this mean for where money is moving?"
Format:}

### 🔴 {Signal headline}
**Source:** {where you found it}
**What happened:** {factual description}
**Why it matters:** {the "so what" — what this implies about future moves, thesis, deals}

### 🟡 {Signal headline}
...

## Current Status
- **Role:** {title} at {company/fund}
- **Fund:** {current fund name, size, vintage, focus}
- **Key affiliations:** {boards, advisory roles, government positions}
- **AUM:** {assets under management if known}

## Deal Flow & Investment Activity

| Date | Type | Company | Stage | Amount | Co-investors | Signal |
|------|------|---------|-------|--------|-------------|--------|
| ... | Lead | ... | Series B | $XM | Sequoia, ... | Doubling down on AI infra |

{For each deal, note what it signals about their thesis direction.
Include not just confirmed deals but also deal signals — e.g., sudden interest in a space, meetings with founders, etc.}

## Fund & Fundraising Activity
{Fund status (deploying/fully invested/raising), LP activity, performance signals.
What stage of the fund cycle are they in? This context changes how you interpret everything else.}

## Portfolio Signals

### Strong Positive 🟢
{Portfolio companies with good signals: new rounds, product launches, revenue milestones}

### Watch 🟡
{Portfolio companies with ambiguous signals: pivots, leadership changes, slowing growth}

### Concerning 🔴
{Portfolio companies with negative signals: layoffs, down rounds, shutdowns}

## Market Thesis & Sector Bets
{Based on all sources — what sectors are they betting on vs. pulling back from?
- **Increasing conviction:** {sectors getting more attention/capital}
- **Decreasing conviction:** {sectors getting less mention, quiet exits}
- **New interest:** {sectors they're exploring for the first time}
- **Thesis evolution:** how has their stated thesis shifted from 3-6 months ago?}

## Opinions & Public Positions
{Public stances with deal-flow relevance:
- Policy positions that affect their portfolio (regulation, tax, trade)
- Industry takes that reveal investment thesis
- Predictions that signal where they'll deploy capital}

## Notable Activity

| Date | Platform | Activity | Signal Strength | Implication |
|------|----------|----------|----------------|-------------|
| ... | X | 3 posts about healthcare AI | 🟡 Moderate | Exploring new vertical |

## Podcast / Interview Highlights
{Only investment-relevant statements from recent appearances.
Skip motivational content — focus on: deal logic, sector thesis, fund strategy, market predictions.}

## Competitive Landscape
{Who are they co-investing with? Competing against for deals?
Whose thesis overlaps or diverges? Any public disagreements?
How are they positioned vs. peers in their category?}

## Signals & Patterns
{Your analysis as a VC analyst — this is the most valuable section:

**Pattern recognition:**
- What recurring themes are emerging across their activity?
- Any acceleration or deceleration in specific areas?

**Forward-looking implications:**
- Based on these signals, what deals might they announce next?
- What sectors should we expect them to enter or exit?
- What does their activity suggest about the broader market?

**Actionable takeaways:**
1. {Specific thing the reader should do or watch for}
2. {Specific thing the reader should do or watch for}
3. {Specific thing the reader should do or watch for}
}
```

### Step 5: Update status tracker

Write/update `~/profile/{slug}/status.md`:

```markdown
# {Name} — Status Tracker
**Last updated:** {today}

## Identity
- **Full name:** {name}
- **Title:** {current title}
- **Company/Fund:** {current fund/company}
- **Location:** {if known}

## Fund Status
- **Current fund:** {name, size, year}
- **AUM:** {total assets under management}
- **Focus sectors:** {where they're deploying capital}
- **Fund stage:** {raising / deploying / fully invested}

## Board Seats & Advisory
{List of current board seats — these signal conviction and influence}

## Current Thesis
{Their current investment thesis in 2-3 sentences, based on latest signals}

## Key Profiles
{Links from profiles.md, summarized}

## Recent Briefs
- [{date}](brief-{date}.md) — {one-line summary of top signals}
```

### Step 6: Present to user

Show the user:
1. **Top 3 signals** from the brief — lead with the most actionable findings
2. Where the files are saved
3. If this is a repeat run, highlight what changed — especially new deals, thesis shifts, or signal strength changes

## Tips for effective signal extraction

- **Investment databases are goldmines.** Always search Crunchbase, PitchBook references, and SEC/EDGAR for deal data. These give hard numbers that social posts don't.
- **Read between the lines.** A VC posting about "the future of X" three times in a week is likely looking at deals in X right now.
- **Follow the portfolio.** Searching for the fund/firm + "portfolio" often reveals more than searching the person directly.
- **Podcast deep dives reveal thesis.** Investors reveal deal logic in long-form conversations that they'd never put in writing. When you find a podcast appearance, search for transcripts or detailed summaries.
- **Co-investor patterns matter.** When you find a deal, note who else invested — this maps alliances and competition.
- **Silence is a signal too.** If someone used to talk about crypto constantly and suddenly stops, that's worth noting.
- **Prioritize recency.** Add the current year/month to queries to bias toward recent content.
- **Track signal across briefs.** When writing Signals & Patterns, reference previous briefs if they exist to show trend evolution.

## File structure

```
~/profile/{slug}/
├── profiles.md          # Discovered social links + investment profiles (persistent)
├── sources.md           # Extensible source registry (grows over time)
├── status.md            # Current role/fund/portfolio focus (updated each run)
├── brief-2026-04-09.md  # Signal brief (one per run, dated)
└── brief-2026-03-25.md  # Previous briefs preserved for trend tracking
```
