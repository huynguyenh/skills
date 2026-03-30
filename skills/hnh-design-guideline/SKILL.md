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

### 3-Level Severity / Difficulty Colors
Use these three colors whenever you need a 3-tier scale (high/medium/low, hard/medium/easy, critical/warning/ok, etc.):

| Level | Hex | Usage |
|---|---|---|
| **Low / Easy / OK** | `#179F65` (green) | Low risk, easy items, success, good status |
| **Medium / Moderate** | `#EB7E11` (orange) | Medium risk, moderate difficulty, warning |
| **High / Hard / Critical** | `#F03333` (red) | High risk, hard items, critical, error |

These override the brand palette specifically for severity/difficulty indicators. Use them as background fills with white text, or as text color on light backgrounds, or as badge/pill colors — whichever fits the context.

```python
# ReportLab severity colors
SEVERITY_LOW    = HexColor("#179F65")  # Green — low/easy/ok
SEVERITY_MEDIUM = HexColor("#EB7E11")  # Orange — medium/moderate
SEVERITY_HIGH   = HexColor("#F03333")  # Red — high/hard/critical
```

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

## Cover Page (PDF)

Every PDF document starts with a branded cover page. The cover page must use the actual project/document content — never placeholder text.

### Cover Page Layout

The cover page has these elements, top to bottom:

1. **Logo** (top of page, no header bar): Use `logo-dark-on-light.png` (dark logo on white/gradient background). Position at 20mm from top edge, 20mm from left, width ~44mm. There is NO dark green header bar.
2. **Green gradient background**: Smooth radial fade concentrated on the RIGHT side of the page. Use 150+ overlapping translucent circles with power-curve alpha (t^2.2) anchored outside the right edge, plus a secondary accent layer near the top-right corner. The LEFT ~40% of the page must stay white so text and logo remain crisp. Do NOT use concentric arc patterns — the gradient must be smooth.
3. **Title** (large, left-aligned, in the white area): Helvetica-Bold 48pt, Primary Black (`#09242E`). Baseline of first line at ~62% from bottom of page. Split long titles across two lines (e.g., "ENAT AI" on line 1, "Content Factory" on line 2, with 18mm gap between baselines).
4. **Subtitle** (below second title line, ~14mm gap): Helvetica-Bold 16pt, Emerald 900 (`#04563E`). The document type (e.g., "Work Breakdown Structure", "Technical Proposal").
5. **Metadata block** (lower-left, starting at ~23% from bottom): Helvetica-Bold 12pt for labels, Helvetica 12pt for values, Primary Black. Each line has a bold label followed by the value, 7mm line spacing:
   - **Client:** [actual client name]
   - **Prepared by:** ZenLabs
   - **Date:** [actual date, formatted as "Month DD, YYYY"]
   - **Version:** [version number]
   - Any other relevant metadata fields
6. **Footer** (bottom of page): Light gray divider line (`#DDDDDD`, 0.5pt) at 18mm from bottom. Below it: document title + " - [type] | ZenLabs" on the left, "Page 1" on the right, Helvetica 7pt, Emerald 700 (`#179F65`).

### Key Rule: Use Real Content

The cover page fields must be populated from the actual document context — the project name, client name, date, etc. Never leave generic placeholders like "Project Title" or "Client Name". If the user hasn't specified a value, ask for it rather than guessing.

### ReportLab Cover Page Pattern
```python
from reportlab.lib.colors import HexColor, Color

LOGO_DARK_PATH = os.path.expanduser("~/.claude/skills/hnh-design-guideline/assets/logos/logo-dark-on-light.png")

def draw_cover_page(c, doc):
    """Draw as onFirstPage callback. Title/subtitle/metadata are hardcoded per document."""
    w, h = A4  # 595.27 x 841.89 points

    # White background
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Green gradient — smooth radial fade from RIGHT side
    # Concentrated on right edge, fading to white on the left ~40%
    import math
    cx, cy = w + 80*mm, h * 0.55  # center outside right edge
    max_r = 320*mm
    steps = 150
    for i in range(steps):
        t = i / float(steps)
        radius = max_r * (1 - t)
        if radius < 3*mm: break
        intensity = t ** 2.2
        alpha = intensity * 0.22
        if alpha < 0.001: continue
        c.setFillColor(Color(0.467, 0.843, 0.616, alpha))
        c.circle(cx, cy, radius, fill=1, stroke=0)

    # Upper-right accent — slightly more vivid near top-right corner
    cx2, cy2 = w + 30*mm, h + 20*mm
    for i in range(100):
        t = i / 100.0
        radius = 220*mm * (1 - t)
        if radius < 3*mm: break
        intensity = t ** 2.5
        alpha = intensity * 0.14
        if alpha < 0.001: continue
        c.setFillColor(Color(0.263, 0.808, 0.506, alpha))
        c.circle(cx2, cy2, radius, fill=1, stroke=0)

    # Logo — dark logo on white/gradient background, with white backing
    from reportlab.lib.utils import ImageReader
    logo_reader = ImageReader(LOGO_DARK_PATH)
    iw, ih = logo_reader.getSize()
    logo_w = 44*mm
    logo_h = logo_w * ih / iw
    logo_x = 20*mm
    logo_y = h - 18*mm - logo_h  # 18mm from top edge
    # White backing to prevent gradient bleed-through
    padding = 2*mm
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(logo_x - padding, logo_y - padding, logo_w + 2*padding, logo_h + 2*padding, fill=1, stroke=0)
    c.drawImage(logo_reader, logo_x, logo_y, width=logo_w, height=logo_h, mask='auto')

    # Title — two lines, baseline at ~62% from bottom, 18mm gap
    c.setFillColor(HexColor("#09242E"))
    c.setFont("Helvetica-Bold", 48)
    line1_y = h * 0.62
    c.drawString(22*mm, line1_y, "ENAT AI")                 # Line 1
    c.drawString(22*mm, line1_y - 18*mm, "Content Factory")  # Line 2

    # Subtitle — below line 2, 14mm gap
    c.setFillColor(HexColor("#04563E"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(22*mm, line1_y - 18*mm - 14*mm, "Work Breakdown Structure")

    # Metadata — starting at 23% from bottom
    y = h * 0.23
    for label, value in metadata.items():
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(HexColor("#09242E"))
        c.drawString(22*mm, y, f"{label}:")
        lw = c.stringWidth(f"{label}:", "Helvetica-Bold", 12)
        c.setFont("Helvetica", 12)
        c.drawString(22*mm + lw + 2*mm, y, value)
        y -= 7*mm

    # Footer with divider
    c.setStrokeColor(HexColor("#DDDDDD"))
    c.setLineWidth(0.5)
    c.line(20*mm, 18*mm, w - 20*mm, 18*mm)
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#179F65"))
    c.drawString(22*mm, 12*mm, "ENAT AI Content Factory - WBS | ZenLabs")
    c.drawRightString(w - 22*mm, 12*mm, "Page 1")
```

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

