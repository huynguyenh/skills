# Proposed Changes

## File: `~/.claude/knowledge/personal/zenlabs.md`

### Change 1: Fix Notion workspace name
**Line 27** — The workspace name has a space ("Zen Labs") but the correct name is "ZenLabs" (no space).

**Before:**
```
- **Workspace:** Zen Labs
```

**After:**
```
- **Workspace:** ZenLabs
```

### Change 2: Update Notion integration name
**Line 28** — The integration was renamed from "Claude Integration" to "Claude Bot".

**Before:**
```
- **Integration name:** Claude Integration
```

**After:**
```
- **Integration name:** Claude Bot
```

### Change 3: Update integration reference in sharing note
**Line 31** — The sharing instruction references the old integration name.

**Before:**
```
- Pages/databases must be shared with the "Claude Integration" connection before the API can access them
```

**After:**
```
- Pages/databases must be shared with the "Claude Bot" connection before the API can access them
```

## Summary

All three changes are in `personal/zenlabs.md` under the `## Notion` section. No new files or INDEX.md updates needed — these are corrections to existing entries.
