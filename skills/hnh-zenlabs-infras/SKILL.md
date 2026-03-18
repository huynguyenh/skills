---
name: hnh-zenlabs-infras
description: |
  Generate a real-time infrastructure health report for ZenLabs — covering EKS cluster (nodes, pods, deployments, replicas, resource usage), AWS services (EC2, RDS, S3, CloudWatch metrics), and application-level health (Sentry error rates, endpoint checks). Use this skill whenever the user asks about infrastructure health, system status, resource utilization, capacity, or says things like "how's our infra", "infra report", "check the cluster", "are we running hot", "capacity check", "resource usage", or any request to understand how the production environment is holding up — even if they don't say "infrastructure" explicitly. Also trigger when the user mentions CPU, memory, disk, replicas, node pressure, or asks if they need to scale up.
---

# ZenLabs Infrastructure Health Report

Generate a unified, decision-ready snapshot of ZenLabs production infrastructure by querying EKS, AWS services, and application health in parallel. The goal is to give the user everything they need to decide: "Do I need to act on anything right now?"

## Execution Flow

### Phase 0: Preflight Checks

Before collecting data, verify access to each system. This determines which sections of the report will have live data vs. "N/A".

```bash
# 1. AWS CLI — should always work (credentials in ~/.aws/credentials)
aws sts get-caller-identity --output json

# 2. kubectl — may need kubeconfig setup
kubectl cluster-info 2>&1 | head -2
# If "connection refused" → run: aws eks update-kubeconfig --name zenlabs-eks-prod --region ap-southeast-1
# If "provide credentials" → IAM identity not authorized in aws-auth ConfigMap. Note as WARNING and skip kubectl sections.

# 3. Sentry — check if credentials exist in ~/.zshrc
grep -E "SENTRY_AUTH_TOKEN" ~/.zshrc 2>/dev/null
# If not found, skip Sentry section with a note.
```

If kubectl or Sentry are unavailable, produce the report with whatever data IS accessible. A partial report is better than no report. Mark unavailable sections clearly so the user knows what's missing.

### Phase 1: Parallel Data Collection

Launch three agents simultaneously — each gathers one slice of the picture. Read each agent's `.md` file from this skill's `agents/` directory and pass its contents as the prompt. Skip agents whose preflight check failed.

| Agent | File | What it gathers | Requires |
|-------|------|-----------------|----------|
| A: EKS Health | `agents/eks-health.md` | Nodes, pods, deployments, replicas, resource usage, warnings | kubectl access |
| B: AWS Health | `agents/aws-health.md` | EC2 metrics, RDS metrics/status, S3 usage, EKS cluster status | AWS CLI (always available) |
| C: App Health | `agents/app-health.md` | Sentry error rates and recent critical issues | Sentry credentials |

Pass to each agent:
- The current timestamp for time-range calculations
- The fact that the region is `ap-southeast-1` and the cluster is `zenlabs-eks-prod`
- Credential note: AWS CLI uses `~/.aws/credentials` (pre-configured). Sentry token is in `~/.zshrc` — read the file and inline the literal value.
- Results from preflight checks (so agents don't waste time on known-broken connections)

### Phase 2: Synthesize & Present

Once all three agents return, combine their findings into the report format below. The report should be scannable — a busy CTO should be able to read it in 60 seconds and know if anything needs attention.

**Severity classification for issues:**

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Service down, node not ready, OOMKills, disk >90%, DB connections maxed | Act now |
| WARNING | High CPU/memory (>70%), pod restarts, replica mismatch, disk >75%, elevated error rates | Monitor closely, consider scaling |
| OK | Everything within normal bounds | No action needed |

### Report Template

```
## ZenLabs Infrastructure Health — {timestamp}

### Overall Status: {HEALTHY / DEGRADED / CRITICAL}
{1-2 sentence executive summary — what's the single most important thing to know right now}

---

### EKS Cluster: zenlabs-eks-prod

**Nodes**
| Node | Status | CPU | Memory | Disk | Pods |
|------|--------|-----|--------|------|------|
| ... | Ready/NotReady | used/capacity (%) | used/capacity (%) | used% | running/capacity |

**Deployments**
| Namespace | Deployment | Ready | Desired | Up-to-date | Available | Image Tag |
|-----------|------------|-------|---------|------------|-----------|-----------|
| ... | ... | X/Y | Y | Z | Z | tag |

{Flag any deployments where ready != desired, or where replicas have changed recently}

**Pod Issues** (if any)
| Namespace | Pod | Status | Restarts | Reason |
|-----------|-----|--------|----------|--------|
| ... | ... | CrashLoopBackOff | 15 | OOMKilled |

**Recent Warnings** (last 1h)
- {event summary}

---

### AWS Services

**EC2 (EKS Worker Node)**
| Metric | Current | 1h Avg | 1h Max | Status |
|--------|---------|--------|--------|--------|
| CPU | ...% | ...% | ...% | OK/WARNING/CRITICAL |
| Network In | ... | ... | ... | ... |
| Network Out | ... | ... | ... | ... |

**RDS (prod-db)**
| Metric | Current | Status |
|--------|---------|--------|
| Status | available | OK |
| CPU | ...% | OK/WARNING |
| Free Storage | ... GB | OK/WARNING |
| Connections | .../max | OK/WARNING |
| Freeable Memory | ... MB | OK/WARNING |

**S3 Buckets**
| Bucket | Objects | Size |
|--------|---------|------|
| ... | ... | ... |

---

### Application Health

**Sentry (last 24h)**
| Project | Unresolved Issues | Events (24h) | Trend |
|---------|-------------------|--------------|-------|
| ... | ... | ... | rising/stable/falling |

**Critical Errors** (if any)
- [{short_id}] {title} — {count} events, {users} users affected

---

### Action Items
{Numbered list of things that need attention, sorted by severity. Each item should be specific and actionable:}
1. **CRITICAL**: {what} — {why} — {suggested action}
2. **WARNING**: {what} — {why} — {suggested action}

{If nothing needs attention: "No action items — infrastructure is healthy."}
```

## Important Notes

- This is a **read-only** skill. Never modify, scale, or restart anything.
- When `kubectl top` fails (metrics-server not available), note it and skip — don't error out.
- When a metric isn't available, show "N/A" rather than failing the whole report.
- Keep the output concise. Skip sections that have nothing to report (e.g., if there are no pod issues, omit the Pod Issues table).
- Round percentages to 1 decimal place. Use human-readable sizes (GB, MB).
- macOS does not have `timeout` command by default. Use Bash tool's built-in timeout parameter instead. Set 15-second timeouts on individual commands.
- Graceful degradation is critical — a partial report covering what IS accessible is always better than failing entirely. If kubectl is broken, still show AWS metrics. If Sentry is missing, still show EKS + AWS.
