# Backlog Scanner Agent

You are scanning a project's backlog spreadsheet to extract current pipeline metrics and
identify status changes since the last report.

## Inputs

You will receive:
- **Spreadsheet ID**: The Google Sheets ID to read
- **Skill path**: Path to the hnh-get-report skill (for the parse script)
- **Previous snapshot path**: Path to previous report's `latest.json` (or "none" if first run)

## Task

Run the parse script to extract all metrics from the backlog:

```bash
python3 ~/.claude/skills/hnh-gg-sheets/scripts/sheets.py read {SPREADSHEET_ID} \
  --sheet-name "Backlog" 2>/dev/null | \
  python3 {SKILL_PATH}/scripts/parse_backlog.py \
  [--previous {PREVIOUS_SNAPSHOT_PATH}]
```

If `--previous` is "none", omit the flag entirely.

The script outputs a JSON object with:
- `total_ucs`: Total number of use cases
- `by_subsystem`: Count by sub-system (e.g., Tenant Portal, Driver App)
- `pipeline`: Count by status at each stage (ba, design, be, fe, qa, pilot, launch)
- `estimation_hours`: Estimated hours by role
- `changes`: List of UCs that changed status since last report (empty if no previous snapshot)
- `uc_statuses`: Per-UC status map for snapshot storage

## Also Read: Sprint Calendar

Read the Week-2026 tab to determine the current sprint:

```bash
python3 ~/.claude/skills/hnh-gg-sheets/scripts/sheets.py read {SPREADSHEET_ID} \
  --sheet-name "Week-2026" --range "A1:E20" 2>/dev/null
```

From this data, find the current week (based on today's date) and its sprint number.
The sprint mapping is: Sprint = Week number - 7, starting from Week 8.

## Output

Return both the parse script's JSON output AND the current sprint info. Format as:

```json
{
  "backlog_metrics": { ... },
  "sprint": {
    "number": 3,
    "week": 11,
    "dates": "Mar 9-15, 2026"
  }
}
```
