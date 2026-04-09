# Default Source Registry Template

When creating a new profile's `sources.md`, start with this template and customize based on what the discovery agent finds.

## Social & Content
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| X/Twitter | `from:{handle}` | High | Primary public channel for most tech/VC figures |
| LinkedIn | `site:linkedin.com/in/{slug}` | Medium | Job changes, announcements |
| Substack/Newsletter | `{name} substack OR newsletter` | Medium | Long-form thesis |
| Personal blog | {discovered URL} | Medium | |
| YouTube | `"{name}" site:youtube.com` | Low | Talks, interviews |
| GitHub | `site:github.com/{handle}` | Low | Only if tech-relevant |

## Investment & Deal Data
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| Crunchbase | `site:crunchbase.com "{name}"` | High | Deal history, rounds |
| PitchBook | `site:pitchbook.com "{name}"` | High | Fund data, valuations |
| SEC/EDGAR | `site:sec.gov "{fund name}"` | Medium | Form D, 13F, fund registrations |
| AngelList/Wellfound | `site:wellfound.com "{name}"` | Low | Angel deals, early stage |

## News & Media
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| TechCrunch | `site:techcrunch.com "{name}"` | High | Deal announcements, fundraises |
| The Information | `site:theinformation.com "{name}"` | High | Scoops, exclusive reporting |
| Bloomberg | `site:bloomberg.com "{name}"` | Medium | Market context, macro |
| Forbes | `site:forbes.com "{name}"` | Medium | Lists, profiles, deal coverage |
| WSJ | `site:wsj.com "{name}"` | Medium | Business/policy angle |
| Reuters | `site:reuters.com "{name}"` | Low | Wire service, M&A |

## Podcasts & Interviews
| Source | URL/Query | Priority | Notes |
|--------|----------|----------|-------|
| General search | `"{name}" podcast {year}` | High | Cast wide net |
| Apple Podcasts | `site:podcasts.apple.com "{name}"` | Medium | Appearance tracker |
| Podchaser | `site:podchaser.com "{name}"` | Medium | Comprehensive history |

## Custom Sources
{User-added sources go here}
