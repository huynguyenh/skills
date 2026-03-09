#!/usr/bin/env python3
"""
Google Sheets CLI — create, read, write, format, share, and search sheets.

Auth: uses Google Application Default Credentials (ADC).
Set up with: gcloud auth application-default login --scopes="..."
"""

import argparse
import json
import sys
import os
import warnings

# Suppress Python 3.9 EOL warnings from Google libraries
warnings.filterwarnings("ignore", category=FutureWarning)

from google.auth import default as google_auth_default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_services():
    """Return (sheets_service, drive_service) using ADC."""
    creds, _ = google_auth_default(scopes=SCOPES)
    creds.refresh(Request())
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return sheets, drive


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------
def cmd_create(args):
    """Create a new Google Sheet, optionally in a Drive folder with headers."""
    sheets, drive = get_services()

    body = {"properties": {"title": args.title}}

    # Add header row via initial sheet data
    if args.headers:
        headers = [h.strip() for h in args.headers.split(",")]
        body["sheets"] = [
            {
                "data": [
                    {
                        "startRow": 0,
                        "startColumn": 0,
                        "rowData": [
                            {"values": [{"userEnteredValue": {"stringValue": h}} for h in headers]}
                        ],
                    }
                ]
            }
        ]

    result = sheets.spreadsheets().create(body=body).execute()
    spreadsheet_id = result["spreadsheetId"]
    url = result["spreadsheetUrl"]

    # Move to folder if specified
    if args.folder:
        # Get current parents
        file_info = drive.files().get(fileId=spreadsheet_id, fields="parents").execute()
        prev_parents = ",".join(file_info.get("parents", []))
        drive.files().update(
            fileId=spreadsheet_id,
            addParents=args.folder,
            removeParents=prev_parents,
            fields="id, parents",
        ).execute()

    # Bold the header row if headers were provided
    if args.headers:
        sheet_id = result["sheets"][0]["properties"]["sheetId"]
        bold_request = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True},
                                "backgroundColor": {
                                    "red": 0.9,
                                    "green": 0.9,
                                    "blue": 0.9,
                                },
                            }
                        },
                        "fields": "userEnteredFormat(textFormat,backgroundColor)",
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {"frozenRowCount": 1},
                        },
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
            ]
        }
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=bold_request
        ).execute()

    print(json.dumps({"spreadsheet_id": spreadsheet_id, "url": url, "title": args.title}))


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------
def cmd_read(args):
    """Read data from a sheet."""
    sheets, _ = get_services()
    range_str = args.range or "A:ZZ"
    if args.sheet_name:
        range_str = f"'{args.sheet_name}'!{range_str}"

    result = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=args.spreadsheet_id, range=range_str)
        .execute()
    )
    values = result.get("values", [])
    print(json.dumps({"range": result.get("range"), "rows": len(values), "values": values}))


# ---------------------------------------------------------------------------
# WRITE (update)
# ---------------------------------------------------------------------------
def cmd_write(args):
    """Write data to a specific range."""
    sheets, _ = get_services()
    values = json.loads(args.values)
    range_str = args.range
    if args.sheet_name:
        range_str = f"'{args.sheet_name}'!{range_str}"

    body = {"values": values}
    result = (
        sheets.spreadsheets()
        .values()
        .update(
            spreadsheetId=args.spreadsheet_id,
            range=range_str,
            valueInputOption=args.input_option,
            body=body,
        )
        .execute()
    )
    print(
        json.dumps(
            {
                "updated_range": result.get("updatedRange"),
                "updated_rows": result.get("updatedRows"),
                "updated_cells": result.get("updatedCells"),
            }
        )
    )


