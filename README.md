# AI-Powered Knowledge Base Demo

**Amazon Q Developer + Amazon Bedrock + AWS CDK**

A production-ready demonstration of scalable AI knowledge retrieval using Amazon Q Developer CLI with dual knowledge bases, automated ticket triage, and infrastructure as code.

---

## Executive Summary

This demo showcases a modern AI-powered knowledge management system with two key capabilities:

1. **Natural Language Knowledge Retrieval** - Query technical documentation using Amazon Q Developer CLI
2. **Automated Ticket Triage** - AI-powered categorization and routing of support tickets

### What Makes This Special

- **Dual Knowledge Base Architecture** - Separate domains (HPC Computing + Presidio IT Solutions) discoverable through a single interface
- **Model Context Protocol (MCP) Integration** - Amazon Q Developer CLI automatically discovers and queries multiple knowledge bases via tag-based routing
- **Fully Automated Infrastructure** - Complete deployment in ~5 minutes using AWS CDK
- **Scalable Design** - Add new knowledge bases without reconfiguring the client

### Technologies Demonstrated

- **Amazon Bedrock Knowledge Base** - Vector-based RAG system with Claude 3 Haiku
- **Amazon Q Developer CLI** - Natural language interface with MCP integration
- **OpenSearch Serverless** - Managed vector storage for embeddings
- **AWS Lambda** - Event-driven ticket processing
- **AWS CDK (TypeScript)** - Infrastructure as code with cross-stack references

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Amazon Q Developer CLI (User Interface)         │
│                                                           │
│  "What cloud migration services does Presidio offer?"   │
│  "How do I optimize NCCL performance?"                   │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Model Context Protocol (MCP)  │
        │  Tag-Based KB Discovery        │
        │  Filter: name=true             │
        └────────┬───────────────┬───────┘
                 │               │
        ┌────────▼──────┐  ┌────▼──────────┐
        │   HPC KB      │  │  Presidio KB  │
        │  MFULK64QPS   │  │  BXSQ7KURLO   │
        │  22 docs      │  │  25 docs      │
        │  NCCL/CUDA    │  │  Cloud/AI     │
        └───────────────┘  └───────────────┘
             │                    │
             └────────┬───────────┘
                      ▼
         ┌────────────────────────────┐
         │  OpenSearch Serverless     │
         │  Vector Storage            │
         │  Titan Embeddings v2       │
         └────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│          Automated Ticket Triage System              │
│                                                        │
│  S3 Upload → Lambda Trigger → Bedrock KB Query      │
│  → AI Analysis → DynamoDB Storage → Email Alert      │
└──────────────────────────────────────────────────────┘
```

---

## Use Case 1: Amazon Q CLI with Knowledge Base

Query technical documentation using natural language through Amazon Q Developer CLI.

### How It Works

1. **User asks a question** in Q Developer CLI
2. **MCP server** discovers all knowledge bases tagged with `name=true`
3. **Bedrock retrieves** relevant chunks from OpenSearch vector store
4. **Claude 3 Haiku** generates answer with citations
5. **User receives** contextual response in seconds

### Example Queries

**HPC Knowledge Base:**
```
> What is NCCL and how does it work?
> How do I troubleshoot NCCL bandwidth issues?
> What are the best practices for GPU collective operations?
```

**Presidio Knowledge Base:**
```
> What cloud migration services does Presidio offer?
> Tell me about Presidio's AWS partnership
> What are Presidio's AI and ML capabilities?
```

### Key Features

- **Multi-KB Discovery** - Single Q CLI session accesses both knowledge bases automatically
- **Semantic Search** - Vector embeddings enable conceptual matching, not just keywords
- **Source Citations** - Responses include document references
- **Fast Retrieval** - Sub-second query response times

---

## Use Case 2: Automated Ticket Triage

AI-powered analysis and categorization of support tickets with zero manual intervention.

### How It Works

1. **Ticket submitted** - JSON or text file uploaded to S3 bucket
2. **Lambda triggered** - S3 event automatically invokes processing function
3. **AI analysis** - Bedrock queries knowledge base for relevant context
4. **Smart triage** - System extracts category, priority, and recommended actions
5. **Results stored** - DynamoDB table maintains triage history
6. **Notification sent** - SES email with AI-generated analysis

### Ticket Processing Flow

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  S3 Bucket  │────▶│    Lambda    │────▶│  Bedrock KB    │
│  (Upload)   │     │  (Processor) │     │  (AI Query)    │
└─────────────┘     └──────┬───────┘     └────────────────┘
                           │
                    ┌──────▼───────┐     ┌────────────────┐
                    │   DynamoDB   │     │   SES Email    │
                    │   (Storage)  │     │ (Notification) │
                    └──────────────┘     └────────────────┘
```

