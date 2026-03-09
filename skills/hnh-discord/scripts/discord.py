#!/usr/bin/env python3
"""
Discord API CLI — read messages, send messages, manage channels, search, react.

Auth: reads DISCORD_BOT_TOKEN from environment or accepts --token flag.
The skill reads the token from ~/.zshrc and inlines it via --token.
"""

import argparse
import json
import sys
import os
import warnings
import time

warnings.filterwarnings("ignore")

import requests

BASE_URL = "https://discord.com/api/v10"


def get_headers(token):
    return {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }


def api_request(method, path, token, data=None, params=None):
    """Make an API request, handle errors and rate limits."""
    url = f"{BASE_URL}/{path}"
    headers = get_headers(token)
    resp = requests.request(method, url, headers=headers, json=data, params=params)

    # Handle rate limiting
    if resp.status_code == 429:
        retry_after = resp.json().get("retry_after", 1)
        time.sleep(retry_after)
        resp = requests.request(method, url, headers=headers, json=data, params=params)

    if resp.status_code >= 400:
        err = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"message": resp.text}
        print(json.dumps({"error": err, "status": resp.status_code}), file=sys.stderr)
        sys.exit(1)

    if resp.status_code == 204:
        return {}
    return resp.json()


def format_message(msg):
    """Format a Discord message for readable output."""
    author = msg.get("author", {})
    result = {
        "id": msg["id"],
        "author": author.get("global_name") or author.get("username", "Unknown"),
        "author_id": author.get("id"),
        "content": msg.get("content", ""),
        "timestamp": msg.get("timestamp"),
        "edited_timestamp": msg.get("edited_timestamp"),
    }

    # Attachments
    attachments = msg.get("attachments", [])
    if attachments:
        result["attachments"] = [
            {"filename": a["filename"], "url": a["url"], "size": a.get("size")}
            for a in attachments
        ]

    # Embeds
    embeds = msg.get("embeds", [])
    if embeds:
        result["embeds"] = [
            {k: e.get(k) for k in ("title", "description", "url", "type") if e.get(k)}
            for e in embeds
        ]

    # Reactions
    reactions = msg.get("reactions", [])
    if reactions:
        result["reactions"] = [
            {"emoji": r["emoji"].get("name", ""), "count": r["count"]}
            for r in reactions
        ]

    # Thread info
    thread = msg.get("thread")
    if thread:
        result["thread"] = {"id": thread["id"], "name": thread.get("name")}

    # Reply reference
    ref = msg.get("message_reference")
    if ref:
        result["reply_to"] = ref.get("message_id")

    # Pinned
    if msg.get("pinned"):
        result["pinned"] = True

    return result


def format_channel(ch):
    """Format a Discord channel for readable output."""
    type_map = {
        0: "text", 1: "dm", 2: "voice", 4: "category",
        5: "announcement", 10: "announcement_thread",
        11: "public_thread", 12: "private_thread",
        13: "stage", 15: "forum", 16: "media",
    }
    result = {
        "id": ch["id"],
        "name": ch.get("name", ""),
        "type": type_map.get(ch.get("type", 0), f"unknown({ch.get('type')})"),
    }
    if ch.get("topic"):
        result["topic"] = ch["topic"]
    if ch.get("parent_id"):
        result["parent_id"] = ch["parent_id"]
    if ch.get("position") is not None:
        result["position"] = ch["position"]
    return result


# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_guilds(args):
    """List servers the bot is in."""
    token = args.token
    result = api_request("GET", "users/@me/guilds", token)

    guilds = []
    for g in result:
        guilds.append({
            "id": g["id"],
            "name": g["name"],
            "icon": g.get("icon"),
            "owner": g.get("owner", False),
        })

    print(json.dumps({"count": len(guilds), "guilds": guilds}, ensure_ascii=False))


def cmd_channels(args):
    """List channels in a guild."""
    token = args.token
    guild_id = args.guild_id

    result = api_request("GET", f"guilds/{guild_id}/channels", token)

    channels = [format_channel(ch) for ch in result]

    # Sort: categories first, then by position
    channels.sort(key=lambda c: (0 if c["type"] == "category" else 1, c.get("position", 999)))

    # Optionally filter by type
    if args.type:
        channels = [c for c in channels if c["type"] == args.type]

    print(json.dumps({"count": len(channels), "channels": channels}, ensure_ascii=False))


def cmd_read(args):
    """Read messages from a channel."""
    token = args.token
    channel_id = args.channel_id
    limit = min(args.limit, 100)

    params = {"limit": limit}
    if args.before:
        params["before"] = args.before
    if args.after:
        params["after"] = args.after
    if args.around:
        params["around"] = args.around

    result = api_request("GET", f"channels/{channel_id}/messages", token, params=params)

    messages = [format_message(msg) for msg in result]

    # API returns newest first; reverse for chronological order
    messages.reverse()

    print(json.dumps({"count": len(messages), "messages": messages}, ensure_ascii=False))