# ---------------------------------------------------------------------------
# APPEND
# ---------------------------------------------------------------------------
def cmd_append(args):
    """Append rows to the end of existing data."""
    sheets, _ = get_services()
    values = json.loads(args.values)
    range_str = args.range or "A:A"
    if args.sheet_name:
        range_str = f"'{args.sheet_name}'!{range_str}"

    body = {"values": values}
    result = (
        sheets.spreadsheets()
        .values()
        .append(
            spreadsheetId=args.spreadsheet_id,
            range=range_str,
            valueInputOption=args.input_option,
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )
    updates = result.get("updates", {})
    print(
        json.dumps(
            {
                "updated_range": updates.get("updatedRange"),
                "updated_rows": updates.get("updatedRows"),
                "updated_cells": updates.get("updatedCells"),
            }
        )
    )


# ---------------------------------------------------------------------------
# FORMAT
# ---------------------------------------------------------------------------
def _parse_color(hex_color):
    """Convert #RRGGBB to Google Sheets color dict."""
    hex_color = hex_color.lstrip("#")
    return {
        "red": int(hex_color[0:2], 16) / 255,
        "green": int(hex_color[2:4], 16) / 255,
        "blue": int(hex_color[4:6], 16) / 255,
    }


def _parse_range(range_str):
    """Parse A1:B2 notation into grid range indices (0-based).
    Supports: A1:D10, A:D (full columns), 1:10 (full rows), A1 (single cell).
    """
    import re

    range_str = range_str.replace("$", "")

    def col_to_idx(col):
        result = 0
        for ch in col.upper():
            result = result * 26 + (ord(ch) - ord("A") + 1)
        return result - 1

    m = re.match(r"^([A-Za-z]*)(\d*):?([A-Za-z]*)(\d*)$", range_str)
    if not m:
        raise ValueError(f"Cannot parse range: {range_str}")

    start_col, start_row, end_col, end_row = m.groups()

    grid = {}
    if start_col:
        grid["startColumnIndex"] = col_to_idx(start_col)
    if end_col:
        grid["endColumnIndex"] = col_to_idx(end_col) + 1
    elif start_col and not end_col:
        grid["endColumnIndex"] = grid["startColumnIndex"] + 1
    if start_row:
        grid["startRowIndex"] = int(start_row) - 1
    if end_row:
        grid["endRowIndex"] = int(end_row)
    elif start_row and not end_row:
        grid["endRowIndex"] = grid["startRowIndex"] + 1

    return grid


def _get_sheet_id(sheets_svc, spreadsheet_id, sheet_name):
    """Resolve a sheet tab name to its sheetId. Returns 0 for first sheet if name is None."""
    if not sheet_name:
        meta = sheets_svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return meta["sheets"][0]["properties"]["sheetId"]
    meta = sheets_svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for s in meta["sheets"]:
        if s["properties"]["title"] == sheet_name:
            return s["properties"]["sheetId"]
    raise ValueError(f"Sheet tab '{sheet_name}' not found")


def cmd_format(args):
    """Apply formatting to a range."""
    sheets, _ = get_services()
    sheet_id = _get_sheet_id(sheets, args.spreadsheet_id, args.sheet_name)

    grid_range = _parse_range(args.range)
    grid_range["sheetId"] = sheet_id

    requests = []

    # --- Cell formatting ---
    cell_format = {}
    fields = []

    if args.bold is not None:
        cell_format.setdefault("textFormat", {})["bold"] = args.bold
        fields.append("userEnteredFormat.textFormat.bold")

    if args.italic is not None:
        cell_format.setdefault("textFormat", {})["italic"] = args.italic
        fields.append("userEnteredFormat.textFormat.italic")

    if args.font_size:
        cell_format.setdefault("textFormat", {})["fontSize"] = args.font_size
        fields.append("userEnteredFormat.textFormat.fontSize")

    if args.font_color:
        cell_format.setdefault("textFormat", {})["foregroundColor"] = _parse_color(args.font_color)
        fields.append("userEnteredFormat.textFormat.foregroundColor")

    if args.bg_color:
        cell_format["backgroundColor"] = _parse_color(args.bg_color)
        fields.append("userEnteredFormat.backgroundColor")

    if args.halign:
        cell_format["horizontalAlignment"] = args.halign.upper()
        fields.append("userEnteredFormat.horizontalAlignment")

    if args.valign:
        cell_format["verticalAlignment"] = args.valign.upper()
        fields.append("userEnteredFormat.verticalAlignment")

    if args.wrap:
        cell_format["wrapStrategy"] = args.wrap.upper()
        fields.append("userEnteredFormat.wrapStrategy")

    if args.number_format:
        cell_format["numberFormat"] = {"type": "NUMBER", "pattern": args.number_format}
        fields.append("userEnteredFormat.numberFormat")

    if fields:
        requests.append(
            {
                "repeatCell": {
                    "range": grid_range,
                    "cell": {"userEnteredFormat": cell_format},
                    "fields": ",".join(fields),
                }
            }
        )

    # --- Column width ---
    if args.col_width:
        requests.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": grid_range.get("startColumnIndex", 0),
                        "endIndex": grid_range.get("endColumnIndex", grid_range.get("startColumnIndex", 0) + 1),
                    },
                    "properties": {"pixelSize": args.col_width},
                    "fields": "pixelSize",
                }
            }
        )

    # --- Row height ---
    if args.row_height:
        requests.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": grid_range.get("startRowIndex", 0),
                        "endIndex": grid_range.get("endRowIndex", grid_range.get("startRowIndex", 0) + 1),
                    },
                    "properties": {"pixelSize": args.row_height},
                    "fields": "pixelSize",
                }
            }
        )

    # --- Merge ---
    if args.merge:
        requests.append(
            {"mergeCells": {"range": grid_range, "mergeType": "MERGE_ALL"}}
        )

    # --- Freeze ---
    if args.freeze_rows is not None or args.freeze_cols is not None:
        props = {}
        freeze_fields = []
        if args.freeze_rows is not None:
            props["frozenRowCount"] = args.freeze_rows
            freeze_fields.append("gridProperties.frozenRowCount")
        if args.freeze_cols is not None:
            props["frozenColumnCount"] = args.freeze_cols
            freeze_fields.append("gridProperties.frozenColumnCount")
        requests.append(
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": props,
                    },
                    "fields": ",".join(freeze_fields),
                }
            }
        )

    # --- Borders ---
    if args.border:
        border_style = {
            "style": args.border.upper(),
            "color": _parse_color(args.border_color) if args.border_color else {"red": 0, "green": 0, "blue": 0},
        }
        requests.append(
            {
                "updateBorders": {
                    "range": grid_range,
                    "top": border_style,
                    "bottom": border_style,
                    "left": border_style,
                    "right": border_style,
                    "innerHorizontal": border_style,
                    "innerVertical": border_style,
                }
            }
        )

    if not requests:
        print(json.dumps({"error": "No formatting options specified"}))
        sys.exit(1)

    result = sheets.spreadsheets().batchUpdate(
        spreadsheetId=args.spreadsheet_id, body={"requests": requests}
    ).execute()
    print(json.dumps({"applied": len(requests), "range": args.range}))


