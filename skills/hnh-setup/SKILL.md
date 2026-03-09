---
name: hnh-setup
description: Set up or update the user's Claude workspace on any machine. Use this skill whenever the user mentions setting up a new laptop, bootstrapping their dev environment, syncing skills/plans/rules from GitHub, restoring their Claude config on a fresh device, or says "hnh-setup". Handles first-time directory creation with basic rules AND subsequent updates/syncs from the backup repo.
---

# hnh-setup

Bootstrap or update a Claude workspace on any machine. The user works across multiple laptops (company + personal), and this skill ensures every device gets the same skills, plans, rules, and directory structure — adapted to the local username.

## Source of truth

- **Backup repo:** `https://github.com/huynguyenh/skills`
- **GitHub account:** `huynguyenh` (the user may have other GitHub accounts on the device — always use this one)
- **Git identity:** `user.name "huynguyenh"`, `user.email "hoanghuy2908@gmail.com"`

## Repo structure

```
CLAUDE.md              # global index (with hnh placeholders)
skills/                # custom Claude skills
  hnh-setup/
  hnh-backup/
  hnh-*/
plans/                 # work plans by ticket
  {TICKET}/
    {YYYY-MM-DD-description}.md
memory/
  MEMORY.md            # memory index
rules/                 # global rules only (global-*.md)
  global-credentials.md
  global-claude.md
  global-github.md
config/                # portable config files
  statusline-command.sh  # status line display script
```

## Step 1: Detect environment

```bash
USERNAME=$(whoami)
```

This username replaces all `hnh` placeholders in restored files. The key path pattern is `/Users/hnh/` — every machine will have a different username but the same directory layout underneath.

## Step 2: Determine first-time vs update

Check whether `~/.claude/` exists and has content:
- If `~/.claude/` barely exists or has no custom skills → **first-time setup**
- Otherwise → **update mode**

## Step 3: First-time setup

Create the workspace and Claude config directories:

```bash
# Workspace roots
mkdir -p ~/ws/code
mkdir -p ~/ws/docs

# Claude directories
mkdir -p ~/.claude/plans
mkdir -p ~/.claude/memory
mkdir -p ~/.claude/rules
```

### Create CLAUDE.md

Create `~/.claude/CLAUDE.md` if it doesn't exist — a global index pointing to the memory and rules system:

```markdown
# Global Index

**IMPORTANT: ALWAYS read the memory files below BEFORE answering questions or starting work.**

**Base path:** `~/.claude/memory/`

| File | What's inside |
|---|---|
| `MEMORY.md` | User preferences, custom skills, top-level index |
| `rules.md` | Strict rules for git, PRs, code style, workflow |

Rules: `~/.claude/rules/`
Plans for Jira tickets: `~/.claude/plans/{TICKET}/`
```

### Create MEMORY.md

Create `~/.claude/memory/MEMORY.md` if it doesn't exist — an empty starting point for the second brain:

```markdown
# Memory Index

This is the top-level index for persistent memory. Add observations, preferences, and learnings here.

## Local Code Path
- All repos stored under `/Users/hnh/ws/code/`
- Documents stored under `/Users/hnh/ws/docs/`

## Custom Skills
- `/hnh-setup` — Bootstrap or update this workspace
- `/hnh-backup` — Back up skills, plans, rules to GitHub
```

### Create basic rules

Create `~/.claude/rules/workspace.md` — foundational rules about where things live. These apply regardless of which machine or project the user is on:

