# Knowledge Base Data Ingestion Strategy

## Table of Contents

1. [Overview](#overview)
2. [Document Preparation](#document-preparation)
3. [Supported Formats](#supported-formats)
4. [Adding Documents to Existing KB](#adding-documents-to-existing-kb)
5. [Creating New Knowledge Bases](#creating-new-knowledge-bases)
6. [Chunking Strategy](#chunking-strategy)
7. [Ingestion Job Management](#ingestion-job-management)
8. [Best Practices](#best-practices)
9. [Presidio KB Example](#presidio-kb-example)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide explains how to add content to existing knowledge bases or create new ones. The system uses Amazon Bedrock's Knowledge Base service with OpenSearch Serverless for vector storage and Titan Embed Text v2 for embeddings.

### Key Concepts

- **Data Source**: S3 bucket containing source documents
- **Ingestion Job**: Process that chunks, embeds, and indexes documents
- **Chunking**: Splitting documents into smaller pieces for better retrieval
- **Embedding**: Converting text chunks into 1024-dimensional vectors
- **Indexing**: Storing vectors in OpenSearch for fast similarity search

---

## Document Preparation

### Content Guidelines

**1. Structure Your Content**
- Use clear headings (H1, H2, H3) to delineate sections
- Keep paragraphs focused on single topics
- Include examples and code snippets where relevant
- Add metadata in frontmatter (for Markdown)

**2. Optimize for RAG (Retrieval-Augmented Generation)**
- Write self-contained sections that make sense in isolation
- Avoid excessive cross-references ("as mentioned above")
- Include context in each section (repeat key terms)
- Use descriptive headings that capture section content

**3. File Naming Conventions**
```
Good:
  nccl-performance-tuning.md
  presidio-aws-partnership-overview.md
  cuda-error-troubleshooting-guide.pdf

Bad:
  doc1.md
  temp_notes.txt
  Untitled-2024.pdf
```

### Document Size Recommendations

| Document Type | Recommended Size | Rationale |
|---------------|------------------|-----------|
| Technical guides | 2-10 KB (500-2500 words) | Fits 4-20 chunks, good for deep technical content |
| Case studies | 3-8 KB (750-2000 words) | Single coherent narrative |
| API docs | 1-5 KB (250-1250 words) | Per-endpoint or per-function granularity |
| Whitepapers | 10-50 KB (2500-12500 words) | Can span 20-100 chunks |

**Why size matters:**
- Too small: Not enough context per chunk
- Too large: Irrelevant content pollutes retrieval
- Sweet spot: 5-15 chunks per document

---

## Supported Formats

Amazon Bedrock Knowledge Base supports the following formats:

| Format | Extension | Notes |
|--------|-----------|-------|
| **Markdown** | `.md` | Best for technical docs, preserves structure |
| **PDF** | `.pdf` | Extracts text automatically, images ignored |
| **Plain Text** | `.txt` | Simple but loses structure |
| **Microsoft Word** | `.docx` | Converted to text, formatting lost |
| **PowerPoint** | `.pptx` | Extracts slide text and notes |
| **HTML** | `.html` | Stripped to plain text |
| **JSON** | `.json` | Structured data, flattened for indexing |

### Format-Specific Considerations

**Markdown (.md):**
- ✅ Preserves headings, lists, code blocks
- ✅ Best for technical documentation
- ⚠️ Links and images ignored during indexing

**PDF (.pdf):**
- ✅ Native format for whitepapers, case studies
- ⚠️ OCR not performed (scanned PDFs won't index text)
- ⚠️ Complex layouts may have extraction issues

**Microsoft Word (.docx):**
- ✅ Common business format
- ⚠️ All formatting stripped (bold, italics, etc.)
- ⚠️ Tables may not convert cleanly

---

## Adding Documents to Existing KB

### Step-by-Step Process

#### 1. Upload Documents to S3

**HPC Knowledge Base:**
```bash
# Upload single file
aws s3 cp my-hpc-guide.md s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/

# Upload directory
aws s3 sync ./new-docs/ s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/
```

**Presidio Knowledge Base:**
```bash
aws s3 cp presidio-case-study.pdf s3://presidio-knowledge-base-docs-{ACCOUNT_ID}/
```

#### 2. Trigger Ingestion Job

**Option A: Via AWS CLI**
```bash
# Get Data Source ID
aws bedrock-agent list-data-sources \
  --knowledge-base-id MFULK64QPS \
  --region us-east-1 \
  --query 'dataSourceSummaries[0].dataSourceId' \
  --output text

# Start ingestion job
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id MFULK64QPS \
  --data-source-id {DATA_SOURCE_ID} \
  --region us-east-1
```

**Option B: Via AWS Console**
1. Navigate to Bedrock → Knowledge Bases
2. Select your KB (e.g., `hpc-computing-knowledge-base`)
3. Go to "Data sources" tab
4. Click "Sync" button
5. Confirm sync job

#### 3. Monitor Ingestion Progress

```bash
# Check ingestion job status
aws bedrock-agent get-ingestion-job \
  --knowledge-base-id MFULK64QPS \
  --data-source-id {DATA_SOURCE_ID} \
  --ingestion-job-id {JOB_ID} \
  --region us-east-1 \
  --query 'ingestionJob.{Status:status,Scanned:statistics.numberOfDocumentsScanned,Indexed:statistics.numberOfNewDocumentsIndexed,Failed:statistics.numberOfDocumentsFailed}' \
  --output table
```

**Expected output:**
```
-------------------------------------------
|            GetIngestionJob              |
+--------+----------+----------+----------+
| Failed | Indexed  | Scanned  | Status   |
+--------+----------+----------+----------+
| 0      | 25       | 25       | COMPLETE |
+--------+----------+----------+----------+
```

#### 4. Verify Indexing

**Test query via Q CLI:**
```bash
q

> What topics are covered in the latest document?
```

Or programmatically:
```bash
aws bedrock-agent-runtime retrieve-and-generate \
  --input "{\"text\": \"What is covered in the new document?\"}" \
  --retrieve-and-generate-configuration "{
    \"type\": \"KNOWLEDGE_BASE\",
    \"knowledgeBaseConfiguration\": {
      \"knowledgeBaseId\": \"MFULK64QPS\",
      \"modelArn\": \"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0\"
    }
  }" \
  --region us-east-1
```

---

## Creating New Knowledge Bases

### Using the Presidio KB as a Template

The Presidio KB demonstrates the pattern for creating additional knowledge bases. Follow these steps:

#### 1. Create New CDK Stack

**File:** `lib/my-new-kb-stack.ts`

```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

export class MyNewKnowledgeBaseStack extends cdk.Stack {
  public readonly kbArn: string;  // Export for cross-stack references

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 Bucket for documents
    const docsBucket = new s3.Bucket(this, 'DocsBucket', {
      bucketName: `my-kb-docs-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create Bedrock Knowledge Base
    const knowledgeBase = new bedrock.VectorKnowledgeBase(this, 'MyKnowledgeBase', {
      name: 'my-topic-knowledge-base',
      description: 'Knowledge base for [your domain]',
      embeddingsModel: bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024,
      instruction: 'Use this knowledge base to answer questions about [your topic].',
    });

    // CRITICAL: Tag for MCP discovery
    cdk.Tags.of(knowledgeBase).add('name', 'true');

    // Add S3 data source
    new bedrock.S3DataSource(this, 'DataSource', {
      bucket: docsBucket,
      knowledgeBase: knowledgeBase,
      dataSourceName: 'my-kb-s3-source',
      chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
        maxTokens: 512,
        overlapPercentage: 20,
      }),
    });

    // Outputs
    new cdk.CfnOutput(this, 'DocsBucketName', {
      value: docsBucket.bucketName,
      description: 'S3 bucket for documents',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseId', {
      value: knowledgeBase.knowledgeBaseId,
      description: 'Knowledge Base ID',
    });

    // Export ARN for cross-stack references
    this.kbArn = knowledgeBase.knowledgeBaseArn;
  }
}
```

#### 2. Update CDK App Entry Point

**File:** `bin/q_ticket_triage.ts`

```typescript
import { MyNewKnowledgeBaseStack } from '../lib/my-new-kb-stack';

const app = new cdk.App();

// Add your new KB stack
const myNewKb = new MyNewKnowledgeBaseStack(app, 'MyNewKnowledgeBaseStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-east-1'
  },
  description: 'My new knowledge base',
});

// If HPC Lambda needs access, pass ARN
new QTicketTriageStack(app, 'HpcKnowledgeBaseStack', {
  presidioKbArn: presidioStack.presidioKbArn,
  myNewKbArn: myNewKb.kbArn,  // Add this
});
```

#### 3. Deploy New Stack

```bash
# Install dependencies (if not done)
npm install

# Deploy
npx cdk deploy MyNewKnowledgeBaseStack --require-approval never

# Deployment output will show:
# - S3 bucket name
# - Knowledge Base ID
```

#### 4. Upload Initial Documents

```bash
# Sync your document collection
aws s3 sync ./my-docs/ s3://my-kb-docs-{ACCOUNT_ID}/

# Or use individual uploads
aws s3 cp important-doc.pdf s3://my-kb-docs-{ACCOUNT_ID}/
```

#### 5. Trigger Initial Ingestion

```bash
# Get data source ID
DATA_SOURCE_ID=$(aws bedrock-agent list-data-sources \
  --knowledge-base-id {YOUR_KB_ID} \
  --region us-east-1 \
  --query 'dataSourceSummaries[0].dataSourceId' \
  --output text)

# Start ingestion
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id {YOUR_KB_ID} \
  --data-source-id $DATA_SOURCE_ID \
  --region us-east-1
```

#### 6. Verify MCP Discovery

**No MCP configuration changes needed!** The tag-based discovery automatically picks up the new KB.

```bash
q

> what knowledge bases do you have access to?

# Should now list 3 KBs:
# - hpc-computing-knowledge-base
# - presidio-solutions-knowledge-base
# - my-topic-knowledge-base
```

---

## Chunking Strategy

### Current Configuration

```typescript
chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
  maxTokens: 512,
  overlapPercentage: 20,
})
```

### Why These Values?

**Max Tokens: 512**
- ~2000 characters per chunk
- Fits within Claude 3 Haiku context window comfortably
- Large enough for semantic coherence
- Small enough for precise retrieval

**Overlap: 20% (102 tokens)**
- Prevents concepts from being split across chunks
- Ensures continuity for queries that span boundaries
- Minimal redundancy while maintaining context

### Alternative Strategies

**For Long-Form Content (whitepapers, case studies):**
```typescript
chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
  maxTokens: 768,
  overlapPercentage: 25,
})
```
Rationale: Longer chunks preserve narrative flow

**For API Documentation or Reference Material:**
```typescript
chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
  maxTokens: 256,
  overlapPercentage: 15,
})
```
Rationale: Shorter chunks for precise lookup

**Hierarchical Chunking (Future):**
Not yet supported by Bedrock, but on roadmap:
- Level 1: Document summary (1024 tokens)
- Level 2: Section summaries (512 tokens)
- Level 3: Detailed chunks (256 tokens)

---

## Ingestion Job Management

### Job Lifecycle

```
STARTING → IN_PROGRESS → COMPLETE
              ↓
            FAILED
