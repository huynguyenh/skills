---
name: hnh-dify
description: >
  Interact with Dify.ai — run workflows, chat with apps, manage knowledge bases, view logs,
  upload files, and manage conversations via the Dify Service API.
  Use this skill whenever the user mentions Dify, says "in Dify", "on Dify", "run my Dify workflow",
  "check Dify logs", shares a Dify app URL, or wants to interact with any Dify application.
  Also trigger when the user mentions "workflow run", "knowledge base", or "dataset" in a context
  that implies Dify. Trigger on any request to run an AI workflow, check workflow logs or failures,
  manage RAG knowledge bases, or chat with a Dify-hosted app — even if the user doesn't explicitly
  say "Dify" but the context makes it clear they mean their Dify platform.
---

# Dify Skill

Interact with the Dify.ai cloud platform through a Python CLI tool wrapping the Dify Service API.

## Prerequisites

- **Python 3** with `requests` library (already installed)
- **API keys** in `~/.zshrc` (see Credential Setup below)

## Credential Setup

Dify uses two types of API keys:

1. **App API Keys** — per-app, used for chat/workflow/completion operations. Each Dify app has its own key.
2. **Dataset API Key** — account-level, used for knowledge base (dataset) operations across all datasets.

Add to `~/.zshrc`:

```bash
# Default app key (your primary workflow/app)
export DIFY_API_KEY="app-xxxxxxxxxxxxxxxxxxxxxxxx"

# Dataset API key (for knowledge base operations)
export DIFY_DATASET_API_KEY="dataset-xxxxxxxxxxxxxxxxxxxxxxxx"

# Optional: named app keys for specific apps
# export DIFY_APP_MYBOT_API_KEY="app-yyyyyyyyyyyyyyyyyyyyyyyy"
```

**Where to find your keys:**
- **App API Key**: Open your app in Dify → click "Access API" (left sidebar) → copy the API key
- **Dataset API Key**: Go to Dify → Knowledge → click "API" in the top right → copy the Dataset API key

## Auth Pattern

Following the credential rules, read tokens from `~/.zshrc` and inline them:

```bash
# Read token value from ~/.zshrc, then:
DIFY_KEY="<value>"
python3 ~/.claude/skills/hnh-dify/scripts/dify.py --api-key "$DIFY_KEY" <command> [args]
```

For knowledge base commands, use the dataset key:
```bash
DIFY_DS_KEY="<dataset key value>"
python3 ~/.claude/skills/hnh-dify/scripts/dify.py --api-key "$DIFY_DS_KEY" <command> [args]
```

## The CLI Tool

```
python3 ~/.claude/skills/hnh-dify/scripts/dify.py --api-key KEY <command> [args]
```

Base URL defaults to `https://api.dify.ai/v1`. Override with `--base-url` for self-hosted instances.

All commands output JSON to stdout, errors to stderr. HTTP errors include status code and response body for debugging.

---

## Commands Reference

### App Info

#### info — Get app name and description
```bash
python3 <script> --api-key $KEY info
```

#### parameters — Get app configuration (input form, file upload settings, opening statement)
```bash
python3 <script> --api-key $KEY parameters
```

---

### Workflow Operations

Use the app API key for the specific workflow app.

#### workflow-run — Execute a workflow
```bash
# Blocking mode (waits for result)
python3 <script> --api-key $KEY workflow-run --inputs '{"key": "value"}' --user "claude"

# Streaming mode
python3 <script> --api-key $KEY workflow-run --inputs '{"key": "value"}' --user "claude" --stream
```

`--inputs`: JSON object of workflow input variables (required).
`--user`: user identifier (required).
`--stream`: use streaming mode (prints events as they arrive).

#### workflow-detail — Get details of a workflow run
```bash
python3 <script> --api-key $KEY workflow-detail WORKFLOW_RUN_ID
```

Returns: status, inputs, outputs, elapsed time, total tokens, error message if failed.

#### workflow-logs — List workflow execution logs
```bash
# All recent logs
python3 <script> --api-key $KEY workflow-logs

# Filter by status
python3 <script> --api-key $KEY workflow-logs --status failed

# Search by keyword
python3 <script> --api-key $KEY workflow-logs --keyword "error"

# Pagination
python3 <script> --api-key $KEY workflow-logs --page 2 --limit 10
```

