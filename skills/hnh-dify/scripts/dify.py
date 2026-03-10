#!/usr/bin/env python3
"""Dify Service API CLI wrapper.

Usage:
    python3 dify.py --api-key KEY [--base-url URL] <command> [args]
"""

import argparse
import json
import sys
import os

import requests

DEFAULT_BASE_URL = "https://api.dify.ai/v1"


def api_request(method, url, api_key, **kwargs):
    """Make an authenticated API request and return parsed JSON or raw response."""
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {api_key}"

    raw = kwargs.pop("raw", False)
    stream = kwargs.pop("stream_response", False)

    resp = requests.request(method, url, headers=headers, stream=stream, **kwargs)

    if stream and resp.status_code == 200:
        return resp  # caller handles SSE

    if resp.status_code == 204:
        return {"result": "success"}

    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.status_code >= 400:
        print(json.dumps({"error": True, "status": resp.status_code, "detail": data}, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    return data


def handle_stream(resp):
    """Process SSE stream and print events."""
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[6:]
        try:
            event = json.loads(payload)
            print(json.dumps(event, ensure_ascii=False))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(payload)
            sys.stdout.flush()


# ── App Info ──────────────────────────────────────────────────────────────────

def cmd_info(args):
    url = f"{args.base_url}/info"
    data = api_request("GET", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_parameters(args):
    url = f"{args.base_url}/parameters"
    data = api_request("GET", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_meta(args):
    url = f"{args.base_url}/meta"
    params = {"user": args.user}
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── Workflow ──────────────────────────────────────────────────────────────────

def cmd_workflow_run(args):
    url = f"{args.base_url}/workflows/run"
    body = {
        "inputs": json.loads(args.inputs),
        "response_mode": "streaming" if args.stream else "blocking",
        "user": args.user,
    }
    if args.stream:
        resp = api_request("POST", url, args.api_key, json=body, stream_response=True)
        handle_stream(resp)
    else:
        data = api_request("POST", url, args.api_key, json=body)
        print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_workflow_detail(args):
    url = f"{args.base_url}/workflows/run/{args.workflow_run_id}"
    data = api_request("GET", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_workflow_logs(args):
    url = f"{args.base_url}/workflows/logs"
    params = {}
    if args.status:
        params["status"] = args.status
    if args.keyword:
        params["keyword"] = args.keyword
    params["page"] = args.page
    params["limit"] = args.limit
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_workflow_stop(args):
    url = f"{args.base_url}/workflows/tasks/{args.task_id}/stop"
    body = {"user": args.user}
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── Chat ──────────────────────────────────────────────────────────────────────

def cmd_chat(args):
    url = f"{args.base_url}/chat-messages"
    body = {
        "query": args.query,
        "user": args.user,
        "response_mode": "streaming" if args.stream else "blocking",
        "inputs": json.loads(args.inputs) if args.inputs else {},
    }
    if args.conversation_id:
        body["conversation_id"] = args.conversation_id
    if args.files:
        body["files"] = json.loads(args.files)

    if args.stream:
        resp = api_request("POST", url, args.api_key, json=body, stream_response=True)
        handle_stream(resp)
    else:
        data = api_request("POST", url, args.api_key, json=body)
        print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_chat_stop(args):
    url = f"{args.base_url}/chat-messages/{args.task_id}/stop"
    body = {"user": args.user}
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_feedback(args):
    url = f"{args.base_url}/messages/{args.message_id}/feedbacks"
    rating = None if args.rating == "null" else args.rating
    body = {"rating": rating, "user": args.user}
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_suggested(args):
    url = f"{args.base_url}/messages/{args.message_id}/suggested"
    params = {"user": args.user}
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── Completion ────────────────────────────────────────────────────────────────

def cmd_completion(args):
    url = f"{args.base_url}/completion-messages"
    body = {
        "inputs": json.loads(args.inputs),
        "response_mode": "streaming" if args.stream else "blocking",
        "user": args.user,
    }
    if args.files:
        body["files"] = json.loads(args.files)

    if args.stream:
        resp = api_request("POST", url, args.api_key, json=body, stream_response=True)
        handle_stream(resp)
    else:
        data = api_request("POST", url, args.api_key, json=body)
        print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_completion_stop(args):
    url = f"{args.base_url}/completion-messages/{args.task_id}/stop"
    body = {"user": args.user}
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── Conversations ─────────────────────────────────────────────────────────────

def cmd_conversations(args):
    url = f"{args.base_url}/conversations"
    params = {"user": args.user, "limit": args.limit}
    if args.sort_by:
        params["sort_by"] = args.sort_by
    if args.last_id:
        params["last_id"] = args.last_id
    if args.pinned is not None:
        params["pinned"] = str(args.pinned).lower()
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_messages(args):
    url = f"{args.base_url}/messages"
    params = {
        "conversation_id": args.conversation_id,
        "user": args.user,
        "limit": args.limit,
    }
    if args.first_id:
        params["first_id"] = args.first_id
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_conversation_delete(args):
    url = f"{args.base_url}/conversations/{args.conversation_id}"
    data = api_request("DELETE", url, args.api_key, json={"user": args.user})
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_conversation_rename(args):
    url = f"{args.base_url}/conversations/{args.conversation_id}/name"
    body = {"user": args.user}
    if args.name:
        body["name"] = args.name
    if args.auto_generate:
        body["auto_generate"] = True
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_conversation_variables(args):
    url = f"{args.base_url}/conversations/{args.conversation_id}/variables"
    params = {"user": args.user, "limit": args.limit}
    if args.last_id:
        params["last_id"] = args.last_id
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── File & Audio ──────────────────────────────────────────────────────────────

def cmd_upload(args):
    url = f"{args.base_url}/files/upload"
    with open(args.file_path, "rb") as f:
        files = {"file": (os.path.basename(args.file_path), f)}
        form_data = {"user": args.user}
        data = api_request("POST", url, args.api_key, files=files, data=form_data)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_audio_to_text(args):
    url = f"{args.base_url}/audio-to-text"
    with open(args.file_path, "rb") as f:
        files = {"file": (os.path.basename(args.file_path), f)}
        form_data = {"user": args.user}
        data = api_request("POST", url, args.api_key, files=files, data=form_data)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_text_to_audio(args):
    url = f"{args.base_url}/text-to-audio"
    body = {"user": args.user}
    if args.message_id:
        body["message_id"] = args.message_id
    if args.text:
        body["text"] = args.text

    resp = requests.post(url, headers={"Authorization": f"Bearer {args.api_key}"}, json=body)
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        print(json.dumps({"error": True, "status": resp.status_code, "detail": detail}, indent=2), file=sys.stderr)
        sys.exit(1)

    output = args.output or "output.mp3"
    with open(output, "wb") as f:
        f.write(resp.content)
    print(json.dumps({"result": "success", "file": output, "size_bytes": len(resp.content)}, indent=2))


# ── Knowledge Base (Datasets) ────────────────────────────────────────────────

def cmd_datasets(args):
    url = f"{args.base_url}/datasets"
    params = {"page": args.page, "limit": args.limit}
    if args.keyword:
        params["keyword"] = args.keyword
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_dataset_create(args):
    url = f"{args.base_url}/datasets"
    body = {"name": args.name}
    if args.description:
        body["description"] = args.description
    if args.indexing_technique:
        body["indexing_technique"] = args.indexing_technique
    if args.permission:
        body["permission"] = args.permission
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_dataset_detail(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}"
    data = api_request("GET", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_dataset_update(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}"
    body = {}
    if args.name:
        body["name"] = args.name
    if args.description:
        body["description"] = args.description
    if args.indexing_technique:
        body["indexing_technique"] = args.indexing_technique
    if args.permission:
        body["permission"] = args.permission
    data = api_request("PATCH", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_dataset_delete(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}"
    data = api_request("DELETE", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_documents(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents"
    params = {"page": args.page, "limit": args.limit}
    if args.keyword:
        params["keyword"] = args.keyword
    data = api_request("GET", url, args.api_key, params=params)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_document_create_text(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/document/create_by_text"
    body = {
        "name": args.name,
        "text": args.text,
        "indexing_technique": args.indexing_technique or "high_quality",
        "process_rule": {"mode": "automatic"},
    }
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_document_create_file(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/document/create-by-file"
    config = {
        "indexing_technique": args.indexing_technique or "high_quality",
        "process_rule": {"mode": "automatic"},
    }
    with open(args.file_path, "rb") as f:
        files = {"file": (os.path.basename(args.file_path), f)}
        form_data = {"data": json.dumps(config)}
        data = api_request("POST", url, args.api_key, files=files, data=form_data)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_document_update_text(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.document_id}/update_by_text"
    body = {}
    if args.name:
        body["name"] = args.name
    if args.text:
        body["text"] = args.text
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_document_delete(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.document_id}"
    data = api_request("DELETE", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_document_detail(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.document_id}"
    data = api_request("GET", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_indexing_status(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.batch_id}/indexing-status"
    data = api_request("GET", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_segments(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.document_id}/segments"
    data = api_request("GET", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_segment_add(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.document_id}/segments"
    body = {"segments": json.loads(args.segments)}
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_segment_update(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.document_id}/segments/{args.segment_id}"
    segment = {}
    if args.content:
        segment["content"] = args.content
    if args.answer:
        segment["answer"] = args.answer
    if args.keywords:
        segment["keywords"] = json.loads(args.keywords)
    if args.enabled is not None:
        segment["enabled"] = args.enabled
    body = {"segment": segment}
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_segment_delete(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/documents/{args.document_id}/segments/{args.segment_id}"
    data = api_request("DELETE", url, args.api_key)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_retrieve(args):
    url = f"{args.base_url}/datasets/{args.dataset_id}/retrieve"
    body = {"query": args.query}
    if args.search_method or args.top_k:
        retrieval = {}
        if args.search_method:
            retrieval["search_method"] = args.search_method
        if args.top_k:
            retrieval["top_k"] = args.top_k
        body["retrieval_model"] = retrieval
    data = api_request("POST", url, args.api_key, json=body)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── Argument Parsing ──────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(description="Dify Service API CLI")
    parser.add_argument("--api-key", required=True, help="Dify API key")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")

    sub = parser.add_subparsers(dest="command", required=True)

    # info
    sub.add_parser("info", help="Get app info")

    # parameters
    sub.add_parser("parameters", help="Get app parameters")

    # meta
    p = sub.add_parser("meta", help="Get app meta")
    p.add_argument("--user", required=True)

    # workflow-run
    p = sub.add_parser("workflow-run", help="Execute a workflow")
    p.add_argument("--inputs", required=True, help="JSON inputs")
    p.add_argument("--user", required=True)
    p.add_argument("--stream", action="store_true")

    # workflow-detail
    p = sub.add_parser("workflow-detail", help="Get workflow run detail")
    p.add_argument("workflow_run_id")

    # workflow-logs
    p = sub.add_parser("workflow-logs", help="List workflow logs")
    p.add_argument("--status", choices=["succeeded", "failed", "stopped", "running"])
    p.add_argument("--keyword")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=20)

    # workflow-stop
    p = sub.add_parser("workflow-stop", help="Stop a workflow")
    p.add_argument("task_id")
    p.add_argument("--user", required=True)

    # chat
    p = sub.add_parser("chat", help="Send a chat message")
    p.add_argument("--query", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--inputs", help="JSON inputs")
    p.add_argument("--conversation-id")
    p.add_argument("--files", help="JSON array of file objects")
    p.add_argument("--stream", action="store_true")

    # chat-stop
    p = sub.add_parser("chat-stop", help="Stop chat generation")
    p.add_argument("task_id")
    p.add_argument("--user", required=True)

    # feedback
    p = sub.add_parser("feedback", help="Rate a message")
    p.add_argument("message_id")
    p.add_argument("--rating", required=True, choices=["like", "dislike", "null"])
    p.add_argument("--user", required=True)

    # suggested
    p = sub.add_parser("suggested", help="Get suggested questions")
    p.add_argument("message_id")
    p.add_argument("--user", required=True)

    # completion
    p = sub.add_parser("completion", help="Create a completion")
    p.add_argument("--inputs", required=True, help="JSON inputs")
    p.add_argument("--user", required=True)
    p.add_argument("--files", help="JSON array of file objects")
    p.add_argument("--stream", action="store_true")

    # completion-stop
    p = sub.add_parser("completion-stop", help="Stop completion")
    p.add_argument("task_id")
    p.add_argument("--user", required=True)

    # conversations
    p = sub.add_parser("conversations", help="List conversations")
    p.add_argument("--user", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--sort-by", default="-updated_at")
    p.add_argument("--last-id")
    p.add_argument("--pinned", type=bool, default=None)

    # messages
    p = sub.add_parser("messages", help="Get message history")
    p.add_argument("conversation_id")
    p.add_argument("--user", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--first-id")

    # conversation-delete
    p = sub.add_parser("conversation-delete", help="Delete a conversation")
    p.add_argument("conversation_id")
    p.add_argument("--user", required=True)

    # conversation-rename
    p = sub.add_parser("conversation-rename", help="Rename a conversation")
    p.add_argument("conversation_id")
    p.add_argument("--user", required=True)
    p.add_argument("--name")
    p.add_argument("--auto-generate", action="store_true")

    # conversation-variables
    p = sub.add_parser("conversation-variables", help="Get conversation variables")
    p.add_argument("conversation_id")
    p.add_argument("--user", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--last-id")

    # upload
    p = sub.add_parser("upload", help="Upload a file")
    p.add_argument("file_path")
    p.add_argument("--user", required=True)

    # audio-to-text
    p = sub.add_parser("audio-to-text", help="Transcribe audio")
    p.add_argument("file_path")
    p.add_argument("--user", required=True)

    # text-to-audio
    p = sub.add_parser("text-to-audio", help="Generate speech")
    p.add_argument("--user", required=True)
    p.add_argument("--message-id")
    p.add_argument("--text")
    p.add_argument("--output", default="output.mp3")

    # datasets
    p = sub.add_parser("datasets", help="List knowledge bases")
    p.add_argument("--keyword")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=20)

    # dataset-create
    p = sub.add_parser("dataset-create", help="Create knowledge base")
    p.add_argument("--name", required=True)
    p.add_argument("--description")
    p.add_argument("--indexing-technique", choices=["high_quality", "economy"])
    p.add_argument("--permission", choices=["only_me", "all_team_members"])

    # dataset-detail
    p = sub.add_parser("dataset-detail", help="Get knowledge base details")
    p.add_argument("dataset_id")

    # dataset-update
    p = sub.add_parser("dataset-update", help="Update knowledge base")
    p.add_argument("dataset_id")
    p.add_argument("--name")
    p.add_argument("--description")
    p.add_argument("--indexing-technique", choices=["high_quality", "economy"])
    p.add_argument("--permission", choices=["only_me", "all_team_members"])

    # dataset-delete
    p = sub.add_parser("dataset-delete", help="Delete knowledge base")
    p.add_argument("dataset_id")

    # documents
    p = sub.add_parser("documents", help="List documents")
    p.add_argument("dataset_id")
    p.add_argument("--keyword")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=20)

    # document-create-text
    p = sub.add_parser("document-create-text", help="Create document from text")
    p.add_argument("dataset_id")
    p.add_argument("--name", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--indexing-technique", choices=["high_quality", "economy"])

    # document-create-file
    p = sub.add_parser("document-create-file", help="Create document from file")
    p.add_argument("dataset_id")
    p.add_argument("file_path")
    p.add_argument("--indexing-technique", choices=["high_quality", "economy"])

    # document-update-text
    p = sub.add_parser("document-update-text", help="Update document text")
    p.add_argument("dataset_id")
    p.add_argument("document_id")
    p.add_argument("--name")
    p.add_argument("--text")

    # document-delete
    p = sub.add_parser("document-delete", help="Delete a document")
    p.add_argument("dataset_id")
    p.add_argument("document_id")

    # document-detail
    p = sub.add_parser("document-detail", help="Get document details")
    p.add_argument("dataset_id")
    p.add_argument("document_id")

    # indexing-status
    p = sub.add_parser("indexing-status", help="Check indexing progress")
    p.add_argument("dataset_id")
    p.add_argument("batch_id")

    # segments
    p = sub.add_parser("segments", help="List segments")
    p.add_argument("dataset_id")
    p.add_argument("document_id")

    # segment-add
    p = sub.add_parser("segment-add", help="Add segments")
    p.add_argument("dataset_id")
    p.add_argument("document_id")
    p.add_argument("--segments", required=True, help="JSON array of segments")

    # segment-update
    p = sub.add_parser("segment-update", help="Update a segment")
    p.add_argument("dataset_id")
    p.add_argument("document_id")
    p.add_argument("segment_id")
    p.add_argument("--content")
    p.add_argument("--answer")
    p.add_argument("--keywords", help="JSON array of keywords")
    p.add_argument("--enabled", type=bool, default=None)

    # segment-delete
    p = sub.add_parser("segment-delete", help="Delete a segment")
    p.add_argument("dataset_id")
    p.add_argument("document_id")
    p.add_argument("segment_id")

    # retrieve
    p = sub.add_parser("retrieve", help="Search knowledge base")
    p.add_argument("dataset_id")
    p.add_argument("--query", required=True)
    p.add_argument("--search-method", choices=["hybrid_search", "semantic_search", "full_text_search", "keyword_search"])
    p.add_argument("--top-k", type=int)

    return parser


COMMAND_MAP = {
    "info": cmd_info,
    "parameters": cmd_parameters,
    "meta": cmd_meta,
    "workflow-run": cmd_workflow_run,
    "workflow-detail": cmd_workflow_detail,
    "workflow-logs": cmd_workflow_logs,
    "workflow-stop": cmd_workflow_stop,
    "chat": cmd_chat,
    "chat-stop": cmd_chat_stop,
    "feedback": cmd_feedback,
    "suggested": cmd_suggested,
    "completion": cmd_completion,
    "completion-stop": cmd_completion_stop,
    "conversations": cmd_conversations,
    "messages": cmd_messages,
    "conversation-delete": cmd_conversation_delete,
    "conversation-rename": cmd_conversation_rename,
    "conversation-variables": cmd_conversation_variables,
    "upload": cmd_upload,
    "audio-to-text": cmd_audio_to_text,
    "text-to-audio": cmd_text_to_audio,
    "datasets": cmd_datasets,
    "dataset-create": cmd_dataset_create,
    "dataset-detail": cmd_dataset_detail,
    "dataset-update": cmd_dataset_update,
    "dataset-delete": cmd_dataset_delete,
    "documents": cmd_documents,
    "document-create-text": cmd_document_create_text,
    "document-create-file": cmd_document_create_file,
    "document-update-text": cmd_document_update_text,
    "document-delete": cmd_document_delete,
    "document-detail": cmd_document_detail,
    "indexing-status": cmd_indexing_status,
    "segments": cmd_segments,
    "segment-add": cmd_segment_add,
    "segment-update": cmd_segment_update,
    "segment-delete": cmd_segment_delete,
    "retrieve": cmd_retrieve,
}


def main():
    parser = build_parser()
    args = parser.parse_args()
    handler = COMMAND_MAP.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