```

### Typical Timings

| Document Count | Expected Duration | Parallel Jobs |
|----------------|-------------------|---------------|
| 1-10 docs      | 30-60 seconds     | N/A           |
| 10-50 docs     | 1-3 minutes       | 1 job at a time |
| 50-100 docs    | 3-8 minutes       | 1 job at a time |
| 100+ docs      | 8-20 minutes      | 1 job at a time |

**Note:** Only one ingestion job can run per data source at a time. Queue additional uploads.

### Monitoring Commands

**List recent jobs:**
```bash
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id MFULK64QPS \
  --data-source-id {DATA_SOURCE_ID} \
  --region us-east-1 \
  --max-results 10
```

**Watch job progress (loop):**
```bash
watch -n 10 "aws bedrock-agent get-ingestion-job \
  --knowledge-base-id MFULK64QPS \
  --data-source-id {DATA_SOURCE_ID} \
  --ingestion-job-id {JOB_ID} \
  --region us-east-1 \
  --query 'ingestionJob.{Status:status,Scanned:statistics.numberOfDocumentsScanned}' \
  --output table"
```

### Failed Ingestion Handling

**Common failure reasons:**
1. **Unsupported file format** - Check file extension
2. **Corrupt file** - Re-upload or repair
3. **Empty file** - Ensure content exists
4. **Permission errors** - Verify IAM roles
5. **S3 access issues** - Check bucket policies

**Recovery steps:**
```bash
# Check failed job details
aws bedrock-agent get-ingestion-job \
  --knowledge-base-id MFULK64QPS \
  --data-source-id {DATA_SOURCE_ID} \
  --ingestion-job-id {FAILED_JOB_ID} \
  --region us-east-1 \
  --query 'ingestionJob.failureReasons'

