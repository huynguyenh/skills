---
name: hnh-zenlabs-release
description: >
  Set up CI/CD and deploy ZenLabs services to production — GitHub Actions workflow, Dockerfile, ECR, Helm values, ArgoCD, GitHub secrets, and DNS. Use this skill whenever the user wants to deploy a new service, set up a release pipeline, create a production deployment, or says "release this", "deploy this", "set up CI/CD", or "make this live". Also trigger when the user mentions ArgoCD, ECR, Helm values, or the devops repo in a deployment context.
---

# ZenLabs Release Pipeline

Set up and manage the full CI/CD pipeline for ZenLabs services: GitHub Actions → Docker → ECR → DevOps repo → ArgoCD → Kubernetes (EKS).

## Architecture

```
Source Repo (push tag v*.*.*)
  → GitHub Actions (build Docker image)
  → Push to ECR (478581585074.dkr.ecr.ap-southeast-1.amazonaws.com/{service}:{tag})
  → Update devops repo (apps/{service}/values.production.yaml)
  → ArgoCD detects change
  → Deploy to Kubernetes (EKS, prod namespace)
```

## Credentials

All credentials live in `~/.zshrc`. Read them inline — never hardcode in this skill or any file.

**IMPORTANT:** There are TWO sets of AWS credentials with different purposes:

| Env Var | Purpose | Used For |
|---------|---------|----------|
| `ZENLABS_AWS_ACCESS_KEY_ID` | AWS root account | **Local only** — ECR create, Route53 DNS, aws CLI |
| `ZENLABS_AWS_SECRET_ACCESS_KEY` | AWS root account secret | **Local only** |
| `ZENLABS_GH_AWS_ACCESS_KEY_ID` | AWS IAM user (`github-action`) | **GitHub secrets** — CI/CD pipeline assumes IAM role |
| `ZENLABS_GH_AWS_SECRET_ACCESS_KEY` | AWS IAM user secret | **GitHub secrets** |
| `ZENLABS_DEVOPS_SSH_PRIVATE_KEY` | SSH key for pushing to `zenlbs/devops` repo | **GitHub secrets** + local |
| `ZENLABS_GO_COMMON_SSH_PRIVATE_KEY` | SSH key for Go private modules (backend only) | **GitHub secrets** + local |

**Why two sets?** The root account credentials cannot assume IAM roles. GitHub Actions needs the IAM user credentials to assume `arn:aws:iam::478581585074:role/github-action` for ECR access. Using root account credentials in GitHub secrets will fail with "Roles may not be assumed by root accounts."

### How to use credentials

```bash
# For GitHub secrets — use ZENLABS_GH_* (IAM user):
GH_AWS_KEY=$(grep ZENLABS_GH_AWS_ACCESS_KEY_ID ~/.zshrc | cut -d'"' -f2)
echo "$GH_AWS_KEY" | gh secret set AWS_ACCESS_KEY_ID -R zenlbs/{repo}

# For local AWS operations — use ZENLABS_AWS_* (root account):
AWS_KEY=$(grep 'ZENLABS_AWS_ACCESS_KEY_ID' ~/.zshrc | head -1 | cut -d'"' -f2)
AWS_ACCESS_KEY_ID=$AWS_KEY aws ecr create-repository ...
```

## Setting Up a New Service

### Step 1: Determine service type

- **Frontend** (Next.js): uses `frontend-production.yml` workflow, port 3000, `Dockerfile.production` with Node
- **Backend** (Go): uses `backend-production.yml` workflow, port 8080, Go-specific Dockerfile

### Step 2: Add Dockerfile.production to the service repo

For **frontend** (Next.js):

```dockerfile
# syntax = docker/dockerfile:1
ARG NODE_VERSION=22.3.0
FROM node:${NODE_VERSION}-slim AS base
WORKDIR /app
ENV NODE_ENV="production"
ENV CI="true"
ENV HUSKY="0"

FROM base AS build
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential node-gyp pkg-config python-is-python3 git
COPY package.json package-lock.json ./
RUN npm ci --include=dev
COPY . .
RUN npm run build
RUN npm prune --production

FROM base
COPY --from=build /app /app
EXPOSE 3000
CMD [ "npm", "run", "start" ]
```

### Step 3: Add GitHub Actions workflow

Copy from the devops repo templates:

```bash
# Clone devops if not already cloned
gh repo clone zenlbs/devops ~/ws/code/github.com/zenlbs/devops

# For frontend
mkdir -p {service-repo}/.github/workflows
cp ~/ws/code/github.com/zenlbs/devops/github-workflows/frontend-production.yml \
   {service-repo}/.github/workflows/frontend-production.yml

# For backend
cp ~/ws/code/github.com/zenlbs/devops/github-workflows/backend-production.yml \
   {service-repo}/.github/workflows/backend-production.yml
```

