---
name: hnh-facebook-manual
description: >
  Interact with Facebook via browser automation using the Chrome Claude Extension —
  fetch comments, reactions, shares, post content, and perform actions like liking,
  commenting, and sharing. Use this skill whenever the user mentions Facebook, shares
  a facebook.com URL, asks about a Facebook post, wants to scrape comments or reactions,
  or asks to interact with Facebook in any way. Also trigger when the user says "FB",
  "check this post", "get comments", "how many likes", or references any facebook.com
  or fb.com link — even if they don't explicitly say "Facebook".
---

# Facebook Browser Automation

Facebook doesn't offer a practical public API for most interactions, so this skill
uses the Chrome Claude Extension (MCP browser tools) to interact with Facebook
directly in the user's browser. The user is already logged in — no auth flow needed.

## Prerequisites

- The user must be logged into Facebook in Chrome
- The Chrome Claude Extension must be connected (use `tabs_context_mcp` to verify)
- Facebook UI may be in English or Vietnamese — handle both

## Core Workflow

Every Facebook task follows this pattern:

1. **Get browser context** — call `tabs_context_mcp` to get available tabs
2. **Navigate** — use `navigate` to go to the Facebook URL (or create a new tab first with `tabs_create_mcp`)
3. **Wait for load** — Facebook is a heavy SPA; after navigation, take a `screenshot` or use `read_page` to confirm content loaded
4. **Extract or interact** — use the appropriate technique below
5. **Return structured data** — always present results in a clean, organized format

## Navigation

When given a Facebook URL:
```
1. tabs_context_mcp (get tab context)
2. tabs_create_mcp (create a fresh tab — don't reuse existing tabs)
3. navigate to the URL
4. computer → screenshot (verify page loaded)
```

When asked to find something (e.g., "go to X's page"):
```
1. Navigate to facebook.com
2. find → "search bar" or use read_page to locate the search input
3. form_input or computer → type the search query
4. computer → key "Enter"
5. screenshot to verify results
```

## Extracting Post Content

To get the full text of a post:

1. Navigate to the post URL — Facebook opens posts in a dialog/modal
2. Take a `screenshot` to visually read the post content — this is the most reliable method because Facebook's SPA makes `get_page_text` return mostly navigation garbage rather than actual post content
3. If the post is truncated (shows "See more" / "Xem thêm"), use `find` to locate the expand button and `computer → left_click` on it, then screenshot again
4. For programmatic extraction, use `javascript_tool` to grab text from the dialog:
   ```javascript
   // IMPORTANT: Use querySelectorAll index 1, NOT 0!
   // Index 0 is often a Messenger popup dialog. Index 1 is the post dialog.
   const dialog = document.querySelectorAll('[role="dialog"]')[1];
   const postText = dialog?.querySelector('[data-ad-preview="message"]')?.innerText
     || dialog?.innerText?.split('\n').slice(2, 10).join('\n'); // fallback
   ```
5. Author name and timestamp are visible in the dialog header — read from screenshot or use `find` to locate them

### Dialog Index Warning

Facebook's dialog count varies. Always verify which index holds the post content:
```javascript
// Check all dialogs and their article counts:
const d = document.querySelectorAll('[role="dialog"]');
Array.from(d).map((x,i) => i+':'+x.querySelectorAll('[role="article"]').length).join(', ');
// e.g. "0:17,1:17" means both are the post dialog (nested) — use index 0
// e.g. "0:0,1:17" means Messenger is at 0 — use index 1
```
Use the dialog with the highest article count. When counts are equal, use index 0.

**Avoid `get_page_text`** for Facebook — it dumps the entire SPA including sidebar, nav, ads, and stories into a single text blob. Screenshots and targeted JS are far more reliable.

**Output format:**
```
Author: [name]
Group: [group name, if posted in a group]
Date: [timestamp]
Content: [full post text]
Media: [description of attached images/videos if any]
Reactions: [count, or "none visible"]
Comments: [count]
```

## Fetching Comments

Comments are the most common task. Facebook loads comments lazily and nests replies.

### Strategy

1. **Navigate** to the post
2. **Expand all comments** — Facebook often shows only "Most relevant" comments:
   - Look for a dropdown/filter near comments that says "Most relevant" / "Phù hợp nhất"
   - Click it and select "All comments" / "Tất cả bình luận" if available
