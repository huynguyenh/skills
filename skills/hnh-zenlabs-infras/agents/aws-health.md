# AWS Health Agent

Collect AWS-level metrics for ZenLabs production infrastructure. All commands use `aws` CLI with `--region ap-southeast-1` (unless noted). Credentials are pre-configured in `~/.aws/credentials`.

Run all commands and return structured data. Don't interpret — just collect.

## Data Collection

### 1. EC2 Instance Status

```bash
# Instance status
aws ec2 describe-instance-status --instance-ids i-0894f8401cd76a578 --region ap-southeast-1 \
  --query 'InstanceStatuses[0].{State:InstanceState.Name,System:SystemStatus.Status,Instance:InstanceStatus.Status}' \
  --output json
```

### 2. EC2 CloudWatch Metrics (last 1 hour)

Collect these metrics for instance `i-0894f8401cd76a578`. Use 300-second (5 min) periods.

```bash
# CPU Utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0894f8401cd76a578 \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average Maximum \
  --region ap-southeast-1 --output json

# CPU Credit Balance (t3 burstable)
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUCreditBalance \
  --dimensions Name=InstanceId,Value=i-0894f8401cd76a578 \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region ap-southeast-1 --output json

# Network In/Out
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name NetworkIn \
  --dimensions Name=InstanceId,Value=i-0894f8401cd76a578 \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region ap-southeast-1 --output json

aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name NetworkOut \
  --dimensions Name=InstanceId,Value=i-0894f8401cd76a578 \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region ap-southeast-1 --output json
```

### 3. RDS Instance Status

```bash
aws rds describe-db-instances --region ap-southeast-1 --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for db in data['DBInstances']:
    print(json.dumps({
        'id': db['DBInstanceIdentifier'],
        'engine': db['Engine'],
        'version': db.get('EngineVersion', 'N/A'),
        'status': db['DBInstanceStatus'],
        'class': db['DBInstanceClass'],
        'storage_gb': db.get('AllocatedStorage', 'N/A'),
        'multi_az': db.get('MultiAZ', False),
        'endpoint': db.get('Endpoint', {}).get('Address', 'N/A')
    }, indent=2))
"
```

### 4. RDS CloudWatch Metrics (last 1 hour)

Collect for `prod-db`:

```bash
# CPU
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 --statistics Average Maximum \
  --region ap-southeast-1 --output json

# Free Storage Space
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name FreeStorageSpace \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 --statistics Average Minimum \
  --region ap-southeast-1 --output json

# Database Connections
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 --statistics Average Maximum \
  --region ap-southeast-1 --output json

# Freeable Memory
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name FreeableMemory \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 --statistics Average Minimum \
  --region ap-southeast-1 --output json

# Read/Write IOPS
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReadIOPS \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 --statistics Average \
  --region ap-southeast-1 --output json

aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name WriteIOPS \
  --dimensions Name=DBInstanceIdentifier,Value=prod-db \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 --statistics Average \
  --region ap-southeast-1 --output json
```

### 5. S3 Bucket Summary

S3 bucket listing with `--recursive --summarize` can be very slow for large buckets. Just list bucket names — that's enough for the health report.

```bash
aws s3api list-buckets --query 'Buckets[].{Name:Name,Created:CreationDate}' --output table
```

### 6. EKS Cluster Status

```bash
aws eks describe-cluster --name zenlabs-eks-prod --region ap-southeast-1 \
  --query 'cluster.{Status:status,Version:version,Platform:platformVersion,Endpoint:endpoint}' \
  --output json
```

### 7. Recent RDS Events

```bash
aws rds describe-events --source-type db-instance --duration 1440 --region ap-southeast-1 \
  --query 'Events[].{Source:SourceIdentifier,Date:Date,Message:Message}' --output json
```

## Output Format

Return all raw outputs clearly labeled:
```
=== EC2 STATUS ===
(output)

=== EC2 CPU ===
(output)

=== RDS STATUS ===
(output)
```

Include raw data — the parent skill formats the final report.
