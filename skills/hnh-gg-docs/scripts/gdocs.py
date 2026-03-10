#!/usr/bin/env python3
"""
Google Docs CLI — read, create, append, insert, replace, and search docs.

Auth: uses Google Application Default Credentials (ADC).
Set up with: gcloud auth application-default login --scopes="..."
"""

import argparse
import json
import re
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

from google.auth import default as google_auth_default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


def get_services():
    """Return (docs_service, drive_service) using ADC."""
    creds, _ = google_auth_default(scopes=SCOPES)
    creds.refresh(Request())
    docs = build("docs", "v1", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return docs, drive


def extract_doc_id(id_or_url):
    """Extract document ID from a Google Docs URL or return as-is."""
    m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", id_or_url)
    return m.group(1) if m else id_or_url


def extract_text(body, with_indexes=False):
    """Extract readable text from a document body, optionally with indexes."""
    lines = []
    for elem in body.get("content", []):
        if "paragraph" in elem:
            para = elem["paragraph"]
            style = para.get("paragraphStyle", {}).get("namedStyleType", "")
            bullet = para.get("bullet")

            text_parts = []
            for pe in para.get("elements", []):
                if "textRun" in pe:
                    content = pe["textRun"]["content"]
                    if with_indexes:
                        text_parts.append(f"[{pe['startIndex']}:{pe['endIndex']}]{content}")
                    else:
                        text_parts.append(content)

            line = "".join(text_parts)

            # Add heading markers
            if style == "HEADING_1":
                line = "# " + line
            elif style == "HEADING_2":
                line = "## " + line
            elif style == "HEADING_3":
                line = "### " + line
            elif style == "HEADING_4":
                line = "#### " + line
            elif bullet:
                nesting = bullet.get("nestingLevel", 0)
                indent = "  " * nesting
                line = f"{indent}- {line}"

            lines.append(line)

        elif "table" in elem:
            table = elem["table"]
            for row in table.get("tableRows", []):
                cells = []
                for cell in row.get("tableCells", []):
                    cell_text = extract_text(cell, with_indexes=False)
                    cells.append(cell_text.strip())
                lines.append("| " + " | ".join(cells) + " |")
            lines.append("")

    return "".join(lines)


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------
def cmd_read(args):
    docs, _ = get_services()
    doc_id = extract_doc_id(args.document_id)

    try:
        doc = docs.documents().get(documentId=doc_id).execute()
    except HttpError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

    text = extract_text(doc.get("body", {}), with_indexes=args.with_indexes)

    result = {
        "document_id": doc["documentId"],
        "title": doc.get("title", ""),
        "url": f"https://docs.google.com/document/d/{doc['documentId']}/edit",
        "content": text,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------
def cmd_create(args):
    docs, drive = get_services()

    try:
        doc = docs.documents().create(body={"title": args.title}).execute()
    except HttpError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

    doc_id = doc["documentId"]

    # Insert content if provided
    content = args.content
    if args.content_file:
        with open(args.content_file, "r") as f:
            content = f.read()

    if content:
        text = content.replace("\\n", "\n")
        try:
            docs.documents().batchUpdate(
                documentId=doc_id,
                body={
                    "requests": [
                        {
                            "insertText": {
                                "text": text,
                                "endOfSegmentLocation": {"segmentId": ""},
                            }
                        }
                    ]
                },
            ).execute()
        except HttpError as e:
            print(json.dumps({"error": f"Created doc but failed to insert content: {e}"}, indent=2), file=sys.stderr)

    # Move to folder if specified
    if args.folder:
        try:
            f = drive.files().get(fileId=doc_id, fields="parents").execute()
            prev_parents = ",".join(f.get("parents", []))
            drive.files().update(
                fileId=doc_id,
                addParents=args.folder,
                removeParents=prev_parents,
                fields="id, parents",
            ).execute()
        except HttpError as e:
            print(json.dumps({"error": f"Created doc but failed to move to folder: {e}"}, indent=2), file=sys.stderr)

    result = {
        "document_id": doc_id,
        "title": args.title,
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# APPEND
# ---------------------------------------------------------------------------
def cmd_append(args):
    docs, _ = get_services()
    doc_id = extract_doc_id(args.document_id)

    content = args.text
    if args.content_file:
        with open(args.content_file, "r") as f:
            content = f.read()

    if not content:
        print(json.dumps({"error": "No content provided"}, indent=2), file=sys.stderr)
        sys.exit(1)

    text = content.replace("\\n", "\n")

    try:
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "text": text,
                            "endOfSegmentLocation": {"segmentId": ""},
                        }
                    }
                ]
            },
        ).execute()
    except HttpError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"result": "success", "chars_appended": len(text)}, indent=2))


