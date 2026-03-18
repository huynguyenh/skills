# EKS Health Agent

Gather a comprehensive snapshot of the Kubernetes cluster state. Run all commands and return structured data — don't interpret or summarize, just collect.

## Prerequisites

Verify kubectl connectivity first:
```bash
kubectl cluster-info 2>&1 | head -2
```
If this fails with "connection refused", try configuring access:
```bash
aws eks update-kubeconfig --name zenlabs-eks-prod --region ap-southeast-1
```
If it fails with "provide credentials" after kubeconfig is set, the current IAM identity is not authorized. Return a clear error message explaining this and stop — the parent skill will mark the EKS section as N/A.

## Data Collection

Run these in sequence (some depend on prior output). Use the Bash tool's timeout parameter (15000ms) on each command to avoid hanging.

### 1. Node Health & Resources

```bash
# Node status
kubectl get nodes -o wide

# Node resource usage (if metrics-server is available)
kubectl top nodes 2>/dev/null || echo "METRICS_UNAVAILABLE"
```

### 2. All Namespaces

```bash
kubectl get namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
```

### 3. Deployments Across All Namespaces

```bash
# All deployments with replica counts and images
kubectl get deployments --all-namespaces -o json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for d in data.get('items', []):
    ns = d['metadata']['namespace']
    name = d['metadata']['name']
    spec_replicas = d['spec'].get('replicas', 0)
    status = d.get('status', {})
    ready = status.get('readyReplicas', 0)
    updated = status.get('updatedReplicas', 0)
    available = status.get('availableReplicas', 0)
    containers = d['spec']['template']['spec']['containers']
    images = ', '.join(c['image'].split('/')[-1] for c in containers)
    print(f'{ns}\t{name}\t{ready}/{spec_replicas}\t{spec_replicas}\t{updated}\t{available}\t{images}')
"
```

### 4. Pod Status Across All Namespaces

```bash
# All pods with status
kubectl get pods --all-namespaces -o wide --sort-by='.metadata.namespace'

# Pods NOT in Running or Succeeded state
kubectl get pods --all-namespaces --field-selector 'status.phase!=Running,status.phase!=Succeeded' 2>/dev/null

# Pods with restarts > 0
kubectl get pods --all-namespaces -o json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for pod in data.get('items', []):
    ns = pod['metadata']['namespace']
    name = pod['metadata']['name']
    for cs in pod.get('status', {}).get('containerStatuses', []):
        restarts = cs.get('restartCount', 0)
        if restarts > 0:
            reason = ''
            last = cs.get('lastState', {}).get('terminated', {})
            if last:
                reason = last.get('reason', '')
            print(f'{ns}\t{name}\t{cs[\"name\"]}\trestarts={restarts}\treason={reason}')
"
```

### 5. Resource Usage by Pod (if metrics available)

```bash
kubectl top pods --all-namespaces --sort-by=cpu 2>/dev/null | head -20 || echo "METRICS_UNAVAILABLE"
```

### 6. Recent Warning Events (last 1h)

```bash
kubectl get events --all-namespaces --field-selector type=Warning --sort-by='.lastTimestamp' 2>/dev/null | tail -15
```

### 7. Services and Ingresses

```bash
# Services with type and external IPs
kubectl get svc --all-namespaces -o wide

# Ingress rules
kubectl get ingress --all-namespaces 2>/dev/null
```

## Output Format

Return all raw command outputs clearly labeled with headers like:
```
=== NODE STATUS ===
(output)

=== NODE RESOURCES ===
(output)

=== DEPLOYMENTS ===
(output)
```

Include the raw data — the parent skill will format the final report.
