#!/usr/bin/env python3
"""
Notion API CLI — read, create, update, search pages and databases.

Auth: reads NOTION_API_TOKEN from environment or accepts --token flag.
The skill reads the token from ~/.zshrc and inlines it via --token.
"""

import argparse
import json
import sys
import os
import warnings
import re

warnings.filterwarnings("ignore")

import requests

BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def api_request(method, path, token, data=None, params=None):
    """Make an API request, handle errors consistently."""
    url = f"{BASE_URL}/{path}"
    headers = get_headers(token)
    resp = requests.request(method, url, headers=headers, json=data, params=params)
    if resp.status_code >= 400:
        err = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"message": resp.text}
        print(json.dumps({"error": err, "status": resp.status_code}), file=sys.stderr)
        sys.exit(1)
    return resp.json()


def extract_id(id_or_url):
    """Extract a Notion ID from a URL or raw ID string."""
    if not id_or_url:
        return id_or_url
    # Match UUID-like patterns (with or without dashes)
    m = re.search(r"([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", id_or_url)
    if m:
        raw = m.group(1).replace("-", "")
        # Format as UUID
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    return id_or_url


# ---------------------------------------------------------------------------
# Block helpers
# ---------------------------------------------------------------------------
def blocks_to_text(blocks, indent=0):
    """Convert Notion blocks to readable text."""
    lines = []
    prefix = "  " * indent
    for block in blocks:
        btype = block.get("type", "")
        data = block.get(btype, {})
        rich_text = data.get("rich_text", [])
        text = "".join([t.get("plain_text", "") for t in rich_text])

        if btype == "paragraph":
            lines.append(f"{prefix}{text}")
        elif btype.startswith("heading_"):
            level = btype[-1]
            lines.append(f"{prefix}{'#' * int(level)} {text}")
        elif btype == "bulleted_list_item":
            lines.append(f"{prefix}- {text}")
        elif btype == "numbered_list_item":
            lines.append(f"{prefix}1. {text}")
        elif btype == "to_do":
            checked = "x" if data.get("checked") else " "
            lines.append(f"{prefix}[{checked}] {text}")
        elif btype == "toggle":
            lines.append(f"{prefix}▸ {text}")
        elif btype == "code":
            lang = data.get("language", "")
            lines.append(f"{prefix}```{lang}")
            lines.append(f"{prefix}{text}")
            lines.append(f"{prefix}```")
        elif btype == "quote":
            lines.append(f"{prefix}> {text}")
        elif btype == "callout":
            icon = data.get("icon", {}).get("emoji", "")
            lines.append(f"{prefix}{icon} {text}")
        elif btype == "divider":
            lines.append(f"{prefix}---")
        elif btype == "table_row":
            cells = data.get("cells", [])
            row = " | ".join(["".join([t.get("plain_text", "") for t in cell]) for cell in cells])
            lines.append(f"{prefix}| {row} |")
        elif btype == "child_page":
            lines.append(f"{prefix}📄 [Child page: {data.get('title', '')}]")
        elif btype == "child_database":
            lines.append(f"{prefix}🗃️ [Child database: {data.get('title', '')}]")
        elif btype == "image":
            img = data.get("file", data.get("external", {}))
            lines.append(f"{prefix}[Image: {img.get('url', '')}]")
        elif btype == "bookmark":
            lines.append(f"{prefix}[Bookmark: {data.get('url', '')}]")
        elif btype == "link_preview":
            lines.append(f"{prefix}[Link: {data.get('url', '')}]")
        else:
            if text:
                lines.append(f"{prefix}[{btype}] {text}")
            else:
                lines.append(f"{prefix}[{btype}]")

    return "\n".join(lines)


def text_to_blocks(text):
    """Convert plain text/markdown to Notion block objects.
    Supports: paragraphs, headings (#/##/###), bullets (-), numbered (1.),
    to-dos ([ ]/[x]), quotes (>), dividers (---), code blocks (```).
    """
    blocks = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)}}],
                    "language": lang,
                },
            })
            i += 1
            continue

        # Divider
        if line.strip() == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # Headings
        if line.startswith("### "):
            blocks.append({
                "object": "block", "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]},
            })
            i += 1
            continue
        if line.startswith("## "):
            blocks.append({
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]},
            })
            i += 1
            continue
        if line.startswith("# "):
            blocks.append({
                "object": "block", "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]},
            })
            i += 1
            continue

        # Bullet
        if line.startswith("- "):
            blocks.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]},
            })
            i += 1
            continue

        # Numbered
        m = re.match(r"^\d+\.\s+(.+)$", line)
        if m:
            blocks.append({
                "object": "block", "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": m.group(1)}}]},
            })
            i += 1
            continue

        # To-do
        m = re.match(r"^\[([ x])\]\s+(.+)$", line)
        if m:
            blocks.append({
                "object": "block", "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": m.group(2)}}],
                    "checked": m.group(1) == "x",
                },
            })
            i += 1
            continue

        # Quote
        if line.startswith("> "):
            blocks.append({
                "object": "block", "type": "quote",
                "quote": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]},
            })
            i += 1
            continue

        # Paragraph (including empty lines)
        blocks.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}] if line.strip() else []},
        })
        i += 1

    return blocks


