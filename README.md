# HPC Knowledge Base Demo: Amazon Q + MCP + CDK

A production-ready demo showcasing Amazon Q Developer CLI with Model Context Protocol (MCP) and Amazon Bedrock Knowledge Base for HPC computing topics including NCCL, RCCL, CUDA testing, and HPC communication patterns.

## Overview

This project deploys a complete AI-powered knowledge base system that allows you to query comprehensive HPC documentation through natural language using Amazon Q Developer CLI. The infrastructure is fully automated using AWS CDK.

### What Gets Deployed

**Knowledge Base System:**
- **Amazon Bedrock Knowledge Base** - Vector-based knowledge retrieval system
- **OpenSearch Serverless** - Vector storage for embeddings
- **S3 Bucket (Docs)** - Storage for HPC documentation
- **IAM Roles & Policies** - Secure access between services
- **MCP Configuration** - Amazon Q Developer CLI integration

**Automated Ticket Triage System:**
- **S3 Bucket (Tickets)** - Accepts ticket submissions
- **Lambda Function** - Processes tickets using Bedrock KB
- **DynamoDB Table** - Stores triage results and history
- **SES Integration** - Email notifications with AI analysis

### Knowledge Base Content

The knowledge base includes comprehensive documentation on:
- **NCCL** - NVIDIA Collective Communications Library
- **RCCL** - ROCm Collective Communications Library
- **CUDA Testing** - Testing methodologies and frameworks
- **HPC Communication Patterns** - AllReduce, AllGather, Broadcast, etc.
- **HPC Networking** - InfiniBand, EFA, topology considerations
- **HPC Best Practices** - Scaling, profiling, optimization techniques

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Node.js** 18.x or later
4. **AWS CDK** installed globally: `npm install -g aws-cdk`
5. **Amazon Q Developer CLI** installed and configured
6. **Python 3.x** with `uvx` (for MCP server)

### AWS Permissions Required

Your AWS user/role needs permissions for:
- Amazon Bedrock (Knowledge Base creation, model access)
- OpenSearch Serverless
- S3
- IAM (role creation)
- CloudFormation

## Installation & Deployment

### Step 1: Install Dependencies

```bash
npm install
```

### Step 2: Bootstrap CDK (First Time Only)

If this is your first time using CDK in this AWS account/region:

```bash
cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

Replace `ACCOUNT-ID` with your AWS account ID.

### Step 3: Build the Project

```bash
npm run build
```

### Step 4: Review Infrastructure

Preview what will be deployed:

```bash
npx cdk diff
```

### Step 5: Deploy to AWS

```bash
npx cdk deploy
```

The deployment will take approximately 5-10 minutes. Note the outputs:
- `DocsBucketName` - S3 bucket for documentation
- `KnowledgeBaseId` - ID for MCP configuration
- `DataSourceId` - For triggering syncs

### Step 6: Upload Documentation to S3

Run the deployment script to upload HPC documentation:

```bash
./scripts/deploy-docs.sh
```

Or manually:

```bash
aws s3 sync ./docs/ s3://$(aws cloudformation describe-stacks \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`DocsBucketName`].OutputValue' \
  --output text)/
```

### Step 7: Sync Knowledge Base

Trigger the knowledge base to ingest the documents:

```bash
./scripts/sync-kb.sh
```

Or manually:

```bash
KB_ID=$(aws cloudformation describe-stacks \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`KnowledgeBaseId`].OutputValue' \
  --output text)

DS_ID=$(aws cloudformation describe-stacks \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`DataSourceId`].OutputValue' \
  --output text)

aws bedrock-agent start-ingestion-job \
  --knowledge-base-id $KB_ID \
  --data-source-id $DS_ID