def cmd_send(args):
    """Send a message to a channel."""
    token = args.token
    channel_id = args.channel_id

    body = {}
    if args.content:
        body["content"] = args.content
    if args.reply_to:
        body["message_reference"] = {"message_id": args.reply_to}

    if not body.get("content"):
        print(json.dumps({"error": "Provide --content"}), file=sys.stderr)
        sys.exit(1)

    result = api_request("POST", f"channels/{channel_id}/messages", token, data=body)

    print(json.dumps({
        "id": result["id"],
        "channel_id": channel_id,
        "content": result.get("content", ""),
        "sent": True,
    }, ensure_ascii=False))


def cmd_edit(args):
    """Edit a bot message."""
    token = args.token
    channel_id = args.channel_id
    message_id = args.message_id

    body = {"content": args.content}
    result = api_request("PATCH", f"channels/{channel_id}/messages/{message_id}", token, data=body)

    print(json.dumps({
        "id": result["id"],
        "content": result.get("content", ""),
        "edited": True,
    }, ensure_ascii=False))


def cmd_delete(args):
    """Delete a message."""
    token = args.token
    channel_id = args.channel_id
    message_id = args.message_id

    api_request("DELETE", f"channels/{channel_id}/messages/{message_id}", token)

    print(json.dumps({"id": message_id, "deleted": True}))


def cmd_react(args):
    """Add a reaction to a message."""
    token = args.token
    channel_id = args.channel_id
    message_id = args.message_id
    emoji = args.emoji

    # URL-encode the emoji for the path
    import urllib.parse
    encoded = urllib.parse.quote(emoji)

    api_request("PUT", f"channels/{channel_id}/messages/{message_id}/reactions/{encoded}/@me", token)

    print(json.dumps({"message_id": message_id, "emoji": emoji, "reacted": True}))


def cmd_pin(args):
    """Pin a message."""
    token = args.token
    channel_id = args.channel_id
    message_id = args.message_id

    api_request("PUT", f"channels/{channel_id}/pins/{message_id}", token)

    print(json.dumps({"message_id": message_id, "pinned": True}))


def cmd_unpin(args):
    """Unpin a message."""
    token = args.token
    channel_id = args.channel_id
    message_id = args.message_id

    api_request("DELETE", f"channels/{channel_id}/pins/{message_id}", token)

    print(json.dumps({"message_id": message_id, "unpinned": True}))


def cmd_pins(args):
    """Get pinned messages in a channel."""
    token = args.token
    channel_id = args.channel_id

    result = api_request("GET", f"channels/{channel_id}/pins", token)

    messages = [format_message(msg) for msg in result]

    print(json.dumps({"count": len(messages), "messages": messages}, ensure_ascii=False))


def cmd_thread(args):
    """Create a thread from a message or in a channel."""
    token = args.token
    channel_id = args.channel_id

    body = {
        "name": args.name,
        "auto_archive_duration": args.archive_duration,
    }

    if args.message_id:
        # Thread from a specific message
        result = api_request(
            "POST",
            f"channels/{channel_id}/messages/{args.message_id}/threads",
            token,
            data=body,
        )
    else:
        # Thread without a message (forum/text channel)
        body["type"] = 11  # PUBLIC_THREAD
        if args.content:
            body["message"] = {"content": args.content}
        result = api_request("POST", f"channels/{channel_id}/threads", token, data=body)

    print(json.dumps({
        "id": result["id"],
        "name": result.get("name"),
        "type": "thread",
        "created": True,
    }, ensure_ascii=False))


def cmd_search(args):
    """Search messages in a guild."""
    token = args.token
    guild_id = args.guild_id

    params = {"content": args.query}
    if args.channel_id:
        params["channel_id"] = args.channel_id
    if args.author_id:
        params["author_id"] = args.author_id
    if args.limit:
        params["limit"] = min(args.limit, 25)
    if args.offset:
        params["offset"] = args.offset

    result = api_request("GET", f"guilds/{guild_id}/messages/search", token, params=params)

    total = result.get("total_results", 0)
    messages = []
    for group in result.get("messages", []):
        for msg in group:
            if msg.get("hit"):
                messages.append(format_message(msg))

    print(json.dumps({
        "total_results": total,
        "count": len(messages),
        "messages": messages,
    }, ensure_ascii=False))


def cmd_members(args):
    """List members of a guild."""
    token = args.token
    guild_id = args.guild_id

    params = {"limit": min(args.limit, 1000)}
    if args.after:
        params["after"] = args.after

    result = api_request("GET", f"guilds/{guild_id}/members", token, params=params)

    members = []
    for m in result:
        user = m.get("user", {})
        members.append({
            "id": user.get("id"),
            "username": user.get("username"),
            "display_name": m.get("nick") or user.get("global_name") or user.get("username"),
            "roles": m.get("roles", []),
            "joined_at": m.get("joined_at"),
        })

    print(json.dumps({"count": len(members), "members": members}, ensure_ascii=False))