# ---------------------------------------------------------------------------
# SHARE
# ---------------------------------------------------------------------------
def cmd_share(args):
    """Share a spreadsheet with someone."""
    _, drive = get_services()

    permission = {"type": "user", "role": args.role, "emailAddress": args.email}

    result = (
        drive.permissions()
        .create(
            fileId=args.spreadsheet_id,
            body=permission,
            sendNotificationEmail=not args.no_notify,
            fields="id,emailAddress,role",
        )
        .execute()
    )
    print(json.dumps({"shared_with": args.email, "role": args.role, "permission_id": result["id"]}))


# ---------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------
def cmd_search(args):
    """Search for sheets by name in Drive."""
    _, drive = get_services()

    query_parts = [
        "mimeType='application/vnd.google-apps.spreadsheet'",
        f"name contains '{args.query}'",
        "trashed=false",
    ]
    if args.folder:
        query_parts.append(f"'{args.folder}' in parents")

    results = (
        drive.files()
        .list(
            q=" and ".join(query_parts),
            fields="files(id,name,webViewLink,modifiedTime,owners)",
            orderBy="modifiedTime desc",
            pageSize=args.limit,
        )
        .execute()
    )

    files = []
    for f in results.get("files", []):
        files.append(
            {
                "id": f["id"],
                "name": f["name"],
                "url": f.get("webViewLink"),
                "modified": f.get("modifiedTime"),
            }
        )
    print(json.dumps({"count": len(files), "sheets": files}))