# Row borders — use neutral gray, NOT Firefly 200 (blue clashes with warm Ecru rows)
("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E0E0E0")),

# Alternating row colors (optional)
# Even rows: white, Odd rows: Ecru 100
```

### Risk Badge Style (Modern Pill)
For risk/severity columns in tables, use rounded pill badges — NOT full-cell background fills. Use the severity colors as pill background with white text:
- **Low**: `#179F65` (green pill)
- **Medium**: `#EB7E11` (orange pill)
- **High**: `#F03333` (red pill)

Pills must be **adaptive width** (`cell_width - 2mm`, giving 1mm margin each side), fully rounded ends (`pill_r = pill_h / 2`), centered in the cell, with Helvetica-Bold 6.5pt white text. This ensures pills fit any column width.

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

## Excalidraw Diagrams

When generating architecture diagrams, system diagrams, or flowcharts in Excalidraw (via `/hnh-excalidraw`), use this style:

### Style: Monochrome + Green Accent

ZenLabs diagrams use a clean, hand-drawn aesthetic — monochrome with a single green accent. No rainbow colors, no filled boxes.

### Colors

| Element | Hex | Notes |
|---|---|---|
| Canvas / box fill | `#FFFFFF` | White — all service boxes are unfilled |
| Service box stroke | `#000000` | Black, solid, ~2-3px |
| Zone container stroke | `#1e7a5e` | Dark teal/green, dashed, ~2px |
| Zone label text | `#1e7a5e` | Same dark green |
| Namespace stroke | `#43CE81` | Emerald 500, dashed, ~2px |
| Namespace label text | `#43CE81` | Same lighter green |
| Arrows | `#000000` | Black, solid, ~2px |
| Severity OK | `#179F65` | Green |
| Severity Warning | `#EB7E11` | Orange |
| Severity Critical | `#F03333` | Red |

### Stroke Rules

| Element | Stroke Style |
|---|---|
| Zone containers (VPC, DNS, Data Layer) | **Dashed**, rounded corners |
| Namespace groups (inside EKS) | **Dashed**, rounded corners, lighter green |
| Service/component boxes | **Solid**, rounded corners |
| Placeholder/future boxes | **Dashed**, black |
| Arrows | **Solid** |

### Typography

Use Excalidraw's default hand-drawn font (Virgil) throughout — never switch to a formal font.

| Element | Size |
|---|---|
| Title | ~28px |
| Zone labels | ~20px |
| Namespace labels | ~18px |
| Service box text | ~16-18px |
| Secondary labels | ~14px |

### Layout

- **Top-down flow** (Users → DNS → LB → Compute → Data)
- **Center-aligned** main flow, sidebars on left (Monitoring, Gitops)
- **Nesting**: up to 3 levels (VPC → EKS → Namespace → Service)
- **No fills** — visual hierarchy via stroke style (dashed = group, solid = component)
- **Spacing**: 40-60px vertical between boxes, 30-40px horizontal, 30-40px zone padding

### Key Principles

1. **Monochrome + one green accent** — never use multiple colors for different services
2. **Hand-drawn font** — matches Excalidraw's whiteboard aesthetic
3. **Dashed = grouping, solid = components** — the only visual hierarchy rule needed
4. **No background fills** — keeps diagrams clean and printable
5. **Sidebars separated** from main flow — supporting systems (monitoring, CI/CD) sit to the left

---

## CRITICAL Cover Page Rules

These rules override any older pattern or memory. Always apply them when generating PDF cover pages:

- Logo MUST be `logo-dark-on-light.png` (dark logo on white background) — NOT `logo-light-on-dark.png`
- Use variable name `LOGO_DARK_PATH` pointing to `logo-dark-on-light.png`
- NO header bar — do NOT draw a dark green rect across the top of the cover page
- Logo is placed directly on the white/gradient background at 20mm from the top edge, 20mm from left
- The cover page background is white with a right-side radial green gradient — no solid colored bar anywhere
