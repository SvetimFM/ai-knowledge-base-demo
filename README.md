# AI Knowledge Base Demo

Amazon Bedrock Knowledge Base demo with Amazon Q Developer CLI integration and automated ticket triage.

## What This Does

**Knowledge Retrieval**: Query technical documentation via Amazon Q Developer CLI using Model Context Protocol (MCP)
**Ticket Triage**: Automated support ticket categorization using AI

## Architecture

- **2 Knowledge Bases**: HPC Computing + Presidio IT Solutions
- **Vector Storage**: OpenSearch Serverless with Titan embeddings
- **AI Model**: Claude 3 Haiku for generation
- **Automation**: Lambda-based ticket processing with DynamoDB storage

## Prerequisites

- AWS Account with Bedrock access in `us-east-1`
- AWS CLI configured
- Node.js 18+ and npm
- (Optional) SES verified email for ticket notifications

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Email (Optional)

For ticket triage email notifications:

```bash
export SES_FROM_EMAIL=your-verified-email@example.com
```

### 3. Deploy Infrastructure

```bash
npx cdk deploy --all --require-approval never
```

This creates:
- HpcKnowledgeBaseStack
- PresidioKnowledgeBaseStack
- TicketTriageStack

### 4. Add Documentation

Download sample docs (not included in repo):

```bash
bash scripts/download-presidio-docs.sh
# Add your HPC docs to docs/ directory
```

Upload to S3:

```bash
bash scripts/deploy-docs.sh
```

Sync knowledge bases:

```bash
bash scripts/sync-kb.sh
```

### 5. Configure Amazon Q CLI

Install [Amazon Q Developer CLI](https://aws.amazon.com/developer/generative-ai/q-developer/)

Add MCP server to `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "bedrock-kb": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/mcp-server-bedrock-kb-retrieval",
        "--filter",
        "name=true"
      ]
    }
  }
}
```

Restart Q CLI and query your knowledge bases.

## Usage Examples

### Knowledge Base Queries

```
What is NCCL and how does it work?
What cloud migration services does Presidio offer?
How do I troubleshoot CUDA performance issues?
```

### Ticket Triage

Upload a ticket to S3:

```bash
aws s3 cp examples/ticket-1.json s3://ticket-triage-{ACCOUNT_ID}/
```

View triage results in DynamoDB table `ticket-triage-results`

## Project Structure

```
lib/
  knowledge-base-construct.ts  # Reusable KB construct
  hpc-kb-stack.ts             # HPC knowledge base
  presidio-kb-stack.ts        # Presidio knowledge base
  ticket-triage-stack.ts      # Ticket processing system
lambda/
  ticket_triage.py            # Ticket processor with structured output
scripts/
  deploy-docs.sh              # Upload docs to S3
  sync-kb.sh                  # Trigger KB sync
examples/
  ticket-1.json               # Sample ticket
```

## Cleanup

```bash
npx cdk destroy --all
```

## Key Features

- **Reusable Infrastructure**: Single `KnowledgeBaseConstruct` for multiple domains
- **Structured AI Output**: Uses Bedrock Converse API with tool use for reliable parsing
- **Tag-Based Discovery**: MCP automatically finds KBs tagged with `name=true`
- **Event-Driven**: S3 uploads trigger automatic ticket processing
- **Environment-Based Config**: SES email via environment variable

## Development

```bash
npm install        # Install dependencies
npm run build      # Compile TypeScript
npm test           # Run tests (requires Docker)
npx cdk synth      # Synthesize CloudFormation
```

## Troubleshooting

**Deployment fails**: Ensure Bedrock model access is enabled in `us-east-1`
**Q CLI can't find KBs**: Check MCP config and verify KB tags
**Email not sending**: Verify SES email address and check Lambda logs
**KB queries return no results**: Run sync script after uploading docs
**Tests fail**: Tests require Docker for CDK bundling. Build still validates TypeScript compilation.

## License

MIT-0