3. **Load ALL comments via PageDown** — this is the ONLY reliable method for triggering Facebook's lazy loading. Scroll buttons and "Load more" clicks are unreliable.
   ```
   Step 1: Click inside the post dialog to give it focus
     computer → left_click on any text area inside the dialog
   Step 2: Press PageDown repeatedly until article count stabilizes
     Loop:
       - javascript_tool: document.querySelectorAll('[role="dialog"]')[0].querySelectorAll('[role="article"]').length
       - computer → key "PageDown" (3-5 times)
       - Wait 2s
       - Check article count again
       - If count stopped growing for 2 consecutive checks → done
   ```
   **Do NOT use scroll, "View more comments" buttons, or scroll_to** — they don't reliably trigger Facebook's lazy loading. PageDown (after clicking inside the dialog) is the proven method.

   **"View previous comments" button:** When navigating to a post via a comment-anchored URL (e.g., `?comment_id=...`), Facebook may open the dialog scrolled to that specific comment and show a "View previous comments" button at the top. Click it (via JS, not the computer tool) to load older comments, then keep expanding:
   ```javascript
   // Safe JS-based button clicking — avoids accidental navigation from computer tool clicks
   const clickAllExpand = () => {
     let clicked = 0;
     document.querySelectorAll('div[role="button"]').forEach(b => {
       if (b.innerText && (
         b.innerText.trim() === 'View previous comments' ||
         b.innerText.match(/View (all \d+|\d+) repl/)
       )) { b.click(); clicked++; }
     });
     return clicked;
   };
   clickAllExpand() + ' buttons clicked';
   ```
   Run this, wait 2-3s, check article count, repeat until 0 buttons clicked and count is stable.

4. **Expand replies** — **always use JS to click reply buttons**, not the `computer` or `find` tools. The `computer` tool can accidentally navigate away if a reply button contains a link. Use this JS approach:
   ```javascript
   // Safe: click all reply expansion buttons via JS
   let clicked = 0;
   document.querySelectorAll('div[role="button"]').forEach(b => {
     if (b.innerText && b.innerText.match(/View (all \d+|\d+) repl/)) {
       b.click(); clicked++;
     }
   });
   clicked + ' reply buttons clicked';
   ```
   Run in a loop (wait 2-3s between iterations) until 0 buttons are found.
5. **Expand truncated comments** — click "See more" / "Xem thêm" within individual comments
6. **Extract** — use `javascript_tool` (see extraction script below)

### Extraction approach

After all comments and replies are expanded, use `javascript_tool` to extract structured data. The proven approach uses `[role="article"]` inside the dialog — each comment (including replies) is an article element.

**IMPORTANT: The `javascript_tool` has a hard output limit of ~1400 characters.** Do NOT try to return large results directly — they will be silently truncated. Instead, use the **console.log bypass** described below.

#### Step 1: Extract and store in browser memory

Run this in `javascript_tool` to parse all comments and store them in `window._fbFull`:

```javascript
// Use the dialog with the highest article count (see Dialog Index Warning above)
const dialogIdx = (() => {
  const d = document.querySelectorAll('[role="dialog"]');
  let best = 0;
  for (let i = 1; i < d.length; i++) {
    if (d[i].querySelectorAll('[role="article"]').length > d[best].querySelectorAll('[role="article"]').length) best = i;
  }
  return best;
})();
const dialog = document.querySelectorAll('[role="dialog"]')[dialogIdx];
const articles = dialog.querySelectorAll('[role="article"]');
const actionWords = ['Like', 'Reply', 'Share', 'Thích', 'Phản hồi', 'Chia sẻ', 'Follow',
  'Theo dõi', 'Hide', 'Ẩn', 'Report', 'Báo cáo', 'Most relevant', 'Phù hợp nhất',
  'All comments', 'Tất cả bình luận', 'Author'];
const results = [];

articles.forEach((article) => {
  const text = article.innerText;
  if (!text || text.trim().length === 0) return;
  const lines = text.split('\n').filter(l => l.trim());
  if (lines.length < 2) return;

  const author = lines[0];
  if (author === 'Author') return;
  const timeMatch = text.match(/(\d+[dhm])\s/);
  const timestamp = timeMatch ? timeMatch[1] : '';

  const contentLines = lines.slice(1).filter(l => {
    const t = l.trim();
    return !actionWords.includes(t) && !t.match(/^\d+[dhm]$/) && t !== 'Follow';
  });
  const content = contentLines.join(' ').trim();

  results.push({ author, text: content || '[emoji]', timestamp }); // empty = emoji-only comment
});

window._fbFull = results;
results.length + ' comments extracted';
```

