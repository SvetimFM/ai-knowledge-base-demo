# Knowledge Base Inventory

**Knowledge Base ID**: `MFULK64QPS`
**Name**: `hpc-computing-knowledge-base`
**Status**: ACTIVE
**Last Updated**: 2025-11-10
**Region**: us-east-1
**Profile**: hyperadmin

## Summary Statistics

- **Total Documents**: 21 files
- **Total Size**: ~11 MB
- **Document Types**: Markdown (12), PDF (9)
- **Topics**: HPC, NCCL, RCCL, CUDA, CDI, FabreX, CFD, AI
- **Estimated Tokens**: ~120,000 tokens

## Configuration

- **Embeddings Model**: Titan Embed Text v2 (1024 dimensions)
- **Generation Model**: Claude 3 Haiku
- **Chunking Strategy**: Fixed size, 512 tokens, 20% overlap
- **Vector Store**: OpenSearch Serverless (auto-managed)
- **S3 Bucket**: `s3://hpc-knowledge-base-docs-053861712634/`

---

## Document Inventory

### 1. HPC Foundations (6 Markdown files)

Original custom documentation covering HPC computing fundamentals:

| File | Size | Topics Covered |
|------|------|----------------|
| `nccl-overview.md` | ~8 KB | NVIDIA Collective Communications Library, GPU-optimized collectives, AllReduce, Broadcast |
| `rccl-overview.md` | ~7 KB | AMD ROCm Collective Communications Library, ROCm ecosystem, multi-GPU training |
| `cuda-testing.md` | ~9 KB | CUDA kernel testing, unit testing frameworks, validation strategies |
| `hpc-networking.md` | ~10 KB | Network topology, InfiniBand, Ethernet, GPUDirect RDMA |
| `hpc-communication-patterns.md` | ~12 KB | AllReduce, AllGather, ReduceScatter, ring algorithms, performance characteristics |
| `hpc-best-practices.md` | ~11 KB | General HPC optimization, profiling, debugging, scalability |

**Total**: ~57 KB, ~15,000 tokens

---

### 2. NVIDIA Official Documentation (7 files)

Official NVIDIA NCCL documentation converted from HTML to Markdown:

