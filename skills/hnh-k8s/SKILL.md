---
name: hnh-k8s
description: |
  Debug and monitor Kubernetes (EKS) clusters — check pod status, read logs, inspect events, troubleshoot crashes, and view resource usage via kubectl. Use this skill whenever the user mentions Kubernetes, K8s, EKS, pods, deployments, services, or asks about server health, container status, or application debugging in a cluster context. Also trigger when the user says "is the server up", "check the backend", "why is it crashing", "show me logs", "pod restart", or any production debugging request — since the infrastructure runs on EKS. Trigger on namespace names, deployment names, or any kubectl-related request.
---

# Kubernetes (EKS) Debugging & Monitoring Skill

Debug and monitor applications running on AWS EKS using `kubectl`. This skill is focused on **observability and troubleshooting** — deployments and infrastructure changes are handled by ArgoCD and Terraform.

## Prerequisites

`kubectl` must be installed and configured to talk to the EKS cluster.

Check connectivity:
```bash
kubectl cluster-info
```

If this fails with "connection refused" or "no configuration", the user needs to configure access:
```bash
# Update kubeconfig for an EKS cluster
aws eks update-kubeconfig --name CLUSTER_NAME --region REGION

# Verify
kubectl get nodes
```

If `aws` CLI isn't installed, that's needed first (see hnh-aws skill).

Check current context:
```bash
kubectl config current-context
kubectl config get-contexts
```

If multiple clusters exist, ask the user which one to target.

## Quick Health Check

When the user asks "is everything up?" or "check the server", run this diagnostic sequence:

```bash
# 1. Node health
kubectl get nodes

# 2. All pods with issues (not Running/Completed)
kubectl get pods --all-namespaces --field-selector 'status.phase!=Running,status.phase!=Succeeded' 2>/dev/null

# 3. Recent events with warnings
kubectl get events --all-namespaces --field-selector type=Warning --sort-by='.lastTimestamp' | tail -20

# 4. Pods with restart counts > 0
kubectl get pods --all-namespaces -o json | jq -r '.items[] | select(.status.containerStatuses[]?.restartCount > 0) | "\(.metadata.namespace)/\(.metadata.name) restarts=\(.status.containerStatuses[0].restartCount)"'
```

Summarize findings concisely: what's healthy, what's not, and what needs attention.

## Pod Operations

### List and Status

```bash
# All pods in a namespace
kubectl get pods -n NAMESPACE

# Pods with more details (node, IP, restarts)
kubectl get pods -n NAMESPACE -o wide

# Filter by label
kubectl get pods -n NAMESPACE -l app=APP_NAME

# Pod details (events, conditions, container status)
kubectl describe pod POD_NAME -n NAMESPACE

# Check why a pod is failing
kubectl get pod POD_NAME -n NAMESPACE -o jsonpath='{.status.containerStatuses[*].state}' | jq .
```

### Logs

```bash
# Current logs
kubectl logs POD_NAME -n NAMESPACE

# Follow logs (live tail)
kubectl logs -f POD_NAME -n NAMESPACE

# Last N lines
kubectl logs --tail=100 POD_NAME -n NAMESPACE

# Previous container logs (after a crash/restart)
kubectl logs POD_NAME -n NAMESPACE --previous

# Specific container (multi-container pod)
kubectl logs POD_NAME -n NAMESPACE -c CONTAINER_NAME

# Logs from all pods matching a label
kubectl logs -l app=APP_NAME -n NAMESPACE --tail=50

# Logs since a time
kubectl logs POD_NAME -n NAMESPACE --since=1h
kubectl logs POD_NAME -n NAMESPACE --since=30m

# Search logs for errors
kubectl logs POD_NAME -n NAMESPACE --tail=500 | grep -i "error\|exception\|fatal\|panic"
```

### Debugging Crashes

When a pod is in CrashLoopBackOff or keeps restarting:

```bash
# 1. Check the pod's events and state
kubectl describe pod POD_NAME -n NAMESPACE

# 2. Check previous container's logs (the one that crashed)
kubectl logs POD_NAME -n NAMESPACE --previous

# 3. Check exit code and reason
kubectl get pod POD_NAME -n NAMESPACE -o jsonpath='{.status.containerStatuses[0].lastState.terminated}' | jq .

# 4. Check resource limits vs usage
kubectl top pod POD_NAME -n NAMESPACE 2>/dev/null

# 5. Check if it's an OOMKill
kubectl get pod POD_NAME -n NAMESPACE -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}'
```