def extract_property_value(prop):
    """Extract a readable value from a Notion property object."""
    ptype = prop.get("type", "")
    data = prop.get(ptype)

    if data is None:
        return None

    if ptype == "title":
        return "".join([t.get("plain_text", "") for t in data])
    elif ptype == "rich_text":
        return "".join([t.get("plain_text", "") for t in data])
    elif ptype in ("number", "checkbox"):
        return data
    elif ptype == "select":
        return data.get("name") if data else None
    elif ptype == "multi_select":
        return [item.get("name") for item in data]
    elif ptype == "status":
        return data.get("name") if data else None
    elif ptype == "date":
        if data:
            start = data.get("start", "")
            end = data.get("end")
            return f"{start} → {end}" if end else start
        return None
    elif ptype == "people":
        return [p.get("name", p.get("id", "")) for p in data]
    elif ptype == "email":
        return data
    elif ptype == "phone_number":
        return data
    elif ptype == "url":
        return data
    elif ptype == "relation":
        return [r.get("id") for r in data]
    elif ptype == "formula":
        ftype = data.get("type", "")
        return data.get(ftype)
    elif ptype == "rollup":
        rtype = data.get("type", "")
        return data.get(rtype)
    elif ptype == "files":
        return [f.get("name", f.get("file", {}).get("url", "")) for f in data]
    elif ptype == "created_time":
        return data
    elif ptype == "last_edited_time":
        return data
    elif ptype == "created_by":
        return data.get("name", data.get("id", ""))
    elif ptype == "last_edited_by":
        return data.get("name", data.get("id", ""))
    elif ptype == "unique_id":
        prefix = data.get("prefix", "")
        number = data.get("number", "")
        return f"{prefix}-{number}" if prefix else str(number)
    else:
        return str(data)


# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_read(args):
    """Read a page: properties + all content blocks."""
    token = args.token
    page_id = extract_id(args.page_id)

    # Get page properties
    page = api_request("GET", f"pages/{page_id}", token)

    # Get title
    title = ""
    for prop_name, prop in page.get("properties", {}).items():
        if prop.get("type") == "title":
            title = extract_property_value(prop)
            break

    # Get all blocks (with pagination)
    all_blocks = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        result = api_request("GET", f"blocks/{page_id}/children", token, params=params)
        all_blocks.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")

    # Get child blocks for any that have children
    for block in all_blocks:
        if block.get("has_children") and block["type"] not in ("child_page", "child_database"):
            child_result = api_request("GET", f"blocks/{block['id']}/children", token, params={"page_size": 100})
            block["_children"] = child_result.get("results", [])

    content = blocks_to_text(all_blocks)

    # Extract properties
    props = {}
    for prop_name, prop in page.get("properties", {}).items():
        props[prop_name] = extract_property_value(prop)

    output = {
        "id": page["id"],
        "title": title,
        "url": page.get("url"),
        "created_time": page.get("created_time"),
        "last_edited_time": page.get("last_edited_time"),
        "properties": props,
        "content": content,
    }

    if args.raw:
        output["raw_blocks"] = all_blocks

    print(json.dumps(output, ensure_ascii=False))


