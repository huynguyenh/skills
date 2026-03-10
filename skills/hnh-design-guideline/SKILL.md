---
name: hnh-design-guideline
description: "ZenLabs brand design system — colors, typography, spacing, and logo usage rules for all generated visual outputs (PDFs, presentations, documents, HTML, spreadsheets). Use this skill whenever generating any visual output for ZenLabs: PDFs (reportlab), PPTX (python-pptx), DOCX, HTML pages, styled spreadsheets, or any document where layout, colors, or fonts matter. Also trigger when the user mentions 'brand', 'design guideline', 'ZenLabs style', 'our colors', 'our fonts', or asks for something to 'look professional' or 'match our branding'. This skill should be consulted BEFORE choosing colors, fonts, or layout for any ZenLabs deliverable — even if the user doesn't explicitly mention branding. If you're about to pick a color or font for a ZenLabs document, check this skill first."
---

# ZenLabs Design Guideline

This skill contains the complete ZenLabs brand system extracted from the official Brand Guidelines 2025. When generating any visual output, follow these specs exactly.

## Quick Reference — Most Used Values

When you're in a hurry, these are the values you'll reach for 90% of the time:

| Element | Value |
|---|---|
| **Primary font** | Rubik (headings, titles) |
| **Secondary font** | Inter (body text, tables, captions) |
| **Dark text color** | `#09242E` (Firefly 600 / Primary Black) |
| **Primary green** | `#04563E` (Emerald 900) |
| **Accent green** | `#43CE81` (Emerald 500) |
| **Light green bg** | `#98D5AB` (Emerald 300) |
| **Soft green bg** | `#C8E6B7` (Emerald 100) |
| **Light blue bg** | `#C0E0EF` (Firefly 200) |
| **Page background** | `#FFFFFF` (white) |
| **Subtle bg / alternating rows** | `#F6F6E8` (Ecru 100) |
| **Border / divider** | `#C0E0EF` (Firefly 200) |
| **White text** (on dark bg) | `#FFFFFF` |

## Typography

### Fonts
- **Primary typeface: Rubik** — Use for headings, titles, document names, hero text. Weights: Regular (400), SemiBold (600), Bold (700).
- **Secondary typeface: Inter** — Use for body copy, paragraphs, table cells, captions, footnotes. Weights: Regular (400), SemiBold (600), Bold (700).

### Font Availability in Code
Both Rubik and Inter are Google Fonts (free, open-source).

**For ReportLab PDFs:** ReportLab doesn't include Rubik/Inter by default. Use these fallbacks:
- Rubik → `Helvetica-Bold` (for headings)
- Inter → `Helvetica` (for body)

If custom fonts are registered via `reportlab.pdfbase`, use the real fonts. Otherwise, Helvetica is the closest system match.

**For HTML/CSS:** Use Google Fonts import:
```css
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600;700&family=Inter:wght@400;600;700&display=swap');
```

**For python-pptx / python-docx:** Set font name to "Rubik" or "Inter" — they render if installed on the system.

### Type Scale (suggested)
| Element | Font | Weight | Size |
|---|---|---|---|
| Document title | Rubik | Bold | 24-28pt |
| Section heading (H1) | Rubik | Bold | 14-16pt |
| Subsection (H2) | Rubik | SemiBold | 11-12pt |
| Body text | Inter | Regular | 9-10pt |
| Table cell | Inter | Regular | 8-9pt |
| Table header | Inter | Bold | 8-9pt |
| Caption / footer | Inter | Regular | 7-8pt |

## Color Palette

### Primary Colors
| Name | Hex | Usage |
|---|---|---|
| **Primary Black** | `#09242E` | Main text, headings, dark UI elements |
| **Emerald 900** | `#04563E` | Primary brand green, dark green backgrounds, header bars |
| **Emerald 500** | `#43CE81` | Accent green, highlights, CTAs, success states |

### Background & Surface Colors
| Name | Hex | Usage |
|---|---|---|
| White | `#FFFFFF` | Page background, cards |
| **Ecru 100** | `#F6F6E8` | Subtle warm background, alternating table rows |
| **Emerald 100** | `#C8E6B7` | Light green tint, LOW RISK / success background |
| **Emerald 300** | `#98D5AB` | Medium green, secondary backgrounds |
| **Firefly 200** | `#C0E0EF` | Light blue, borders, dividers, info backgrounds |

### Status / Semantic Colors
| Status | Background | Text |
|---|---|---|
| Low risk / Success | `#C8E6B7` (Emerald 100) | `#04563E` (Emerald 900) |
| Medium / Warning | `#F6F6E8` (Ecru 100) | `#636230` (Ecru 700) |
| High risk / Error | `#D8EDF5` (Firefly 100) with `#09242E` text, or use Ecru 300 `#E3E2BC` | `#09242E` |