| File | Size | Source | Topics Covered |
|------|------|--------|----------------|
| `nvidia/nccl-official-overview.md` | 28 KB | [NCCL 2.28.6 Docs](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html) | NCCL architecture, design goals, performance characteristics |
| `nvidia/nccl-official-usage.md` | 31 KB | [NCCL Usage](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage.html) | Getting started, initialization, basic usage, code examples |
| `nvidia/nccl-official-collectives.md` | 33 KB | [Collectives](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html) | Detailed API reference for all collective operations |
| `nvidia/nccl-official-api.md` | 30 KB | [API Reference](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api.html) | Complete NCCL API documentation, function signatures, parameters |
| `nvidia/nccl-official-env-vars.md` | 103 KB | [Environment Vars](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html) | Comprehensive environment variable reference for tuning NCCL |
| `nvidia/nccl-official-troubleshooting.md` | 41 KB | [Troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html) | Common issues, debugging techniques, performance optimization |
| `nvidia-nccl-sc15.pdf` | 1.4 MB | [NVIDIA SC15](https://images.nvidia.com/events/sc15/pdfs/NCCL-Woolley.pdf) | Original NCCL presentation, ring algorithms, topology awareness |

**Total**: ~267 KB + 1.4 MB = ~1.67 MB, ~50,000 tokens

---

### 3. GigaIO Composable Infrastructure (8 PDFs)

Official GigaIO documentation on CDI and FabreX technology:

#### Primers & Core Documentation

| File | Size | Description |
|------|------|-------------|
| `gigaio-cdi-primer-v2-1.pdf` | 591 KB | Comprehensive CDI primer - architecture, benefits, use cases |
| `gigaio-fabrex-primer-v2-1.pdf` | 515 KB | FabreX PCIe memory fabric overview - technology, topology, performance |
| `gigaio-cdi-comparison-v2-0.pdf` | 133 KB | CDI vs traditional architectures - comparison tool, TCO analysis |
| `gigaio-fabrex-cdi-cxl-pcie5.pdf` | 263 KB | Next-gen composability with CXL and PCIe 5.0 |

#### White Papers

| File | Size | Description |
|------|------|-------------|
| `gigaio-microchip-cdi-wp-2020.pdf` | 1.0 MB | Original Microchip collaboration white paper (2020) - cloud-class CDI |
| `gigaio-microchip-2021.pdf` | 680 KB | Updated Microchip partnership documentation (2021) |

#### Case Studies

| File | Size | Description |
|------|------|-------------|
| `gigaio-microchip-ai-case-study.pdf` | 5.7 MB | PCIe for AI workloads - real-world deployment, performance benchmarks |
| `gigaio-fluidx3d-cfd-case-study.pdf` | 2.3 MB | FluidX3D computational fluid dynamics - HPC use case, performance gains |

**Total**: ~11 MB, ~55,000 tokens

---

## Knowledge Base Coverage

### Topics Covered

✅ **NCCL/RCCL Fundamentals**
- Collective communication operations
- Ring algorithms and topology awareness
- Environment variable tuning
- Performance optimization
- Troubleshooting and debugging

✅ **HPC Infrastructure**
- Network topology (InfiniBand, Ethernet)
- GPUDirect RDMA
- Multi-GPU training patterns
- Communication patterns (AllReduce, AllGather, etc.)

✅ **CUDA Development**
- Kernel testing methodologies
- Validation frameworks
- Best practices

✅ **Composable Disaggregated Infrastructure (CDI)**
- Architecture and design principles
- FabreX PCIe memory fabric technology
- Resource pooling and composability
- Next-gen CXL and PCIe 5.0 integration

✅ **Real-World Applications**
- AI/ML workload optimization
- Computational Fluid Dynamics (CFD)
- HPC system architecture
- Cloud-class composability

### Use Cases Supported

1. **HPC System Design** - Network topology, resource allocation, composability
2. **Multi-GPU Training** - NCCL/RCCL configuration, performance tuning
3. **Performance Troubleshooting** - Debug techniques, environment variables, profiling
4. **Infrastructure Modernization** - CDI adoption, cost analysis, migration strategies
5. **AI Workload Optimization** - PCIe fabric, GPU pooling, shared resources
6. **CFD Simulations** - Large-scale distributed computing, performance scaling

---

## Ingestion History

| Date | Documents | Type | Ingestion Job ID | Status |
|------|-----------|------|------------------|--------|
| 2025-11-10 (Initial) | 6 | Markdown (HPC) | - | ✅ Complete |
| 2025-11-10 (Phase 1) | 5 | PDF (NVIDIA + GigaIO) | - | ✅ Complete |
| 2025-11-10 (Phase 3) | 6 | Markdown (NVIDIA official) | KHPQUII5LR | ✅ Complete |
| 2025-11-10 (Phase 4) | 4 | PDF (GigaIO case studies) | DT9OHADIHH | ⏳ In Progress |

---

## Query Examples

### NCCL Performance Tuning
```
Q: How can I optimize NCCL performance for multi-GPU training?
Expected Sources: nvidia/nccl-official-env-vars.md, nccl-overview.md, hpc-best-practices.md
```

### CDI Architecture
```
Q: What is Composable Disaggregated Infrastructure and how does it differ from traditional server architecture?
Expected Sources: gigaio-cdi-primer-v2-1.pdf, gigaio-cdi-comparison-v2-0.pdf
```

### Troubleshooting
```
Q: My distributed training is hanging with NCCL. What should I check?
Expected Sources: nvidia/nccl-official-troubleshooting.md, hpc-networking.md
```

### FabreX Technology
```
Q: How does FabreX enable rack-scale composability?
Expected Sources: gigaio-fabrex-primer-v2-1.pdf, gigaio-fabrex-cdi-cxl-pcie5.pdf
```

### Real-World Applications
```
Q: What are proven use cases for composable infrastructure in AI workloads?
Expected Sources: gigaio-microchip-ai-case-study.pdf, gigaio-fluidx3d-cfd-case-study.pdf
```

---

## Access Methods

### 1. Amazon Q Developer CLI (MCP Integration)
- **Configuration**: `~/.aws/amazonq/mcp.json`
- **Auto-discovery**: Via tag `name=hpc-knowledge-base`
- **Tools**: `ListKnowledgeBases`, `QueryKnowledgeBases`

### 2. Direct Bedrock API
```python
import boto3

bedrock = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

response = bedrock.retrieve_and_generate(
    input={'text': 'Your query here'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'MFULK64QPS',
            'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
        }
    }
)
```

### 3. Ticket Triage Lambda
- Automatically queries KB for incoming HPC support tickets
- Categorizes by: NCCL, RCCL, CUDA, Networking, Performance, CDI
- Suggests troubleshooting actions
- Stores results in DynamoDB

---

## Maintenance

### Adding New Documents

1. Upload to S3:
   ```bash
   aws s3 cp new-doc.pdf s3://hpc-knowledge-base-docs-053861712634/
   ```

2. Trigger ingestion:
   ```bash
   ./scripts/sync-kb.sh
   ```

3. Monitor ingestion:
   ```bash
   aws bedrock-agent list-ingestion-jobs \
     --knowledge-base-id MFULK64QPS \
     --profile hyperadmin
   ```

### Updating Existing Documents

- S3 versioning is enabled
- Re-upload with same filename triggers automatic re-ingestion
- Previous versions retained for 30 days

### Cost Monitoring

**Current Usage** (21 documents, ~120K tokens):
- **Storage**: 2 OCUs minimum = ~$90/month (OpenSearch Serverless)
- **Embeddings**: ~$0.002 per ingestion (one-time)
- **Queries**: $0.0006/1K tokens (varies by usage)

**Estimated Monthly Cost** (1000 queries/day):
- Storage: $90
- Query inference: ~$135-180
- **Total**: ~$225-270/month

---

## Security Status

### ✅ Secure Components

- **S3 Buckets**: Private, encrypted (S3-managed encryption)
- **MCP Server**: Local-only, uses user AWS credentials
- **Knowledge Base**: IAM-restricted access
- **Lambda IAM**: Scoped DynamoDB and S3 permissions

### 🔴 Known Issues (Documented, Not Fixed)

1. **SES Permissions Too Broad**: Lambda can send as any email address (`resources: ['*']`)
2. **No Email Validation**: Accepts any email in ticket submissions
3. **Prompt Injection Vulnerability**: User input directly in LLM prompts
4. **No Rate Limiting**: Lambda can be triggered unlimited times
5. **S3 Bucket Access**: Any IAM user in account can upload tickets

**Status**: Security hardening deferred to future phase per user request.

---

## Future Enhancements

### Planned Additions

1. **More NVIDIA Documentation**
   - NCCL Developer Guide
   - CUDA Toolkit documentation
   - Multi-GPU programming guide

2. **AMD ROCm Documentation**
   - RCCL official docs
   - ROCm installation guides
   - AMD GPU architecture

3. **Additional Case Studies**
   - TACC Lonestar6 deployment
   - More GigaIO customer implementations
   - Performance benchmarking results

### Potential Improvements

1. **Enhanced Chunking**: Semantic chunking instead of fixed-size
2. **Metadata Filtering**: Add tags for document type, version, topic
3. **Hybrid Search**: Combine vector search with keyword filtering
4. **Multi-modal Support**: Include architecture diagrams, charts
5. **Reranking**: Enable Bedrock KB reranking for improved precision

---

## Testing & Validation

See `QCLI_TEST_GUIDE.md` for comprehensive Q CLI testing procedures.

**Key Test Queries**:
- NCCL performance optimization
- CDI architecture comparison
- Troubleshooting distributed training
- FabreX use cases
- Real-world deployment examples

**Expected Results**:
- Accurate citations from knowledge base
- Comprehensive answers drawing from multiple sources
- Proper source attribution
