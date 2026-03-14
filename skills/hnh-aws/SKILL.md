---
name: hnh-aws
description: |
  Interact with AWS infrastructure — S3 buckets, ECR container registries, RDS databases, CloudWatch logs/metrics, and IAM users/roles via the AWS CLI. Use this skill whenever the user mentions AWS, says "check S3", "show ECR images", "RDS status", "CloudWatch logs", "IAM roles", or any request to manage AWS resources. Also trigger when the user mentions "bucket", "container registry", "database instance" (in AWS context), "cloud logs", or "cloud metrics". Trigger on any AWS service URL (console.aws.amazon.com) or ARN. Even if the user just says "check our infra" or "is our database up", use this skill since the infrastructure runs on AWS.
---

# AWS Infrastructure Skill

Interact with AWS services using the `aws` CLI. This skill covers the core infrastructure services: **S3**, **ECR**, **RDS**, **CloudWatch**, and **IAM**.

## Prerequisites

The `aws` CLI must be installed and configured. If it's not installed, guide the user:

```bash
# macOS
brew install awscli

# Verify
aws --version
```

After installation, configure credentials:
```bash
aws configure
# Prompts for: AWS Access Key ID, Secret Access Key, Default region, Output format
```

Or for multiple accounts/environments, use named profiles:
```bash
aws configure --profile production
aws configure --profile staging
```

Check if AWS is configured before running any commands:
```bash
aws sts get-caller-identity
```

If this fails, stop and help the user configure credentials first.

## Profile Handling

If the user has multiple profiles, ask which one to use. Pass it with `--profile <name>` on every command. If only one profile exists (default), no flag needed.

Check available profiles:
```bash
aws configure list-profiles
```

## S3 — Object Storage

Common operations:

```bash
# List all buckets
aws s3 ls

# List contents of a bucket
aws s3 ls s3://bucket-name/
aws s3 ls s3://bucket-name/path/prefix/ --recursive

# Bucket size (summarize)
aws s3 ls s3://bucket-name/ --recursive --summarize | tail -2

# Copy files
aws s3 cp local-file.txt s3://bucket-name/path/
aws s3 cp s3://bucket-name/path/file.txt ./local-file.txt

# Sync directories
aws s3 sync ./local-dir s3://bucket-name/path/ --delete

# Presigned URL (temporary access link)
aws s3 presign s3://bucket-name/path/file.txt --expires-in 3600

# Delete
aws s3 rm s3://bucket-name/path/file.txt
aws s3 rm s3://bucket-name/path/ --recursive  # delete folder
```

## ECR — Container Registry

```bash
# List repositories
aws ecr describe-repositories --output table

# List images in a repo (most recent first)
aws ecr describe-images --repository-name REPO_NAME \
  --query 'sort_by(imageDetails,&imagePushedAt)[*].{Tag:imageTags[0],Pushed:imagePushedAt,Size:imageSizeInBytes}' \
  --output table

# Get latest image tag
aws ecr describe-images --repository-name REPO_NAME \
  --query 'sort_by(imageDetails,&imagePushedAt)[-1].imageTags[0]' \
  --output text

# Login to ECR (needed before docker push/pull)
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com

# Image lifecycle policies
aws ecr get-lifecycle-policy --repository-name REPO_NAME
```

## RDS — Relational Database Service

```bash
# List all DB instances with status
aws rds describe-db-instances \
  --query 'DBInstances[*].{ID:DBInstanceIdentifier,Engine:Engine,Status:DBInstanceStatus,Class:DBInstanceClass,Endpoint:Endpoint.Address}' \
  --output table

# Get specific instance details
aws rds describe-db-instances --db-instance-identifier INSTANCE_ID

# Check storage and connections
aws rds describe-db-instances --db-instance-identifier INSTANCE_ID \
  --query 'DBInstances[0].{Storage:AllocatedStorage,MaxStorage:MaxAllocatedStorage,StorageType:StorageType,MultiAZ:MultiAZ,Status:DBInstanceStatus}'

# Recent events (last 24h)
aws rds describe-events --source-type db-instance --duration 1440

# Snapshots
aws rds describe-db-snapshots --db-instance-identifier INSTANCE_ID \
  --query 'sort_by(DBSnapshots,&SnapshotCreateTime)[-5:].{ID:DBSnapshotIdentifier,Created:SnapshotCreateTime,Status:Status}' \
  --output table
```

## CloudWatch — Logs & Metrics

### Logs

```bash
# List log groups
aws logs describe-log-groups --query 'logGroups[*].{Name:logGroupName,Stored:storedBytes}' --output table

# Tail live logs (follow mode)
aws logs tail LOG_GROUP_NAME --follow --since 5m

# Search logs with filter pattern
aws logs filter-log-events \
  --log-group-name LOG_GROUP_NAME \
  --filter-pattern "ERROR" \
  --start-time $(date -v-1H +%s000) \
  --limit 50

# Get recent log streams
aws logs describe-log-streams \
  --log-group-name LOG_GROUP_NAME \
  --order-by LastEventTime --descending \
  --limit 5
```

### Metrics

```bash
# List available metrics for a service
aws cloudwatch list-metrics --namespace AWS/RDS

# Get CPU utilization for RDS (last 1 hour, 5-min intervals)
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=INSTANCE_ID \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average Maximum

# Active alarms
aws cloudwatch describe-alarms --state-value ALARM \
  --query 'MetricAlarms[*].{Name:AlarmName,State:StateValue,Reason:StateReason}' \
  --output table
```

## IAM — Identity & Access Management

```bash
# Who am I?
aws sts get-caller-identity

# List users
aws iam list-users --query 'Users[*].{User:UserName,Created:CreateDate}' --output table

# List roles
aws iam list-roles --query 'Roles[*].{Role:RoleName,Arn:Arn}' --output table

# Get user's policies
aws iam list-attached-user-policies --user-name USERNAME
aws iam list-user-policies --user-name USERNAME

# Get role's policies
aws iam list-attached-role-policies --role-name ROLE_NAME

# Check last access
aws iam get-access-key-last-used --access-key-id ACCESS_KEY_ID
```

## General Tips

- Always use `--output table` for human-readable output when presenting to the user
- Use `--output json` when you need to parse the response programmatically
- Use `--query` (JMESPath) to filter and shape output — avoids noisy full responses
- For destructive operations (delete, terminate), always confirm with the user first
- Use `--dry-run` where available to preview changes
- If a command fails with "Unable to locate credentials", help the user run `aws configure`
- Region matters — if results look empty, check if the right region is set (`aws configure get region`)

## Safety Rules

- NEVER create or delete IAM users/roles without explicit user confirmation
- NEVER modify security groups or network ACLs
- NEVER delete S3 buckets or RDS instances without explicit confirmation
- NEVER expose access keys, secrets, or credentials in output
- For any destructive action, describe what will happen and ask for confirmation first
