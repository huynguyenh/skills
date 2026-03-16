---
name: hnh-backup
description: Back up Claude skills, plans, rules, memory index, and global CLAUDE.md to GitHub — safely removing credentials and device-specific info. Use this skill whenever the user wants to save their Claude config, back up skills, sync to GitHub, preserve their setup, or says "hnh-backup". Strips API tokens, usernames, and device-specific paths before pushing to the backup repo.
---

# hnh-backup

Back up the portable parts of the Claude workspace to GitHub, stripping credentials and device-specific info so the backup works across machines.

## Backup repo

- **Remote:** `https://github.com/huynguyenh/skills`
- **Local clone:** `~/ws/code/github.com/huynguyenh/skills`
- **GitHub account:** `huynguyenh` — the user may have other GitHub accounts configured on this device. Always verify and use huynguyenh specifically.
- **Git identity:** `user.name "huynguyenh"`, `user.email "<email>"`

## What gets backed up

| Source | Destination in repo | Notes |
|--------|-------------------|-------|
| `~/.claude/CLAUDE.md` | `CLAUDE.md` | Global index — sanitize paths |
| `~/.claude/skills/hnh-*` | `skills/` | Custom skills only |
| `~/.claude/memory/MEMORY.md` | `memory/MEMORY.md` | Memory index — sanitize paths & credentials |
| `~/.claude/rules/global-*.md` | `rules/` | Only global rules (safe to share across devices) |
| `~/.claude/statusline-command.sh` | `config/statusline-command.sh` | Status line script — sanitize paths |

## What does NOT get backed up

- **Marketplace skills** (claude-api, pdf, xlsx, docx, pptx, doc-coauthoring, web-artifacts-builder, webapp-testing, skill-creator, canvas-design, frontend-design, brand-guidelines, internal-comms, keybindings-help, simplify, loop)
- **Sensitive memory files:** `credentials.md`, `service-mapping.md` — these contain tokens or company-specific mappings
- **Plans:** `~/.claude/plans/` — contain company-specific work content (ticket numbers, implementation details)
- **Company-specific memory:** employer-specific convention files — tied to a specific employer
- **Local-only rules:** any rule file NOT prefixed with `global-` (e.g., `workspace.md` is local, `global-claude.md` gets backed up)
- **Settings:** `settings.json`, `settings.local.json`, `.claude.json`
- **Runtime data:** debug/, telemetry/, cache/, backups/, `.env` files

## Repo structure

```
CLAUDE.md              # global index (sanitized)
skills/                # custom skills
  hnh-setup/
    SKILL.md
  hnh-backup/
    SKILL.md
    scripts/
      sanitize.py
  hnh-*/               # any other custom skills
memory/
  MEMORY.md            # memory index (sanitized)
rules/                 # global rules only (global-*.md)
  global-credentials.md
  global-claude.md
  global-github.md
config/                # portable config files
  statusline-command.sh  # status line display script
```

## Step 1: Verify GitHub auth

Check that `gh` is authenticated as huynguyenh:

```bash
gh auth status
```

Look for `huynguyenh` in the output. If it's not there or a different account is active, ask the user to authenticate:

```bash
gh auth login
```

Tell the user: "Please select your **huynguyenh** GitHub account when prompted." Do not proceed until confirmed.

## Step 2: Ensure local clone exists

```bash
# Clone if needed
if [ ! -d ~/ws/code/github.com/huynguyenh/skills ]; then
  mkdir -p ~/ws/code/github.com/huynguyenh
  gh repo clone huynguyenh/skills ~/ws/code/github.com/huynguyenh/skills
fi

# Pull latest
cd ~/ws/code/github.com/huynguyenh/skills && git pull
```

Set the git remote to explicitly use the huynguyenh account (important on multi-account machines):

```bash
git remote set-url origin https://<email>/huynguyenh/skills.git
git config user.name "huynguyenh"
git config user.email "<email>"
```

## Step 3: Identify skills to back up

**Already tracked:** Look at what's in the repo's `skills/` directory — these always get synced.

**New skills:** Scan `~/.claude/skills/` for directories that are NOT in the marketplace exclusion list above and NOT already tracked in the repo.

If new custom skills are found, ask the user: "I found these new skills that aren't backed up yet: [list]. Want to include them?"

## Step 4: Copy files to repo

