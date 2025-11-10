# Quick Deployment Guide

This guide provides step-by-step instructions to deploy and test the complete HPC Knowledge Base and Ticket Triage system using the `hypearadmin` AWS profile.

## Prerequisites Checklist

- [ ] AWS CLI installed and configured
- [ ] AWS profile `hypearadmin` configured
- [ ] Node.js 18.x or later installed
- [ ] CDK installed globally: `npm install -g aws-cdk`
- [ ] Amazon Q Developer CLI installed
- [ ] Python 3.x with `uvx` for MCP server

## Phase 1: Deploy Infrastructure

### Step 1: Install Dependencies

```bash
npm install
```

### Step 2: Bootstrap CDK (First Time Only)

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --profile hypearadmin --query Account --output text)

# Bootstrap CDK
cdk bootstrap aws://$ACCOUNT_ID/us-east-1 --profile hypearadmin
```

### Step 3: Build Project

```bash
npm run build
```

### Step 4: Preview Changes

```bash
npx cdk diff --profile hypearadmin
```

### Step 5: Deploy Stack

```bash
npx cdk deploy --profile hypearadmin HpcKnowledgeBaseStack
```

**Expected deployment time:** 5-10 minutes

**Resources created:**
- OpenSearch Serverless collection (hpc-kb-vectors)
- Bedrock Knowledge Base (hpc-computing-knowledge-base)
- S3 bucket for docs (hpc-knowledge-base-docs-ACCOUNT_ID)
- S3 bucket for tickets (hpc-tickets-ACCOUNT_ID)
- DynamoDB table (hpc-ticket-triage-results)
- Lambda function (hpc-ticket-triage-processor)
- IAM roles and policies

### Step 6: Upload Documentation

```bash
./scripts/deploy-docs.sh
```

**Expected output:**
```
===========================================
HPC Documentation Deployment Script
===========================================

Using AWS profile: hypearadmin
Found bucket: hpc-knowledge-base-docs-ACCOUNT_ID
Uploading 6 documentation files to S3...
✅ Documentation uploaded successfully!
```

### Step 7: Sync Knowledge Base

```bash
./scripts/sync-kb.sh
```

**Expected output:**
```
====================================
Knowledge Base Sync Script
====================================

Using AWS profile: hypearadmin
Starting ingestion job...
✅ Ingestion job started successfully!

Monitoring ingestion job status...
Status: IN_PROGRESS (attempt 1/60)
Status: IN_PROGRESS (attempt 2/60)
...
Status: COMPLETE (attempt X/60)

✅ Ingestion completed successfully!
Your knowledge base is ready to use!
```

**Wait time:** 2-5 minutes

## Phase 2: Test with Amazon Q Developer CLI

### Step 1: Verify MCP Configuration

```bash
cat .amazonq/mcp.json
```

Ensure `AWS_PROFILE` is set to `hypearadmin`.

### Step 2: Start Amazon Q CLI

```bash
q
```

### Step 3: Trust MCP Server (First Time Only)

```
/tools trust awslabsbedrock_kb_retrieval_mcp_server___QueryKnowledgeBases
```

### Step 4: Test Queries

Try these example queries:

```
What are the key differences between NCCL and RCCL?
```

```
How do I optimize AllReduce performance in multi-GPU training?
```

```
What are best practices for testing CUDA kernels?
```

**Expected behavior:** Amazon Q queries the knowledge base and provides detailed answers based on HPC documentation.

## Phase 3: Test Ticket Triage System

### Step 1: Get Tickets Bucket Name

```bash
TICKETS_BUCKET=$(aws cloudformation describe-stacks \
  --profile hypearadmin \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`TicketsBucketName`].OutputValue' \
  --output text)

echo "Tickets bucket: $TICKETS_BUCKET"
```

### Step 2: Submit Test Ticket

```bash
aws s3 cp examples/tickets/nccl-performance-issue.json \
  "s3://$TICKETS_BUCKET/" \
  --profile hypearadmin
```

### Step 3: Wait for Processing

Lambda function will automatically:
1. Detect new ticket in S3
2. Read ticket content
3. Query Bedrock Knowledge Base
4. Categorize and prioritize ticket
5. Store results in DynamoDB
6. Send email (if email field provided)

**Processing time:** ~10-30 seconds

### Step 4: View Results in DynamoDB

```bash
TABLE=$(aws cloudformation describe-stacks \
  --profile hypearadmin \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`TriageTableName`].OutputValue' \
  --output text)

aws dynamodb scan \
  --profile hypearadmin \
  --table-name $TABLE \
  --limit 10
```

### Step 5: Check Lambda Logs

```bash
aws logs tail /aws/lambda/hpc-ticket-triage-processor \
  --profile hypearadmin \
  --follow