```markdown
# Workspace Rules

## Directory Structure
- **Code:** All repositories and coding projects go under `~/ws/code/`
  - GitHub repos follow the pattern: `~/ws/code/github.com/{org}/{repo}/`
- **Documents:** All project documents, notes, and references go under `~/ws/docs/`
- **Claude config:** `~/.claude/` — never modify this structure manually without updating the backup

## Claude Directory Layout
- `~/.claude/CLAUDE.md` — Global index, always loaded into context
- `~/.claude/memory/MEMORY.md` — Persistent observations and preferences (second brain)
- `~/.claude/memory/*.md` — Topic-specific memory files
- `~/.claude/plans/{TICKET}/*.md` — Implementation plans organized by ticket
- `~/.claude/rules/*.md` — Personal discipline rules (this file and others)
- `~/.claude/skills/` — Installed skills (custom + marketplace)

## Backup Discipline
- Back up regularly using `/hnh-backup`
- The backup repo is `github.com/huynguyenh/skills`
- Only custom skills, plans, rules, MEMORY.md, and CLAUDE.md get backed up
- Credentials and device-specific files stay local
```

Report what directories and files were created so the user knows the state of their machine.

## Step 4: Clone or pull the backup repo

The local clone lives at `~/ws/code/github.com/huynguyenh/skills` (following the user's convention of `~/ws/code/{host}/{org}/{repo}`).

```bash
# First time
mkdir -p ~/ws/code/github.com/huynguyenh
gh repo clone huynguyenh/skills ~/ws/code/github.com/huynguyenh/skills

# Already cloned
cd ~/ws/code/github.com/huynguyenh/skills && git pull
```

If `gh` isn't authenticated for huynguyenh, ask the user to run `gh auth login` and select the huynguyenh account before continuing.

## Step 5: Restore from backup

Copy from the repo into the Claude directories:

```bash
REPO=~/ws/code/github.com/huynguyenh/skills

# CLAUDE.md
cp "$REPO/CLAUDE.md" ~/.claude/CLAUDE.md

# Skills — copy each custom skill
cp -r "$REPO/skills/"* ~/.claude/skills/ 2>/dev/null || true

# Plans — preserve ticket subdirectory structure
cp -r "$REPO/plans/"* ~/.claude/plans/ 2>/dev/null || true

# Memory index
cp "$REPO/memory/MEMORY.md" ~/.claude/memory/MEMORY.md 2>/dev/null || true

# Global rules (only global-* files from backup — local rules like workspace.md are created separately)
cp "$REPO/rules/"global-*.md ~/.claude/rules/ 2>/dev/null || true

# Status line script
cp "$REPO/config/statusline-command.sh" ~/.claude/statusline-command.sh 2>/dev/null || true
```

Be careful not to overwrite marketplace skills that are already installed. The repo only contains custom skills, so there shouldn't be conflicts — but check before clobbering.

### Configure status line

If `~/.claude/statusline-command.sh` was restored, add the status line config to `settings.json`. Read `~/.claude/settings.json` (create it if it doesn't exist), and ensure it has:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  }
}
```

Use `~/.claude/statusline-command.sh` (not an absolute path with the username) so it's portable. If `settings.json` already has other keys (permissions, etc.), merge — don't overwrite.

## Step 6: Desanitize paths

The backup repo stores paths with `hnh` as a placeholder. Replace them with the actual local username across all restored files.

Find all text files and replace:
- `/Users/hnh/` → `/Users/$USERNAME/`

Use `grep -rl 'hnh'` to find files that need updating, then `sed -i '' "s|hnh|$USERNAME|g"` on each. Apply to:
- `~/.claude/CLAUDE.md`
- `~/.claude/skills/hnh-*` (custom skills)
- `~/.claude/plans/`
- `~/.claude/memory/MEMORY.md`
- `~/.claude/rules/`

Leave marketplace skills untouched.

## Step 7: Update mode

If this isn't a first-time setup:

1. Pull latest from the backup repo
2. Compare local files with repo versions
3. If local files have been modified since last sync, ask the user before overwriting — they may have local changes worth keeping
4. Copy new/changed files from repo
5. Re-run desanitization
6. Report what changed (new skills, updated plans, new rules, etc.)

## Step 8: Report

Summarize what happened:
- Directories created (if first-time)
- Files restored: CLAUDE.md, MEMORY.md, rules
- Skills restored/updated (list them)
- Plans restored/updated (list them)
- Path placeholders replaced
- Any issues encountered