# Fix issues and retry
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id MFULK64QPS \
  --data-source-id {DATA_SOURCE_ID} \
  --region us-east-1
```

---

## Best Practices

### 1. Organize by Topic

```
s3://my-kb-docs-{account}/
├── fundamentals/
│   ├── intro.md
│   ├── concepts.md
│   └── architecture.md
├── how-to-guides/
│   ├── setup.md
│   ├── configuration.md
│   └── troubleshooting.md
├── api-reference/
│   └── api-docs.pdf
└── case-studies/
    ├── customer-a.md
    └── customer-b.md
```

**Benefits:**
- Easier to manage and update
- Clear semantic boundaries
- Simpler debugging of retrieval issues

### 2. Version Your Documents

**Filename pattern:**
```
nccl-optimization-guide-v2.1.md
presidio-aws-services-2024-q4.pdf
```

**Or use S3 versioning:**
- Enable versioning on bucket (already done in CDK)
- Bedrock always uses latest version
- Can roll back by restoring previous version

### 3. Add Metadata (Markdown Frontmatter)

```markdown
---
title: "NCCL Performance Tuning Guide"
version: "2.1"
date: "2024-11-10"
author: "HPC Team"
tags: ["nccl", "performance", "gpu"]
---

# NCCL Performance Tuning Guide

