#!/usr/bin/env python3
"""
Google Drive CLI — list, search, upload, download, move, copy, rename, trash, and organize files.

Auth: uses Google Application Default Credentials (ADC).
Set up with: gcloud auth application-default login --scopes="..."
"""

import argparse
import io
import json
import mimetypes
import os
import re
import sys
import warnings

# Suppress Python 3.9 EOL warnings from Google libraries
warnings.filterwarnings("ignore", category=FutureWarning)

from google.auth import default as google_auth_default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]

STANDARD_FIELDS = "id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink, trashed"


def get_service():
    """Return Drive v3 service using ADC."""
    creds, _ = google_auth_default(scopes=SCOPES)
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _extract_id(value):
    """Extract file/folder ID from a URL or return as-is if already an ID."""
    if "drive.google.com" in value or "docs.google.com" in value:
        # Match /d/ID, /folders/ID, or id= param
        m = re.search(r"(?:/d/|/folders/|[?&]id=)([a-zA-Z0-9_-]+)", value)
        if m:
            return m.group(1)
    return value


def _format_size(size_bytes):
    """Human-readable file size."""
    if size_bytes is None:
        return None
    size = int(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------
def cmd_list(args):
    drive = get_service()
    folder_id = _extract_id(args.folder) if args.folder else None

    q_parts = ["trashed = false"]
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    if args.type == "folder":
        q_parts.append("mimeType = 'application/vnd.google-apps.folder'")
    elif args.type == "file":
        q_parts.append("mimeType != 'application/vnd.google-apps.folder'")

    query = " and ".join(q_parts)
    results = []
    page_token = None
    limit = args.limit

    while True:
        resp = (
            drive.files()
            .list(
                q=query,
                fields=f"nextPageToken, files({STANDARD_FIELDS})",
                orderBy=args.sort or "modifiedTime desc",
                pageSize=min(limit - len(results), 100),
                pageToken=page_token,
            )
            .execute()
        )
        files = resp.get("files", [])
        for f in files:
            f["size_human"] = _format_size(f.get("size"))
        results.extend(files)
        if len(results) >= limit:
            results = results[:limit]
            break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    print(json.dumps({"count": len(results), "files": results}, indent=2))


# ---------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------
def cmd_search(args):
    drive = get_service()

    q_parts = ["trashed = false"]
    if args.query:
        escaped = args.query.replace("\\", "\\\\").replace("'", "\\'")
        q_parts.append(f"name contains '{escaped}'")
    if args.folder:
        folder_id = _extract_id(args.folder)
        q_parts.append(f"'{folder_id}' in parents")
    if args.mime_type:
        q_parts.append(f"mimeType = '{args.mime_type}'")
    if args.type == "folder":
        q_parts.append("mimeType = 'application/vnd.google-apps.folder'")
    elif args.type == "file":
        q_parts.append("mimeType != 'application/vnd.google-apps.folder'")

    query = " and ".join(q_parts)
    results = []
    page_token = None
    limit = args.limit

    while True:
        resp = (
            drive.files()
            .list(
                q=query,
                fields=f"nextPageToken, files({STANDARD_FIELDS})",
                orderBy="modifiedTime desc",
                pageSize=min(limit - len(results), 100),
                pageToken=page_token,
            )
            .execute()
        )
        files = resp.get("files", [])
        for f in files:
            f["size_human"] = _format_size(f.get("size"))
        results.extend(files)
        if len(results) >= limit:
            results = results[:limit]
            break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    print(json.dumps({"count": len(results), "files": results}, indent=2))


# ---------------------------------------------------------------------------
# INFO
# ---------------------------------------------------------------------------
def cmd_info(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)
    fields = "id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink, owners, permissions, trashed, shared"
    meta = drive.files().get(fileId=file_id, fields=fields).execute()
    meta["size_human"] = _format_size(meta.get("size"))
    print(json.dumps(meta, indent=2))


# ---------------------------------------------------------------------------
# CREATE-FOLDER
# ---------------------------------------------------------------------------
def cmd_create_folder(args):
    drive = get_service()
    body = {
        "name": args.name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if args.parent:
        body["parents"] = [_extract_id(args.parent)]

    folder = drive.files().create(body=body, fields="id, name, webViewLink").execute()
    print(json.dumps(folder, indent=2))


# ---------------------------------------------------------------------------
# UPLOAD
# ---------------------------------------------------------------------------
def cmd_upload(args):
    drive = get_service()
    local_path = os.path.expanduser(args.local_path)

    if not os.path.isfile(local_path):
        print(json.dumps({"error": f"File not found: {local_path}"}), file=sys.stderr)
        sys.exit(1)

    mime_type = args.mime_type or mimetypes.guess_type(local_path)[0] or "application/octet-stream"
    file_name = args.name or os.path.basename(local_path)

    body = {"name": file_name}
    if args.folder:
        body["parents"] = [_extract_id(args.folder)]

    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    result = (
        drive.files()
        .create(body=body, media_body=media, fields="id, name, mimeType, size, webViewLink")
        .execute()
    )
    result["size_human"] = _format_size(result.get("size"))
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------------------------------
# Export MIME mappings for Google Workspace files
EXPORT_MIMES = {
    "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.spreadsheet": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xlsx",
    ),
    "application/vnd.google-apps.presentation": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.drawing": ("application/pdf", ".pdf"),
}


def cmd_download(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)

    meta = drive.files().get(fileId=file_id, fields="id, name, mimeType, size").execute()
    mime = meta["mimeType"]

    out_dir = os.path.expanduser(args.output_dir or ".")
    os.makedirs(out_dir, exist_ok=True)

    # Google Workspace files need export
    if mime in EXPORT_MIMES:
        export_mime, ext = EXPORT_MIMES[mime]
        if args.export_mime:
            export_mime = args.export_mime
            ext = mimetypes.guess_extension(export_mime) or ""
        file_name = (args.name or meta["name"]) + ext
        request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        file_name = args.name or meta["name"]
        request = drive.files().get_media(fileId=file_id)

    out_path = os.path.join(out_dir, file_name)
    fh = io.FileIO(out_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.close()

    print(json.dumps({"downloaded": out_path, "name": file_name, "size_human": _format_size(os.path.getsize(out_path))}))


# ---------------------------------------------------------------------------
# MOVE
# ---------------------------------------------------------------------------
def cmd_move(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)
    dest_id = _extract_id(args.destination)

    # Get current parents
    meta = drive.files().get(fileId=file_id, fields="parents").execute()
    prev_parents = ",".join(meta.get("parents", []))

    result = (
        drive.files()
        .update(
            fileId=file_id,
            addParents=dest_id,
            removeParents=prev_parents,
            fields="id, name, parents, webViewLink",
        )
        .execute()
    )
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# COPY
# ---------------------------------------------------------------------------
def cmd_copy(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)

    body = {}
    if args.name:
        body["name"] = args.name
    if args.folder:
        body["parents"] = [_extract_id(args.folder)]

    result = (
        drive.files()
        .copy(fileId=file_id, body=body, fields="id, name, mimeType, webViewLink")
        .execute()
    )
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# RENAME
# ---------------------------------------------------------------------------
def cmd_rename(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)
    result = (
        drive.files()
        .update(fileId=file_id, body={"name": args.new_name}, fields="id, name, webViewLink")
        .execute()
    )
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# TRASH / RESTORE
# ---------------------------------------------------------------------------
def cmd_trash(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)
    result = (
        drive.files()
        .update(fileId=file_id, body={"trashed": True}, fields="id, name, trashed")
        .execute()
    )
    print(json.dumps(result, indent=2))


def cmd_restore(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)
    result = (
        drive.files()
        .update(fileId=file_id, body={"trashed": False}, fields="id, name, trashed")
        .execute()
    )
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# SHARE
# ---------------------------------------------------------------------------
def cmd_share(args):
    drive = get_service()
    file_id = _extract_id(args.file_id)

    permission = {"type": "user", "role": args.role, "emailAddress": args.email}
    result = (
        drive.permissions()
        .create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=not args.no_notify,
            fields="id, role, emailAddress",
        )
        .execute()
    )
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Google Drive CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List files in a folder")
    p.add_argument("--folder", help="Folder ID or URL (default: root)")
    p.add_argument("--type", choices=["file", "folder"], help="Filter by type")
    p.add_argument("--sort", default="modifiedTime desc", help="Sort order")
    p.add_argument("--limit", type=int, default=50, help="Max results")
    p.set_defaults(func=cmd_list)

    # search
    p = sub.add_parser("search", help="Search files by name")
    p.add_argument("query", help="Search term (partial name match)")
    p.add_argument("--folder", help="Restrict to folder ID or URL")
    p.add_argument("--type", choices=["file", "folder"], help="Filter by type")
    p.add_argument("--mime-type", help="Filter by MIME type")
    p.add_argument("--limit", type=int, default=20, help="Max results")
    p.set_defaults(func=cmd_search)

    # info
    p = sub.add_parser("info", help="Get file/folder metadata")
    p.add_argument("file_id", help="File ID or URL")
    p.set_defaults(func=cmd_info)

    # create-folder
    p = sub.add_parser("create-folder", help="Create a new folder")
    p.add_argument("name", help="Folder name")
    p.add_argument("--parent", help="Parent folder ID or URL")
    p.set_defaults(func=cmd_create_folder)

    # upload
    p = sub.add_parser("upload", help="Upload a local file to Drive")
    p.add_argument("local_path", help="Path to the local file")
    p.add_argument("--folder", help="Destination folder ID or URL")
    p.add_argument("--name", help="Override the filename in Drive")
    p.add_argument("--mime-type", help="Override MIME type detection")
    p.set_defaults(func=cmd_upload)

    # download
    p = sub.add_parser("download", help="Download a file from Drive")
    p.add_argument("file_id", help="File ID or URL")
    p.add_argument("--output-dir", default=".", help="Local directory to save to")
    p.add_argument("--name", help="Override the filename locally")
    p.add_argument("--export-mime", help="Export MIME for Google Workspace files")
    p.set_defaults(func=cmd_download)

    # move
    p = sub.add_parser("move", help="Move a file to another folder")
    p.add_argument("file_id", help="File ID or URL")
    p.add_argument("destination", help="Destination folder ID or URL")
    p.set_defaults(func=cmd_move)

    # copy
    p = sub.add_parser("copy", help="Copy a file")
    p.add_argument("file_id", help="File ID or URL")
    p.add_argument("--name", help="Name for the copy")
    p.add_argument("--folder", help="Destination folder ID or URL")
    p.set_defaults(func=cmd_copy)

    # rename
    p = sub.add_parser("rename", help="Rename a file or folder")
    p.add_argument("file_id", help="File ID or URL")
    p.add_argument("new_name", help="New name")
    p.set_defaults(func=cmd_rename)

    # trash
    p = sub.add_parser("trash", help="Move a file to trash")
    p.add_argument("file_id", help="File ID or URL")
    p.set_defaults(func=cmd_trash)

    # restore
    p = sub.add_parser("restore", help="Restore a file from trash")
    p.add_argument("file_id", help="File ID or URL")
    p.set_defaults(func=cmd_restore)

    # share
    p = sub.add_parser("share", help="Share a file with someone")
    p.add_argument("file_id", help="File ID or URL")
    p.add_argument("--email", required=True, help="Email address")
    p.add_argument("--role", default="reader", choices=["reader", "commenter", "writer"], help="Permission role")
    p.add_argument("--no-notify", action="store_true", help="Skip email notification")
    p.set_defaults(func=cmd_share)

    args = parser.parse_args()
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
