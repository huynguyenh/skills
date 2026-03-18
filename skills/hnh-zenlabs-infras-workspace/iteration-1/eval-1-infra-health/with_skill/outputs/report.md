## ZenLabs Infrastructure Health — 2026-03-18 22:53 UTC+7

### Overall Status: HEALTHY
EC2 and RDS are running normally with low utilization. EKS cluster is active. kubectl access unavailable from this machine (auth issue) — pod-level health could not be verified.

---

### EKS Cluster: zenlabs-eks-prod

| Property | Value | Status |
|----------|-------|--------|
| Cluster Status | ACTIVE | OK |
| Kubernetes Version | 1.33 | OK |
| Platform | eks.29 | OK |

**Nodes / Pods / Deployments**: N/A — kubectl authentication failed from this machine. Run `aws eks update-kubeconfig` with an IAM user that has cluster access to enable pod-level monitoring.

---

### AWS Services

**EC2 (EKS Worker Node — i-0894f8401cd76a578)**
| Metric | 1h Avg | 1h Max | Status |
|--------|--------|--------|--------|
| Instance State | running | — | OK |
| System Status | ok | — | OK |
| CPU Utilization | 29.3% | 31.1% | OK |

**RDS (prod-db — PostgreSQL, db.t4g.small)**
| Metric | Value | Status |
|--------|-------|--------|
| DB Status | available | OK |
| CPU Utilization | 3.5% avg, 5.1% max | OK |
| Free Storage | 16.18 GB / 20 GB (80.9% free) | OK |
| Database Connections | 13 avg, 14 max | OK |
| Freeable Memory | 611 MB avg, 606 MB min | OK |

---

### Application Health

**Sentry**: N/A — Sentry credentials not configured on this machine. Set `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, and `SENTRY_URL` in `~/.zshrc` to enable error tracking.

---

### Action Items

1. **WARNING**: kubectl authentication not working — the current IAM identity (root) is not authorized in the EKS cluster's aws-auth ConfigMap. This blocks pod-level monitoring (deployments, replicas, resource usage, crash detection). Fix by adding the root user to aws-auth or using an authorized IAM user/role.
2. **WARNING**: Sentry credentials missing — application error rates cannot be monitored. Configure Sentry environment variables to enable this section.
3. No resource-level concerns detected — EC2 CPU at ~29%, RDS CPU at ~3.5%, storage is healthy (81% free).