`--status`: `succeeded`, `failed`, `stopped`, `running`.

#### workflow-stop — Stop a running workflow
```bash
python3 <script> --api-key $KEY workflow-stop TASK_ID --user "claude"
```

---

### Chat Operations

Use the app API key for a Chat or Chatflow app.

#### chat — Send a chat message
```bash
# New conversation
python3 <script> --api-key $KEY chat --query "Hello!" --user "claude"

# Continue conversation
python3 <script> --api-key $KEY chat --query "Follow up" --user "claude" --conversation-id CONV_ID

# With files
python3 <script> --api-key $KEY chat --query "What's in this image?" --user "claude" \
  --files '[{"type":"image","transfer_method":"remote_url","url":"https://example.com/img.png"}]'

# Streaming
python3 <script> --api-key $KEY chat --query "Tell me a story" --user "claude" --stream
```

#### chat-stop — Stop a streaming chat response
```bash
python3 <script> --api-key $KEY chat-stop TASK_ID --user "claude"
```

#### feedback — Rate a message (like/dislike)
```bash
python3 <script> --api-key $KEY feedback MESSAGE_ID --rating like --user "claude"
python3 <script> --api-key $KEY feedback MESSAGE_ID --rating dislike --user "claude"
python3 <script> --api-key $KEY feedback MESSAGE_ID --rating null --user "claude"  # revoke
```

#### suggested — Get suggested follow-up questions
```bash
python3 <script> --api-key $KEY suggested MESSAGE_ID --user "claude"
```

---

### Completion Operations

Use the app API key for a Text Generation app.

#### completion — Create a completion
```bash
python3 <script> --api-key $KEY completion --inputs '{"query": "Summarize this"}' --user "claude"

# Streaming
python3 <script> --api-key $KEY completion --inputs '{"query": "Summarize this"}' --user "claude" --stream
```

#### completion-stop — Stop a completion
```bash
python3 <script> --api-key $KEY completion-stop TASK_ID --user "claude"
```

---

### Conversation Management

#### conversations — List conversations
```bash
python3 <script> --api-key $KEY conversations --user "claude"
python3 <script> --api-key $KEY conversations --user "claude" --limit 50 --sort-by "-updated_at"
python3 <script> --api-key $KEY conversations --user "claude" --pinned
```

#### messages — Get conversation message history
```bash
python3 <script> --api-key $KEY messages CONVERSATION_ID --user "claude"
python3 <script> --api-key $KEY messages CONVERSATION_ID --user "claude" --limit 50
```

#### conversation-delete — Delete a conversation
```bash
python3 <script> --api-key $KEY conversation-delete CONVERSATION_ID --user "claude"
```

#### conversation-rename — Rename a conversation
```bash
python3 <script> --api-key $KEY conversation-rename CONVERSATION_ID --name "New Name" --user "claude"
python3 <script> --api-key $KEY conversation-rename CONVERSATION_ID --auto-generate --user "claude"
```

#### conversation-variables — Get conversation variables
```bash
python3 <script> --api-key $KEY conversation-variables CONVERSATION_ID --user "claude"
```

---

### File & Audio Operations

#### upload — Upload a file
```bash
python3 <script> --api-key $KEY upload /path/to/file.png --user "claude"
```

Returns: file ID to use in chat/workflow file inputs.

#### audio-to-text — Transcribe audio
```bash
python3 <script> --api-key $KEY audio-to-text /path/to/audio.mp3 --user "claude"
```

Supported: mp3, mp4, mpeg, mpga, m4a, wav, webm. Max 15MB.

#### text-to-audio — Generate speech
```bash
# From text
python3 <script> --api-key $KEY text-to-audio --text "Hello world" --user "claude" --output speech.mp3

# From a message
python3 <script> --api-key $KEY text-to-audio --message-id MSG_ID --user "claude" --output speech.mp3
```

---

### Knowledge Base Operations

**Use the Dataset API key** (`DIFY_DATASET_API_KEY`) for all knowledge base commands.

#### datasets — List knowledge bases
```bash
python3 <script> --api-key $DS_KEY datasets
python3 <script> --api-key $DS_KEY datasets --keyword "FAQ" --page 1 --limit 10
```

