# RAG Knowledge Base with Milvus

**Production-Ready RAG System on AWS**

A scalable, partitioned RAG (Retrieval-Augmented Generation) knowledge base system built on AWS, featuring Milvus vector database, Amazon Bedrock, and secure MCP (Model Context Protocol) integration for Claude Desktop.

---

## Features

- **High-Performance Vector Search**: Milvus on ECS Fargate with partitioned collections (4-5x faster queries)
- **Automatic Document Ingestion**: S3 upload triggers automatic chunking, embedding, and indexing
- **Multiple Knowledge Bases**: Support for multiple independent knowledge bases with dynamic partition-based isolation
- **HyDE Retrieval**: Hypothetical Document Embeddings for improved retrieval accuracy
- **Enterprise LLM**: Amazon Bedrock Claude 3.5 Sonnet for answer generation
- **MCP Integration**: Secure Claude Desktop integration via Model Context Protocol
- **Cognito Authentication**: Secure access with AWS Cognito User Pools
- **Infrastructure as Code**: Complete AWS CDK deployment with configuration management

---

## Quick Start

### Deploy to Your AWS Account

**Complete step-by-step deployment guide**: [DEPLOYMENT.md](./DEPLOYMENT.md)

```bash
# 1. Clone and install dependencies
git clone https://github.com/yourusername/rag-knowledge-base.git
cd rag-knowledge-base
npm install

# 2. Configure deployment (create .env from .env.example)
cp .env.example .env
# Edit .env with your settings (DEPLOYMENT_TIER, PROJECT_NAME, KNOWLEDGE_BASES)

# 3. Bootstrap CDK (first-time only)
cdk bootstrap

# 4. Deploy infrastructure (~10-15 minutes)
cdk deploy --all

# 5. Upload documents
aws s3 cp your-docs/ s3://kb-documents-YOUR_ACCOUNT_ID/docs/ --recursive

# 6. Query your knowledge base
curl -X POST https://YOUR_API_ENDPOINT/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "What is X?", "knowledge_base": "docs"}'
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions, troubleshooting, and post-deployment configuration.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Document Ingestion                       │
│                                                               │
│  S3 Upload → SQS Queue → Lambda Ingestor → Embeddings       │
│  (PDF/MD/TXT)           (Orchestration)     (Titan v2)       │
│                                ↓                              │
│                         Milvus Insert                         │
│                       (Partitioned by KB)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       Query Pipeline                          │
│                                                               │
│  API Gateway → Lambda RAG Query → Milvus Search (HyDE)      │
│  (Cognito Auth)                   (Partition-filtered)       │
│                    ↓                                          │
│              Bedrock Claude 3.5 Sonnet                        │
│              (Answer Generation)                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    MCP Integration (Optional)                 │
│                                                               │
│  Claude Desktop → MCP Stream Handler → RAG Query            │
│  (JWT Auth)        (WebSocket)                               │
│                                                               │
│  Provides: Query tool, upload tool, status checking          │
└─────────────────────────────────────────────────────────────┘
```

### AWS Resources

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Milvus (ECS)** | Vector database | Fargate tasks with etcd + MinIO |
| **Lambda** | Document processing, embeddings, RAG queries | Python 3.12, Docker images |
| **S3** | Document storage with versioning | Versioned bucket with lifecycle policies |
| **DynamoDB** | Ingestion state tracking | On-demand billing, PITR enabled |
| **Cognito** | User authentication | Email-based auth with optional SES |
| **API Gateway** | Public HTTP API | REST API with Cognito authorizer |
| **Bedrock** | LLM & embeddings | Claude 3.5 Sonnet, Titan Embeddings v2 |
| **VPC** | Network isolation | Public/private subnets, NAT Gateway |

---

## Key Features

### 1. Partitioned Vector Database

Milvus collections are partitioned by knowledge base, providing:
- **4-5x faster queries** compared to metadata filtering
- **Isolated data** per knowledge base
- **Efficient scaling** as you add more KBs
- **Partition pruning** for optimized vector search

### 2. Automated Ingestion Pipeline

Documents are automatically processed on S3 upload:
- **Chunking**: Intelligent text splitting with overlap
- **Embedding**: Amazon Bedrock Titan Embeddings v2
- **Indexing**: Inserted into Milvus with partition routing
- **State Tracking**: DynamoDB tracks processing status
- **Dead Letter Queue**: Failed documents for manual review

### 3. HyDE-Enhanced Retrieval

Hypothetical Document Embeddings (HyDE) improve retrieval:
- Generate hypothetical answer from question
- Embed hypothetical answer
- Search for semantically similar documents
- **Results**: Better context retrieval, improved answer quality

