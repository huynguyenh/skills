# AWS Cost Agent

Collect AWS cost data for ZenLabs. Uses AWS Cost Explorer API via `us-east-1` (global endpoint). Credentials are pre-configured in `~/.aws/credentials`.

Run all commands and return structured data. Don't interpret — just collect.

## Data Collection

### 1. Monthly Cost by Service (current + previous month)

```bash
# Current month MTD + previous full month, grouped by service
aws ce get-cost-and-usage \
  --time-period Start=$(date -v-1m -v1d +%Y-%m-%d),End=$(date -v+1d +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1 --output json
```

### 2. Daily Cost Trend (last 14 days)

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -v-14d +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --region us-east-1 --output json
```

### 3. Cost by Service (last 7 days, daily granularity)

This helps spot which service is causing any daily fluctuations.

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -v-7d +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1 --output json
```

## Output Format

Return all raw outputs clearly labeled:
```
=== MONTHLY COST BY SERVICE ===
(output)

=== DAILY COST TREND (14d) ===
(output)

=== DAILY COST BY SERVICE (7d) ===
(output)
```

Include raw data — the parent skill formats the final report.