#### dataset-create — Create a knowledge base
```bash
python3 <script> --api-key $DS_KEY dataset-create --name "My KB" --description "FAQ documents"
```

Optional: `--indexing-technique` (`high_quality` or `economy`), `--permission` (`only_me`, `all_team_members`).

#### dataset-detail — Get knowledge base details
```bash
python3 <script> --api-key $DS_KEY dataset-detail DATASET_ID
```

#### dataset-update — Update a knowledge base
```bash
python3 <script> --api-key $DS_KEY dataset-update DATASET_ID --name "Updated Name"
```

#### dataset-delete — Delete a knowledge base
```bash
python3 <script> --api-key $DS_KEY dataset-delete DATASET_ID
```

#### documents — List documents in a knowledge base
```bash
python3 <script> --api-key $DS_KEY documents DATASET_ID
```

#### document-create-text — Create a document from text
```bash
python3 <script> --api-key $DS_KEY document-create-text DATASET_ID \
  --name "FAQ" --text "Question: What is Dify?\nAnswer: An LLMOps platform."
```

#### document-create-file — Create a document from file upload
```bash
python3 <script> --api-key $DS_KEY document-create-file DATASET_ID /path/to/document.pdf
```

#### document-update-text — Update document content
```bash
python3 <script> --api-key $DS_KEY document-update-text DATASET_ID DOCUMENT_ID \
  --name "Updated FAQ" --text "New content here"
```

#### document-delete — Delete a document
```bash
python3 <script> --api-key $DS_KEY document-delete DATASET_ID DOCUMENT_ID
```

#### document-detail — Get document details
```bash
python3 <script> --api-key $DS_KEY document-detail DATASET_ID DOCUMENT_ID
```

#### indexing-status — Check document indexing progress
```bash
python3 <script> --api-key $DS_KEY indexing-status DATASET_ID BATCH_ID
```

#### segments — List segments (chunks) in a document
```bash
python3 <script> --api-key $DS_KEY segments DATASET_ID DOCUMENT_ID
```

#### segment-add — Add segments to a document
```bash
python3 <script> --api-key $DS_KEY segment-add DATASET_ID DOCUMENT_ID \
  --segments '[{"content": "Chunk text", "keywords": ["key1"]}]'
```

#### segment-update — Update a segment
```bash
python3 <script> --api-key $DS_KEY segment-update DATASET_ID DOCUMENT_ID SEGMENT_ID \
  --content "Updated text" --keywords '["new_keyword"]'
```

#### segment-delete — Delete a segment
```bash
python3 <script> --api-key $DS_KEY segment-delete DATASET_ID DOCUMENT_ID SEGMENT_ID
```

#### retrieve — Search/test retrieval from a knowledge base
```bash
python3 <script> --api-key $DS_KEY retrieve DATASET_ID --query "How to deploy?"

# With search config
python3 <script> --api-key $DS_KEY retrieve DATASET_ID --query "deploy" \
  --search-method hybrid_search --top-k 5
```

---

## Workflow Patterns

### Check for failed workflow runs
1. `workflow-logs --status failed --limit 10` — list recent failures
2. `workflow-detail <run_id>` — get error details for a specific failure

### Run a workflow and check result
1. `parameters` — see what inputs the workflow expects
2. `workflow-run --inputs '{"key":"value"}' --user "claude"` — execute it
3. `workflow-detail <run_id>` — check status and outputs if needed

### Manage knowledge base content
1. `datasets` — list all knowledge bases
2. `documents <dataset_id>` — see what's in one
3. `document-create-text` or `document-create-file` — add content
4. `retrieve <dataset_id> --query "test"` — verify retrieval works

### Chat with an app
1. `info` + `parameters` — understand the app
2. `chat --query "..." --user "claude"` — start chatting
3. `messages <conv_id> --user "claude"` — review history

## Error Handling

- **400 Bad Request**: Check input parameters, variable names, file types
- **401 Unauthorized**: API key is invalid — check `~/.zshrc`
- **404 Not Found**: Resource doesn't exist (wrong ID)
- **409 Conflict**: Dataset name already exists
- **413 File Too Large**: File exceeds size limit
- **429 Rate Limited**: Too many requests — wait and retry
- **500 Server Error**: Dify internal issue — retry later