def cmd_channel_info(args):
    """Get detailed channel information."""
    token = args.token
    channel_id = args.channel_id

    result = api_request("GET", f"channels/{channel_id}", token)

    info = format_channel(result)
    # Add extra details
    if result.get("last_message_id"):
        info["last_message_id"] = result["last_message_id"]
    if result.get("rate_limit_per_user"):
        info["slowmode_seconds"] = result["rate_limit_per_user"]
    if result.get("nsfw") is not None:
        info["nsfw"] = result["nsfw"]

    print(json.dumps(info, ensure_ascii=False))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Discord API CLI")
    parser.add_argument("--token", help="Discord Bot token (overrides env)", default=os.environ.get("DISCORD_BOT_TOKEN"))
    sub = parser.add_subparsers(dest="command", required=True)

    # guilds
    p = sub.add_parser("guilds", help="List servers the bot is in")
    p.set_defaults(func=cmd_guilds)

    # channels
    p = sub.add_parser("channels", help="List channels in a guild")
    p.add_argument("guild_id", help="Guild/server ID")
    p.add_argument("--type", help="Filter by type: text, voice, category, forum, etc.")
    p.set_defaults(func=cmd_channels)

    # read
    p = sub.add_parser("read", help="Read messages from a channel")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("--limit", type=int, default=50, help="Number of messages (max 100, default 50)")
    p.add_argument("--before", help="Get messages before this message ID")
    p.add_argument("--after", help="Get messages after this message ID")
    p.add_argument("--around", help="Get messages around this message ID")
    p.set_defaults(func=cmd_read)

    # send
    p = sub.add_parser("send", help="Send a message to a channel")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("--content", required=True, help="Message content")
    p.add_argument("--reply-to", help="Message ID to reply to")
    p.set_defaults(func=cmd_send)

    # edit
    p = sub.add_parser("edit", help="Edit a bot message")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("message_id", help="Message ID to edit")
    p.add_argument("--content", required=True, help="New message content")
    p.set_defaults(func=cmd_edit)

    # delete
    p = sub.add_parser("delete", help="Delete a message")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("message_id", help="Message ID to delete")
    p.set_defaults(func=cmd_delete)

    # react
    p = sub.add_parser("react", help="Add a reaction to a message")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("message_id", help="Message ID")
    p.add_argument("--emoji", required=True, help="Emoji to react with (unicode or name:id for custom)")
    p.set_defaults(func=cmd_react)

    # pin
    p = sub.add_parser("pin", help="Pin a message")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("message_id", help="Message ID to pin")
    p.set_defaults(func=cmd_pin)

    # unpin
    p = sub.add_parser("unpin", help="Unpin a message")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("message_id", help="Message ID to unpin")
    p.set_defaults(func=cmd_unpin)

    # pins
    p = sub.add_parser("pins", help="Get pinned messages in a channel")
    p.add_argument("channel_id", help="Channel ID")
    p.set_defaults(func=cmd_pins)

    # thread
    p = sub.add_parser("thread", help="Create a thread")
    p.add_argument("channel_id", help="Channel ID")
    p.add_argument("--name", required=True, help="Thread name")
    p.add_argument("--message-id", help="Create thread from this message")
    p.add_argument("--content", help="Initial message content (for threads without a source message)")
    p.add_argument("--archive-duration", type=int, default=1440, choices=[60, 1440, 4320, 10080],
                   help="Auto-archive after N minutes (60, 1440, 4320, 10080)")
    p.set_defaults(func=cmd_thread)

    # search
    p = sub.add_parser("search", help="Search messages in a guild")
    p.add_argument("guild_id", help="Guild/server ID")
    p.add_argument("query", help="Search query")
    p.add_argument("--channel-id", help="Filter to specific channel")
    p.add_argument("--author-id", help="Filter to specific author")
    p.add_argument("--limit", type=int, default=25, help="Max results (max 25)")
    p.add_argument("--offset", type=int, help="Offset for pagination")
    p.set_defaults(func=cmd_search)

    # members
    p = sub.add_parser("members", help="List guild members")
    p.add_argument("guild_id", help="Guild/server ID")
    p.add_argument("--limit", type=int, default=100, help="Max results (max 1000)")
    p.add_argument("--after", help="Get members after this user ID (pagination)")
    p.set_defaults(func=cmd_members)

    # channel-info
    p = sub.add_parser("channel-info", help="Get detailed channel information")
    p.add_argument("channel_id", help="Channel ID")
    p.set_defaults(func=cmd_channel_info)

    args = parser.parse_args()

    if not args.token:
        print(json.dumps({"error": "No token. Set DISCORD_BOT_TOKEN or use --token"}), file=sys.stderr)
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
