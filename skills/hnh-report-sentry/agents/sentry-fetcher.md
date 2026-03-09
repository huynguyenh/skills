# Agent A: Sentry Fetcher

Fetch comprehensive data about a Sentry issue — events, stacktraces, tags, breadcrumbs, and frequency. The goal is to give the report everything it needs to understand the error without anyone having to open the Sentry UI.

## Inputs you'll receive

- `issue_id` — the Sentry issue ID
- `SENTRY_AUTH_TOKEN` — literal token value (inline in commands)
- `SENTRY_URL` — the Sentry instance base URL
- `SENTRY_ORG` — the organization slug
- `project_slug` — the Sentry project slug
- Initial issue metadata (title, count, firstSeen, lastSeen, etc.)

## What to fetch

Make these API calls in sequence (some depend on earlier results):

### 1. Latest events with full stacktraces

```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  "<SENTRY_URL>/api/0/issues/<issue_id>/events/?full=true" \
  | python3 -m json.tool
```

From the events, extract:
- **Stacktraces** — every frame with file path, function name, line number, and context lines. Focus on application frames (not library/framework frames).
- **Exception type and value** — the actual error message
- **Breadcrumbs** — the sequence of actions/events leading up to the error
- **Request data** — URL, method, headers (if it's an HTTP error)
- **User context** — user ID, IP, affected accounts
- **Tags** — environment, release, server name, browser, OS

If the events response is paginated, fetch up to 3 pages (most recent events are most useful).

### 2. Tags breakdown

```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  "<SENTRY_URL>/api/0/issues/<issue_id>/tags/" \
  | python3 -m json.tool
```

This shows which tag values are most common — helps identify if the error is isolated to specific environments, releases, or user segments.

For the most interesting tags (environment, release, browser, url), also fetch the values breakdown:

```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  "<SENTRY_URL>/api/0/issues/<issue_id>/tags/<tag_key>/values/" \
  | python3 -m json.tool
```

### 3. Event frequency (optional, if the stats endpoint is available)

```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  "<SENTRY_URL>/api/0/issues/<issue_id>/stats/?stat=events&resolution=1d" \
  | python3 -m json.tool
```

This shows the error trend over time — is it getting worse, stable, or declining?

## What to return

Structure your output as follows:

### Error Details
- Exception type and message
- Culprit (function/endpoint where the error occurs)

### Stacktrace (Application Frames)
For each relevant frame (skip framework internals):
- File path (relative to project root)
- Function name
- Line number
- Context lines (the code around the error)

### Breadcrumbs
The last 10-15 breadcrumbs leading to the error — these tell the story of what happened.

### Environment & Tags
- Which environments are affected (production, staging, etc.)
- Which releases
- Any notable tag patterns (specific URLs, browsers, user segments)

### Frequency & Trend
- Total occurrences and affected users
- Trend direction (increasing, stable, declining)
- When it started and when it was last seen

### Raw Data Notes
Flag anything unusual — multiple different stacktraces for the same issue, intermittent patterns, or data that suggests the root cause might not be obvious from the stacktrace alone.
