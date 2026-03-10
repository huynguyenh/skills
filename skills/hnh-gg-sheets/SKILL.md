---
name: hnh-gg-sheets
description: >
  Interact with Google Sheets — create, read, write, format, share, and search spreadsheets
  via the Google Sheets & Drive APIs. Use this skill whenever the user wants to work with
  Google Sheets: creating a new sheet, reading data from a sheet, writing/updating data,
  formatting cells, sharing with collaborators, or finding sheets by name. Trigger on mentions
  of "Google Sheet", "gsheet", "spreadsheet" (when the context is Google Drive, not local .xlsx),
  sheet URLs (docs.google.com/spreadsheets), or any request to create/read/update a sheet
  in Google Drive. If the user doesn't specify a project or location, assume it's for ZenLabs
  (check ~/.claude/knowledge/personal/zenlabs.md for Drive structure and file naming rules).
  Do NOT trigger for local .xlsx/.csv file operations — those belong to the xlsx skill.
---

# Google Sheets Skill

Interact with Google Sheets through a Python CLI tool that wraps the Sheets and Drive APIs.

## Prerequisites

- **gcloud CLI** with Application Default Credentials configured
- **Python packages**: `google-api-python-client`, `google-auth`
- ADC scopes must include `spreadsheets` and `drive`

If auth fails with a credentials error, run:
```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive"
```

## The CLI Tool

All operations go through a single script:

```
python3 ~/.claude/skills/hnh-gg-sheets/scripts/sheets.py <command> [args]
```

The script outputs JSON to stdout, errors to stderr.

## ZenLabs Defaults

When the user doesn't specify a project or destination, this is a ZenLabs task. Read `~/.claude/knowledge/personal/zenlabs.md` for full context. Key rules:

- **Default folder**: `6. Brainstorming` in ZenLabs Drive
- **File naming**: Always prefix with `zenlabs | {descriptive name}`
- **Drive root folder ID**: `1CHEn7mozKXpKU9O76Q5HQ2ZUnEgLOzd0`

To find the folder ID for a specific subfolder (e.g., "6. Brainstorming"), use the search command or navigate Drive. Cache folder IDs in the conversation once discovered.

## Commands Reference

### create — Create a new spreadsheet

```bash
python3 <script> create "zenlabs | project tracker" \
  --folder FOLDER_ID \
  --headers "Task,Owner,Status,Due Date"
```

- `--folder`: Drive folder ID. For ZenLabs, find the right subfolder first.
- `--headers`: Comma-separated. Auto-bolds and freezes the header row.

### read — Read data from a spreadsheet

```bash
python3 <script> read SPREADSHEET_ID \
  --range "A1:D10" \
  --sheet-name "Sheet1"
```

- Accepts spreadsheet ID or full URL (auto-extracts the ID).
- Omit `--range` to read everything.
- `--sheet-name` targets a specific tab.

### write — Update a specific range

```bash
python3 <script> write SPREADSHEET_ID \
  --range "A2" \
  --values '[["Task 1","Alice","In Progress","2026-04-01"],["Task 2","Bob","Done","2026-03-15"]]'
```

- `--values`: JSON 2D array. Each inner array is a row.
- `--input-option`: `USER_ENTERED` (default, interprets formulas/dates) or `RAW`.

### append — Add rows after existing data

```bash
python3 <script> append SPREADSHEET_ID \
  --values '[["New task","Charlie","Todo","2026-05-01"]]'
```

- Detects the last row and appends below it.
- `--range` can target a specific column range (default: `A:A`).

### format — Style cells

```bash
python3 <script> format SPREADSHEET_ID \
  --range "A1:D1" \
  --bold true \
  --bg-color "#4285F4" \
  --font-color "#FFFFFF" \
  --halign center \
  --freeze-rows 1
```

**Available options:**
| Flag | Values | What it does |
|------|--------|-------------|
| `--bold` | true/false | Bold text |
| `--italic` | true/false | Italic text |
| `--font-size` | integer | Font size in pt |
| `--font-color` | #RRGGBB | Text color |
| `--bg-color` | #RRGGBB | Cell background |
| `--halign` | left/center/right | Horizontal alignment |
| `--valign` | top/middle/bottom | Vertical alignment |
| `--wrap` | overflow/clip/wrap | Text wrapping |
| `--number-format` | pattern | e.g. `#,##0.00`, `0%` |
| `--col-width` | pixels | Column width |
| `--row-height` | pixels | Row height |
| `--merge` | (flag) | Merge cells in range |
| `--freeze-rows` | integer | Freeze top N rows |
| `--freeze-cols` | integer | Freeze left N columns |
| `--border` | solid/dashed/dotted/double | Add borders |
| `--border-color` | #RRGGBB | Border color |
| `--sheet-name` | string | Target a specific tab |

Multiple flags can be combined in one call.

### share — Invite collaborators

```bash
python3 <script> share SPREADSHEET_ID \
  --email "<email>" \
  --role writer
```

- `--role`: `reader`, `commenter`, or `writer`
- `--no-notify`: Skip the email notification

### search — Find sheets by name

```bash
python3 <script> search "revenue" \
  --folder FOLDER_ID \
  --limit 5
```

- Searches by name (partial match) across Drive.
- `--folder` restricts to a specific Drive folder.

### info — Get spreadsheet metadata

```bash
python3 <script> info SPREADSHEET_ID
```

Returns title, URL, and all tabs with row/col counts and freeze state.

### add-sheet — Add a new tab

```bash
python3 <script> add-sheet SPREADSHEET_ID "Q1 Data"
```

### clear — Clear values (keep formatting)

```bash
python3 <script> clear SPREADSHEET_ID \
  --range "A2:D100" \
  --sheet-name "Sheet1"
```

## Workflow Patterns

### Creating a new ZenLabs sheet

1. Read `~/.claude/knowledge/personal/zenlabs.md` for folder structure
2. Search Drive for the target subfolder to get its folder ID (or use a cached ID)
3. Create the sheet with `zenlabs | ` prefix, headers, and the folder ID
4. Apply additional formatting if needed
5. Share with collaborators if requested
6. Return the sheet URL to the user

### Populating a sheet from data

1. Create the sheet (or get its ID if it exists)
2. Write headers if not done during creation
3. Write data in batches — the API handles up to ~50k cells per call
4. Format as needed (bold headers, number formats, column widths)

### Reading and reporting

1. Use `info` to understand the sheet structure (tabs, dimensions)
2. Read the relevant range
3. Process and present the data to the user

## Error Handling

- **Auth errors**: Re-run the `gcloud auth application-default login` command above
- **404 / not found**: Double-check the spreadsheet ID (URL extraction might fail on unusual URLs)
- **Permission denied**: The authenticated account needs access to the sheet
- **Quota errors**: Google Sheets API has a limit of 300 requests per minute per project