Or write the workflow file directly — it's the same across all services (uses `${{ github.event.repository.name }}` for auto-detection).

### Step 4: Set GitHub secrets on the service repo

Read credentials from `~/.zshrc` and set them. **Use `ZENLABS_GH_*` for AWS keys** (IAM user, NOT root):

```bash
# Read values — IMPORTANT: use GH_ prefix for AWS keys
AWS_KEY=$(grep ZENLABS_GH_AWS_ACCESS_KEY_ID ~/.zshrc | cut -d'"' -f2)
AWS_SECRET=$(grep ZENLABS_GH_AWS_SECRET_ACCESS_KEY ~/.zshrc | cut -d'"' -f2)
DEVOPS_SSH=$(grep ZENLABS_DEVOPS_SSH_PRIVATE_KEY ~/.zshrc | cut -d'"' -f2)
GO_SSH=$(grep ZENLABS_GO_COMMON_SSH_PRIVATE_KEY ~/.zshrc | cut -d'"' -f2)

# Set on repo
echo "$AWS_KEY" | gh secret set AWS_ACCESS_KEY_ID -R zenlbs/{repo}
echo "$AWS_SECRET" | gh secret set AWS_SECRET_ACCESS_KEY -R zenlbs/{repo}
echo "$DEVOPS_SSH" | gh secret set DEVOPS_SSH_PRIVATE_KEY -R zenlbs/{repo}
echo "$GO_SSH" | gh secret set GO_COMMON_SSH_PRIVATE_KEY -R zenlbs/{repo}
```

Verify:
```bash
gh api repos/zenlbs/{repo}/actions/secrets --jq '.secrets[].name'
# Should show: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DEVOPS_SSH_PRIVATE_KEY, GO_COMMON_SSH_PRIVATE_KEY
```

### Step 5: Create GitHub environment

```bash
gh api repos/zenlbs/{repo}/environments/production -X PUT
```

### Step 6: Create ECR repository

This requires AWS admin access. The `github-action` IAM user/role does NOT have `ecr:CreateRepository` permission.

Option A — If the user has AWS console access:
> AWS Console → ECR → Create repository → Private → Name: `{service-name}` → Region: `ap-southeast-1`

Option B — If a different AWS profile has admin access:
```bash
aws ecr create-repository --repository-name {service-name} --region ap-southeast-1 --profile admin
```

The ECR repo URL will be: `478581585074.dkr.ecr.ap-southeast-1.amazonaws.com/{service-name}`

### Step 7: Create app config in devops repo

```bash
cd ~/ws/code/github.com/zenlbs/devops
git pull

mkdir -p apps/{service-name}
```

**Chart.yaml:**
```yaml
apiVersion: v2
name: {service-name}
description: {Service Description}
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
  - name: app
    version: "*"
    repository: "file://../../charts/app"
```

**values.production.yaml** (frontend example):
```yaml
app:
  fullnameOverride: "{service-name}"
  nameOverride: "{service-name}"
  image:
    repository: "478581585074.dkr.ecr.ap-southeast-1.amazonaws.com/{service-name}"
    pullPolicy: IfNotPresent
    tag: "initial"
  envFromExternalSecrets: []
  serviceAccount:
    create: true
    annotations: {}
  workloads:
    web:
      mode: api
      replicaCount: 1
      service:
        type: ClusterIP
        port: 3000    # 3000 for frontend, 8080 for backend
      ingress:
        enabled: true
        className: nginx
        annotations:
        hosts:
          - host: {service-name}.zenlabs.gg
            paths:
              - path: /
                pathType: Prefix
      resources:
        limits:
          memory: 512Mi
        requests:
          cpu: 100m
          memory: 256Mi
      autoscaling:
        enabled: false
        minReplicas: 2
        maxReplicas: 5
        targetCPUUtilizationPercentage: 70
        targetMemoryUtilizationPercentage: 80
      readinessProbe:
        tcpSocket:
          port: http
        initialDelaySeconds: 10
        periodSeconds: 15
      livenessProbe:
        tcpSocket:
          port: http
        initialDelaySeconds: 30
        periodSeconds: 30
```

### Step 8: Create ArgoCD application definition

```yaml
# apps/argocd/templates/{service-name}-prod.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {service-name}-prod
  namespace: argocd
  labels:
    app: {service-name}
    environment: production
    tier: application
spec:
  project: default
  source:
    repoURL: <email>:zenlbs/devops.git
    targetRevision: HEAD
    path: apps/{service-name}
    helm:
      valueFiles:
        - values.production.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
  revisionHistoryLimit: 5
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
```

### Step 9: Commit and push devops changes

