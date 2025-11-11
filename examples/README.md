# Demo Scenarios & Examples

This directory contains examples and demo scenarios for testing both use cases: Q CLI knowledge retrieval and automated ticket triage.

---

## Table of Contents

1. [Q CLI Demo Scenarios](#q-cli-demo-scenarios)
2. [Ticket Triage Examples](#ticket-triage-examples)
3. [Sample Queries](#sample-queries)
4. [Expected Responses](#expected-responses)

---

## Q CLI Demo Scenarios

### Scenario 1: HPC Knowledge Base Queries

**Goal:** Demonstrate technical depth of HPC KB

```bash
q

# Discovery check
> what knowledge bases do you have access to?

# Basic NCCL query
> What is NCCL and how does it work?

# Advanced optimization query
> How do I optimize NCCL performance for an 8-GPU AllReduce operation?

# Troubleshooting query
> My NCCL bandwidth test shows low throughput. What should I check?

# Environment variable query
> What NCCL environment variables control GPU affinity?

# Comparison query
> What's the difference between NCCL and RCCL?
```

**Expected Results:**
- Clear explanations with source citations
- Code examples from documentation
- Links to relevant docs (NCCL official guides, HPC best practices)
- Practical troubleshooting steps

---

### Scenario 2: Presidio Knowledge Base Queries

**Goal:** Demonstrate business/solutions content retrieval

```bash
q

# Service overview
> What cloud migration services does Presidio offer?

# AWS partnership
> Tell me about Presidio's AWS partnership

# AI capabilities
> What are Presidio's AI and ML platform capabilities?

# Case study query
> Can you summarize the Q2 Holdings case study with Presidio?

# DevOps services
> What DevOps automation services does Presidio provide?

# Cybersecurity query
> What is Presidio's approach to zero trust security?
```

**Expected Results:**
- Business-focused responses
- Case study highlights
- Service descriptions
- References to specific documents (AWS partnership page, case studies)

---

### Scenario 3: Cross-KB Intelligence

**Goal:** Show that Q CLI doesn't get confused between domains

```bash
q

# Ask HPC question → should query HPC KB
> How do I debug CUDA kernel performance issues?

# Ask Presidio question → should query Presidio KB
> What cloud platforms does Presidio support besides AWS?

# Mixed question → should intelligently combine or clarify
> Does Presidio have experience with HPC GPU clusters?
```

**Expected Behavior:**
- Q CLI routes queries to appropriate KB automatically
- No manual KB selection needed
- Clear source attribution in responses

---

## Ticket Triage Examples

### Example 1: NCCL Performance Issue

**File:** `examples/ticket-nccl-performance.json`

```json
{
  "id": "TICKET-001",
  "title": "NCCL AllReduce performance degradation",
  "description": "Experiencing significantly slower AllReduce operations on our 8-GPU A100 cluster. Bandwidth tests show only 150 GB/s when we should be getting 300+ GB/s. Running NCCL 2.18 with CUDA 12.1 on NVLink-connected GPUs.",
  "email": "engineer@example.com",
  "timestamp": "2025-01-10T14:30:00Z",
  "environment": {
    "nccl_version": "2.18",
    "cuda_version": "12.1",
    "gpu_type": "A100",
    "num_gpus": 8,
    "interconnect": "NVLink"
  }
}
```

**Submit:**
```bash
aws s3 cp examples/ticket-nccl-performance.json s3://hpc-tickets-{ACCOUNT_ID}/
```

**Expected Triage:**
- **Category:** NCCL
- **Priority:** High (performance degradation)
- **Actions:**
  - Check NCCL_DEBUG environment variable
  - Verify GPU topology with nvidia-smi topo
  - Test with NCCL_ALGO=Ring
  - Check for CPU affinity issues
- **KB Response:** Detailed troubleshooting steps from NCCL guides

---

### Example 2: CUDA Testing Question

**File:** `examples/ticket-cuda-testing.json`

```json
{
  "id": "TICKET-002",
  "title": "Need CUDA unit testing framework recommendation",
  "description": "Our team is developing custom CUDA kernels and we need a robust testing framework. What tools and best practices are recommended for CUDA kernel testing and validation?",
  "email": "developer@example.com",
  "timestamp": "2025-01-10T15:45:00Z"
}
```

**Expected Triage:**
- **Category:** CUDA
- **Priority:** Medium (development question)
- **Actions:**
  - Review CUDA testing documentation
  - Consider Google Test with CUDA support
  - Use cuda-memcheck for validation
  - Set up CI/CD with GPU runners
- **KB Response:** Testing framework recommendations from CUDA docs

---

### Example 3: HPC Networking Question

**File:** `examples/ticket-networking.json`

```json
{
  "id": "TICKET-003",
  "title": "InfiniBand vs EFA for multi-node training",
  "description": "Planning a 64-node GPU cluster for large model training. Should we use InfiniBand or AWS EFA? What are the performance and cost trade-offs?",
  "email": "architect@example.com",
  "timestamp": "2025-01-10T16:20:00Z",
  "environment": {
    "num_nodes": 64,
    "gpus_per_node": 8,
    "cloud_provider": "AWS"
  }
}
```

**Expected Triage:**
- **Category:** Networking
- **Priority:** Medium (architectural decision)
- **Actions:**
  - Review HPC networking best practices
  - Compare InfiniBand vs EFA latency
  - Consider AWS-specific optimizations
  - Benchmark both options if possible
- **KB Response:** Networking comparison from HPC guides

---

### Example 4: Plain Text Ticket

**File:** `examples/ticket-simple.txt`

```
URGENT: NCCL crash on multi-GPU training

Our production training job is crashing with "NCCL error: unhandled system error"
Running 4x V100 GPUs, NCCL 2.17, CUDA 11.8
Need immediate help!

Contact: ops@example.com
```

**Submit:**
```bash
aws s3 cp examples/ticket-simple.txt s3://hpc-tickets-{ACCOUNT_ID}/
```

**Expected Triage:**
- **Category:** NCCL
- **Priority:** High (crash + "URGENT")
- **Actions:**
  - Check NCCL_DEBUG=INFO logs
  - Verify GPU health with nvidia-smi
  - Update to latest NCCL 2.18+
  - Check for CUDA driver issues
- **KB Response:** Troubleshooting steps for NCCL crashes

---

## Sample Queries

### Technical (HPC KB)

```
# Fundamentals
- What is collective communication in HPC?
- Explain AllReduce vs AllGather operations
- How does ring algorithm work in NCCL?

# Performance
- What factors affect NCCL bandwidth?
- How do I profile GPU communication overhead?
- What's the optimal message size for AllReduce?

# Troubleshooting
- NCCL hangs during initialization, what should I check?
- My bandwidth is lower than expected, how do I diagnose?
- What do NCCL timeout errors mean?

# Configuration
- What environment variables control NCCL behavior?
- How do I set CPU affinity for GPU workers?
- What NCCL algorithms are available?

# Advanced
- How does NCCL optimize for NVLink topology?
- What's the difference between NCCL and MPI?
- How do I implement custom NCCL collectives?
```

### Business (Presidio KB)

```
# Services
- What cloud services does Presidio offer?
- Tell me about Presidio's managed services
- What cybersecurity solutions does Presidio provide?

# Partnerships
- What's Presidio's relationship with AWS?
- Does Presidio have VMware expertise?
- What cloud platforms does Presidio support?

# Case Studies
- What healthcare customers has Presidio worked with?
- Tell me about Presidio's work with financial services
- What sports/entertainment projects has Presidio done?

# Technical Capabilities
- What AI/ML services does Presidio offer?
- How does Presidio approach cloud migration?
- What DevOps automation does Presidio provide?

# Industry Focus
- What government IT solutions does Presidio have?
- How does Presidio help with digital transformation?
- What are Presidio's FinOps capabilities?
```

---

## Expected Responses

### Good Response Example (HPC KB)

**Query:** "How do I optimize NCCL for AllReduce?"

**Expected Response:**
```
To optimize NCCL AllReduce performance:

1. **GPU Topology**: Ensure GPUs are NVLink-connected for maximum bandwidth
   - Verify with: nvidia-smi topo -m

2. **NCCL Algorithm**: Try different algorithms:
   - NCCL_ALGO=Ring (default, works on most topologies)
   - NCCL_ALGO=Tree (better for some hierarchical topologies)

3. **Environment Variables**:
   - Set NCCL_IB_HCA=mlx5 for InfiniBand
   - Use NCCL_SOCKET_IFNAME for correct network interface
   - Enable NCCL_DEBUG=INFO for diagnostics

4. **Message Size**: Larger messages (>1MB) typically achieve better bandwidth

5. **CPU Affinity**: Pin processes to CPUs near their GPUs

Sources:
- NCCL Official Performance Tuning Guide
- HPC Best Practices Documentation
```

### Poor Response Example

**Query:** "How do I optimize NCCL?"

**Bad Response:**
```
NCCL can be optimized. You should check the documentation.
```

**Why it's bad:**
- Too vague
- No actionable steps
- No source citations
- Doesn't use KB content

---

## Testing Workflow

### Complete Test Sequence

```bash
# 1. Verify deployment
aws cloudformation describe-stacks \
  --stack-name HpcKnowledgeBaseStack \
  --query 'Stacks[0].StackStatus'

aws cloudformation describe-stacks \
  --stack-name PresidioKnowledgeBaseStack \
  --query 'Stacks[0].StackStatus'

# 2. Test Q CLI discovery
q
> what knowledge bases do you have access to?
# Should list both KBs

# 3. Test HPC KB
> What is NCCL?
# Should get detailed technical response

# 4. Test Presidio KB
> What services does Presidio offer?
# Should get business-focused response

# 5. Test ticket triage
aws s3 cp examples/ticket-nccl-performance.json \
  s3://hpc-tickets-{ACCOUNT_ID}/test-$(date +%s).json

# 6. Check DynamoDB for results (wait 10 seconds)
aws dynamodb scan \
  --table-name hpc-ticket-triage \
  --max-items 1

# 7. Check CloudWatch logs
aws logs tail /aws/lambda/hpc-ticket-triage-processor --follow
```

---

## Troubleshooting Demo Issues

### Q CLI Not Finding KBs

**Check:**
1. MCP config: `cat ~/.aws/amazonq/mcp.json`
2. Tags: `aws bedrock-agent list-tags-for-resource --resource-arn {KB_ARN}`
3. AWS credentials: `aws sts get-caller-identity --profile {PROFILE}`

**Fix:**
```bash
# Restart Q CLI
q
```

### Ticket Not Processing

**Check:**
1. Lambda logs: `aws logs tail /aws/lambda/hpc-ticket-triage-processor --follow`
2. S3 bucket: `aws s3 ls s3://hpc-tickets-{ACCOUNT_ID}/`
3. DynamoDB: `aws dynamodb scan --table-name hpc-ticket-triage`

**Fix:**
- Verify ticket is .json or .txt
- Check Lambda has Bedrock permissions
- Retry upload

### Poor Response Quality

**Improve:**
1. Rephrase query more specifically
2. Check if relevant docs are in KB
3. Verify ingestion completed successfully
4. Try different question formats

---

## Demo Presentation Tips

1. **Start with discovery** - Show Q CLI finds both KBs automatically
2. **Show contrast** - Technical query → HPC KB, Business query → Presidio KB
3. **Highlight sources** - Point out Claude cites specific documents
4. **Demo ticket triage** - Upload ticket, show DynamoDB result within seconds
5. **Explain scalability** - Adding KB just requires tagging with `name=true`

---

For full documentation:
- [README.md](../README.md) - System overview
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical architecture
- [DATA_INGESTION.md](../DATA_INGESTION.md) - Adding content
