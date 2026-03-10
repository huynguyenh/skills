---
name: hnh-gg-docs
description: >
  Interact with Google Docs — read content, create documents, append text, find-and-replace,
  and get document metadata via the Google Docs API. Use this skill whenever the user wants
  to work with Google Docs: reading a doc's content, creating a new doc, updating or appending
  text, doing find-and-replace, or getting document info. Trigger on mentions of "Google Doc",
  "gdoc", "document" (when the context is Google Drive, not local .docx), Google Doc URLs
  (docs.google.com/document), or any request to create/read/update a document in Google Drive.
  If the user doesn't specify a project or location, assume it's for ZenLabs
  (check ~/.claude/knowledge/personal/zenlabs.md for Drive structure and file naming rules).
  Do NOT trigger for local .docx file operations — those belong to the docx skill.
  Do NOT trigger for Google Sheets operations — those belong to the hnh-gg-sheets skill.
---

# Google Docs Skill

Interact with Google Docs through a Python CLI tool that wraps the Docs and Drive APIs.

## Prerequisites

- **gcloud CLI** with Application Default Credentials configured
- **Python packages**: `google-api-python-client`, `google-auth`
- ADC scopes must include `documents` and `drive`

If auth fails with a credentials error, run:
```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive"
```

## The CLI Tool

All operations go through a single script:

```
python3 ~/.claude/skills/hnh-gg-docs/scripts/gdocs.py <command> [args]
```

The script outputs JSON to stdout, errors to stderr. Accepts both document IDs and full Google Docs URLs (auto-extracts the ID).

## ZenLabs Defaults

When the user doesn't specify a project or destination, this is a ZenLabs task. Read `~/.claude/knowledge/personal/zenlabs.md` for full context. Key rules:

- **Default folder**: `6. Brainstorming` in ZenLabs Drive
- **File naming**: Always prefix with `zenlabs | {descriptive name}`
- **Drive root folder ID**: `1CHEn7mozKXpKU9O76Q5HQ2ZUnEgLOzd0`

## Commands Reference

### read — Get document content as text

```bash
python3 <script> read DOCUMENT_ID_OR_URL
```

Returns the full document text rendered as readable content with headings marked by `#`, `##`, etc. Also includes document metadata (title, ID, URL).

### create — Create a new document

```bash
# Empty document
python3 <script> create "Meeting Notes - March 2026"

# With initial content
python3 <script> create "Project Brief" --content "# Overview\n\nThis document covers..."

# In a specific Drive folder
python3 <script> create "zenlabs | Q1 Report" --folder FOLDER_ID

# With content from a file
python3 <script> create "Design Doc" --content-file /path/to/content.md --folder FOLDER_ID
```

- `--content`: Text content to insert (supports `\n` for newlines).
- `--content-file`: Read content from a file instead.
- `--folder`: Move the created doc to this Drive folder.

### append — Add content to the end of a document

```bash
python3 <script> append DOCUMENT_ID "## New Section\n\nMore content here."

# From a file
python3 <script> append DOCUMENT_ID --content-file /path/to/notes.md
```

Appends text at the end of the document body.

### insert — Insert text at a specific position

```bash
# Insert at the beginning (index 1)
python3 <script> insert DOCUMENT_ID "DRAFT - " --index 1

# Insert at a specific index
python3 <script> insert DOCUMENT_ID "inserted text" --index 42
```

Use `read --with-indexes` to see character indexes for precise placement.

### replace — Find and replace text

```bash
# Case-sensitive replace
python3 <script> replace DOCUMENT_ID --find "{{client_name}}" --replace "Acme Corp"

# Case-insensitive
python3 <script> replace DOCUMENT_ID --find "todo" --replace "DONE" --ignore-case
```

Returns the number of occurrences changed.

### info — Get document metadata

```bash
python3 <script> info DOCUMENT_ID_OR_URL
```

Returns title, document ID, URL, revision ID, and tab info.

### search — Find documents by name in Drive

```bash
python3 <script> search "project brief" --limit 5
python3 <script> search "meeting notes" --folder FOLDER_ID
```

Searches Google Drive for documents matching the name.

## Workflow Patterns

### Reading a Google Doc the user shares

1. Extract the document ID from the URL
2. Run `read` to get the full text content
3. Present a summary to the user

### Creating a new ZenLabs document

1. Read `~/.claude/knowledge/personal/zenlabs.md` for folder structure
2. Create with `zenlabs | ` prefix and target folder
3. Return the document URL to the user

### Template-based document generation

1. Create or find a template document
2. Use `replace` to fill in `{{placeholder}}` values
3. Each `replace` call handles one placeholder across the whole document

### Appending meeting notes or updates

1. Use `read` to check current content
2. Use `append` to add new section at the end

## Error Handling

- **Auth errors**: Re-run the `gcloud auth application-default login` command above
- **404 / not found**: Check the document ID — may need to share the doc with your Google account
- **Permission denied**: The authenticated account needs access to the document
- **403 Quota**: Google Docs API has rate limits — wait and retry