# ---------------------------------------------------------------------------
# INSERT
# ---------------------------------------------------------------------------
def cmd_insert(args):
    docs, _ = get_services()
    doc_id = extract_doc_id(args.document_id)
    text = args.text.replace("\\n", "\n")

    try:
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "text": text,
                            "location": {"index": args.index},
                        }
                    }
                ]
            },
        ).execute()
    except HttpError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"result": "success", "index": args.index, "chars_inserted": len(text)}, indent=2))


# ---------------------------------------------------------------------------
# REPLACE
# ---------------------------------------------------------------------------
def cmd_replace(args):
    docs, _ = get_services()
    doc_id = extract_doc_id(args.document_id)

    try:
        resp = docs.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {
                                "text": args.find,
                                "matchCase": not args.ignore_case,
                            },
                            "replaceText": args.replace,
                        }
                    }
                ]
            },
        ).execute()
    except HttpError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

    changed = 0
    for reply in resp.get("replies", []):
        if "replaceAllText" in reply:
            changed = reply["replaceAllText"].get("occurrencesChanged", 0)

    print(json.dumps({"result": "success", "occurrences_changed": changed}, indent=2))


# ---------------------------------------------------------------------------
# INFO
# ---------------------------------------------------------------------------
def cmd_info(args):
    docs, _ = get_services()
    doc_id = extract_doc_id(args.document_id)

    try:
        doc = docs.documents().get(documentId=doc_id).execute()
    except HttpError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

    # Count content length
    body = doc.get("body", {})
    content = body.get("content", [])
    end_index = content[-1].get("endIndex", 0) if content else 0

    result = {
        "document_id": doc["documentId"],
        "title": doc.get("title", ""),
        "url": f"https://docs.google.com/document/d/{doc['documentId']}/edit",
        "revision_id": doc.get("revisionId", ""),
        "content_length": end_index,
        "tabs": [
            {"tab_id": t.get("tabProperties", {}).get("tabId", ""), "title": t.get("tabProperties", {}).get("title", "")}
            for t in doc.get("tabs", [])
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------
def cmd_search(args):
    _, drive = get_services()

    query = f"mimeType='application/vnd.google-apps.document' and name contains '{args.query}' and trashed=false"
    if args.folder:
        query += f" and '{args.folder}' in parents"

    try:
        resp = drive.files().list(
            q=query,
            pageSize=args.limit,
            fields="files(id,name,modifiedTime,webViewLink)",
            orderBy="modifiedTime desc",
        ).execute()
    except HttpError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)

    files = resp.get("files", [])
    result = {
        "count": len(files),
        "results": [
            {
                "id": f["id"],
                "name": f["name"],
                "url": f.get("webViewLink", ""),
                "modified": f.get("modifiedTime", ""),
            }
            for f in files
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# ARGUMENT PARSING
# ---------------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(description="Google Docs CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # read
    p = sub.add_parser("read", help="Read document content")
    p.add_argument("document_id", help="Document ID or URL")
    p.add_argument("--with-indexes", action="store_true", help="Show character indexes")

    # create
    p = sub.add_parser("create", help="Create a new document")
    p.add_argument("title", help="Document title")
    p.add_argument("--content", help="Initial text content")
    p.add_argument("--content-file", help="Read content from file")
    p.add_argument("--folder", help="Drive folder ID to move doc into")

    # append
    p = sub.add_parser("append", help="Append text to a document")
    p.add_argument("document_id", help="Document ID or URL")
    p.add_argument("text", nargs="?", help="Text to append")
    p.add_argument("--content-file", help="Read content from file")

    # insert
    p = sub.add_parser("insert", help="Insert text at a position")
    p.add_argument("document_id", help="Document ID or URL")
    p.add_argument("text", help="Text to insert")
    p.add_argument("--index", type=int, default=1, help="Character index (default: 1 = start)")

    # replace
    p = sub.add_parser("replace", help="Find and replace text")
    p.add_argument("document_id", help="Document ID or URL")
    p.add_argument("--find", required=True, help="Text to find")
    p.add_argument("--replace", required=True, help="Replacement text")
    p.add_argument("--ignore-case", action="store_true", help="Case-insensitive match")

    # info
    p = sub.add_parser("info", help="Get document metadata")
    p.add_argument("document_id", help="Document ID or URL")

    # search
    p = sub.add_parser("search", help="Search for documents in Drive")
    p.add_argument("query", help="Search term")
    p.add_argument("--folder", help="Restrict to Drive folder ID")
    p.add_argument("--limit", type=int, default=10, help="Max results")

    return parser


COMMAND_MAP = {
    "read": cmd_read,
    "create": cmd_create,
    "append": cmd_append,
    "insert": cmd_insert,
    "replace": cmd_replace,
    "info": cmd_info,
    "search": cmd_search,
}


def main():
    parser = build_parser()
    args = parser.parse_args()
    handler = COMMAND_MAP.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