def cmd_create(args):
    """Create a new page under a parent page or database."""
    token = args.token
    parent_id = extract_id(args.parent_id)

    # Determine parent type
    if args.database:
        parent = {"database_id": parent_id}
    else:
        parent = {"page_id": parent_id}

    # Build properties
    properties = {}
    if args.title:
        if args.database:
            # For database pages, the title property name might vary
            title_prop = args.title_property or "Name"
            properties[title_prop] = {
                "title": [{"text": {"content": args.title}}]
            }
        else:
            properties["title"] = {
                "title": [{"text": {"content": args.title}}]
            }

    # Parse extra properties from JSON
    if args.properties:
        extra = json.loads(args.properties)
        properties.update(extra)

    body = {"parent": parent, "properties": properties}

    # Add content blocks
    if args.content:
        body["children"] = text_to_blocks(args.content)
    elif args.content_file:
        with open(args.content_file, "r") as f:
            body["children"] = text_to_blocks(f.read())

    result = api_request("POST", "pages", token, data=body)
    print(json.dumps({
        "id": result["id"],
        "url": result.get("url"),
        "title": args.title,
    }, ensure_ascii=False))


def cmd_update(args):
    """Update a page's properties."""
    token = args.token
    page_id = extract_id(args.page_id)

    body = {}
    if args.properties:
        body["properties"] = json.loads(args.properties)

    if args.archive:
        body["archived"] = True
    if args.unarchive:
        body["archived"] = False

    if not body:
        print(json.dumps({"error": "Provide --properties, --archive, or --unarchive"}), file=sys.stderr)
        sys.exit(1)

    result = api_request("PATCH", f"pages/{page_id}", token, data=body)
    print(json.dumps({
        "id": result["id"],
        "url": result.get("url"),
        "updated": True,
    }))


def cmd_append(args):
    """Append content blocks to a page."""
    token = args.token
    page_id = extract_id(args.page_id)

    if args.content:
        blocks = text_to_blocks(args.content)
    elif args.content_file:
        with open(args.content_file, "r") as f:
            blocks = text_to_blocks(f.read())
    else:
        print(json.dumps({"error": "Provide --content or --content-file"}), file=sys.stderr)
        sys.exit(1)

    result = api_request("PATCH", f"blocks/{page_id}/children", token, data={"children": blocks})
    print(json.dumps({
        "appended": len(blocks),
        "page_id": page_id,
    }))


def cmd_query(args):
    """Query a database with optional filters and sorts."""
    token = args.token
    db_id = extract_id(args.database_id)

    body = {"page_size": args.limit}

    if args.filter:
        body["filter"] = json.loads(args.filter)
    if args.sort:
        body["sorts"] = json.loads(args.sort)
    if args.cursor:
        body["start_cursor"] = args.cursor

    result = api_request("POST", f"databases/{db_id}/query", token, data=body)

    records = []
    for page in result.get("results", []):
        record = {"id": page["id"], "url": page.get("url")}
        for prop_name, prop in page.get("properties", {}).items():
            record[prop_name] = extract_property_value(prop)
        records.append(record)

    output = {
        "count": len(records),
        "has_more": result.get("has_more", False),
        "next_cursor": result.get("next_cursor"),
        "records": records,
    }
    print(json.dumps(output, ensure_ascii=False))


def cmd_create_record(args):
    """Create a new record in a database (alias for create --database)."""
    args.database = True
    args.content = None
    args.content_file = None
    args.parent_id = args.database_id
    cmd_create(args)


def cmd_update_record(args):
    """Update a database record's properties."""
    cmd_update(args)


def cmd_schema(args):
    """Get a database's property schema."""
    token = args.token
    db_id = extract_id(args.database_id)

    result = api_request("GET", f"databases/{db_id}", token)

    props = {}
    for name, prop in result.get("properties", {}).items():
        info = {"type": prop["type"], "id": prop.get("id")}

        # Include select/multi_select options
        if prop["type"] == "select":
            info["options"] = [o["name"] for o in prop.get("select", {}).get("options", [])]
        elif prop["type"] == "multi_select":
            info["options"] = [o["name"] for o in prop.get("multi_select", {}).get("options", [])]
        elif prop["type"] == "status":
            info["options"] = [o["name"] for o in prop.get("status", {}).get("options", [])]
            info["groups"] = [g["name"] for g in prop.get("status", {}).get("groups", [])]
        elif prop["type"] == "relation":
            info["database_id"] = prop.get("relation", {}).get("database_id")
        elif prop["type"] == "formula":
            info["expression"] = prop.get("formula", {}).get("expression")

        props[name] = info

    output = {
        "id": result["id"],
        "title": "".join([t.get("plain_text", "") for t in result.get("title", [])]),
        "url": result.get("url"),
        "properties": props,
    }
    print(json.dumps(output, ensure_ascii=False))


