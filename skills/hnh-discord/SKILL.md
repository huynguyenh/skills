---
name: hnh-discord
description: >
  Interact with Discord — read messages, send messages, search, react, pin, manage threads,
  and browse channels and members via the Discord Bot API.
  Use this skill whenever the user mentions Discord, says "in Discord", "on Discord",
  "post to Discord", "check Discord", shares a Discord channel/message link, or wants to
  read/send/search messages in a Discord server. Also trigger when the user mentions
  "server", "channel", or "thread" in a context that implies Discord. This skill is for
  any Discord server the bot has been invited to.
---

# Discord Skill

Interact with Discord through a Python CLI tool wrapping the Discord REST API (v10).

## Prerequisites

- **Python `requests` library** (already installed)
- **DISCORD_BOT_TOKEN** in `~/.zshrc`

The bot must be invited to the server with appropriate permissions. If a 403 Forbidden error occurs, the bot likely lacks permissions in that channel/server.

### Bot Setup (one-time)

1. Go to https://discord.com/developers/applications → "New Application"
2. Go to **Bot** tab → copy the **Bot Token** → add to `~/.zshrc` as `DISCORD_BOT_TOKEN`
3. Enable **Message Content Intent** under Bot → Privileged Gateway Intents
4. Go to **OAuth2 → URL Generator** → scopes: `bot` → permissions: `Read Messages/View Channels`, `Send Messages`, `Read Message History`, `Add Reactions`, `Manage Messages`, `Create Public Threads`
5. Use the generated URL to invite the bot to the server

## Auth Pattern

Following the credential rules, read the token from `~/.zshrc` and inline it:

```bash
# Read token, then use it inline
DISCORD_TOKEN="<value from ~/.zshrc>"
python3 ~/.claude/skills/hnh-discord/scripts/discord.py --token "$DISCORD_TOKEN" <command> [args]
```

## The CLI Tool

```
python3 ~/.claude/skills/hnh-discord/scripts/discord.py --token TOKEN <command> [args]
```

All commands output JSON to stdout, errors to stderr. Rate limits are handled automatically (retry after backoff).

## Commands Reference

### guilds — List servers the bot is in

```bash
python3 <script> --token $TOKEN guilds
```

Returns: list of servers with id, name, owner status.

### channels — List channels in a guild

```bash
python3 <script> --token $TOKEN channels GUILD_ID
python3 <script> --token $TOKEN channels GUILD_ID --type text
```

Returns: channels sorted by category → position. Filter with `--type` (text, voice, category, forum, announcement).

### read — Read messages from a channel

```bash
# Latest 50 messages
python3 <script> --token $TOKEN read CHANNEL_ID

# Last 20 messages
python3 <script> --token $TOKEN read CHANNEL_ID --limit 20

# Messages before/after a specific message
python3 <script> --token $TOKEN read CHANNEL_ID --before MESSAGE_ID
python3 <script> --token $TOKEN read CHANNEL_ID --after MESSAGE_ID
```

Returns: messages in chronological order with author, content, attachments, embeds, reactions, thread info, and reply references.

### send — Send a message

```bash
# Simple message
python3 <script> --token $TOKEN send CHANNEL_ID --content "Hello from Claude!"

# Reply to a message
python3 <script> --token $TOKEN send CHANNEL_ID --content "Great point!" --reply-to MESSAGE_ID
```

### edit — Edit a bot message

```bash
python3 <script> --token $TOKEN edit CHANNEL_ID MESSAGE_ID --content "Updated message"
```

Only works on messages sent by the bot.

### delete — Delete a message

```bash
python3 <script> --token $TOKEN delete CHANNEL_ID MESSAGE_ID
```

Can delete the bot's own messages or others' messages if the bot has Manage Messages permission.

### react — Add a reaction

```bash
# Unicode emoji
python3 <script> --token $TOKEN react CHANNEL_ID MESSAGE_ID --emoji "👍"

# Custom emoji (name:id format)
python3 <script> --token $TOKEN react CHANNEL_ID MESSAGE_ID --emoji "custom_emoji:123456789"
```

### pin / unpin — Pin or unpin a message

```bash
python3 <script> --token $TOKEN pin CHANNEL_ID MESSAGE_ID
python3 <script> --token $TOKEN unpin CHANNEL_ID MESSAGE_ID
```

### pins — Get pinned messages

```bash
python3 <script> --token $TOKEN pins CHANNEL_ID
```

### thread — Create a thread

```bash
# Thread from a message
python3 <script> --token $TOKEN thread CHANNEL_ID --name "Discussion" --message-id MESSAGE_ID

# New thread in a channel
python3 <script> --token $TOKEN thread CHANNEL_ID --name "New Topic" --content "Let's discuss this"
```

`--archive-duration`: auto-archive after 60, 1440 (1 day, default), 4320 (3 days), or 10080 (7 days) minutes.

### search — Search messages in a guild

```bash
# Search all channels
python3 <script> --token $TOKEN search GUILD_ID "deployment issue"

# Search in a specific channel
python3 <script> --token $TOKEN search GUILD_ID "bug report" --channel-id CHANNEL_ID

# Search by author
python3 <script> --token $TOKEN search GUILD_ID "fix" --author-id USER_ID

# Pagination
python3 <script> --token $TOKEN search GUILD_ID "error" --offset 25
```

Returns: matching messages with total count. Max 25 results per call, use `--offset` for pagination.

### members — List guild members

```bash
python3 <script> --token $TOKEN members GUILD_ID
python3 <script> --token $TOKEN members GUILD_ID --limit 50
```

Returns: members with id, username, display name, roles, join date. Use `--after USER_ID` for pagination.

### channel-info — Get channel details

```bash
python3 <script> --token $TOKEN channel-info CHANNEL_ID
```

Returns: channel name, type, topic, slowmode, last message ID.

## Workflow Patterns

### Reading recent channel activity

1. Run `guilds` to find the server
2. Run `channels GUILD_ID --type text` to list text channels
3. Run `read CHANNEL_ID` to get recent messages

### Sending a message

1. Know the channel ID (from `channels` or a previous read)
2. Run `send CHANNEL_ID --content "your message"`

### Searching for something

1. Run `guilds` to get the guild ID
2. Run `search GUILD_ID "search terms"` — optionally filter by channel or author

### Monitoring a conversation

1. Run `read CHANNEL_ID --limit 20` for recent context
2. Use `--after LAST_MESSAGE_ID` to get only new messages since last check

## Error Handling

- **401 Unauthorized**: Token is invalid or expired — check `~/.zshrc`
- **403 Forbidden**: Bot lacks permissions in this channel/server — check bot role permissions
- **404 Not Found**: Channel/message/guild doesn't exist or bot can't see it
- **429 Rate Limited**: Handled automatically (retries after backoff)
- **50001 Missing Access**: Bot hasn't been invited to the server or channel is restricted
