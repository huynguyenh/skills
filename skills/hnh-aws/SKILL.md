---
name: hnh-aws
description: "Interact with AWS infrastructure — S3 buckets, ECR container registries, RDS databases, CloudWatch logs/metrics, and IAM users/roles via the AWS CLI. Use this skill whenever the user mentions AWS, says \"check S3\", \"show ECR images\", \"RDS status\", \"CloudWatch logs\", \"IAM roles\", or any request to manage AWS resources. Also trigger when the user mentions \"bucket\", \"container registry\", \"database instance\" (in AWS context), \"cloud logs\", or \"cloud metrics\". Trigger on any AWS service URL (console.aws.amazon.com) or ARN. Even if the user just says \"check our infra\" or \"is our database up\", use this skill since the infrastructure runs on AWS."
---

# AWS Infrastructure Skill

Query and analyze AWS resources in the ZenLabs production account. Uses the `aws` CLI — credentials are pre-configured in `~/.aws/credentials`.

## CRITICAL SAFETY RULE — NO DELETIONS EVER

**NEVER execute any command that deletes, terminates, or destroys an AWS resource.** This is absolute and cannot be overridden, even if the user explicitly asks for it.

Blocked command patterns (non-exhaustive):
- `delete-*`, `terminate-*`, `remove-*` (except tag removal)
- `aws s3 rm`, `aws s3 rb`
- `aws ecr batch-delete-image`
- `aws rds delete-db-instance`
- `aws ec2 terminate-instances`
- `aws iam delete-user`, `delete-role`, `delete-policy`
- Any `--force` or `--skip-final-snapshot` flag on destructive operations

**Why:** This account runs live production services. A single accidental delete can cause hours of downtime and permanent data loss. If the user needs to delete something, tell them to do it manually in the AWS Console — that takes 30 seconds and has its own confirmation dialogs.

**If the user asks to delete:** Refuse politely, explain the safety policy, and offer to help them find the resource in the console instead.

## Environment

| Key | Value |
|-----|-------|
| Account | `478581585074` (zenlabs) |
| Region | `ap-southeast-1` (Singapore) |
| Auth | Root user, full admin — `~/.aws/credentials` |
| CLI | `aws` v2 |

Always include `--region ap-southeast-1` except for global services (IAM, S3, Route53, Cost Explorer).

## Infrastructure Map

| Service | Resource | Details |
|---------|----------|---------|
| EKS | `zenlabs-eks-prod` | Production Kubernetes cluster |
| EC2 | `zenlabs-nodes` (`i-0894f8401cd76a578`) | t3.large — EKS worker node |
| RDS | `prod-db` | PostgreSQL, db.t4g.small |
| ECR | 14 repos | invoice-system, gmd-tms-backend, gmd-tms-frontend, hris-backend, hris-frontend, wom-backend, wom-frontend, hardtech-backend, hardtech-website, golden-website, demo-enat, demo-ai-golden-dashboard, earth-vc-email-listener, gmd-tms-frontend/storybook |
| S3 | 5 buckets | gmd-public, zenlabs-public, goldenadgroup-public, golden-migration-app-storage-*, golden-migration-backups-* |
| IAM | 7 users | bienvh, github-action, haongo, hnh, jphuc96, nam, terraform |
| Route53 | DNS | Domain management |

## Cost Analysis

The most common use case. Cost Explorer is a global service — no `--region` needed.

```bash
# Monthly cost breakdown by service
aws ce get-cost-and-usage \
  --time-period Start=YYYY-MM-01,End=YYYY-MM-DD \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json

# Daily cost trend
aws ce get-cost-and-usage \
  --time-period Start=YYYY-MM-01,End=YYYY-MM-DD \
  --granularity DAILY \
  --metrics BlendedCost \
  --output json

# Cost forecast
aws ce get-cost-forecast \
  --time-period Start=YYYY-MM-DD,End=YYYY-MM-DD \
  --metric BLENDED_COST \
  --granularity MONTHLY
```

**Important:** JMESPath `--query` has escaping issues in zsh. Always pipe through `python3` for cost data:

```bash
aws ce get-cost-and-usage ... --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for group in sorted(data['ResultsByTime'][0]['Groups'],
                    key=lambda x: float(x['Metrics']['BlendedCost']['Amount']), reverse=True):
    cost = float(group['Metrics']['BlendedCost']['Amount'])
    if cost > 0.01:
        print(f'{group[\"Keys\"][0]:50s} \${cost:.2f}')
"
```

## CloudWatch Metrics

Metrics for monitoring EC2, RDS, and EKS health. Use `date -u -v-1H` (macOS) for time math.

### EC2 Metrics (zenlabs-nodes)

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0894f8401cd76a578 \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average Maximum \
  --region ap-southeast-1