### 4. Configurable Deployment Tiers

Three preset tiers for different use cases:

| Tier | Cost | ECS Size | Use Case |
|------|------|----------|----------|
| **Dev** | ~$30-40/mo | 0.25 vCPU, 512 MB | Development, testing |
| **Staging** | ~$65-100/mo | 0.5 vCPU, 1024 MB | Pre-production, demos |
| **Prod** | ~$350-500/mo | 1 vCPU, 2048 MB | Production workloads |

Configure via `DEPLOYMENT_TIER` in `.env`.

### 5. MCP Integration (Optional)

Claude Desktop integration via Model Context Protocol:
- **Secure authentication**: JWT-based auth with RSA keys
- **Tools**: Query knowledge base, upload documents, check ingestion status
- **Streaming**: Real-time responses via WebSocket
- **Multi-session**: Support for concurrent users

---

## Configuration

All configuration is centralized in `.env` (created from `.env.example`).

### Required Configuration

```bash
DEPLOYMENT_TIER=dev              # dev, staging, or prod
PROJECT_NAME=rag-kb              # Project identifier
KNOWLEDGE_BASES=docs,manuals     # Comma-separated KB prefixes
```

### Optional Configuration

```bash
# AWS
CDK_DEFAULT_REGION=us-east-1

# Resource Naming
BUCKET_PREFIX=kb-documents
STATE_TABLE_NAME=document-ingestion-state
USER_POOL_NAME=rag-query-users

# Bedrock Models
CLAUDE_SONNET_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
TITAN_EMBED_MODEL_ID=amazon.titan-embed-text-v2:0

# Email (optional)
VERIFIED_EMAIL_DOMAIN=example.com  # Requires SES domain verification

# ECS (advanced)
MILVUS_IMAGE_TAG=milvusdb/milvus:v2.6.5
MINIO_IMAGE_TAG=minio/minio:latest
```

See `.env.example` for complete list with descriptions.

---

## Usage

### Upload Documents

Supported formats: PDF, Markdown (.md), Text (.txt)

```bash
# Upload single document
aws s3 cp document.pdf s3://kb-documents-YOUR_ACCOUNT_ID/docs/

# Upload directory
aws s3 cp ./my-docs/ s3://kb-documents-YOUR_ACCOUNT_ID/manuals/ --recursive
```

Documents are automatically processed within seconds.

### Query via API

```bash
# Get Cognito token
TOKEN=$(aws cognito-idp admin-initiate-auth \
  --user-pool-id YOUR_USER_POOL_ID \
  --client-id YOUR_CLIENT_ID \
  --auth-flow ADMIN_NO_SRP_AUTH \
  --auth-parameters USERNAME=user@example.com,PASSWORD=password \
  --query 'AuthenticationResult.IdToken' --output text)

# Query knowledge base
curl -X POST https://YOUR_API_ENDPOINT/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the installation process?",
    "knowledge_base": "docs",
    "top_k": 5
  }'
```

### Query via MCP (Claude Desktop)

If you deployed MCPRemoteStack, configure Claude Desktop:

```json
{
  "mcpServers": {
    "rag-kb": {
      "url": "YOUR_MCP_STREAM_URL",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN"
      }
    }
  }
}
```

Then query directly in Claude Desktop:
```
> Query the docs KB: What is the installation process?
```

---

## Cost Breakdown

### Monthly Infrastructure Costs

**Development Tier (~$30-40/month)**:
- ECS Fargate: ~$10-15
- NAT Gateway: ~$32 (largest cost)
- DynamoDB: ~$1-2
- S3: ~$1
- Other: ~$1

**Cost Optimization Tips**:
- Use VPC endpoints to eliminate NAT Gateway ($32/mo savings)
- Scale down ECS tasks when not in use
- Use S3 lifecycle policies to archive old versions

### Usage-Based Costs (Bedrock)

- **Embeddings** (Titan v2): ~$0.10 per 1M tokens
- **Generation** (Claude 3.5 Sonnet):
  - Input: ~$3.00 per 1M tokens
  - Output: ~$15.00 per 1M tokens

**Example**: 1,000 documents (500 pages each) + 10,000 queries/month = ~$50-100 in Bedrock costs.

---

## Repository Structure

