# Documentation Directory

This directory contains documentation files for the knowledge bases. **These files are not tracked in git** to keep the repository lightweight and fast.

## Required Documentation

### HPC Computing Knowledge Base

The following files should be in this directory:

**Markdown Files:**
- `cuda-testing.md` - CUDA testing frameworks and best practices
- `hpc-best-practices.md` - General HPC optimization strategies
- `hpc-communication-patterns.md` - AllReduce, AllGather, Broadcast patterns
- `hpc-networking.md` - InfiniBand, EFA, network topology
- `nccl-overview.md` - NVIDIA Collective Communications Library overview
- `rccl-overview.md` - ROCm Collective Communications Library overview

**PDF Files:**
- `networks-for-hpc-survey.pdf` - Academic survey on HPC networking
- `nvidia-nccl-sc15.pdf` - NVIDIA NCCL technical presentation
- GigaIO case studies and technical documentation (8 PDFs)

**NVIDIA Documentation (`nvidia/` subdirectory):**
- 6 official NCCL documentation files (converted from HTML)

### Presidio IT Solutions Knowledge Base

**Location:** `presidio/` subdirectory (26 files)

## How to Obtain Documentation

### Option 1: Download Presidio Docs (Automated)

```bash
# From project root
bash scripts/download-presidio-docs.sh
```

This script will:
- Create the `docs/presidio/` directory
- Download 26 Presidio documents from their website
- Format them for knowledge base ingestion

### Option 2: Manual Collection

If you have HPC or GigaIO documentation:

1. Place markdown files directly in `docs/`
2. Place PDF files directly in `docs/`
3. Place NVIDIA HTML documentation in `docs/nvidia/`

### Option 3: Use Your Own Documentation

You can replace these with your own domain-specific documentation:

1. **Markdown files** - Any technical documentation
2. **PDF files** - Whitepapers, case studies, manuals
3. **Text files** - Plain text documentation

## After Adding Documentation

### 1. Upload to S3

```bash
# HPC Knowledge Base
bash scripts/deploy-docs.sh

# Or manually:
aws s3 sync docs/ s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/ \\
  --exclude "presidio/*" \\
  --exclude "README.md" \\
  --profile your-profile
```

### 2. Trigger Ingestion

```bash
# Sync and ingest into knowledge base
bash scripts/sync-kb.sh
```

### 3. Verify Ingestion

```bash
# Check ingestion status
aws bedrock-agent list-data-sources \\
  --knowledge-base-id {KB_ID} \\
  --profile your-profile
```

## File Requirements

### Supported Formats
- **Markdown** (.md) - Best for structured text
- **PDF** (.pdf) - For existing documentation
- **Text** (.txt) - Plain text files

### Size Limits
- Individual files: Max 50 MB
- Total directory: No hard limit, but keep reasonable for S3 sync performance

### Best Practices
- Use descriptive filenames
- Keep files under 10 MB when possible
- Organize in subdirectories if you have many files
- Avoid special characters in filenames

## Knowledge Base Configuration

Once uploaded to S3 and ingested, the files are:
- **Chunked** into 512-token segments with 20% overlap
- **Embedded** using Amazon Titan Embed Text v2 (1024 dimensions)
- **Indexed** in OpenSearch Serverless vector store
- **Tagged** with `name=true` for MCP discovery

## Troubleshooting

### Docs not appearing in knowledge base?
1. Check S3 bucket: `aws s3 ls s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/`
2. Verify ingestion job completed: `bash scripts/sync-kb.sh`
3. Wait 2-5 minutes for ingestion to complete

### Query not finding relevant info?
- Try rephrasing your question
- Check if the topic is actually in your documentation
- Verify file uploaded successfully to S3

### Permission errors?
- Ensure your AWS profile has Bedrock and S3 permissions
- Check IAM role attached to knowledge base

---

For more information, see the main [README.md](../README.md) and [DATA_INGESTION.md](../DATA_INGESTION.md).
