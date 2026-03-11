---
name: hnh-record-screen
description: >
  Record screen demos and optimize video output. Use this skill whenever the user wants to
  record their screen, create a product demo video, capture a walkthrough, make a screencast,
  produce a screen recording, or show how something works visually. Trigger on 'record',
  'screen capture', 'demo video', 'screencast', 'screen recording', 'walkthrough video',
  'record a demo', or any request to visually demonstrate on-screen activity — even if the
  user doesn't say "record screen" explicitly. Also trigger when the user has a large video
  file (MOV, MP4) they want compressed or optimized. Handles browser-based recordings
  (Playwright automates and records simultaneously at 30fps) and desktop recordings, then
  compresses output to keep files small.
---

# Screen Recording

Record polished product demos and screen captures, output optimized MP4.

Uses **Playwright** to launch a browser, automate actions, and record smooth 30fps video —
all completely hands-off. No user interaction needed, no permissions dialogs.

## Prerequisites

- **ffmpeg** installed (`brew install ffmpeg`)
- **Playwright** Python: `pip3 install playwright && python3 -m playwright install chromium`

## Workflow

### Phase 1: Recording Plan

Ask the user what they want to demo, then produce a structured JSON plan:

```json
{
  "title": "Feature X Demo",
  "url": "https://app.example.com",
  "initial_wait": 3,
  "viewport": {"width": 1920, "height": 1080},
  "steps": [
    {"action": "navigate", "url": "https://app.example.com/dashboard", "description": "Open dashboard", "wait": 2},
    {"action": "click", "selector": "#new-project-btn", "description": "Create new project", "wait": 2},
    {"action": "type", "selector": "#project-name", "text": "Demo Project", "description": "Enter name", "type_delay": 80, "wait": 1.5},
    {"action": "scroll", "direction": "down", "amount": 3, "description": "Show full form", "wait": 1.5},
    {"action": "hover", "selector": ".feature-card", "description": "Hover feature card", "wait": 1},
    {"action": "press", "key": "Enter", "description": "Submit form", "wait": 2}
  ]
}
```

**Plan fields:**
- `url`: Starting URL (loaded before steps begin)
- `initial_wait`: Seconds to wait after loading start URL (default: 2)
- `viewport`: Recording resolution (default: 1920x1080)

**Step fields:**
- `action`: navigate, click, type, press, scroll, hover, wait, screenshot
- `selector`: CSS selector to target (for click, type, hover)
- `text`: Text content to match (alternative to selector for click/hover), or text to type
- `description`: Human-readable label for the plan review
- `wait`: Seconds to pause after this action (1.5–3s recommended for demos)
- `type_delay`: Ms between keystrokes when typing (default: 80, makes typing look natural)
- `key`: Key to press (for press action — e.g., "Enter", "Tab", "Escape")
- `direction`: "up" or "down" (for scroll)
- `amount`: Scroll wheel ticks (for scroll, default: 3)

Present the plan to the user for approval before recording.

**Important note about Google/search engines:** Google aggressively blocks headless browsers
with CAPTCHAs. For demos involving search, either navigate directly to the target URL or
use the Chrome MCP gif_creator fallback (see below).

### Phase 2: Record

Save the plan to a temp JSON file, then run the recording script:

```bash
# Save plan
cat > /tmp/recording_plan.json << 'PLAN'
<the JSON plan>
PLAN

# Record (headless — no browser window shown)
python3 <skill-path>/scripts/record_browser.py /tmp/recording_plan.json \
  --output /tmp/raw_recording.webm

# Or record with browser visible (for debugging)
python3 <skill-path>/scripts/record_browser.py /tmp/recording_plan.json \
  --output /tmp/raw_recording.webm --headed
```

The script:
1. Launches Chromium with video recording enabled
2. Navigates to the starting URL
3. Executes each action with natural timing
4. Saves a WebM video + `moments.json` with timestamps of every action
5. Completely automated — zero user interaction needed

**Output files:**
- `/tmp/raw_recording.webm` — The raw video (smooth 30fps, full-color)
- `/tmp/raw_recording.moments.json` — Timestamped action log (useful for trimming)

### Phase 3: Optimize

Convert and compress the raw recording:

```bash
python3 <skill-path>/scripts/optimize_video.py /tmp/raw_recording.webm \
  --output ~/ws/docs/<descriptive-name>.mp4 \
  --crf 23 --preset medium
```

**Options:**
- `--crf 23` — Quality: 18=high, 23=balanced, 28=small file
- `--max-width 1920` — Scale down, keeping aspect ratio
- `--resolution 1920x1080` — Force exact resolution (adds letterboxing)
- `--trim-start 1.5` — Remove N seconds from start
- `--trim-end 0.5` — Remove N seconds from end
- `--fps 30` — Override framerate
- `--preset medium` — Encoding speed: ultrafast, fast, medium, slow

### Phase 4: Deliver

Report to the user:
- Final file path and size
- Duration and resolution
- Size reduction percentage

Save the optimized MP4 to `~/ws/docs/` per workspace rules.

## Fallback: Chrome MCP gif_creator

For cases where you need to record an already-open browser session (e.g., a logged-in app,
or a page that requires the user's cookies/auth), use the Chrome MCP gif_creator as a
fallback. This captures frame-by-frame screenshots (not smooth video) but works with the
user's live browser.

1. `gif_creator: action="start_recording"` → take screenshots → automate actions → `stop_recording`
2. `gif_creator: action="export", download=true, filename="recording.gif"`
3. Convert: `python3 <skill-path>/scripts/optimize_video.py ~/Downloads/recording.gif -o output.mp4`

Trade-off: GIF mode is limited to 256 colors and captures only at action points (slideshow
feel), but it works with authenticated sessions without needing to handle login flows.

## Desktop Recording Mode

For desktop apps (not browser), use ffmpeg screen recording. Requires Terminal to have
screen recording permission (System Settings → Privacy & Security → Screen Recording).

```bash
# List devices to find screen index
ffmpeg -f avfoundation -list_devices true -i "" 2>&1

# Record (replace "2" with your screen capture index)
ffmpeg -f avfoundation -capture_cursor 1 -framerate 30 \
  -i "2:none" -c:v libx264 -preset ultrafast -crf 18 \
  -pix_fmt yuv420p -y /tmp/raw_recording.mov &
FFMPEG_PID=$!

# ... user performs actions ...

# Stop
kill -INT $FFMPEG_PID && wait $FFMPEG_PID 2>/dev/null

# Optimize
python3 <skill-path>/scripts/optimize_video.py /tmp/raw_recording.mov \
  --output ~/ws/docs/<name>.mp4 --crf 23
```

## Quick Reference

| Task | Command |
|------|---------|
| Record browser demo | `python3 scripts/record_browser.py plan.json -o recording.webm` |
| Optimize any video | `python3 scripts/optimize_video.py input.mov -o output.mp4` |
| Aggressive compression | Add `--crf 28` |
| Scale down | Add `--max-width 1280` |
| GIF to MP4 | Same optimize script — auto-detects format |
| Trim video | `--trim-start 2 --trim-end 1` |

## Tips

- Use 2–3 second waits between actions so viewers can follow along
- Keep demos under 60 seconds for maximum impact
- For pages with loading animations, increase wait times
- Use CSS selectors when possible (`selector` field) — they're more reliable than text matching
- For authenticated pages, either handle login in the plan steps or use the Chrome MCP fallback
- If a step fails, the recording continues (error is logged in moments.json)
- Run with `--headed` to debug plan issues visually