#### Step 2: Build row data with reply detection

```javascript
const c = window._fbFull;
const authors = c.map(x => x.author);
const startId = NEXT_ID; // sequential ID for this post's first comment
const postName = 'POST_NAME';
const postUrl = 'POST_URL';
const rows = [];

for (let i = 0; i < c.length; i++) {
  const myId = String(startId + i);
  let replyTo = '';
  // Reply detection: if comment text starts with another author's name
  for (let j = 0; j < i; j++) {
    if (c[i].text.startsWith(authors[j] + ' ')) {
      replyTo = String(startId + j);
      break;
    }
  }
  // Guard: never self-reference (can happen when author name matches their own text prefix)
  if (replyTo === myId) replyTo = '';
  rows.push([myId, postName, postUrl, c[i].author, c[i].text, c[i].timestamp, replyTo]);
}

window._fbFullRows = rows;
rows.length + ' rows built';
```

#### Step 3: Extract full data via console.log bypass

**This is the key technique.** The JS tool truncates output at ~1400 chars, but `console.log` has no such limit. Log the full JSON to console, then read it back with `read_console_messages`:

```javascript
// In javascript_tool:
console.log('FB_DATA:' + JSON.stringify(window._fbFullRows));
'logged ' + window._fbFullRows.length + ' rows to console';
```

Then immediately call `read_console_messages` with `pattern: "FB_DATA"`. The full JSON (can be 50-100KB+) gets saved to a local file. Parse that file with Python:

```python
import json
with open('TOOL_RESULT_FILE') as f:
    data = json.loads(f.read())
for item in data:
    if 'FB_DATA:' in item.get('text', ''):
        json_str = item['text'][item['text'].index('FB_DATA:') + 8:]
        rows = json.loads(json_str)
        # rows is now the full 2D array ready for Google Sheets
        with open('/tmp/fb_full_rows.json', 'w') as out:
            json.dump(rows, out, ensure_ascii=False)
        break
```

#### Step 4: Batch write to Google Sheets

Write rows in batches of 5 using `sheets.py` to avoid payload size issues:

```python
import json, subprocess
SHEET_ID = 'SHEET_ID'
SHEETS_PY = '/Users/hnh/.claude/skills/hnh-gg-sheets/scripts/sheets.py'

with open('/tmp/fb_full_rows.json') as f:
    rows = json.load(f)

for i in range(0, len(rows), 5):
    batch = rows[i:i+5]
    sheet_row = START_ROW + i
    values_json = json.dumps(batch, ensure_ascii=False)
    subprocess.run(['python3', SHEETS_PY, 'write', SHEET_ID,
                    '--sheet-name', 'Comments', '--range', f'A{sheet_row}',
                    '--values', values_json], check=True)
```

**Detecting replies vs top-level comments:** Facebook's DOM nesting is unreliable for distinguishing replies from top-level comments. Instead, check if the comment text starts with another commenter's name (e.g., `c[i].text.startsWith(authors[j] + ' ')`). If it does, it's a reply to that commenter.

**Comment count mismatch:** Facebook's "X comments" count includes the original poster's own replies in threads. So if a post says "19 comments" but you extract 17 `role="article"` elements, the gap is likely the OP's replies being counted differently or the post itself being counted. This is normal.

**NEVER truncate comment text with .substring()** — always extract and store the full text. Use the console.log bypass to get it out of the browser.

**Output format:**
```
## Comments on [post title/URL] (total: N)

1. **[Author Name]** — [timestamp]
   [comment text]
   👍 [reaction count] | 💬 [reply count]

   ↳ **[Reply Author]** — [timestamp]
     [reply text]
     👍 [reaction count]

2. ...
```

## Getting Reactions / Likes

Reaction counts are usually visible on the post itself.

1. Navigate to the post
2. Use `read_page` or `find` to locate the reaction bar (the row with 👍😂❤️ icons and a count)
3. For a **breakdown by reaction type**, click on the reaction count — this opens a modal/popup showing the breakdown
4. Use `read_page` on the modal to extract counts per reaction type
5. Close the modal when done

**Output format:**
```
Total reactions: N
  👍 Like: X
  ❤️ Love: X
  😂 Haha: X
  😮 Wow: X
  😢 Sad: X
  😡 Angry: X
```

## Getting Share Count