```
.
├── README.md                          # This file
├── DEPLOYMENT.md                      # Complete deployment guide
├── LICENSE                            # MIT License
│
├── bin/
│   └── app.ts                         # CDK app entry point
│
├── lib/                               # CDK stack definitions
│   ├── milvus-stack.ts                # Milvus vector database (ECS)
│   ├── embeddings-stack.ts            # Bedrock embeddings generation
│   ├── ingestion-stack.ts             # S3 + SQS + Lambda orchestration
│   ├── rag-stack.ts                   # RAG query Lambda
│   ├── auth-stack.ts                  # Cognito authentication
│   ├── api-stack.ts                   # API Gateway
│   ├── mcp-remote-stack.ts            # MCP integration (optional)
│   ├── mcp-api-stack.ts               # MCP API Gateway (optional)
│   ├── security-stack.ts              # CloudTrail logging
│   └── waf-stack.ts                   # WAF rate limiting
│
├── lambda/                            # Lambda function code
│   ├── document-ingestor/             # S3 event processor
│   ├── embeddings-generator/          # Bedrock Titan embeddings
│   ├── rag-query/                     # HyDE + Claude query handler
│   └── mcp-*/                         # MCP handlers (optional)
│
├── config/
│   └── deployment-config.ts           # Centralized configuration
│
├── scripts/
│   ├── validate-deployment.sh         # Health check script
│   └── download-hpc-docs.sh           # Example doc downloader
│
├── .env.example                       # Configuration template
└── cdk.json                           # CDK configuration
```

---

## Monitoring and Troubleshooting

### Health Checks

Run the validation script to verify deployment:

```bash
./scripts/validate-deployment.sh
```

Checks:
- All CDK stacks deployed
- ECS services running
- Lambda functions responsive
- S3 buckets accessible
- DynamoDB tables created

### View Logs

```bash
# Lambda logs
aws logs tail /aws/lambda/FUNCTION_NAME --follow

# ECS logs
aws logs tail /aws/ecs/milvus-cluster/milvus-service --follow

# CloudTrail (API activity)
aws logs tail /aws/cloudtrail/rag-kb-trail --follow
```

### Common Issues

See [DEPLOYMENT.md - Troubleshooting](./DEPLOYMENT.md#troubleshooting) for solutions to:
- Access denied errors
- Documents not processing
- Milvus connection failures
- Lambda timeouts
- Bedrock throttling

---

## Development

### Prerequisites

- Node.js 18.x+
- AWS CLI configured
- Docker (for Lambda container builds)
- Python 3.12+ (for Lambda development)

### Local Development

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Run tests
npm test

# Synthesize CloudFormation
cdk synth

# Deploy to dev environment
DEPLOYMENT_TIER=dev cdk deploy --all
```

### Adding a New Knowledge Base

1. Update `KNOWLEDGE_BASES` in `.env`:
   ```bash
   KNOWLEDGE_BASES=docs,manuals,newkb
   ```

2. Redeploy stacks:
   ```bash
   cdk deploy IngestionStack EmbeddingsStack
   ```

3. Upload documents to new prefix:
   ```bash
   aws s3 cp ./newkb-docs/ s3://kb-documents-YOUR_ACCOUNT_ID/newkb/ --recursive
   ```

Partitions are created automatically on first document upload.

---

## Security

### Authentication

- **API Gateway**: Cognito JWT authorization
- **MCP**: RSA-signed JWT tokens
- **S3**: Bucket policies with least-privilege access
- **Lambda**: IAM roles with scoped permissions

### Network Isolation

- Milvus runs in private subnets (no internet access)
- Lambda functions use VPC endpoints for AWS services
- Security groups restrict traffic to necessary ports
- NACLs provide additional network-level protection

### Data Protection

- S3 buckets: Server-side encryption (SSE-S3)
- DynamoDB: Encryption at rest (AWS-managed keys)
- Secrets Manager: RSA keys for JWT signing
- CloudTrail: API activity logging for audit

### Compliance

- **GDPR**: Document versioning with retention policies
- **SOC 2**: CloudTrail logging, encryption at rest/in-transit
- **HIPAA**: Enable HIPAA-eligible services mode (requires BAA)

---

## Roadmap

- [ ] Multi-modal support (images, tables, charts)
- [ ] Reranking with cross-encoder models
- [ ] Query caching for frequently asked questions
- [ ] Admin UI for knowledge base management
- [ ] Fine-tuning embedding models on domain data
- [ ] Integration with Slack, Teams, ServiceNow

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Support

- **Documentation**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/rag-knowledge-base/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rag-knowledge-base/discussions)

---

**Built with AWS CDK, Amazon Bedrock, and Milvus**

Milvus partitions provide 4-5x faster queries than metadata filtering, making this system production-ready for large-scale knowledge retrieval workloads.
