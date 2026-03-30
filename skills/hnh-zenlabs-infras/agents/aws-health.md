# AWS Resources Agent

Collect AWS resource metrics for ZenLabs production infrastructure. All commands use `aws` CLI with `--region ap-southeast-1` (unless noted). Credentials are pre-configured in `~/.aws/credentials`.

Run all commands and return structured data. Don't interpret — just collect.

## Data Collection

### 1. EC2 Instance Details & Status

```bash
# Instance type and state
aws ec2 describe-instances --instance-ids i-0894f8401cd76a578 --region ap-southeast-1 \
  --query 'Reservations[0].Instances[0].{Type:InstanceType,State:State.Name,LaunchTime:LaunchTime,PrivateIp:PrivateIpAddress}' \
  --output json

# Instance health checks
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
```

### 5. S3 Bucket Summary

```bash
aws s3api list-buckets --query 'Buckets[].{Name:Name,Created:CreationDate}' --output table
```

### 6. EKS Cluster Status (AWS API only — no kubectl)

```bash
aws eks describe-cluster --name zenlabs-eks-prod --region ap-southeast-1 \
  --query 'cluster.{Status:status,Version:version,Platform:platformVersion,Endpoint:endpoint}' \
  --output json
```

### 7. Recent RDS Events (last 24h)

```bash
aws rds describe-events --source-type db-instance --duration 1440 --region ap-southeast-1 \
  --query 'Events[].{Source:SourceIdentifier,Date:Date,Message:Message}' --output json
```

## Output Format

Return all raw outputs clearly labeled:
```
=== EC2 DETAILS ===
(output)

=== EC2 STATUS ===
(output)

=== EC2 CPU ===
(output)

=== EC2 CREDITS ===
(output)

=== EC2 NETWORK ===
(output)

=== RDS STATUS ===
(output)

=== RDS CPU ===
(output)

=== RDS STORAGE ===
(output)

=== RDS CONNECTIONS ===
(output)

=== RDS MEMORY ===
(output)

=== S3 BUCKETS ===
(output)

=== EKS CLUSTER ===
(output)

=== RDS EVENTS ===
(output)
```

Include raw data — the parent skill formats the final report.
