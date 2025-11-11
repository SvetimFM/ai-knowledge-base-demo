# Q CLI + Knowledge Base Integration Test Guide

## What We Fixed

**Problem**: Q CLI's `ListKnowledgeBases` was returning empty, causing Q to guess the KB ID incorrectly.

**Root Cause**: MCP config had `"KB_INCLUSION_TAG_KEY": "name=hpc-knowledge-base"` (wrong format)

**Fix**: Changed to `"KB_INCLUSION_TAG_KEY": "name"` (just the tag key, not key=value)

## Testing Steps

### 1. Restart Q CLI

Exit and restart Q CLI to reload the updated MCP configuration:

```bash
# Exit Q CLI
exit

# Start fresh Q CLI session
q
```

### 2. Verify MCP Server Loaded

You should see:
```
✓ awslabs.bedrock-kb-retrieval-mcp-server loaded in ~1-2s
```

### 3. Check Available MCP Tools

```bash
/tools
```

**Expected Output**:
```
awslabs.bedrock-kb-retrieval-mcp-server (MCP):
- ListKnowledgeBases     * not trusted
- QueryKnowledgeBases    * not trusted
```

### 4. Trust the MCP Tools

When Q prompts to use an MCP tool, respond with `t` to trust it for the session:
```
Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:
> t
```

### 5. Test Knowledge Base Discovery

Ask Q to list available knowledge bases:

**Query**:
> "What knowledge bases are available?"

**Expected Result**: Q should use `ListKnowledgeBases` and return:
- Knowledge Base ID: `MFULK64QPS`
- Name: `hpc-computing-knowledge-base`
- Status: ACTIVE

### 6. Test Automatic KB Querying

Now Q should automatically query the KB without you specifying the ID. Try these test queries:

#### Test Query 1: NCCL Basics
```
What is NCCL and what are its main features?
```

**Expected**: Response citing your `nccl-overview.md` documentation about NVIDIA Collective Communications Library, GPU-optimized collectives, etc.

#### Test Query 2: Performance Optimization
```
How can I optimize NCCL performance for multi-GPU training? What are the key environment variables?
```

**Expected**: Response citing documentation about:
- `NCCL_SOCKET_IFNAME`
- `NCCL_IB_DISABLE`
- `NCCL_NET_GDR_LEVEL`
- GPUDirect RDMA
- InfiniBand tuning

#### Test Query 3: Troubleshooting
```
My distributed training is hanging with NCCL. What should I check?
```

**Expected**: Response citing troubleshooting steps from your documentation:
- Check topology with `nvidia-smi topo -m`
- Verify all ranks call NCCL operations
- Check network connectivity
- Increase `NCCL_TIMEOUT`
- Enable debug with `NCCL_DEBUG=INFO`

#### Test Query 4: GigaIO CDI (New Content)
```
What is Composable Disaggregated Infrastructure and how does FabreX work?
```

**Expected**: Response citing the GigaIO PDFs you added:
- CDI definition and benefits
- FabreX as PCIe memory fabric
- Resource pooling and composability
- CXL and PCIe 5.0 integration

#### Test Query 5: Specific NVIDIA Content
```
What did the NVIDIA NCCL SC15 presentation cover about ring algorithms?
```

**Expected**: Response citing the `nvidia-nccl-sc15.pdf`:
- Ring-based AllReduce algorithm
- Bandwidth-optimal (N-1)/N efficiency
- Topology awareness
- Performance characteristics

## Success Criteria

✅ **ListKnowledgeBases returns KB**: Q should find `MFULK64QPS` without you specifying it

✅ **No manual KB ID needed**: Q shouldn't ask you for the knowledge base ID

✅ **Accurate responses**: Q should cite specific documents from your knowledge base

✅ **Citations included**: Q should reference which documents it used (check for source citations)

✅ **Handles 11 documents**: Q should be able to pull from all your docs:
  - 6 HPC markdown files
  - 1 NVIDIA SC15 PDF
  - 4 GigaIO PDFs

## Troubleshooting

### MCP Server Still Not Finding KB

Check the tag on your Knowledge Base:
```bash
aws bedrock-agent list-tags-for-resource \
  --profile hyperadmin \
  --region us-east-1 \
  --resource-arn "arn:aws:bedrock:us-east-1:053861712634:knowledge-base/MFULK64QPS" \
  --output json
```

Should show: `"name": "hpc-knowledge-base"`

### Q Still Using Wrong KB ID

Clear Q CLI cache and restart:
```bash
# Kill any background MCP processes
pkill -f bedrock-kb-retrieval-mcp-server

# Restart Q
q
```

### Verify MCP Config Location

Ensure config is in the **global** location, not workspace:
```bash
cat ~/.aws/amazonq/mcp.json
```

Should show `"KB_INCLUSION_TAG_KEY": "name"`

## Next Steps After Testing

Once you confirm Q CLI can auto-discover and query the KB:

1. **Document successful test results** - Save example Q&A sessions
2. **Proceed with Phase 3** - Convert NVIDIA NCCL HTML docs to Markdown
3. **Proceed with Phase 4** - Add remaining GigaIO resources
4. **Create demo scenarios** - Build realistic HPC support ticket scenarios

## Current Knowledge Base Contents

Your KB currently has **11 documents** (~75,000 tokens):

### HPC Documentation (Markdown)
1. `nccl-overview.md` - NVIDIA Collective Communications Library
2. `rccl-overview.md` - AMD ROCm equivalent
3. `cuda-testing.md` - CUDA kernel testing practices
4. `hpc-networking.md` - Network topology for HPC
5. `hpc-communication-patterns.md` - AllReduce, AllGather patterns
6. `hpc-best-practices.md` - General HPC optimization

### NVIDIA Documentation (PDF)
7. `nvidia-nccl-sc15.pdf` - Official NCCL presentation from SC15

### GigaIO CDI Documentation (PDF)
8. `gigaio-cdi-primer-v2-1.pdf` - CDI concepts and architecture
9. `gigaio-fabrex-primer-v2-1.pdf` - FabreX PCIe fabric overview
10. `gigaio-cdi-comparison-v2-0.pdf` - CDI vs traditional architectures
11. `gigaio-fabrex-cdi-cxl-pcie5.pdf` - Next-gen integration guide

## Knowledge Base Info

- **ID**: `MFULK64QPS`
- **Name**: `hpc-computing-knowledge-base`
- **Region**: `us-east-1`
- **Profile**: `hyperadmin`
- **Embeddings**: Titan Embed Text v2 (1024 dimensions)
- **LLM**: Claude 3 Haiku
- **Chunking**: 512 tokens, 20% overlap
- **Storage**: OpenSearch Serverless (auto-managed by AWS Labs construct)