```

Wait 2-5 minutes for ingestion to complete.

## Using Amazon Q Developer CLI with MCP

### Step 1: Configure MCP

The `.amazonq/mcp.json` file is pre-configured. Verify the settings:

```bash
cat .amazonq/mcp.json
```

If needed, update `AWS_PROFILE` and ensure the `KB_INCLUSION_TAG_KEY` matches your knowledge base tag (`name=hpc-knowledge-base`).

### Step 2: Start Amazon Q Developer CLI

Navigate to this project directory and start Q:

```bash
q
```

### Step 3: Trust the MCP Server

On first use, trust the Bedrock KB MCP server:

```bash
/tools trust awslabsbedrock_kb_retrieval_mcp_server___QueryKnowledgeBases
```

### Step 4: Query Your Knowledge Base

Try example queries:

```
What are the key differences between NCCL and RCCL?
```

```
How do I optimize AllReduce performance in multi-GPU training?
```

```
What are best practices for testing CUDA kernels?
```

```
Explain the ring algorithm used in NCCL for AllReduce operations
```

```
What network topologies are best for HPC clusters?
```

Amazon Q will automatically query the knowledge base using the MCP server and provide detailed answers based on your HPC documentation.

## Automated Ticket Triage System

In addition to interactive queries via Amazon Q CLI, this stack includes an automated ticket triage system that uses the HPC Knowledge Base to analyze and categorize support tickets.

### How It Works

1. **Submit Ticket** - Upload a ticket file (.json or .txt) to the S3 tickets bucket
2. **Auto-Process** - Lambda function automatically triggers on upload
3. **AI Analysis** - Bedrock queries the HPC Knowledge Base to analyze the ticket
4. **Categorize & Prioritize** - AI determines category (NCCL, RCCL, CUDA, etc.) and priority
5. **Store Results** - Triage results saved to DynamoDB
6. **Email Notification** - Results sent via SES (if email provided in ticket)

### Quick Start: Submit a Test Ticket

```bash
# Get the tickets bucket name
TICKETS_BUCKET=$(aws cloudformation describe-stacks \
  --profile hypearadmin \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`TicketsBucketName`].OutputValue' \
  --output text)

# Submit an example ticket
aws s3 cp examples/tickets/nccl-performance-issue.json \
  "s3://$TICKETS_BUCKET/" \
  --profile hypearadmin

# Wait ~30 seconds, then view results in DynamoDB or check email
```

### Ticket Format Examples

**JSON Format (Recommended):**
```json
{
  "id": "TICKET-001",
  "title": "Slow NCCL AllReduce performance",
  "description": "Detailed description of the issue...",
  "email": "your-email@example.com",
  "environment": {
    "nccl_version": "2.18",
    "gpu_model": "NVIDIA A100"
  }
}
```

**Plain Text Format:**
```
Title: Slow NCCL AllReduce performance

Detailed description of the issue...

Environment:
- NCCL 2.18
- NVIDIA A100
```

### View Triage Results

**Option 1: DynamoDB Console**
- Navigate to `hpc-ticket-triage-results` table
- Query by `ticketId`

**Option 2: AWS CLI**
```bash
TABLE=$(aws cloudformation describe-stacks \
  --profile hypearadmin \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].Outputs[?OutputKey==`TriageTableName`].OutputValue' \
  --output text)

aws dynamodb scan --profile hypearadmin --table-name $TABLE --limit 10
```

**Option 3: Email**
- Tickets with `email` field receive automated triage results via SES

### Enable Email Notifications

To receive email notifications, verify your email in SES:

```bash
aws ses verify-email-identity \
  --profile hypearadmin \
  --email-address your-email@example.com
