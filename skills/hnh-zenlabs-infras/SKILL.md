---
name: hnh-zenlabs-infras
description: |
  Generate a cost-focused AWS infrastructure monitoring report for ZenLabs — covering AWS Cost Explorer (monthly/daily spend by service), EC2 metrics (CPU, credits, network), RDS metrics (CPU, storage, connections, memory), S3 buckets, and EKS cluster status. Use this skill whenever the user asks about infrastructure health, costs, spending, resource utilization, or says things like "how's our infra", "infra report", "cost check", "how much are we spending", "resource usage", or any request to understand AWS costs and server health — even if they don't say "infrastructure" explicitly. Also trigger when the user mentions CPU, memory, disk, budget, or asks about AWS bills.
---

# ZenLabs Infrastructure Monitoring Report

Generate a cost-focused, decision-ready snapshot of ZenLabs AWS infrastructure. The goal is to give the user everything they need to decide: "Are costs on track, and do any resources need attention?"

## Scope

**Included:** AWS Cost Explorer, EC2 CloudWatch metrics, RDS CloudWatch metrics, S3 bucket listing, EKS cluster status (via AWS API only).

**Not included:** kubectl/pod-level data, Sentry error tracking. These are intentionally excluded — the IAM root user doesn't have EKS API server access, and Sentry credentials are not configured on this machine.

## Execution Flow

### Phase 0: Preflight

```bash
# Verify AWS CLI access — should always work
aws sts get-caller-identity --output json
```

If this fails, stop and report the error. All data collection depends on AWS CLI.

### Phase 1: Parallel Data Collection

Launch two agents simultaneously. Read each agent's `.md` file from this skill's `agents/` directory and pass its contents as the prompt.

| Agent | File | What it gathers |
|-------|------|-----------------|
| A: AWS Cost | `agents/aws-cost.md` | Cost Explorer: monthly spend by service, daily spend trend, projected costs |
| B: AWS Resources | `agents/aws-health.md` | EC2 status/metrics, RDS status/metrics, S3 buckets, EKS cluster status |

Pass to each agent:
- The current timestamp for time-range calculations
- Region: `ap-southeast-1`
- AWS CLI uses `~/.aws/credentials` (pre-configured)

### Phase 2: Synthesize & Present

Once both agents return, combine their findings into the report format below. The report should be scannable — a busy CTO should read it in 60 seconds and know if costs are on track and if anything needs attention.

**Severity classification:**

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Cost spike >50% vs prior period, disk >90%, instance down | Act now |
| WARNING | Cost trending up >20%, CPU >70%, disk >75%, credits depleted at high usage | Monitor closely |
| OK | Everything within normal bounds | No action needed |

### Report Template

```
## ZenLabs Infrastructure Monitoring — {timestamp}

### Overall Status: {HEALTHY / WARNING / CRITICAL}
{1-2 sentence executive summary — costs on track? any resource pressure?}

---

### AWS Cost Summary

**Month-to-date: ${MTD_TOTAL} (projected: ${PROJECTED})**

| Service | MTD Cost | % of Total | Projected (31d) |
|---------|----------|------------|-----------------|
| ... | $X.XX | X.X% | ~$X.XX |

**Daily cost trend (last 7 days):**
{ASCII bar chart or table showing daily spend}

{Flag any cost anomalies — spikes, new services appearing, unexpected growth}

---

### EC2 (EKS Worker Node)

**Instance:** i-0894f8401cd76a578 — {type}, running since {date}

| Metric | 1h Avg | 1h Max | Status |
|--------|--------|--------|--------|
| CPU | ...% | ...% | OK/WARNING |
| CPU Credit Balance | ... | ... | OK/WARNING |
| Network In | ... | ... | OK |
| Network Out | ... | ... | OK |

---

### RDS (prod-db)

**Instance:** {class} — {engine} {version}, {az_mode}, {storage}GB

| Metric | Current | Status |
|--------|---------|--------|
| Status | ... | OK |
| CPU | ...% | OK/WARNING |
| Free Storage | ... GB / ... GB | OK/WARNING |
| Connections | ... | OK/WARNING |
| Freeable Memory | ... MB | OK/WARNING |

---

### S3 Buckets
| Bucket | Created |
|--------|---------|
| ... | ... |

---

### Action Items
{Numbered list sorted by severity. Each item: what, why, suggested action.}
{If nothing needs attention: "No action items — infrastructure is healthy and costs are on track."}
```

## Important Notes

- This is a **read-only** skill. Never modify, scale, or restart anything.
- When a metric isn't available, show "N/A" rather than failing.
- Keep the output concise. Skip empty sections.
- Round percentages to 1 decimal place. Use human-readable sizes (GB, MB).
- macOS does not have `timeout` command by default. Use Bash tool's built-in timeout parameter instead (15000ms).
- Cost Explorer API is in `us-east-1` (global endpoint). All other commands use `ap-southeast-1`.