# ---------------------------------------------------------------------------
# INFO (get spreadsheet metadata)
# ---------------------------------------------------------------------------
def cmd_info(args):
    """Get spreadsheet metadata: title, sheets/tabs, row/col counts."""
    sheets, _ = get_services()
    meta = sheets.spreadsheets().get(spreadsheetId=args.spreadsheet_id).execute()

    tabs = []
    for s in meta["sheets"]:
        props = s["properties"]
        grid = props.get("gridProperties", {})
        tabs.append(
            {
                "title": props["title"],
                "sheet_id": props["sheetId"],
                "index": props["index"],
                "rows": grid.get("rowCount"),
                "cols": grid.get("columnCount"),
                "frozen_rows": grid.get("frozenRowCount", 0),
                "frozen_cols": grid.get("frozenColumnCount", 0),
            }
        )

    print(
        json.dumps(
            {
                "spreadsheet_id": meta["spreadsheetId"],
                "title": meta["properties"]["title"],
                "url": meta["spreadsheetUrl"],
                "tabs": tabs,
            }
        )
    )


# ---------------------------------------------------------------------------
# ADD-SHEET (add a new tab)
# ---------------------------------------------------------------------------
def cmd_add_sheet(args):
    """Add a new sheet tab to an existing spreadsheet."""
    sheets, _ = get_services()
    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {"title": args.title}
                }
            }
        ]
    }
    result = sheets.spreadsheets().batchUpdate(
        spreadsheetId=args.spreadsheet_id, body=body
    ).execute()
    new_sheet = result["replies"][0]["addSheet"]["properties"]
    print(json.dumps({"sheet_id": new_sheet["sheetId"], "title": new_sheet["title"]}))


