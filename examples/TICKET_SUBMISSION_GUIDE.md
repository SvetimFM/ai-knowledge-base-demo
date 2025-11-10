# Ticket Submission Guide

This guide explains how to submit tickets to the HPC Ticket Triage System for automated AI-powered analysis.

## Overview

The ticket triage system uses Amazon Bedrock with your HPC Knowledge Base to automatically:
- Categorize tickets (NCCL, RCCL, CUDA, Networking, Performance, etc.)
- Assign priority levels (High, Medium, Low)
- Suggest troubleshooting actions based on knowledge base
- Store results in DynamoDB
- Send email notifications with triage results

## Ticket Formats

You can submit tickets in two formats:

### 1. JSON Format (Recommended)

JSON format provides structured data and supports all fields:

```json
{
  "id": "TICKET-001",
  "title": "Brief description of the issue",
  "description": "Detailed description of the problem including steps to reproduce, expected vs actual behavior, and any error messages",
  "email": "your-email@example.com",
  "timestamp": "2025-01-10T14:30:00Z",
  "environment": {
    "nccl_version": "2.18",
    "gpu_model": "NVIDIA A100",
    "network": "InfiniBand 200Gbps",
    "framework": "PyTorch 2.0"
  },
  "priority": "high",
  "tags": ["nccl", "performance", "multi-node"]
}
```

**Required fields:**
- `title` - Brief summary of the issue
- `description` - Detailed description

**Optional fields:**
- `id` - Unique ticket ID (auto-generated if not provided)
- `email` - Email address for triage results notification
- `timestamp` - Submission time (ISO 8601 format)
- `environment` - Technical environment details
- `priority` - Suggested priority (will be overridden by AI triage)
- `tags` - Keywords for classification

### 2. Plain Text Format

For quick submissions, plain text is supported:

```
Title: Brief description

Detailed description of the problem...

Environment:
- Key details
- Configuration info
- Error messages

Any additional context...
```

Text files will be automatically parsed, with the first line becoming the title.

## Submission Methods

### Method 1: AWS CLI (Recommended)

Upload your ticket file to the S3 bucket:

```bash
# Get bucket name from stack outputs
BUCKET=$(aws cloudformation describe-stacks \
  --profile hypearadmin \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`TicketsBucketName`].OutputValue' \
  --output text)

# Submit JSON ticket
aws s3 cp examples/tickets/my-ticket.json "s3://$BUCKET/" --profile hypearadmin

# Submit text ticket
aws s3 cp examples/tickets/my-ticket.txt "s3://$BUCKET/" --profile hypearadmin
```

### Method 2: AWS Console

1. Navigate to S3 in the AWS Console
2. Find the `hpc-tickets-ACCOUNT_ID` bucket
3. Click "Upload"
4. Select your ticket file (.json or .txt)
5. Click "Upload"

### Method 3: Automated Script

Create a submission script:

```bash
#!/bin/bash
# submit-ticket.sh

PROFILE="hypearadmin"
STACK="HpcKnowledgeBaseStack"
TICKET_FILE="$1"

if [ -z "$TICKET_FILE" ]; then
    echo "Usage: ./submit-ticket.sh <ticket-file>"
    exit 1
fi

BUCKET=$(aws cloudformation describe-stacks \
  --profile $PROFILE \
  --stack-name $STACK \
  --query 'Stacks[0].Outputs[?OutputKey==`TicketsBucketName`].OutputValue' \
  --output text)

echo "Submitting ticket to: $BUCKET"
aws s3 cp "$TICKET_FILE" "s3://$BUCKET/" --profile $PROFILE

echo "Ticket submitted! Triage will complete in ~30 seconds."
```

Usage:
```bash
chmod +x submit-ticket.sh
./submit-ticket.sh examples/tickets/my-ticket.json
```

## Viewing Triage Results

### DynamoDB Console

1. Go to DynamoDB in AWS Console
2. Select `hpc-ticket-triage-results` table
3. Click "Explore table items"
4. Find your ticket by `ticketId`

### AWS CLI