```

Then update the Lambda function's `SES_FROM_EMAIL` environment variable.

For detailed instructions, see [examples/TICKET_SUBMISSION_GUIDE.md](examples/TICKET_SUBMISSION_GUIDE.md).

## Project Structure

```
.
├── .amazonq/
│   └── mcp.json                    # MCP server configuration
├── bin/
│   └── q_ticket_triage.ts          # CDK app entry point
├── lib/
│   └── q_ticket_triage-stack.ts    # Main CDK stack (KB + Triage System)
├── docs/                            # HPC documentation
│   ├── nccl-overview.md
│   ├── rccl-overview.md
│   ├── cuda-testing.md
│   ├── hpc-communication-patterns.md
│   ├── hpc-networking.md
│   └── hpc-best-practices.md
├── scripts/
│   ├── deploy-docs.sh              # Upload docs to S3
│   └── sync-kb.sh                  # Trigger KB sync
├── examples/
│   ├── queries.txt                 # Example Q CLI queries
│   ├── TICKET_SUBMISSION_GUIDE.md  # Ticket triage guide
│   └── tickets/                    # Example ticket files
│       ├── nccl-performance-issue.json
│       ├── cuda-kernel-error.json
│       ├── rccl-setup-question.json
│       └── network-bottleneck.txt
├── cdk.json                         # CDK configuration
├── package.json
└── README.md
```

## Troubleshooting

### Knowledge Base Returns No Results

1. Check ingestion job status:
   ```bash
   aws bedrock-agent list-ingestion-jobs \
     --knowledge-base-id YOUR_KB_ID \
     --max-results 5
   ```

2. Verify documents are in S3:
   ```bash
   aws s3 ls s3://YOUR_BUCKET_NAME/
   ```

3. Re-trigger ingestion:
   ```bash
   ./scripts/sync-kb.sh
   ```

### MCP Server Not Found

1. Ensure `uvx` is installed:
   ```bash
   pip install uv
   ```

2. Check MCP configuration:
   ```bash
   cat .amazonq/mcp.json
   ```

3. Restart Amazon Q Developer CLI

### Permission Errors

Verify your AWS credentials have access to:
- Bedrock Knowledge Base
- S3 bucket created by the stack
- OpenSearch Serverless collection

Check IAM policies and ensure you're using the correct AWS profile.

## Cleanup

To avoid ongoing charges, destroy the stack when done:

```bash
npx cdk destroy
```

This will remove:
- OpenSearch Serverless collection
- Knowledge Base
- S3 bucket (including all documents)
- IAM roles

## Cost Considerations

Estimated monthly costs (us-east-1, minimal usage):
- **OpenSearch Serverless**: ~$90/month (minimum 4 OCUs)
- **Amazon Bedrock**: Pay-per-use (embeddings + queries)
- **S3**: < $1/month (small docs)

For a demo, expect ~$3-5 total if destroyed within 24 hours.

## Customization

### Add More Documentation

1. Add markdown files to `docs/` directory
2. Run `./scripts/deploy-docs.sh`
3. Run `./scripts/sync-kb.sh`

### Change Embedding Model

Edit `lib/q_ticket_triage-stack.ts`:

```typescript
embeddingModelArn: `arn:aws:bedrock:${this.region}::foundation-model/cohere.embed-english-v3`,
```

Available models:
- `amazon.titan-embed-text-v2:0`
- `cohere.embed-english-v3`
- `cohere.embed-multilingual-v3`

### Modify Chunking Strategy

Adjust in `lib/q_ticket_triage-stack.ts`:

```typescript
chunkingConfiguration: {
  chunkingStrategy: 'FIXED_SIZE',
  fixedSizeChunkingConfiguration: {
    maxTokens: 512,        // Adjust size
    overlapPercentage: 20, // Adjust overlap
  },
}
```

## CDK Commands

- `npm run build` - Compile TypeScript to JavaScript
- `npm run watch` - Watch for changes and compile
- `npm run test` - Run Jest unit tests
- `npx cdk deploy` - Deploy stack to AWS
- `npx cdk diff` - Compare deployed vs current state
- `npx cdk synth` - Emit CloudFormation template
- `npx cdk destroy` - Remove all resources

## Resources

- [Amazon Q Developer CLI Documentation](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line.html)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [AWS MCP Servers GitHub](https://github.com/awslabs/aws-mcp-servers)
- [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)

## Support

For issues or questions:
- Open an issue in this repository
- Consult AWS Bedrock documentation
- Check Amazon Q Developer CLI docs

## License

This project is provided as-is for demonstration purposes.