# ---------------------------------------------------------------------------
# CLEAR
# ---------------------------------------------------------------------------
def cmd_clear(args):
    """Clear values from a range (keeps formatting)."""
    sheets, _ = get_services()
    range_str = args.range
    if args.sheet_name:
        range_str = f"'{args.sheet_name}'!{range_str}"

    sheets.spreadsheets().values().clear(
        spreadsheetId=args.spreadsheet_id, range=range_str, body={}
    ).execute()
    print(json.dumps({"cleared": range_str}))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Google Sheets CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p = sub.add_parser("create", help="Create a new spreadsheet")
    p.add_argument("title", help="Spreadsheet title")
    p.add_argument("--folder", help="Drive folder ID to create in")
    p.add_argument("--headers", help="Comma-separated header names")
    p.set_defaults(func=cmd_create)

    # read
    p = sub.add_parser("read", help="Read data from a spreadsheet")
    p.add_argument("spreadsheet_id", help="Spreadsheet ID or URL")
    p.add_argument("--range", help="A1 range (e.g. A1:D10). Reads all if omitted")
    p.add_argument("--sheet-name", help="Sheet tab name")
    p.set_defaults(func=cmd_read)

    # write
    p = sub.add_parser("write", help="Write data to a range")
    p.add_argument("spreadsheet_id")
    p.add_argument("--range", required=True, help="Start cell/range (e.g. A1)")
    p.add_argument("--values", required=True, help="JSON 2D array: [[r1c1,r1c2],[r2c1,r2c2]]")
    p.add_argument("--sheet-name", help="Sheet tab name")
    p.add_argument("--input-option", default="USER_ENTERED", choices=["RAW", "USER_ENTERED"])
    p.set_defaults(func=cmd_write)

    # append
    p = sub.add_parser("append", help="Append rows after existing data")
    p.add_argument("spreadsheet_id")
    p.add_argument("--values", required=True, help="JSON 2D array of rows to append")
    p.add_argument("--range", help="Range to detect table (default: A:A)")
    p.add_argument("--sheet-name", help="Sheet tab name")
    p.add_argument("--input-option", default="USER_ENTERED", choices=["RAW", "USER_ENTERED"])
    p.set_defaults(func=cmd_append)

    # format
    p = sub.add_parser("format", help="Format a cell range")
    p.add_argument("spreadsheet_id")
    p.add_argument("--range", required=True, help="A1 range to format")
    p.add_argument("--sheet-name", help="Sheet tab name")
    p.add_argument("--bold", type=lambda x: x.lower() == "true", default=None)
    p.add_argument("--italic", type=lambda x: x.lower() == "true", default=None)
    p.add_argument("--font-size", type=int)
    p.add_argument("--font-color", help="#RRGGBB")
    p.add_argument("--bg-color", help="#RRGGBB")
    p.add_argument("--halign", choices=["left", "center", "right"])
    p.add_argument("--valign", choices=["top", "middle", "bottom"])
    p.add_argument("--wrap", choices=["overflow", "clip", "wrap"])
    p.add_argument("--number-format", help="Number format pattern (e.g. #,##0.00)")
    p.add_argument("--col-width", type=int, help="Column width in pixels")
    p.add_argument("--row-height", type=int, help="Row height in pixels")
    p.add_argument("--merge", action="store_true", help="Merge cells in range")
    p.add_argument("--freeze-rows", type=int)
    p.add_argument("--freeze-cols", type=int)
    p.add_argument("--border", choices=["solid", "dashed", "dotted", "double"])
    p.add_argument("--border-color", help="#RRGGBB for border")
    p.set_defaults(func=cmd_format)

    # share
    p = sub.add_parser("share", help="Share spreadsheet with someone")
    p.add_argument("spreadsheet_id")
    p.add_argument("--email", required=True)
    p.add_argument("--role", default="writer", choices=["reader", "commenter", "writer"])
    p.add_argument("--no-notify", action="store_true", help="Skip email notification")
    p.set_defaults(func=cmd_share)

    # search
    p = sub.add_parser("search", help="Search for sheets by name in Drive")
    p.add_argument("query", help="Search term")
    p.add_argument("--folder", help="Restrict to this Drive folder ID")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    # info
    p = sub.add_parser("info", help="Get spreadsheet metadata")
    p.add_argument("spreadsheet_id")
    p.set_defaults(func=cmd_info)

    # add-sheet
    p = sub.add_parser("add-sheet", help="Add a new tab to a spreadsheet")
    p.add_argument("spreadsheet_id")
    p.add_argument("title", help="Name for the new tab")
    p.set_defaults(func=cmd_add_sheet)

    # clear
    p = sub.add_parser("clear", help="Clear values from a range")
    p.add_argument("spreadsheet_id")
    p.add_argument("--range", required=True)
    p.add_argument("--sheet-name")
    p.set_defaults(func=cmd_clear)

    args = parser.parse_args()

    # Normalize spreadsheet_id — accept URLs
    if hasattr(args, "spreadsheet_id") and args.spreadsheet_id:
        sid = args.spreadsheet_id
        if "docs.google.com" in sid or "drive.google.com" in sid:
            # Extract ID from URL
            import re
            m = re.search(r"/d/([a-zA-Z0-9_-]+)", sid)
            if m:
                args.spreadsheet_id = m.group(1)

    try:
        args.func(args)
    except HttpError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