Common crash reasons:
- **OOMKilled**: Container exceeded memory limit → check memory limits and actual usage
- **Error (exit code 1)**: Application error → check logs with `--previous`
- **Error (exit code 137)**: SIGKILL (usually OOM or eviction) → check node resources
- **Error (exit code 143)**: SIGTERM (graceful shutdown) → usually normal during rollouts
- **CrashLoopBackOff**: Container keeps crashing → check `--previous` logs and describe pod

### Execute into a Pod

```bash
# Open a shell
kubectl exec -it POD_NAME -n NAMESPACE -- /bin/sh

# Run a single command
kubectl exec POD_NAME -n NAMESPACE -- env
kubectl exec POD_NAME -n NAMESPACE -- cat /app/config.yaml

# Specific container
kubectl exec -it POD_NAME -n NAMESPACE -c CONTAINER_NAME -- /bin/sh
```

## Deployment Operations

```bash
# List deployments
kubectl get deployments -n NAMESPACE

# Deployment details (strategy, replicas, conditions)
kubectl describe deployment DEPLOYMENT_NAME -n NAMESPACE

# Rollout status
kubectl rollout status deployment/DEPLOYMENT_NAME -n NAMESPACE

# Rollout history
kubectl rollout history deployment/DEPLOYMENT_NAME -n NAMESPACE

# Current image version
kubectl get deployment DEPLOYMENT_NAME -n NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check all container images in a namespace
kubectl get pods -n NAMESPACE -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
```

Note: Do NOT perform rollbacks or scaling — those should go through ArgoCD/Terraform. Only observe and report.

## Services & Networking

```bash
# List services
kubectl get svc -n NAMESPACE

# Service details (endpoints, ports)
kubectl describe svc SERVICE_NAME -n NAMESPACE

# Check if endpoints exist (no endpoints = nothing backing the service)
kubectl get endpoints SERVICE_NAME -n NAMESPACE

# Ingress rules
kubectl get ingress -n NAMESPACE
kubectl describe ingress INGRESS_NAME -n NAMESPACE

# Test DNS resolution from inside a pod
kubectl exec -it POD_NAME -n NAMESPACE -- nslookup SERVICE_NAME
```

## Resource Usage

```bash
# Node resource usage
kubectl top nodes

# Pod resource usage in a namespace
kubectl top pods -n NAMESPACE

# Sort by CPU
kubectl top pods -n NAMESPACE --sort-by=cpu

# Sort by memory
kubectl top pods -n NAMESPACE --sort-by=memory

# Resource requests vs limits for a deployment
kubectl get deployment DEPLOYMENT_NAME -n NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].resources}' | jq .
```

Note: `kubectl top` requires metrics-server to be installed. If it fails, mention this to the user.

## ConfigMaps & Secrets

```bash
# List configmaps
kubectl get configmap -n NAMESPACE

# View configmap data
kubectl get configmap CONFIG_NAME -n NAMESPACE -o yaml

# List secrets (names only — never show secret values unless explicitly asked)
kubectl get secrets -n NAMESPACE

# Check if a secret exists and its keys
kubectl get secret SECRET_NAME -n NAMESPACE -o jsonpath='{.data}' | jq 'keys'
```

## Events

Events are extremely useful for debugging — they tell you what Kubernetes itself observed:

```bash
# All events in a namespace, sorted by time
kubectl get events -n NAMESPACE --sort-by='.lastTimestamp'

# Warning events only
kubectl get events -n NAMESPACE --field-selector type=Warning --sort-by='.lastTimestamp'

# Events for a specific pod
kubectl get events -n NAMESPACE --field-selector involvedObject.name=POD_NAME

# Recent events (last 1 hour)
kubectl get events -n NAMESPACE --sort-by='.lastTimestamp' | tail -30
```

## Namespace Discovery

If the user doesn't specify a namespace, list available ones:

```bash
kubectl get namespaces
```

Common patterns: `default`, `production`, `staging`, `kube-system`, or app-specific namespaces. Ask the user which namespace to target if unclear.

## Safety Rules

- This skill is for **read-only debugging and monitoring**. Deployments, scaling, and config changes go through ArgoCD and Terraform.
- NEVER delete pods, deployments, services, or any resources without explicit user confirmation
- NEVER modify deployments, replicas, or resource limits directly — suggest the proper GitOps workflow instead
- NEVER display secret values in plain text unless the user explicitly asks
- NEVER run `kubectl apply`, `kubectl patch`, or `kubectl edit` unless the user specifically requests a one-off fix and understands the implications
- If asked to make changes, remind the user that infrastructure is managed by ArgoCD/Terraform and suggest the proper workflow
- Port-forwarding (`kubectl port-forward`) is OK for debugging — it's temporary and local
