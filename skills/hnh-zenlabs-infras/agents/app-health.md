# App Health Agent

Check application-level health: Sentry error rates and recent critical issues across all ZenLabs projects.

## Sentry Data

### Setup

Read `~/.zshrc` to get `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, and `SENTRY_URL`. Inline the literal values in curl commands — don't use `$ENV_VAR` syntax.

### 1. List All Projects

```bash
curl -s -H "Authorization: Bearer <SENTRY_AUTH_TOKEN>" \
  "<SENTRY_URL>/api/0/organizations/<SENTRY_ORG>/projects/" | python3 -c "
import json, sys
projects = json.load(sys.stdin)
for p in projects:
    print(f'{p[\"slug\"]}\t{p[\"name\"]}\t{p.get(\"platform\", \"N/A\")}')
"
```

### 2. Unresolved Issues Per Project (last 24h)

For each project from step 1, fetch unresolved issue count and recent events:

```bash
# Unresolved issues with event counts (last 24h)
curl -s -H "Authorization: Bearer <SENTRY_AUTH_TOKEN>" \
  "<SENTRY_URL>/api/0/projects/<SENTRY_ORG>/<PROJECT_SLUG>/issues/?query=is:unresolved&statsPeriod=24h&sort=freq" | python3 -c "
import json, sys
issues = json.load(sys.stdin)
total_issues = len(issues)
total_events = sum(int(i.get('count', '0')) for i in issues)
total_users = sum(int(i.get('userCount', 0)) for i in issues)
print(f'unresolved={total_issues} events_24h={total_events} users_affected={total_users}')
# Top 3 by frequency
for i in issues[:3]:
    print(f'  [{i.get(\"shortId\", \"?\")}] {i[\"title\"]} — events={i.get(\"count\", \"?\")} users={i.get(\"userCount\", 0)}')
"
```

### 3. New Issues (appeared in last 24h)

```bash
curl -s -H "Authorization: Bearer <SENTRY_AUTH_TOKEN>" \
  "<SENTRY_URL>/api/0/organizations/<SENTRY_ORG>/issues/?query=is:unresolved+firstSeen:-24h&statsPeriod=24h&sort=date" | python3 -c "
import json, sys
issues = json.load(sys.stdin)
print(f'new_issues_24h={len(issues)}')
for i in issues[:5]:
    print(f'  [{i.get(\"shortId\", \"?\")}] {i[\"title\"]} — project={i[\"project\"][\"slug\"]} events={i.get(\"count\", \"?\")}')
"
```

## Output Format

Return all raw outputs clearly labeled:
```
=== SENTRY PROJECTS ===
(output)

=== SENTRY: project-slug ===
(output per project)

=== NEW ISSUES (24h) ===
(output)
```

Include raw data — the parent skill formats the final report.