1. Navigate to the post
2. Use `find` or `read_page` to locate the share count (usually near "X shares" / "X lượt chia sẻ")
3. If the user wants to see who shared, click on the share count to open the share list

## Interactive Actions

### Liking a post
1. Find the Like button (👍 / "Thích")
2. `computer → left_click` on it
3. Screenshot to confirm

### Commenting on a post
1. Find the comment input box (usually at the bottom of comments)
2. `computer → left_click` on it to focus
3. `computer → type` the comment text
4. `computer → key "Enter"` to submit
5. Screenshot to confirm

### Sharing a post
1. Find the Share button ("Share" / "Chia sẻ")
2. `computer → left_click` on it
3. A menu appears — use `read_page` to see options
4. **Always ask the user to confirm** before completing the share action (this is a public action)

### Reacting to a post (specific reaction)
1. Find the Like button
2. `computer → hover` over it (this reveals the reaction picker)
3. Wait 1-2 seconds for the picker to appear
4. Screenshot to see available reactions
5. `computer → left_click` on the desired reaction

## Handling Facebook's Dynamic UI

Facebook is a React SPA with aggressive lazy loading. Key tips:

- **Post detail pages open in a dialog** — when you navigate to a post URL, Facebook renders it inside a `[role="dialog"]` modal. All content extraction (post text, comments) should scope to this dialog element
- **After any navigation**, wait 3 seconds and take a screenshot before proceeding — content may still be loading
- **After clicking "load more"**, wait 2-3 seconds for new content to render
- **Infinite scroll** — to load more content, use `computer → scroll` with `scroll_direction: "down"` repeatedly
- **Modals and popups** — Facebook uses portals; after clicking something that opens a modal, use `read_page` to find the modal content (it's often at the end of the DOM)
- **Don't use `get_page_text`** — Facebook's SPA dumps navigation, sidebar, stories, and ads into the text output, making it useless for extracting specific content. Use `screenshot` for visual reading or `javascript_tool` for programmatic extraction
- **`read_page` can be huge** — the accessibility tree for a Facebook page with expanded comments can exceed 60K characters. Use `javascript_tool` for extraction instead, or use `read_page` with a focused `ref_id` on a specific section
- **Login walls** — if you see a login prompt, tell the user they need to log in manually first

## Bilingual UI Elements

Facebook UI labels change based on language. Common mappings:

| English | Vietnamese |
|---------|-----------|
| Like | Thích |
| Comment | Bình luận |
| Share | Chia sẻ |
| See more | Xem thêm |
| View more comments | Xem thêm bình luận |
| View X replies | Xem X phản hồi |
| Most relevant | Phù hợp nhất |
| All comments | Tất cả bình luận |
| Newest first | Mới nhất |

When searching for UI elements, try both languages. For `find` queries, use the English term first — if not found, try Vietnamese.

## Important Safety Notes

- **Interactive actions** (like, comment, share) are visible to others — always confirm with the user before performing these actions
- **Rate limiting** — don't scroll/click too aggressively; Facebook may flag automated behavior. Add small waits (1-2s) between rapid actions
- **Privacy** — extracted data (comments, reactions) may contain personal information. Present it to the user but don't store it externally
- **Never** attempt to bypass login walls or access restricted content

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Page shows login prompt | User needs to log into Facebook manually in Chrome |
| Comments not loading | Click inside dialog first, then use PageDown key — scroll/buttons don't work |
| "Content not available" | Post may be deleted or restricted — inform the user |
| Selectors not matching | Facebook updated their DOM — use `read_page` to inspect current structure and adapt |
| Extension not connected | Ask user to check Chrome Claude Extension is active |
| JS tool output truncated | **Never return large data from javascript_tool.** Use `console.log('PREFIX:' + JSON.stringify(data))` then `read_console_messages` with `pattern: "PREFIX"` to get the full output saved to a file |
| Dialog index wrong | Messenger popup may take index 0 — use `querySelectorAll('[role="dialog"]')[1]` and verify with `.querySelectorAll('[role="article"]').length` |
| Comment text truncated in sheet | Never use `.substring()` on comment text. Use console.log bypass to get full text out of browser |
| Emoji-only comment has empty text | The extraction filters out action words leaving blank content. Store as `[emoji]` — the extraction script handles this automatically |
| Self-referential replyTo (row points to itself) | Happens when author's own name matches another author prefix in their text. The row-building script guards against this: `if (replyTo === myId) replyTo = ''` |