Query the results table:

```bash
# Get table name
TABLE=$(aws cloudformation describe-stacks \
  --profile hypearadmin \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`TriageTableName`].OutputValue' \
  --output text)

# Query specific ticket
aws dynamodb query \
  --profile hypearadmin \
  --table-name $TABLE \
  --key-condition-expression "ticketId = :id" \
  --expression-attribute-values '{":id":{"S":"TICKET-001"}}'

# Scan recent triages
aws dynamodb scan \
  --profile hypearadmin \
  --table-name $TABLE \
  --limit 10
```

### Email Notification

If you included an `email` field in your ticket, you'll receive an email with:
- Ticket title and description
- AI-determined category
- Priority level
- Suggested troubleshooting actions
- Relevant excerpts from knowledge base

**Note:** You must verify your email address in Amazon SES before receiving notifications.

## SES Email Setup

To enable email notifications:

1. **Verify sender email in SES:**
   ```bash
   aws ses verify-email-identity \
     --profile hypearadmin \
     --email-address noreply@your-domain.com
   ```

2. **Update Lambda environment variable:**
   - Go to Lambda console
   - Find `hpc-ticket-triage-processor` function
   - Edit environment variables
   - Set `SES_FROM_EMAIL` to your verified email

3. **For production (optional):**
   - Move SES out of sandbox mode
   - Request production access in SES console
   - This allows sending to any email address

## Triage Results Schema

Each triage result stored in DynamoDB contains:

```json
{
  "ticketId": "TICKET-001",
  "timestamp": 1704899400,
  "status": "triaged",
  "ticketTitle": "Brief description",
  "ticketDescription": "Full description...",
  "category": "NCCL",
  "priority": "High",
  "suggestedActions": [
    "Check NCCL environment variables",
    "Verify network topology configuration",
    "Review InfiniBand settings"
  ],
  "kbResponse": "Based on the knowledge base, this appears to be...",
  "s3Key": "ticket-001.json"
}
```

## Example Tickets

See the `examples/tickets/` directory for sample tickets:

- `nccl-performance-issue.json` - Multi-node NCCL performance problem
- `cuda-kernel-error.json` - CUDA kernel bug with specific inputs
- `rccl-setup-question.json` - RCCL configuration question for AMD GPUs
- `network-bottleneck.txt` - Network performance issue (text format)

## Best Practices

1. **Be specific** - Include exact error messages, version numbers, and configurations
2. **Provide context** - Describe what you were doing when the issue occurred
3. **Include environment** - GPU models, CUDA/ROCm versions, network setup
4. **Add reproducible steps** - How can someone else recreate the issue?
5. **Use JSON for complex tickets** - Structured data enables better triage
6. **Check your email** - AI analysis results are sent to the provided address

## Troubleshooting

### Ticket not processed

- Check S3 bucket for file upload
- Verify Lambda function logs in CloudWatch
- Ensure file has `.json` or `.txt` extension

### No email received

- Verify email address in SES
- Check Lambda environment variables
- Look for SES errors in CloudWatch logs
- Ensure SES is out of sandbox mode (for production)

### Incorrect triage

- Review knowledge base content
- Check if knowledge base ingestion completed
- Verify Lambda has Bedrock permissions
- Update ticket description with more details

## Monitoring

View Lambda logs:
```bash
aws logs tail /aws/lambda/hpc-ticket-triage-processor \
  --profile hypearadmin \
  --follow
```

Check Lambda metrics:
```bash
aws cloudwatch get-metric-statistics \
  --profile hypearadmin \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=hpc-ticket-triage-processor \
  --start-time 2025-01-10T00:00:00Z \
  --end-time 2025-01-10T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## Support

For issues with the triage system itself:
1. Check CloudWatch logs for Lambda function
2. Verify all stack resources deployed successfully
3. Ensure knowledge base is synced and ready
4. Review IAM permissions for Lambda role

For HPC technical issues:
- The triage system provides initial analysis
- Follow suggested actions from AI triage
- Consult your HPC team for complex problems
