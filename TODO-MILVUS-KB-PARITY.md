# Milvus Knowledge Base - Missing Components for Parity

**Status:** Infrastructure deployed (~$52/month vs $700 OpenSearch Serverless)

**Goal:** Achieve feature parity with deleted Bedrock Knowledge Bases

---

## ✅ What's Built

- **VPC + ECS Fargate**: Milvus Standalone container (private, Lambda-only access)
- **EFS Storage**: Persistent vector data storage
- **Query Lambda**: Basic Milvus query interface (search, insert, list)
- **Security**: Proper VPC isolation, security groups

---

## ❌ Missing Components (Tackle One-by-One)

### 1. **Embeddings Generation**

**Current State:** No way to convert text → vectors

**Needed:**
- Integration with embedding model (Titan Embeddings v2 or similar)
- Lambda function to call Bedrock for embeddings
- Batch processing support for large documents
- Consistent embedding dimensions (1024 for Titan v2)

**Estimated Effort:** 2-3 hours
**Cost Impact:** ~$0.01 per 1K documents (Titan pricing)

**Files to Create:**
- `lambda/embeddings-generator/handler.py`
- Update `lib/milvus-stack.ts` with Bedrock permissions

---

### 2. **Document Ingestion Pipeline**

**Current State:** No way to load documents into Milvus

**Needed:**
- S3 bucket for document uploads (PDFs, markdown, text)
- Lambda triggered by S3 uploads
- Document parsing (PyPDF2, markdown parser)
- Text chunking strategy (512 tokens, 20% overlap like old KB)
- Call embeddings Lambda → insert into Milvus
- Metadata storage (source file, chunk index, timestamps)

**Estimated Effort:** 4-6 hours
**Cost Impact:** ~$0.50 for 100 documents

**Files to Create:**
- `lambda/document-ingestor/handler.py`
- `lambda/document-ingestor/requirements.txt` (PyPDF2, langchain)
- Update `lib/milvus-stack.ts` with S3 bucket + event triggers

---

### 3. **RAG Query Pipeline (Bedrock Integration)**

**Current State:** Query Lambda can search Milvus but can't generate answers

**Needed:**
- Query flow: User question → embed question → Milvus search → retrieve chunks
- Pass retrieved chunks to Bedrock (Claude 3 Haiku)
- RAG prompt template: "Given context: {chunks}, answer: {question}"
- Return generated answer + source citations
- Handle no-results gracefully

**Estimated Effort:** 3-4 hours
**Cost Impact:** ~$0.25 per 1M input tokens, $1.25 per 1M output tokens

**Files to Update:**
- `lambda/milvus-query/handler.py` (add `rag_query` action)
- Add Bedrock permissions to query Lambda

---

### 4. **MCP Server Integration (Amazon Q CLI)**

**Current State:** No way for Q CLI to discover this KB

**Needed:**
- MCP server implementation (Python or TypeScript)
- Expose Milvus queries via MCP tools
- Tag-based discovery (like old KBs with `name=true`)
- Compatible with `~/.aws/amazonq/mcp.json` config
- Handle collection listing, search, stats

**Estimated Effort:** 6-8 hours (most complex)
**Cost Impact:** $0 (local process)

**Files to Create:**
- `mcp-server/milvus-mcp-server.py` (or .ts)
- `mcp-server/package.json` or `requirements.txt`
- Update README with MCP config instructions

---

## Priority Order (Suggested)

1. **Embeddings Generation** (prerequisite for everything)
2. **Document Ingestion Pipeline** (can load docs once embeddings work)
3. **RAG Query Pipeline** (can query and get answers)
4. **MCP Integration** (final piece for Q CLI compatibility)

---

## Current Cost Comparison

| Component | OpenSearch KB | Milvus (Current) | Milvus (Complete) |
|-----------|---------------|------------------|-------------------|
| Vector Storage | $350/month | $16/month (ECS) | $16/month |
| Infrastructure | $350/month (2nd OCU) | $33/month (NAT) | $33/month |
| Embeddings | Included | - | ~$0.01/1K docs |
| Queries | Included | - | ~$0.25/1M tokens |
| EFS | N/A | $3/month | $3/month |
| **Total** | **$700/month** | **$52/month** | **$52/month + usage** |

**Savings: ~$650/month (93%)** 🎉

---

## Next Steps

Choose which component to build first and we'll tackle it!