def cmd_search(args):
    """Search for pages or databases by title."""
    token = args.token

    body = {"page_size": args.limit}
    if args.query:
        body["query"] = args.query
    if args.type:
        body["filter"] = {"value": args.type, "property": "object"}
    if args.sort_direction:
        body["sort"] = {"direction": args.sort_direction, "timestamp": "last_edited_time"}

    result = api_request("POST", "search", token, data=body)

    items = []
    for obj in result.get("results", []):
        item = {
            "id": obj["id"],
            "type": obj["object"],
            "url": obj.get("url"),
            "last_edited": obj.get("last_edited_time"),
        }
        # Extract title
        if obj["object"] == "page":
            for prop_name, prop in obj.get("properties", {}).items():
                if prop.get("type") == "title":
                    item["title"] = extract_property_value(prop)
                    break
        elif obj["object"] == "database":
            item["title"] = "".join([t.get("plain_text", "") for t in obj.get("title", [])])

        items.append(item)

    print(json.dumps({"count": len(items), "results": items}, ensure_ascii=False))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Notion API CLI")
    parser.add_argument("--token", help="Notion API token (overrides env)", default=os.environ.get("NOTION_API_TOKEN"))
    sub = parser.add_subparsers(dest="command", required=True)

    # read
    p = sub.add_parser("read", help="Read a page (properties + content)")
    p.add_argument("page_id", help="Page ID or URL")
    p.add_argument("--raw", action="store_true", help="Include raw block objects")
    p.set_defaults(func=cmd_read)

    # create
    p = sub.add_parser("create", help="Create a new page")
    p.add_argument("parent_id", help="Parent page ID/URL or database ID/URL")
    p.add_argument("--title", help="Page title")
    p.add_argument("--database", action="store_true", help="Parent is a database")
    p.add_argument("--title-property", help="Name of the title property (for databases, default: Name)")
    p.add_argument("--properties", help="JSON object of additional properties")
    p.add_argument("--content", help="Text/markdown content for the page body")
    p.add_argument("--content-file", help="File containing text/markdown content")
    p.set_defaults(func=cmd_create)

    # update
    p = sub.add_parser("update", help="Update a page's properties")
    p.add_argument("page_id", help="Page ID or URL")
    p.add_argument("--properties", help="JSON object of properties to update")
    p.add_argument("--archive", action="store_true", help="Archive the page")
    p.add_argument("--unarchive", action="store_true", help="Unarchive the page")
    p.set_defaults(func=cmd_update)

    # append
    p = sub.add_parser("append", help="Append content blocks to a page")
    p.add_argument("page_id", help="Page ID or URL")
    p.add_argument("--content", help="Text/markdown to append")
    p.add_argument("--content-file", help="File containing text/markdown to append")
    p.set_defaults(func=cmd_append)

    # query
    p = sub.add_parser("query", help="Query a database")
    p.add_argument("database_id", help="Database ID or URL")
    p.add_argument("--filter", help="JSON filter object")
    p.add_argument("--sort", help="JSON sort array")
    p.add_argument("--limit", type=int, default=100, help="Max results (default: 100)")
    p.add_argument("--cursor", help="Pagination cursor")
    p.set_defaults(func=cmd_query)

    # create-record
    p = sub.add_parser("create-record", help="Create a new database record")
    p.add_argument("database_id", help="Database ID or URL")
    p.add_argument("--title", help="Title/name of the record")
    p.add_argument("--title-property", help="Name of the title property (default: Name)")
    p.add_argument("--properties", help="JSON object of properties")
    p.set_defaults(func=cmd_create_record)

    # update-record (alias for update)
    p = sub.add_parser("update-record", help="Update a database record")
    p.add_argument("page_id", help="Record/page ID or URL")
    p.add_argument("--properties", required=True, help="JSON object of properties to update")
    p.add_argument("--archive", action="store_true")
    p.add_argument("--unarchive", action="store_true")
    p.set_defaults(func=cmd_update_record)

    # schema
    p = sub.add_parser("schema", help="Get database property schema")
    p.add_argument("database_id", help="Database ID or URL")
    p.set_defaults(func=cmd_schema)

    # search
    p = sub.add_parser("search", help="Search pages and databases")
    p.add_argument("query", nargs="?", help="Search query")
    p.add_argument("--type", choices=["page", "database"], help="Filter by object type")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--sort-direction", choices=["ascending", "descending"], default="descending")
    p.set_defaults(func=cmd_search)

    args = parser.parse_args()

    if not args.token:
        print(json.dumps({"error": "No token. Set NOTION_API_TOKEN or use --token"}), file=sys.stderr)
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
