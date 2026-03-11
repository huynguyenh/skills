# Proposed Changes

## Target file: `~/.claude/knowledge/personal/zenlabs-employees.md`

## Classification
- **Scope:** Personal (ZenLabs employee info)
- **Domain:** zenlabs-employees (existing file)

## Changes

### 1. Add "Ray" as an alternate nickname
The entry currently lists `hao / hào` as nicknames. Add `Ray` since Hao also goes by that name.

**Before:**
```markdown
- **Nickname:** hao / hào
```

**After:**
```markdown
- **Nickname:** hao / hào / Ray
```

### 2. Fix GitHub field to show username instead of email
The entry currently has `<email> (same email)` for GitHub, but the user explicitly stated the GitHub username is `haoxray`. Replace the email-based entry with the actual username.

**Before:**
```markdown
- **GitHub:** <email> (same email)
```

**After:**
```markdown
- **GitHub:** haoxray
```

### 3. Discord ID — no change needed
The Discord ID `1412635437901676625` is already present in the file. No modification required.

## No changes to INDEX.md
No new domain was created, so INDEX.md remains unchanged.
