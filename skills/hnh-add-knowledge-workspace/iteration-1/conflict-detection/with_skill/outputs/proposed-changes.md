# Proposed Changes to Knowledge Base

## File: `personal/zenlabs.md`

### Change 1: Update Notion workspace name

**Classification:** Update (existing entry covers the same topic but the detail has changed)

**Old:**
```
- **Workspace:** Zen Labs
```

**New:**
```
- **Workspace:** ZenLabs
```

**Reasoning:** The user confirmed the workspace is called "ZenLabs" (one word, camelCase), not "Zen Labs" (two words). This is a factual correction to an existing entry — replace in place, do not append.

---

### Change 2: Update Notion integration name

**Classification:** Update (existing entry covers the same topic but the detail has changed)

**Old (line 28):**
```
- **Integration name:** Claude Integration
```

**New:**
```
- **Integration name:** Claude Bot
```

**Reasoning:** The integration was renamed from "Claude Integration" to "Claude Bot". Replace the existing value.

---

### Change 3: Update Notion sharing instructions to reflect new integration name

**Classification:** Update (cascading reference — same rename applies here)

**Old (line 31):**
```
- Pages/databases must be shared with the "Claude Integration" connection before the API can access them
```

**New:**
```
- Pages/databases must be shared with the "Claude Bot" connection before the API can access them
```

**Reasoning:** This is a downstream reference to the same integration name. If only the `Integration name` field were updated but this instruction still said "Claude Integration", the knowledge base would be internally inconsistent. Both must be updated together.

---

## Files with no changes needed

- `personal/zenlabs-employees.md` — no entries reference the workspace name or integration name
- `INDEX.md` — no changes needed (no new domain, no scope change)