Content here...
```

**Benefits:**
- Improves retrievability (metadata is indexed)
- Helps with source attribution
- Easier content management

### 4. Test Retrieval Quality

After adding documents, test with representative queries:

```bash
q

# Test broad query
> What topics does the knowledge base cover?

# Test specific query
> How do I optimize NCCL for large clusters?

# Test edge case
> What's the difference between NCCL 2.17 and 2.18?
```

### 5. Incremental Updates

**Don't delete and re-upload everything.** Add new documents incrementally:

```bash
# Add new doc
aws s3 cp new-guide.md s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/

# Sync (only uploads changed files)
aws s3 sync ./updated-docs/ s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/

# Trigger ingestion
aws bedrock-agent start-ingestion-job ...
```

**Bedrock handles:**
- Detecting new files
- Re-indexing modified files
- Removing deleted files

---

## Presidio KB Example

### Document Collection Process

The Presidio Knowledge Base demonstrates automated document collection:

**Script:** `scripts/download-presidio-docs.sh`

```bash
#!/bin/bash
# Downloads 26 Presidio documents from public sources
# Converts HTML to Markdown using pandoc
# Organizes by category (case-studies, technical-blogs, etc.)

# Example usage:
bash scripts/download-presidio-docs.sh

# Output:
# docs/presidio/
# ├── case-studies/ (9 files)
# ├── technical-blogs/ (9 files)
# ├── partner-docs/ (7 files)
# └── solution-briefs/ (2 PDFs)
```

### Documents Ingested

| Category | Count | Format | Examples |
|----------|-------|--------|----------|
| Case Studies | 9 | Markdown | Q2 Holdings, NHL, DraftKings |
| Technical Blogs | 9 | Markdown | AI, Cloud, Security topics |
| Partner Docs | 7 | Markdown | AWS partnership, FinOps, DevOps |
| Solution Briefs | 2 | PDF | Fortinet SD-WAN, VMware Security |

**Total:** 26 documents, 25 indexed (1 failed due to corrupt source)

### Ingestion Results

```bash
$ aws bedrock-agent get-ingestion-job --knowledge-base-id BXSQ7KURLO ...