```bash
cd ~/ws/code/github.com/zenlbs/devops
git config user.name "huynguyenh"
git config user.email "<email>"
git add apps/{service-name}/ apps/argocd/templates/{service-name}-prod.yaml
git commit -m "Add {service-name} app config and ArgoCD definition"
git push
```

### Step 10: DNS (Route53)

Add an A record in Route53 for `{service-name}.zenlabs.gg` pointing to the nginx ingress IP (`54.169.93.177`).

This requires AWS console access → Route53 → `zenlabs.gg` hosted zone → Create Record.

### Step 11: Deploy

```bash
cd ~/ws/code/github.com/zenlbs/{repo}
git tag v0.1.0
git push origin v0.1.0
```

Monitor deployment — there are **two stages**:

**Stage 1: GitHub Actions (build + push image)**
```bash
# Wait for the pipeline to finish building the Docker image
gh run watch $(gh run list -R zenlbs/{repo} --limit 1 --json databaseId -q '.[0].databaseId') -R zenlbs/{repo}
```

**Stage 2: ArgoCD (actual deployment to K8s)**
The GitHub Actions pipeline only builds and pushes the Docker image to ECR, then updates the devops repo. The **actual deployment** is handled by ArgoCD, which picks up the devops repo change.

ArgoCD typically syncs within 3 minutes. Verify deployment status:
```bash
# Check if the site is responding
curl -so /dev/null -w "%{http_code}" https://{service-name}.zenlabs.gg
# Should return 200

# If 503 or not responding, check ArgoCD UI:
# https://argocd.zenlabs.gg → find {service-name}-prod app → check sync status and pod health
```

**Important:** A successful GitHub Actions run does NOT mean the deploy is done. Always verify via ArgoCD or the actual endpoint. Common ArgoCD delays:
- Auto-sync interval: up to 3 minutes
- Pod startup: 10-30 seconds after sync
- If ArgoCD shows `OutOfSync`, click Sync manually

## Releasing a New Version

For subsequent releases after initial setup:

```bash
cd ~/ws/code/github.com/zenlbs/{repo}
git tag v{major}.{minor}.{patch}
git push origin v{major}.{minor}.{patch}
```

The pipeline has two stages:
1. **GitHub Actions** — builds Docker image, pushes to ECR, updates devops repo
2. **ArgoCD** — detects devops repo change, syncs to Kubernetes (this is the actual deploy)

Always verify the deploy via the live endpoint, not just the GitHub Actions status.

## Rollback

```bash
# Option 1: Tag a previous commit as new version
git tag v1.2.4 <previous-commit-sha>
git push origin v1.2.4

# Option 2: Update devops repo directly
cd ~/ws/code/github.com/zenlbs/devops
# Edit apps/{service}/values.production.yaml → change image.tag to previous version
git commit -am "Rollback {service} to v1.2.2"
git push
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| GH Actions ✅ but site still 503 | ArgoCD hasn't synced yet | Wait 3 min or manually Sync in ArgoCD UI |
| 503 every ~10 minutes | Pod OOMKilled (memory limit too low) | Increase `resources.limits.memory` in values.production.yaml |
| 503 Service Unavailable | Pod not ready, crashing, or node issue | Check ArgoCD UI → pod status and logs |
| `FailedScheduling` + `disk-pressure` | Node out of disk | SSH into node: `sudo crictl rmi --prune`, or reboot instance from EC2 Console |
| `ImagePullBackOff` | ECR repo doesn't exist or image tag wrong | Create ECR repo or check tag |
| `CrashLoopBackOff` | App crashing on startup | Check pod logs for error |
| ArgoCD `ComparisonError` | Can't render Helm chart | Sync/Refresh in ArgoCD UI |
| GitHub Actions `AccessDenied` on ECR | Missing secrets or wrong role | Verify secrets with `gh api repos/.../actions/secrets` |
| ArgoCD synced but old pods remain | Old replica sets not cleaned up | Sync with "Prune" checkbox enabled |
| Scale to 0 doesn't work | Helm chart has `default 1` in template | Use `replicaCount: 0` at the workloads level, not nested under `app` |

## Reference

- **Devops repo:** `zenlbs/devops` — Helm charts, values, ArgoCD definitions
- **AWS Account:** `478581585074`
- **AWS Region:** `ap-southeast-1` (Singapore)
- **ECR Registry:** `478581585074.dkr.ecr.ap-southeast-1.amazonaws.com`
- **ArgoCD:** `https://argocd.zenlabs.gg`
- **Ingress IP:** `54.169.93.177`
- **DNS:** Route53 → `zenlabs.gg` hosted zone
- **Notion guide:** https://www.notion.so/zenlbs/How-to-Deploy-a-new-Repo-with-CI-CD-2cbff75e4b9f80f297a0c8eda253e3d3