```bash
REPO=~/ws/code/github.com/huynguyenh/skills

# Clean repo dirs to start fresh (avoids orphaned files from deleted items)
rm -rf "$REPO/skills/" "$REPO/memory/" "$REPO/rules/"
mkdir -p "$REPO/skills" "$REPO/memory" "$REPO/rules"

# CLAUDE.md (global index)
cp ~/.claude/CLAUDE.md "$REPO/CLAUDE.md"

# Custom skills
for skill_dir in ~/.claude/skills/hnh-*; do
  [ -d "$skill_dir" ] && cp -r "$skill_dir" "$REPO/skills/"
done
# (plus any other custom skills the user confirmed)

# Memory index (MEMORY.md only — not credentials or company-specific files)
cp ~/.claude/memory/MEMORY.md "$REPO/memory/MEMORY.md" 2>/dev/null || true

# Rules (only global-* files — local rules stay on this device)
cp ~/.claude/rules/global-*.md "$REPO/rules/" 2>/dev/null || true

# Status line script
mkdir -p "$REPO/config"
cp ~/.claude/statusline-command.sh "$REPO/config/statusline-command.sh" 2>/dev/null || true
```

## Step 5: Sanitize

This is the most important step — the backup must be safe to push to GitHub.

Run the sanitization script bundled with this skill:

```bash
python3 ~/.claude/skills/hnh-backup/scripts/sanitize.py "$REPO"
```

The script handles:

**Path replacement:**
- `/Users/<actual_username>/` → `/Users/hnh/`

**Credential patterns to strip** (replaced with `<REDACTED>`):
- API tokens (`JIRA_API_TOKEN=...`, `SENTRY_AUTH_TOKEN=...`, `ESA_ACCESS_TOKEN=...`, `GH_TOKEN=...`)
- Bearer tokens (`Bearer ...`, `token ...` in curl headers)
- Long hex/base64 strings in token-like contexts
- GitHub personal access tokens (`ghp_...`, `gho_...`, `github_pat_...`)
- Email addresses in credential contexts

**Extra caution for CLAUDE.md and MEMORY.md** — these are the most likely to contain sensitive info. After the script runs, manually review the sanitized versions of these two files and flag anything that looks like it should have been redacted.

If the script finds something it can't safely sanitize, it reports it and skips the file. Review any warnings before proceeding.

## Step 6: Update indexes

The repo has two files that list skills — both must stay in sync with whatever is in `skills/`.

### README.md — skills table and repo structure

Read `$REPO/README.md`. Compare the skills listed in the table and repo structure tree against the actual `$REPO/skills/` directories. For each skill directory:
- If it's **missing from the table**, add a row with the skill name, trigger phrase, and a one-line description (read the skill's `SKILL.md` frontmatter `description` field to write this)
- If it's **in the table but no longer in `skills/`**, remove the row
- Also update the repo structure tree to match

### MEMORY.md — custom skills list

Read `$REPO/memory/MEMORY.md`. Compare the "Custom Skills" list against `$REPO/skills/`. Add/remove entries so the list matches what's actually backed up. Use the skill's `SKILL.md` frontmatter description to write a short summary for each entry.

### CLAUDE.md — preserve generic version

The repo's `CLAUDE.md` and `README.md` are maintained as generic/public-friendly versions. Before Step 4 copies the local `~/.claude/CLAUDE.md` over them, save the repo versions to `/tmp/` and restore them after copying:

```bash
cp "$REPO/CLAUDE.md" /tmp/claude-md-generic-backup 2>/dev/null
cp "$REPO/README.md" /tmp/readme-md-generic-backup 2>/dev/null
# ... (Step 4 copy happens) ...
cp /tmp/claude-md-generic-backup "$REPO/CLAUDE.md"
cp /tmp/readme-md-generic-backup "$REPO/README.md"
```

This step is critical — without it, the local company-specific CLAUDE.md overwrites the public-safe version.

## Step 7: Commit and push

```bash
cd "$REPO"
git add -A
git status  # show what changed
```

Show the user what will be committed. Then commit with a useful message that describes what actually changed — not just a date stamp:

```bash
# Good examples:
#   "add hnh-setup and hnh-backup skills"
#   "update global rules, add APKNOWLEDG-640 plan"
#   "sync memory and credential rules"
git commit -m "<concise description of what changed>"
git push
```

If the push fails due to auth issues, remind the user to check `gh auth status` for the huynguyenh account.

## Step 8: Post-backup verification

After pushing, do a quick sanity check:
- `git log -1` to confirm the commit
- Scan the committed files one more time for any leaked credentials (grep for common token patterns)
- If anything slipped through, immediately warn the user

## Step 9: Report

Tell the user:
- Files backed up (CLAUDE.md, MEMORY.md, skills, plans, rules — list them)
- Files sanitized (summary of replacements made)
- Commit SHA and push status
- Any warnings or files skipped