> **Important:** ZenLabs does NOT use red as a brand color. For "high risk" or "error" states, use the dark Firefly palette or warm Ecru tones instead. Avoid `#FF0000`, `#c62828`, or any bright red.

### Full Emerald Scale (Green)
| Step | Hex |
|---|---|
| 100 | `#C8E6B7` |
| 200 | `#A9DEA7` |
| 300 | `#98D5AB` |
| 400 | `#70D094` |
| 500 | `#43CE81` |
| 600 | `#26BE73` |
| 700 | `#179F65` |
| 800 | `#0B7C54` |

### Full Sky Scale (Blue)
| Step | Hex |
|---|---|
| 100 | `#DFF2FE` |
| 200 | `#B8E6FE` |
| 300 | `#74D4FF` |
| 400 | `#00BCFF` |
| 500 | `#00A6F4` |
| 600 | `#0084D1` |
| 700 | `#0069A8` |
| 900 | `#024A70` |

### Full Firefly Scale (Dark Teal/Navy)
| Step | Hex |
|---|---|
| 100 | `#D8EDF5` |
| 200 | `#C0E0EF` |
| 300 | `#478FB4` |
| 400 | `#30637C` |
| 500 | `#1A3645` |
| 600 | `#09242E` |
| 700 | `#071A21` |
| 800 | `#041116` |

### Full Ecru Scale (Warm Neutral)
| Step | Hex |
|---|---|
| 100 | `#F6F6E8` |
| 200 | `#EEEED7` |
| 300 | `#E3E2BC` |
| 400 | `#D8D7A3` |
| 500 | `#C2C171` |
| 600 | `#9B9A4C` |
| 700 | `#636230` |
| 800 | `#464622` |

## Layout Patterns

### PDF Documents (ReportLab)
```python
from reportlab.lib.colors import HexColor

# Core palette
PRIMARY_BLACK  = HexColor("#09242E")  # Text, headings
EMERALD_900    = HexColor("#04563E")  # Dark green, header bars
EMERALD_500    = HexColor("#43CE81")  # Accent green
EMERALD_300    = HexColor("#98D5AB")  # Light green bg
EMERALD_100    = HexColor("#C8E6B7")  # Soft green bg (success/low-risk)
FIREFLY_200    = HexColor("#C0E0EF")  # Borders, light blue bg
FIREFLY_100    = HexColor("#D8EDF5")  # Info bg
ECRU_100       = HexColor("#F6F6E8")  # Alternating rows, warm subtle bg
ECRU_300       = HexColor("#E3E2BC")  # Warning bg
ECRU_700       = HexColor("#636230")  # Warning text
WHITE          = HexColor("#FFFFFF")
```

### Table Styling Pattern
```python
# Table header: Emerald 900 bg + white text
("BACKGROUND", (0, 0), (-1, 0), EMERALD_900),
("TEXTCOLOR", (0, 0), (-1, 0), WHITE),

# Row borders
("GRID", (0, 0), (-1, -1), 0.5, FIREFLY_200),

# Alternating row colors (optional)
# Even rows: white, Odd rows: Ecru 100
```

### Document Structure
- **Page size:** A4 (210 x 297 mm)
- **Margins:** 18-20mm all sides
- **Header:** Rubik Bold, 24pt, Primary Black
- **Section headings:** Rubik Bold, 13-14pt, Emerald 900
- **Body:** Inter Regular, 9pt, Primary Black
- **Footer:** Inter Regular, 7pt, Firefly 300

## Logo

### Assets
Logo files are bundled in this skill's `assets/logos/` directory:

| File | Description | Use on |
|---|---|---|
| `logo-dark-on-light.png` | Full logo (green mark + dark text) | White/light backgrounds |
| `logo-light-on-dark.png` | Full logo (light mark + light text) | Dark green/dark backgrounds |
| `logomark-dark.png` | Z mark only (green, medium shade) | Light backgrounds, icons |
| `logomark-light.png` | Z mark only (light green) | Dark backgrounds |

### Logo Placement Rules
- Clear space around logo = 1/3 the cap height of the "Z"
- Never distort, stretch, recolor, or add effects to the logo
- Approved background colors for logo: white, Emerald 100, Emerald 300, Firefly 200 (light), or Emerald 900 (dark)

### Embedding Logo in ReportLab
```python
from reportlab.platypus import Image
import os

SKILL_DIR = os.path.dirname(__file__)  # or hardcode path
LOGO_PATH = os.path.expanduser("~/.claude/skills/hnh-design-guideline/assets/logos/logo-dark-on-light.png")

# Add to document (typical width: 40-60mm)
logo = Image(LOGO_PATH, width=50*mm, height=12*mm)
```

## Brand Voice (for document tone)
- Professional but approachable
- Tech-forward, clean, minimal
- Avoid jargon when possible
- Use active voice