### AI-Powered Features

- **Automatic categorization** (NCCL, RCCL, CUDA, Networking, Performance, etc.)
- **Priority assignment** (High, Medium, Low) based on keywords and context
- **Action recommendations** extracted from knowledge base
- **Full audit trail** in DynamoDB with timestamps

---

## Knowledge Base Content

### HPC Computing Knowledge Base (22 documents)

Comprehensive documentation on high-performance computing topics:

- **NCCL** - NVIDIA Collective Communications Library (6 docs)
  - API reference, collectives, environment variables
  - Troubleshooting guides, performance tuning
- **RCCL** - ROCm Collective Communications Library
- **CUDA Testing** - Testing frameworks and methodologies
- **HPC Communication Patterns** - AllReduce, AllGather, Broadcast patterns
- **HPC Networking** - InfiniBand, EFA, topology optimization
- **HPC Best Practices** - Scaling strategies, profiling techniques
- **Research Papers** - Networks for High-Performance Computing survey

### Presidio IT Solutions Knowledge Base (25 documents)

Business-focused content covering Presidio's service offerings:

- **Cloud Solutions** (7 docs)
  - AWS partnership, cloud migration, FinOps
  - VMware on AWS integration
- **Case Studies** (9 docs)
  - Q2 Holdings, NHL, DraftKings, OrthoCarolina
  - Higher education, healthcare, sports & gaming
- **Technical Capabilities** (9 docs)
  - Cybersecurity, AI/ML platforms, DevOps automation
  - Data center modernization, managed services
  - Zero trust security, disaster recovery

---

## Quick Start

### Prerequisites

- **AWS Account** with Bedrock access
- **AWS CLI** configured with appropriate profile
- **Node.js** 18.x or later
- **AWS CDK** installed: `npm install -g aws-cdk`
- **Amazon Q Developer CLI** installed and configured

### Deploy Infrastructure

```bash
# 1. Install dependencies
npm install

# 2. Set your AWS profile
export AWS_PROFILE=your-profile-name

# 3. Deploy both knowledge base stacks
npx cdk deploy PresidioKnowledgeBaseStack --require-approval never
npx cdk deploy HpcKnowledgeBaseStack --require-approval never

# Deployment completes in ~5 minutes
```

### Configure Amazon Q Developer CLI

The MCP configuration file at `~/.aws/amazonq/mcp.json` enables automatic knowledge base discovery:

```json
{
  "mcpServers": {
    "awslabs.bedrock-kb-retrieval-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.bedrock-kb-retrieval-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "your-profile-name",
        "AWS_REGION": "us-east-1",
        "KB_INCLUSION_TAG_KEY": "name"
      }
    }
  }
}
```

### Test the System

**1. Test Q CLI Knowledge Retrieval:**
```bash
q

> what knowledge bases do you have access to?
# Should list: hpc-computing-knowledge-base and presidio-solutions-knowledge-base

> What cloud services does Presidio offer?
# AI-generated response with Presidio KB citations

> How do I optimize NCCL performance?
# AI-generated response with HPC KB citations
```