Status: COMPLETE
Scanned: 26 documents
Indexed: 25 documents
Failed: 1 document (corrupt PDF)
Duration: 32 seconds
```

### Reproducibility

To regenerate Presidio KB content:

```bash
# Clean existing docs
rm -rf docs/presidio/

# Re-download (script is idempotent)
bash scripts/download-presidio-docs.sh

# Upload to S3
aws s3 sync docs/presidio/ s3://presidio-knowledge-base-docs-{ACCOUNT_ID}/

# Trigger ingestion
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id BXSQ7KURLO \
  --data-source-id 59TYDS4YOH \
  --region us-east-1
```

---

## Troubleshooting

### Issue: Documents Not Indexed

**Symptoms:**
- Ingestion job shows `Scanned: 0`
- Q CLI can't find content

**Diagnosis:**
```bash
# Check S3 bucket contents
aws s3 ls s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/ --recursive

# Verify data source configuration
aws bedrock-agent get-data-source \
  --knowledge-base-id MFULK64QPS \
  --data-source-id {DATA_SOURCE_ID} \
  --region us-east-1
```

**Solutions:**
1. Verify files are in correct S3 bucket
2. Check file extensions are supported
3. Ensure IAM role has S3 read permissions
4. Retry ingestion job

---

### Issue: Poor Retrieval Quality

**Symptoms:**
- Q CLI returns irrelevant answers
- Missing expected documents in results

**Diagnosis:**
```bash
# Test direct retrieval
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id MFULK64QPS \
  --retrieval-query "{\"text\": \"test query\"}" \
  --region us-east-1
```

**Solutions:**
1. **Improve document structure** - Add clear headings
2. **Adjust chunking** - Try larger chunks (768 tokens)
3. **Add metadata** - Include tags and descriptions
4. **Refine queries** - Be more specific in prompts
5. **Review content** - Ensure documents actually contain expected info

---

### Issue: Ingestion Job Stuck

**Symptoms:**
- Job status remains `IN_PROGRESS` for >30 minutes
- No progress on scanned documents

**Solutions:**
```bash
# Cancel stuck job (not directly supported, wait for timeout)
# Timeout after 2 hours

# Check CloudWatch logs for errors
aws logs tail /aws/bedrock/knowledgebases --follow

# Start new job after timeout
aws bedrock-agent start-ingestion-job ...
```

---

### Issue: Duplicate Content

**Symptoms:**
- Same information returned multiple times
- Responses feel repetitive

**Diagnosis:**
- Check for duplicate files in S3
- Review document overlap

**Solutions:**
```bash
# Find duplicate files (by size)
aws s3 ls s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/ --recursive \
  | sort -k3 -n | uniq -f2 -D

# Remove duplicates
aws s3 rm s3://hpc-knowledge-base-docs-{ACCOUNT_ID}/duplicate.md

# Re-sync
aws bedrock-agent start-ingestion-job ...
```

---

## Summary Checklist

**Adding Documents:**
- [ ] Prepare documents (structure, naming, metadata)
- [ ] Upload to S3 bucket
- [ ] Trigger ingestion job
- [ ] Monitor job completion
- [ ] Test retrieval with Q CLI
- [ ] Document the update

**Creating New KB:**
- [ ] Create new CDK stack (copy Presidio pattern)
- [ ] Tag KB with `name=true`
- [ ] Deploy stack via CDK
- [ ] Upload initial documents
- [ ] Trigger first ingestion
- [ ] Verify MCP discovery
- [ ] Test queries

**Best Practices:**
- [ ] Organize documents by topic
- [ ] Use clear filenames
- [ ] Add metadata frontmatter
- [ ] Test incremental updates
- [ ] Monitor ingestion metrics
- [ ] Track document versions

---

For architecture details, see [ARCHITECTURE.md](./ARCHITECTURE.md).
For system overview, see [README.md](./README.md).