```

Available EC2 metrics: `CPUUtilization`, `CPUCreditBalance`, `CPUCreditUsage`, `NetworkIn`, `NetworkOut`, `EBSReadOps`, `EBSWriteOps`, `StatusCheckFailed`, `StatusCheckFailed_Instance`, `StatusCheckFailed_System`.

### RDS Metrics (prod-db)

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average Maximum \
  --region ap-southeast-1
```

Useful RDS metrics: `CPUUtilization`, `DatabaseConnections`, `FreeStorageSpace`, `ReadIOPS`, `WriteIOPS`, `FreeableMemory`, `NetworkReceiveThroughput`, `NetworkTransmitThroughput`.

## EKS

```bash
# Cluster info
aws eks describe-cluster --name zenlabs-eks-prod --region ap-southeast-1

# Node groups
aws eks list-nodegroups --cluster-name zenlabs-eks-prod --region ap-southeast-1

# Describe node group
aws eks describe-nodegroup --cluster-name zenlabs-eks-prod --nodegroup-name NODEGROUP --region ap-southeast-1
```

## ECR

```bash
# List all repos
aws ecr describe-repositories --region ap-southeast-1 \
  --query 'repositories[].repositoryName' --output table

# Latest 5 images in a repo
aws ecr describe-images --repository-name REPO_NAME --region ap-southeast-1 \
  --query 'sort_by(imageDetails, &imagePushedAt)[-5:].[imageTags[0], imagePushedAt, imageSizeInBytes]' \
  --output table

# Image count in a repo
aws ecr describe-images --repository-name REPO_NAME --region ap-southeast-1 \
  --query 'length(imageDetails)'
```

## RDS

```bash
# Instance status
aws rds describe-db-instances --region ap-southeast-1 \
  --query 'DBInstances[].{ID:DBInstanceIdentifier,Engine:Engine,Status:DBInstanceStatus,Class:DBInstanceClass}' \
  --output table

# Recent events
aws rds describe-events --source-type db-instance --duration 1440 --region ap-southeast-1

# Snapshots
aws rds describe-db-snapshots --db-instance-identifier prod-db --region ap-southeast-1 \
  --query 'sort_by(DBSnapshots,&SnapshotCreateTime)[-5:].{ID:DBSnapshotIdentifier,Created:SnapshotCreateTime,Status:Status}' \
  --output table
```

## S3

```bash
# List buckets
aws s3 ls

# List bucket contents
aws s3 ls s3://BUCKET_NAME/ --recursive --summarize

# Bucket size
aws s3 ls s3://BUCKET_NAME/ --recursive --summarize | tail -2

# Presigned URL (temporary share link)
aws s3 presign s3://BUCKET_NAME/path/file --expires-in 3600
```

## IAM

```bash
# Current identity
aws sts get-caller-identity

# List users
aws iam list-users --query 'Users[].{User:UserName,Created:CreateDate}' --output table

# User policies
aws iam list-attached-user-policies --user-name USERNAME
aws iam list-user-policies --user-name USERNAME

# List roles
aws iam list-roles --query 'Roles[].{Name:RoleName,Created:CreateDate}' --output table

# Access key last used
aws iam get-access-key-last-used --access-key-id ACCESS_KEY_ID
```

## CloudWatch Logs

```bash
# List log groups
aws logs describe-log-groups --region ap-southeast-1 \
  --query 'logGroups[].{Name:logGroupName,Bytes:storedBytes}' --output table

# Recent events from a log group
aws logs filter-log-events \
  --log-group-name LOG_GROUP \
  --start-time $(python3 -c "import time; print(int((time.time()-3600)*1000))") \
  --region ap-southeast-1 --limit 50

# Search for errors
aws logs filter-log-events \
  --log-group-name LOG_GROUP \
  --filter-pattern "ERROR" \
  --start-time $(python3 -c "import time; print(int((time.time()-3600)*1000))") \
  --region ap-southeast-1 --limit 20
```

## Route53

```bash
# List hosted zones
aws route53 list-hosted-zones --query 'HostedZones[].{Name:Name,ID:Id,Records:ResourceRecordSetCount}' --output table

# List records in a zone
aws route53 list-resource-record-sets --hosted-zone-id ZONE_ID \
  --query 'ResourceRecordSets[].{Name:Name,Type:Type,TTL:TTL}' --output table
```

## Safe Write Operations (Allowed)

- Adding/updating tags on resources
- Creating CloudWatch alarms
- Uploading files to S3
- Creating RDS snapshots, EBS snapshots
- Pushing images to ECR
- Creating IAM users, roles, policies
- Adding security group rules
- Scaling EKS node groups

## Tips

- Use `--output json | python3 -c "..."` for complex data — more reliable than `--query` in zsh
- macOS date math: `date -u -v-1H` (1h ago), `date -u -v-1d` (1d ago), `date -u -v-7d` (7d ago)
- Cost Explorer is global — no `--region` flag
- When showing metrics, calculate min/max/avg summaries rather than dumping raw datapoints
- Use `--output table` for quick human-readable output, `--output json` for programmatic parsing
