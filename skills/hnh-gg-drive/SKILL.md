---
name: hnh-gg-drive
description: >
  Interact with Google Drive — list, search, upload, download, move, copy, rename, trash,
  and organize files and folders via the Google Drive API. Use this skill whenever the user
  wants to work with Google Drive: uploading files, downloading files, organizing folders,
  searching for files, moving or copying files between folders, checking file info, or
  managing file sharing. Trigger on mentions of "Google Drive", "Drive", "upload to Drive",
  "download from Drive", Drive folder URLs (drive.google.com), or any request to manage files
  in Google Drive. Also trigger when the user wants to upload a local file to the cloud,
  download a cloud file, or organize files in folders — even if they don't explicitly say
  "Google Drive". If the user doesn't specify a project or location, assume it's for ZenLabs
  (check ~/.claude/knowledge/personal/zenlabs.md for Drive structure and file naming rules).
  Do NOT trigger for Google Sheets operations (reading/writing cell data, formatting cells) —
  those belong to the hnh-gg-sheets skill. Do NOT trigger for local file operations.
---

# Google Drive Skill

Manage files and folders in Google Drive through a Python CLI tool wrapping the Drive v3 API.

## Prerequisites

- **gcloud CLI** with Application Default Credentials configured
- **Python packages**: `google-api-python-client`, `google-auth`
- ADC scopes must include `drive`

If auth fails with a credentials error, run:
```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/drive"
```

## The CLI Tool

All operations go through a single script:

```
python3 ~/.claude/skills/hnh-gg-drive/scripts/drive.py <command> [args]
```

The script outputs JSON to stdout, errors to stderr. All commands accept file/folder IDs or full Drive URLs — IDs are auto-extracted from URLs.

## ZenLabs Defaults

When the user doesn't specify a project or destination, this is a ZenLabs task. Read `~/.claude/knowledge/personal/zenlabs.md` for full context. Key rules:

- **Default folder for new files**: `6. Brainstorming` (ID: `1lOIDiTCJi84wuvgK0b1LRV882tzf9ntL`)
- **File naming**: Always prefix with `zenlabs | {descriptive name}`
- **Drive root folder ID**: `1CHEn7mozKXpKU9O76Q5HQ2ZUnEgLOzd0`

## Commands Reference

### list — List files in a folder

```bash
python3 <script> list --folder FOLDER_ID --type folder --limit 20
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--folder` | root | Folder ID or URL to list |
| `--type` | all | `file` or `folder` |
| `--sort` | `modifiedTime desc` | Sort order |
| `--limit` | 50 | Max results |

### search — Find files by name

```bash
python3 <script> search "quarterly report" --folder FOLDER_ID --type file --limit 10
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--folder` | anywhere | Restrict to folder |
| `--type` | all | `file` or `folder` |
| `--mime-type` | any | Filter by MIME type |
| `--limit` | 20 | Max results |

### info — Get file/folder metadata

```bash
python3 <script> info FILE_ID_OR_URL
```

Returns name, MIME type, size, dates, parents, permissions, sharing status, and web link.

### create-folder — Create a new folder

```bash
python3 <script> create-folder "Project Alpha" --parent PARENT_FOLDER_ID
```

### upload — Upload a local file to Drive

```bash
python3 <script> upload /path/to/file.pdf --folder FOLDER_ID --name "zenlabs | report.pdf"
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--folder` | root | Destination folder ID or URL |
| `--name` | local filename | Override the Drive filename |
| `--mime-type` | auto-detected | Override MIME type |

### download — Download a file from Drive

```bash
python3 <script> download FILE_ID --output-dir ~/Downloads --name "report.pdf"
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--output-dir` | current dir | Local directory to save to |
| `--name` | original name | Override local filename |
| `--export-mime` | auto | Export MIME for Google Workspace files |

Google Workspace files (Docs, Sheets, Slides) are automatically exported — Docs/Slides/Drawings to PDF, Sheets to .xlsx. Use `--export-mime` to override (e.g., `text/plain` for Docs).

### move — Move a file to another folder

```bash
python3 <script> move FILE_ID DESTINATION_FOLDER_ID
```

### copy — Copy a file

```bash
python3 <script> copy FILE_ID --name "Copy of report" --folder FOLDER_ID
```

### rename — Rename a file or folder

```bash
python3 <script> rename FILE_ID "New name here"
```

### trash — Move to trash

```bash
python3 <script> trash FILE_ID
```

### restore — Restore from trash

```bash
python3 <script> restore FILE_ID
```

### share — Share a file with someone

```bash
python3 <script> share FILE_ID --email <email> --role writer
```

| Flag | Default | What it does |
|------|---------|-------------|
| `--email` | (required) | Email address to share with |
| `--role` | `reader` | `reader`, `commenter`, or `writer` |
| `--no-notify` | false | Skip the email notification |

## Workflow Patterns

### Uploading a file to ZenLabs Drive

1. Read `~/.claude/knowledge/personal/zenlabs.md` for folder structure
2. Determine the right subfolder (default: 6. Brainstorming)
3. Upload with `zenlabs | ` prefix in the name
4. Return the web link to the user

### Organizing files

1. Use `search` or `list` to find files
2. Use `create-folder` if new folders are needed
3. Use `move` to reorganize
4. Use `rename` to fix names

### Downloading for local work

1. Use `search` or `info` to identify the file
2. Use `download` with an appropriate output directory
3. Google Workspace files auto-export to standard formats

## Error Handling

- **Auth errors**: Re-run the `gcloud auth application-default login` command above
- **404 / not found**: Check the file ID — URL extraction might fail on unusual URLs
- **Permission denied**: The authenticated account needs access to the file
- **Quota errors**: Drive API has per-user and per-project rate limits
