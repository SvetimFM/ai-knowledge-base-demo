# System Architecture

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Breakdown](#component-breakdown)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Knowledge Base Architecture](#knowledge-base-architecture)
5. [MCP Integration](#mcp-integration)
6. [Ticket Triage System](#ticket-triage-system)
7. [Infrastructure as Code](#infrastructure-as-code)
8. [Security & IAM](#security--iam)
9. [Scalability Patterns](#scalability-patterns)

---

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                         User Interaction Layer                          │
│                                                                          │
│  ┌──────────────────────┐           ┌──────────────────────────────┐  │
│  │  Amazon Q CLI        │           │  S3 Ticket Submission        │  │
│  │  (Terminal Interface)│           │  (File Upload)               │  │
│  └──────────┬───────────┘           └────────────┬─────────────────┘  │
└─────────────┼──────────────────────────────────────┼──────────────────┘
              │                                      │
              ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        MCP & Event Layer                                 │
│                                                                           │
│  ┌──────────────────────────────┐      ┌──────────────────────────┐    │
│  │  MCP Server                  │      │  S3 Event Notification   │    │
│  │  (bedrock-kb-retrieval)      │      │  (ObjectCreated)         │    │
│  │  - Tag-based KB discovery    │      └──────────┬───────────────┘    │
│  │  - KB_INCLUSION_TAG_KEY=name │                 │                     │
│  └──────────┬───────────────────┘                 │                     │
└─────────────┼───────────────────────────────────────┼──────────────────┘
              │                                      │
              ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        AWS Service Layer                                 │
│                                                                           │
│  ┌──────────────────────┐  ┌─────────────────────┐  ┌────────────────┐ │
│  │  Bedrock Agent       │  │  Lambda Function    │  │  DynamoDB      │ │
│  │  Runtime             │  │  (Ticket Processor) │  │  (Triage Data) │ │
│  │  - RetrieveAndGen    │  │  - Python 3.12      │  │                │ │
│  └──────────┬───────────┘  └──────────┬──────────┘  └────────────────┘ │
└─────────────┼─────────────────────────┼──────────────────────────────────┘
              │                         │
              ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Knowledge Base Layer                                 │
│                                                                           │
│  ┌─────────────────────┐           ┌──────────────────────┐            │
│  │  HPC KB             │           │  Presidio KB         │            │
│  │  ID: MFULK64QPS     │           │  ID: BXSQ7KURLO      │            │
│  │  Tag: name=true     │           │  Tag: name=true      │            │
│  │                     │           │                      │            │
│  │  ┌───────────────┐  │           │  ┌───────────────┐  │            │
│  │  │ S3 Data Source│  │           │  │ S3 Data Source│  │            │
│  │  │ 22 documents  │  │           │  │ 25 documents  │  │            │
│  │  └───────┬───────┘  │           │  └───────┬───────┘  │            │
│  └──────────┼──────────┘           └──────────┼──────────┘            │
│             │                                  │                        │
│             └──────────────┬───────────────────┘                        │
│                            ▼                                             │
│                  ┌────────────────────┐                                 │
│                  │  OpenSearch        │                                 │
│                  │  Serverless        │                                 │
│                  │  Collections       │                                 │
│                  └────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Amazon Q Developer CLI
- **Purpose**: Natural language interface for querying knowledge bases
- **Technology**: Terminal-based CLI with MCP integration
- **Location**: Client machine (developer workstation)
- **Configuration**: `~/.aws/amazonq/mcp.json`

### Model Context Protocol (MCP) Server
- **Package**: `awslabs.bedrock-kb-retrieval-mcp-server`
- **Deployment**: Runs via `uvx` on client machine
- **Function**: Automatically discovers Bedrock KBs via tags
- **Discovery Logic**: Filters KBs where tag key="name" and value="true"
- **Communication**: Uses AWS SDK to call Bedrock APIs

### Amazon Bedrock Knowledge Base
**Two Independent Instances:**

**1. HPC Computing KB (MFULK64QPS)**
- Stack: `HpcKnowledgeBaseStack`
- Purpose: Technical HPC documentation
- Documents: 22 (NCCL, RCCL, CUDA, networking, best practices)
- S3 Bucket: `s3://hpc-knowledge-base-docs-{account}/`
- OpenSearch Collection: Auto-generated name

**2. Presidio Solutions KB (BXSQ7KURLO)**
- Stack: `PresidioKnowledgeBaseStack`
- Purpose: Business and solutions content
- Documents: 25 (case studies, cloud solutions, technical capabilities)
- S3 Bucket: `s3://presidio-knowledge-base-docs-{account}/`
- OpenSearch Collection: Auto-generated name

### OpenSearch Serverless
- **Type**: Managed vector database
- **Collections**: One per Knowledge Base (2 total)
- **Capacity**: Auto-scaled by AWS
- **Cost**: Based on OCU (OpenSearch Compute Units)
- **Dimensions**: 1024 (Titan Embed Text v2)
- **Index Strategy**: HNSW (Hierarchical Navigable Small World)

### Lambda Function (Ticket Triage)
- **Runtime**: Python 3.12
- **Trigger**: S3 ObjectCreated event
- **Memory**: 256 MB (configurable)
- **Timeout**: 60 seconds
- **Permissions**: Read S3, query both KBs, write DynamoDB, send SES emails
- **Location**: `lambda/ticket-triage-processor/index.py`

### DynamoDB Table
- **Name**: `hpc-ticket-triage`
- **Primary Key**: `ticketId` (String)
- **Sort Key**: `timestamp` (String)
- **Billing**: On-demand (pay per request)
- **Attributes**: ticketId, timestamp, category, priority, actions, kb_response

### S3 Buckets
**1. HPC Docs Bucket**
- Purpose: Source documents for HPC KB
- Versioning: Enabled
- Encryption: S3-managed (SSE-S3)

**2. Presidio Docs Bucket**
- Purpose: Source documents for Presidio KB
- Versioning: Enabled
- Encryption: S3-managed (SSE-S3)

**3. Tickets Bucket**
- Purpose: Ticket submission endpoint
- Event Notification: Triggers Lambda on .json/.txt files
- Versioning: Enabled

---

## Data Flow Diagrams

### Flow 1: Q CLI Query Processing

```
┌─────────────┐
│  User asks  │
│  question   │
└──────┬──────┘
       │
       ▼
┌───────────────────────────────────────┐
│  Q CLI sends query to MCP server      │
└──────┬────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│  MCP server calls                     │
│  ListKnowledgeBases(TagFilter=name)   │
└──────┬────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│  Returns: [MFULK64QPS, BXSQ7KURLO]   │
└──────┬────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│  MCP server calls                     │
│  RetrieveAndGenerate() on relevant KB │
└──────┬────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│  Bedrock retrieves chunks from        │
│  OpenSearch (vector similarity)       │
└──────┬────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│  Bedrock invokes Claude 3 Haiku with  │
│  retrieved chunks as context          │
└──────┬────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│  Claude generates response with       │
│  source citations                     │
└──────┬────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│  MCP server returns response to Q CLI │
└──────┬────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  User sees  │
│  answer     │
└─────────────┘
```

### Flow 2: Ticket Triage Processing

```
┌──────────────┐
│  User uploads│
│  ticket.json │
│  to S3       │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│  S3 triggers Lambda via             │
│  Event Notification                 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda reads ticket from S3        │
│  Parses JSON or plain text          │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda constructs triage prompt:   │
│  "Analyze this ticket and           │
│   categorize it (NCCL/RCCL/CUDA/…)" │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda calls                       │
│  bedrock-agent-runtime:             │
│  RetrieveAndGenerate()              │
│  KB ID: MFULK64QPS (HPC KB)         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Bedrock retrieves relevant docs    │
│  and generates AI analysis          │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda parses response:            │
│  - Category (NCCL, CUDA, etc.)      │
│  - Priority (High, Medium, Low)     │
│  - Recommended actions              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda writes to DynamoDB:         │
│  {ticketId, category, priority,     │
│   actions, kb_response, timestamp}  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda sends SES email:            │
│  - To: ticket submitter             │
│  - Subject: Ticket Triage Results   │
│  - Body: AI analysis + actions      │
└──────┬──────────────────────────────┘
       │
       ▼
┌──────────────┐
│  User receives│
│  email        │
└──────────────┘
```

---

## Knowledge Base Architecture

### Embedding & Retrieval Process

```
┌─────────────────────┐
│  Document Upload    │
│  to S3              │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Ingestion Job      │
│  Triggered          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Bedrock KB splits documents into       │
│  chunks (512 tokens, 20% overlap)       │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Titan Embed Text v2 generates          │
│  1024-dimensional vector per chunk      │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Vectors stored in OpenSearch           │
│  Serverless with HNSW index             │
└─────────────────────────────────────────┘


┌─────────────────────┐
│  User Query         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Query embedded using same              │
│  Titan Embed Text v2 model              │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  OpenSearch performs vector similarity  │
│  search (cosine similarity)             │
│  Returns top-k chunks (default k=5)     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Claude 3 Haiku receives chunks         │
│  as context and generates answer        │
└─────────────────────────────────────────┘
```

### Chunking Strategy

**Configuration:**
- **Method**: Fixed size
- **Chunk size**: 512 tokens (~2000 characters)
- **Overlap**: 20% (102 tokens)
- **Rationale**: Balance between context and precision

**Example:**
```
Document (2500 tokens):
┌────────────────────────────────────────────────┐
│ Chunk 1: tokens 0-512    (512 tokens)         │
│         Overlap: 102 tokens                    │
│ Chunk 2: tokens 410-922  (512 tokens)         │
│         Overlap: 102 tokens                    │
│ Chunk 3: tokens 820-1332 (512 tokens)         │
│         Overlap: 102 tokens                    │
│ ...                                             │
└────────────────────────────────────────────────┘
```

---

## MCP Integration

### Configuration File Structure

**Location:** `~/.aws/amazonq/mcp.json`

```json
{
  "mcpServers": {
    "awslabs.bedrock-kb-retrieval-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.bedrock-kb-retrieval-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "your-profile",
        "AWS_REGION": "us-east-1",
        "KB_INCLUSION_TAG_KEY": "name",
        "BEDROCK_KB_RERANKING_ENABLED": "false"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Tag-Based Discovery Mechanism

**How it works:**

1. **MCP server startup**: Q CLI loads MCP configuration
2. **KB discovery**: Server calls `bedrock-agent:ListKnowledgeBases`
3. **Tag filtering**: Filters for KBs where tag key = `"name"`
4. **Tag value check**: Includes KB if tag value = `"true"`
5. **Result**: Returns list of qualifying KB IDs

**CDK Tag Implementation:**
```typescript
// HPC KB Stack
cdk.Tags.of(knowledgeBase).add('name', 'true');

// Presidio KB Stack
cdk.Tags.of(presidioKnowledgeBase).add('name', 'true');
```

**Why This Design:**

- **Scalable**: Add KBs by tagging, no client config changes
- **Flexible**: Different teams can tag KBs independently
- **Simple**: Single MCP server handles multiple KBs

---

## Ticket Triage System

### Lambda Function Architecture

**File:** `lambda/ticket-triage-processor/index.py`

**Key Functions:**

```python
def handler(event, context):
    """Main Lambda handler triggered by S3 events"""
    # 1. Parse S3 event
    # 2. Read ticket file
    # 3. Perform triage via Bedrock KB
    # 4. Store results in DynamoDB
    # 5. Send email notification

def perform_triage(ticket):
    """Query Bedrock KB for AI-powered triage"""
    # Construct prompt with ticket details
    # Call RetrieveAndGenerate()
    # Parse AI response

def parse_triage_response(response):
    """Extract category, priority, actions from AI response"""
    # Simple NLP parsing
    # Returns structured triage data
```

### Ticket Schema

**JSON Format:**
```json
{
  "id": "TICKET-001",
  "title": "NCCL performance issue",
  "description": "Slow AllReduce on 8 GPUs...",
  "email": "user@example.com",
  "timestamp": "2025-01-10T14:30:00Z",
  "environment": {
    "nccl_version": "2.18",
    "cuda_version": "12.1",
    "gpu_type": "A100",
    "num_gpus": 8
  }
}
```

### DynamoDB Schema

**Table:** `hpc-ticket-triage`

| Attribute       | Type   | Description                    |
|-----------------|--------|--------------------------------|
| ticketId (PK)   | String | Unique ticket identifier       |
| timestamp (SK)  | String | ISO 8601 timestamp             |
| category        | String | NCCL, RCCL, CUDA, Network, etc |
| priority        | String | High, Medium, Low              |
| actions         | List   | Recommended troubleshooting    |
| kb_response     | String | Full AI-generated analysis     |
| email           | String | Submitter email                |
| status          | String | New, InProgress, Resolved      |

---

## Infrastructure as Code

### CDK Stack Architecture

**Two Independent Stacks:**

#### 1. PresidioKnowledgeBaseStack
```typescript
// lib/presidio-kb-stack.ts
export class PresidioKnowledgeBaseStack extends cdk.Stack {
  public readonly presidioKbArn: string;  // Exported for cross-stack ref

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    // S3 bucket for Presidio docs
    // Bedrock Knowledge Base
    // OpenSearch Serverless collection
    // IAM roles & policies
    // Tag: name=true
  }
}
```

**Resources Created:**
- S3 bucket: `presidio-knowledge-base-docs-{account}`
- Bedrock KB: `presidio-solutions-knowledge-base`
- OpenSearch collection: auto-generated
- IAM execution role
- S3 data source

#### 2. HpcKnowledgeBaseStack (QTicketTriageStack)
```typescript
// lib/q_ticket_triage-stack.ts
export interface QTicketTriageStackProps extends cdk.StackProps {
  presidioKbArn?: string;  // Cross-stack reference
}

export class QTicketTriageStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: QTicketTriageStackProps) {
    // HPC Knowledge Base
    // Ticket triage Lambda
    // DynamoDB table
    // S3 buckets (docs + tickets)
    // SES configuration
    // Cross-stack KB permissions
  }
}
```

**Resources Created:**
- S3 bucket: `hpc-knowledge-base-docs-{account}`
- S3 bucket: `hpc-tickets-{account}`
- Bedrock KB: `hpc-computing-knowledge-base`
- OpenSearch collection: auto-generated
- Lambda function: `hpc-ticket-triage-processor`
- DynamoDB table: `hpc-ticket-triage`
- IAM roles & policies
- S3 event notifications

### Cross-Stack References

**Pattern:** Presidio stack exports KB ARN, HPC stack imports it

```typescript
// bin/q_ticket_triage.ts
const presidioStack = new PresidioKnowledgeBaseStack(app, 'PresidioKB', {...});

new QTicketTriageStack(app, 'HpcKB', {
  presidioKbArn: presidioStack.presidioKbArn  // Cross-stack reference
});
```

**Usage in HPC Stack:**
```typescript
// Lambda gets permissions for both KBs
const bedrockResources = [
  knowledgeBase.knowledgeBaseArn,  // HPC KB
  `arn:aws:bedrock:${this.region}::foundation-model/*`,
];

if (props?.presidioKbArn) {
  bedrockResources.push(props.presidioKbArn);  // Presidio KB
}
```

---

## Security & IAM

### Least Privilege Principles

**MCP Server (Client-side):**
- Permissions: `bedrock:ListKnowledgeBases`, `bedrock:Retrieve`, `bedrock:RetrieveAndGenerate`
- Scope: User's AWS credentials via profile
- No write access

**Lambda Execution Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate",
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1:{account}:knowledge-base/MFULK64QPS",
        "arn:aws:bedrock:us-east-1:{account}:knowledge-base/BXSQ7KURLO",
        "arn:aws:bedrock:us-east-1::foundation-model/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::hpc-tickets-{account}/*"
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:{account}:table/hpc-ticket-triage"
    },
    {
      "Effect": "Allow",
      "Action": ["ses:SendEmail"],
      "Resource": "*"
    }
  ]
}
```

### Encryption

- **S3 Buckets**: Server-side encryption (SSE-S3)
- **DynamoDB**: Encryption at rest (default)
- **OpenSearch**: Encryption at rest and in transit (managed by AWS)
- **Data in Transit**: TLS 1.2+ for all API calls

---

## Scalability Patterns

### Horizontal Scaling

**Adding Knowledge Bases:**
1. Create new CDK stack (copy `PresidioKnowledgeBaseStack` pattern)
2. Tag KB with `name=true`
3. Deploy
4. Q CLI automatically discovers it (no config changes)

**Adding Documents:**
- Upload to S3 bucket
- Trigger ingestion job
- Scales automatically (Bedrock handles chunking, embedding, indexing)

### Vertical Scaling

**OpenSearch Serverless:**
- Auto-scales OCUs (OpenSearch Compute Units) based on workload
- No manual capacity management

**Lambda:**
- Concurrency: Scales automatically to 1000 concurrent executions (default)
- Can request higher limits if needed

### Cost Optimization

**Idle Costs:**
- OpenSearch Serverless: ~$2-3/month per collection (minimum)
- S3: Storage only (~$0.02/GB)
- DynamoDB: On-demand, pay per request

**Active Costs:**
- Bedrock KB queries: ~$0.0025 per 1000 tokens retrieved
- Claude 3 Haiku: ~$0.00025 per 1000 input tokens
- Lambda: Free tier covers most demo usage

---

## Deployment Architecture

```
Development → CDK Synth → CloudFormation → AWS Resources

┌──────────────┐
│ TypeScript   │
│ CDK Code     │
└──────┬───────┘
       │
       │ npm run build
       │
       ▼
┌──────────────┐
│ JavaScript   │
│ Compiled     │
└──────┬───────┘
       │
       │ cdk synth
       │
       ▼
┌──────────────┐
│ CloudForm    │
│ Template     │
│ (JSON/YAML)  │
└──────┬───────┘
       │
       │ cdk deploy
       │
       ▼
┌──────────────┐
│ CloudForm    │
│ Stack        │
│ (AWS)        │
└──────┬───────┘
       │
       │ Creates
       │
       ▼
┌────────────────────────────────┐
│ AWS Resources                  │
│ - Bedrock KB                   │
│ - OpenSearch Serverless        │
│ - Lambda                       │
│ - DynamoDB                     │
│ - S3                           │
│ - IAM                          │
└────────────────────────────────┘
```

---

## Performance Characteristics

### Query Latency

- **Q CLI query (cold start)**: 2-4 seconds
- **Q CLI query (warm)**: 0.5-1.5 seconds
- **Lambda ticket triage**: 3-6 seconds
- **Ingestion job**: 30-90 seconds for 20-30 documents

### Throughput

- **Concurrent Q CLI users**: 10-20 (limited by MCP server on client)
- **Ticket processing**: 100+ tickets/second (Lambda auto-scales)
- **KB queries**: 1000+ QPS (Bedrock scales automatically)

---

## Monitoring & Observability

### CloudWatch Metrics

**Lambda:**
- Invocations, Duration, Errors, Throttles

**Bedrock:**
- ModelInvocations, TokensConsumed

**DynamoDB:**
- ReadCapacityUnits, WriteCapacityUnits, ThrottledRequests

### CloudWatch Logs

**Lambda Logs:**
- `/aws/lambda/hpc-ticket-triage-processor`
- Retention: 7 days (configurable in CDK)

**MCP Server Logs:**
- Client-side: stderr output visible in Q CLI

### Tracing

- X-Ray: Not currently enabled (can be added to Lambda)
- Bedrock: Native request tracing available in CloudWatch

---

## Disaster Recovery

### Backup Strategy

**S3:**
- Versioning enabled
- Cross-region replication: Not configured (can be added)

**DynamoDB:**
- Point-in-time recovery: Enabled
- Backup retention: 35 days

**OpenSearch:**
- Managed by AWS, automatic backups
- Recovery: Automatic via AWS

### Recovery Time Objective (RTO)

- **CDK redeploy**: ~5 minutes for infrastructure
- **Document re-ingestion**: ~2 minutes for 50 documents
- **Total RTO**: ~10 minutes

### Recovery Point Objective (RPO)

- **S3**: Near-zero (versioning enabled)
- **DynamoDB**: <1 second (continuous backup)

---

## Future Enhancements

1. **Multi-region deployment** for high availability
2. **Web UI** built on AWS Amplify or Next.js
3. **Real-time chat** interface using AppSync + WebSocket
4. **Fine-tuned embeddings** for domain-specific queries
5. **Feedback loop** to track query quality
6. **Integration with Jira/ServiceNow** for ticket routing
7. **A/B testing** of different LLMs (Claude 3 Sonnet vs Haiku)
8. **Cost dashboard** using CloudWatch metrics

---

For implementation details, see [README.md](./README.md).
For data ingestion strategy, see [DATA_INGESTION.md](./DATA_INGESTION.md).