**2. Test Ticket Triage:**
```bash
# Create a test ticket
cat > test-ticket.json << EOF
{
  "title": "NCCL performance degradation",
  "description": "Experiencing slow all-reduce operations on 8 GPU cluster",
  "email": "user@example.com"
}
EOF

# Upload to trigger processing
aws s3 cp test-ticket.json s3://hpc-tickets-{ACCOUNT_ID}/test-ticket.json

# Check DynamoDB for triage results
aws dynamodb scan --table-name hpc-ticket-triage
```

---

## Repository Structure

```
.
├── README.md                          # This file
├── ARCHITECTURE.md                    # Technical architecture deep-dive
├── DATA_INGESTION.md                  # Knowledge base ingestion strategy
│
├── bin/
│   └── q_ticket_triage.ts             # CDK app entry point (instantiates both stacks)
│
├── lib/
│   ├── q_ticket_triage-stack.ts       # HPC KB + Ticket Triage stack
│   └── presidio-kb-stack.ts           # Presidio KB stack (separate lifecycle)
│
├── lambda/
│   └── ticket-triage-processor/       # Python Lambda for ticket processing
│
├── docs/
│   ├── nvidia/                        # NCCL official documentation (6 files)
│   ├── *.md                           # HPC topic documentation (6 files)
│   ├── *.pdf                          # Research papers (1 file)
│   └── presidio/                      # Presidio docs (26 files, gitignored)
│
├── scripts/
│   └── download-presidio-docs.sh      # Automated doc collection script
│
└── examples/
    └── README.md                       # Demo scenarios and sample tickets
```

---

## Key Design Decisions

### Why Separate CDK Stacks?

- **Independent lifecycle** - Deploy, update, or destroy KBs independently
- **Resource isolation** - Separate S3 buckets, OpenSearch collections, IAM roles
- **Cross-stack references** - Ticket triage Lambda can still access both KBs via ARN exports

### Why Tag-Based Discovery?

- **Scalability** - Add new KBs by tagging `name=true`, no MCP config changes needed
- **Flexibility** - Different teams can manage different KBs independently
- **Single interface** - Users don't need to know which KB to query

### Why Two Knowledge Bases?

- **Domain separation** - HPC technical content vs. business/solutions content
- **Different audiences** - Engineers query HPC KB, sales/executives query Presidio KB
- **Proof of concept** - Demonstrates multi-KB architecture for enterprise scenarios

---

## Business Value

### For Technical Teams
- **Instant expertise** - Query complex HPC topics without searching documentation
- **Reduced resolution time** - Automated ticket triage accelerates support workflows
- **Knowledge preservation** - Institutional knowledge captured in queryable form

### For Business Teams
- **Sales enablement** - Quick answers to customer questions about Presidio capabilities
- **Consistent messaging** - AI-generated responses based on official documentation
- **Competitive intelligence** - Easy access to case studies and solution briefs

### For IT Leadership
- **Scalable architecture** - Add knowledge bases as organization grows
- **Cost-effective** - Serverless design scales to zero when not in use
- **Modern stack** - Demonstrates latest AWS AI/ML capabilities

---

## Next Steps

1. **Add More Knowledge Bases** - Follow the Presidio KB pattern (see `DATA_INGESTION.md`)
2. **Customize Ticket Triage** - Modify Lambda logic for your workflow
3. **Enhance UI** - Build web interface on top of Bedrock APIs
4. **Add Feedback Loop** - Track query quality and refine chunking strategy
5. **Integrate with Tools** - Connect to Jira, ServiceNow, Slack

---

## Technical Details

**Embeddings Model:** Amazon Titan Embed Text v2 (1024 dimensions)
**Generation Model:** Anthropic Claude 3 Haiku
**Vector Store:** OpenSearch Serverless (auto-managed)
**Chunking Strategy:** Fixed size, 512 tokens, 20% overlap
**Region:** us-east-1
**Cost:** ~$5/month for demo workloads (mostly OpenSearch Serverless)

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md).
For data ingestion guidelines, see [DATA_INGESTION.md](./DATA_INGESTION.md).

---

## Support

For questions or issues with this demo, please open a GitHub issue.

Built with AWS CDK, Amazon Bedrock, and Amazon Q Developer.