```

## Optional: Enable Email Notifications

### Step 1: Verify SES Email

```bash
aws ses verify-email-identity \
  --profile hypearadmin \
  --email-address your-email@example.com
```

Check your email and click the verification link.

### Step 2: Update Lambda Environment Variable

Option A: AWS Console
1. Go to Lambda → `hpc-ticket-triage-processor`
2. Configuration → Environment variables
3. Edit `SES_FROM_EMAIL` to your verified email

Option B: AWS CLI
```bash
aws lambda update-function-configuration \
  --profile hypearadmin \
  --function-name hpc-ticket-triage-processor \
  --environment Variables={KNOWLEDGE_BASE_ID=YOUR_KB_ID,TABLE_NAME=hpc-ticket-triage-results,SES_FROM_EMAIL=your-email@example.com}
```

### Step 3: Test Email Notification

```bash
# Submit a ticket with email field
aws s3 cp examples/tickets/cuda-kernel-error.json \
  "s3://$TICKETS_BUCKET/" \
  --profile hypearadmin
```

Check your email for triage results!

## Troubleshooting

### Issue: CDK deployment fails

**Solution:**
- Verify `hypearadmin` profile has correct permissions
- Check you're deploying to us-east-1
- Ensure CDK is bootstrapped: `cdk bootstrap --profile hypearadmin`

### Issue: Knowledge Base returns no results

**Solution:**
1. Check ingestion job status:
   ```bash
   aws bedrock-agent list-ingestion-jobs \
     --profile hypearadmin \
     --knowledge-base-id YOUR_KB_ID \
     --max-results 5
   ```
2. Re-run sync: `./scripts/sync-kb.sh`

### Issue: Lambda function errors

**Solution:**
1. Check CloudWatch logs:
   ```bash
   aws logs tail /aws/lambda/hpc-ticket-triage-processor \
     --profile hypearadmin
   ```
2. Verify Lambda has Bedrock permissions
3. Check environment variables are set correctly

### Issue: No email received

**Solution:**
- Verify email address in SES
- Check SES is in correct region (us-east-1)
- Review Lambda logs for SES errors
- Ensure ticket JSON includes `email` field

## Cleanup

To remove all resources and avoid charges:

```bash
npx cdk destroy --profile hypearadmin HpcKnowledgeBaseStack
```

**Warning:** This will permanently delete:
- All S3 buckets and contents
- DynamoDB table and data
- OpenSearch Serverless collection
- Lambda function
- Bedrock Knowledge Base

## Cost Estimates

**For 24-hour demo:**
- OpenSearch Serverless: ~$3-5 (minimum 4 OCUs)
- Bedrock: ~$0.10-0.50 (embeddings + queries)
- Lambda: < $0.01 (minimal invocations)
- DynamoDB: < $0.01 (on-demand pricing)
- S3: < $0.01 (minimal storage)
- **Total: ~$3-6**

**Monthly ongoing (if not destroyed):**
- OpenSearch Serverless: ~$90/month (minimum charge)
- Other services: Pay-per-use (variable)

**Recommendation:** Deploy, test, and destroy within 24 hours to minimize costs.

## Next Steps

1. ✅ Deploy infrastructure
2. ✅ Test with Amazon Q CLI
3. ✅ Submit test tickets
4. ✅ View triage results
5. 📧 Configure SES for emails (optional)
6. 📊 Monitor with CloudWatch
7. 🎯 Customize for your use case
8. 🧹 Destroy when done testing

## Support

- Review logs: CloudWatch Logs
- Check stack events: CloudFormation console
- View metrics: CloudWatch Metrics
- Documentation: [README.md](README.md)
- Ticket guide: [examples/TICKET_SUBMISSION_GUIDE.md](examples/TICKET_SUBMISSION_GUIDE.md)

## Quick Reference Commands

```bash
# Deploy
npx cdk deploy --profile hypearadmin HpcKnowledgeBaseStack

# Upload docs
./scripts/deploy-docs.sh

# Sync KB
./scripts/sync-kb.sh

# Submit ticket
aws s3 cp ticket.json s3://hpc-tickets-ACCOUNT_ID/ --profile hypearadmin

# View results
aws dynamodb scan --profile hypearadmin --table-name hpc-ticket-triage-results --limit 10

# Check logs
aws logs tail /aws/lambda/hpc-ticket-triage-processor --profile hypearadmin --follow

# Destroy
npx cdk destroy --profile hypearadmin HpcKnowledgeBaseStack
```

## Success Criteria

✅ Stack deploys successfully
✅ Knowledge base ingestion completes
✅ Amazon Q CLI returns relevant answers
✅ Test ticket gets triaged automatically
✅ Results appear in DynamoDB
✅ (Optional) Email notification received

---

**Ready to deploy?** Start with Phase 1, Step 1!
