#!/bin/bash
# Comprehensive HPC Documentation Download Script
# Downloads documentation from NVIDIA, AMD, GitHub repos, and community resources
# For HPC computing, node configuration, and LLM benchmarking

set -e

BASE_DIR="/mnt/j/DevWorkspace/Active Projects/Q_TicketTriage/docs"
TEMP_DIR="/tmp/hpc-docs"

mkdir -p "$TEMP_DIR"
mkdir -p "$BASE_DIR"/{nvidia,amd,github-repos,community,benchmarking,llm-benchmarking}

echo "🚀 Downloading Comprehensive HPC Documentation"
echo "=============================================================="
echo ""

# Function to download PDFs
download_pdf() {
    local url="$1"
    local output_file="$2"
    local title="$3"

    echo "📥 Downloading: $title"

    if wget -q --timeout=30 --tries=3 "$url" -O "$output_file" 2>/dev/null; then
        size=$(du -h "$output_file" | cut -f1)
        echo "   ✓ Downloaded ($size)"
        return 0
    else
        echo "   ⚠️  Failed to download"
        return 1
    fi
}

# Function to download and convert HTML to Markdown
download_html() {
    local url="$1"
    local output_file="$2"
    local title="$3"

    echo "📥 Downloading: $title"

    if wget -q --timeout=30 --tries=3 "$url" -O "$TEMP_DIR/temp.html" 2>/dev/null; then
        if command -v pandoc >/dev/null 2>&1; then
            if pandoc "$TEMP_DIR/temp.html" \
                --from=html \
                --to=gfm \
                --wrap=none \
                -o "$output_file" 2>/dev/null; then

                # Add metadata header
                temp_file="${output_file}.tmp"
                {
                    echo "# $title"
                    echo ""
                    echo "**Source**: $url"
                    echo "**Downloaded**: $(date '+%Y-%m-%d')"
                    echo ""
                    echo "---"
                    echo ""
                    cat "$output_file"
                } > "$temp_file"
                mv "$temp_file" "$output_file"

                size=$(wc -c < "$output_file")
                echo "   ✓ Converted ($size bytes)"
                return 0
            fi
        else
            # Fallback if pandoc not installed
            cp "$TEMP_DIR/temp.html" "$output_file"
            echo "   ⚠️  pandoc not found, saved as HTML"
            return 0
        fi
    fi

    echo "   ⚠️  Failed to download/convert"
    return 1
}

# Function to clone GitHub repos (shallow)
clone_repo() {
    local url="$1"
    local dest_dir="$2"
    local title="$3"

    echo "📦 Cloning: $title"

    if git clone --depth 1 -q "$url" "$dest_dir" 2>/dev/null; then
        # Remove .git directory to save space
        rm -rf "$dest_dir/.git"
        size=$(du -sh "$dest_dir" | cut -f1)
        echo "   ✓ Cloned ($size)"
        return 0
    else
        echo "   ⚠️  Failed to clone"
        return 1
    fi
}

# =============================================================================
# 1. NVIDIA DOCUMENTATION
# =============================================================================

echo ""
echo "=== NVIDIA HPC Documentation ==="
echo ""

# NCCL Documentation
download_pdf \
    "https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2212/pdf/NCCL-Developer-Guide.pdf" \
    "$BASE_DIR/nvidia/nccl-developer-guide-v2.22.12.pdf" \
    "NCCL Developer Guide v2.22.12"

download_pdf \
    "https://docs.nvidia.com/deeplearning/nccl/archives/nccl_212/nccl-developer-guide.pdf" \
    "$BASE_DIR/nvidia/nccl-api-reference-v2.12.pdf" \
    "NCCL API Reference v2.12"

# CUDA Programming Guides
download_pdf \
    "https://docs.nvidia.com/cuda/pdf/CUDA_C_Programming_Guide.pdf" \
    "$BASE_DIR/nvidia/cuda-c-programming-guide.pdf" \
    "CUDA C Programming Guide (Latest)"

download_pdf \
    "https://docs.nvidia.com/cuda/pdf/CUDA_C_Best_Practices_Guide.pdf" \
    "$BASE_DIR/nvidia/cuda-best-practices-guide.pdf" \
    "CUDA Best Practices Guide (Latest)"

download_pdf \
    "https://docs.nvidia.com/cuda/pdf/CUDA_Runtime_API.pdf" \
    "$BASE_DIR/nvidia/cuda-runtime-api.pdf" \
    "CUDA Runtime API Reference"

# NVIDIA Networking & GPUDirect
download_pdf \
    "https://docs.nvidia.com/cuda/pdf/GPUDirect_RDMA.pdf" \
    "$BASE_DIR/nvidia/gpudirect-rdma.pdf" \
    "GPUDirect RDMA Guide"

download_pdf \
    "https://www.nvidia.com/content/PDF/nvswitch-technical-overview.pdf" \
    "$BASE_DIR/nvidia/nvswitch-technical-overview.pdf" \
    "NVSwitch Technical Overview"

# NVIDIA HPC SDK
download_pdf \
    "https://docs.nvidia.com/hpc-sdk/archive/24.1/pdf/hpc-sdk-release-notes.pdf" \
    "$BASE_DIR/nvidia/hpc-sdk-release-notes-v24.1.pdf" \
    "HPC SDK Release Notes v24.1"

# GPU Architecture
download_pdf \
    "https://resources.nvidia.com/en-us-grace-cpu/nvidia-grace-hopper" \
    "$BASE_DIR/nvidia/grace-hopper-superchip-whitepaper.pdf" \
    "Grace Hopper Superchip Whitepaper" || true

# Math Libraries
download_pdf \
    "https://docs.nvidia.com/cuda/pdf/CUBLAS_Library.pdf" \
    "$BASE_DIR/nvidia/cublas-library.pdf" \
    "cuBLAS Library Documentation"

download_pdf \
    "https://docs.nvidia.com/cuda/pdf/CUSPARSE_Library.pdf" \
    "$BASE_DIR/nvidia/cusparse-library.pdf" \
    "cuSPARSE Library Documentation"

# =============================================================================
# 2. AMD ROCM DOCUMENTATION
# =============================================================================

echo ""
echo "=== AMD ROCm Documentation ==="
echo ""

# ROCm Installation
download_pdf \
    "https://rocm.docs.amd.com/_/downloads/install-on-linux/en/latest/pdf/" \
    "$BASE_DIR/amd/rocm-installation-linux-latest.pdf" \
    "ROCm Installation on Linux (Latest)"

# RCCL Documentation
download_pdf \
    "https://rocm.docs.amd.com/_/downloads/rccl/en/latest/pdf/" \
    "$BASE_DIR/amd/rccl-documentation-latest.pdf" \
    "RCCL Documentation (Latest)"

download_pdf \
    "https://rocm.docs.amd.com/_/downloads/rccl/en/develop/pdf/" \
    "$BASE_DIR/amd/rccl-documentation-develop.pdf" \
    "RCCL Documentation (Develop)"

# HIP Documentation
download_pdf \
    "https://rocm.docs.amd.com/_/downloads/HIP/en/docs-6.1.2/pdf/" \
    "$BASE_DIR/amd/hip-documentation-v6.1.2.pdf" \
    "HIP Documentation v6.1.2"

download_pdf \
    "https://rocm.docs.amd.com/_/downloads/HIPCC/en/latest/pdf/" \
    "$BASE_DIR/amd/hipcc-documentation-latest.pdf" \
    "HIPCC Documentation (Latest)"

download_pdf \
    "https://rocm.docs.amd.com/_/downloads/HIPIFY/en/latest/pdf/" \
    "$BASE_DIR/amd/hipify-documentation-latest.pdf" \
    "HIPIFY Documentation (CUDA to HIP)"

download_pdf \
    "https://www.amd.com/system/files/documents/porting-cuda-to-hip.pdf" \
    "$BASE_DIR/amd/porting-cuda-to-hip-guide.pdf" \
    "Official AMD CUDA to HIP Porting Guide"

# AMD Instinct GPUs
download_pdf \
    "https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/instruction-set-architectures/amd-instinct-mi300-cdna3-instruction-set-architecture.pdf" \
    "$BASE_DIR/amd/mi300-cdna3-isa.pdf" \
    "MI300 CDNA3 Instruction Set Architecture"

download_pdf \
    "https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/instruction-set-architectures/instinct-mi200-cdna2-instruction-set-architecture.pdf" \
    "$BASE_DIR/amd/mi200-cdna2-isa.pdf" \
    "MI200 CDNA2 Instruction Set Architecture"

download_pdf \
    "https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf" \
    "$BASE_DIR/amd/cdna3-architecture-whitepaper.pdf" \
    "AMD CDNA 3 Architecture Whitepaper"

download_pdf \
    "https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna2-white-paper.pdf" \
    "$BASE_DIR/amd/cdna2-architecture-whitepaper.pdf" \
    "AMD CDNA 2 Architecture Whitepaper"

download_pdf \
    "https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf" \
    "$BASE_DIR/amd/mi300x-datasheet.pdf" \
    "MI300X Accelerator Datasheet"

download_pdf \
    "https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/other/instinct-mi300-series-cluster-reference-guide.pdf" \
    "$BASE_DIR/amd/mi300-cluster-reference-guide.pdf" \
    "MI300 Series Cluster Reference Architecture"

# ROCm Math Libraries
download_pdf \
    "https://rocm.docs.amd.com/_/downloads/rocBLAS/en/latest/pdf/" \
    "$BASE_DIR/amd/rocblas-documentation-latest.pdf" \
    "rocBLAS Documentation (Latest)"

download_pdf \
    "https://rocm.docs.amd.com/_/downloads/rocFFT/en/develop/pdf/" \
    "$BASE_DIR/amd/rocfft-documentation-develop.pdf" \
    "rocFFT Documentation (Develop)"

# Profiling Tools
download_pdf \
    "https://rocm.docs.amd.com/_/downloads/rocprofiler/en/amd-master/pdf/" \
    "$BASE_DIR/amd/rocprofiler-documentation-latest.pdf" \
    "ROCProfiler Documentation (Latest)"

download_pdf \
    "https://rocm.docs.amd.com/_/downloads/roctracer/en/latest/pdf/" \
    "$BASE_DIR/amd/roctracer-documentation-latest.pdf" \
    "ROCTracer Documentation (Latest)"

# =============================================================================
# 3. HPC BENCHMARKING TOOLS (GitHub Repos)
# =============================================================================

echo ""
echo "=== HPC Benchmarking GitHub Repositories ==="
echo ""

# STREAM Memory Bandwidth
clone_repo \
    "https://github.com/jeffhammond/STREAM.git" \
    "$BASE_DIR/github-repos/STREAM" \
    "STREAM Memory Bandwidth Benchmark"

# HPL (High-Performance Linpack)
clone_repo \
    "https://github.com/davidrohr/hpl-gpu.git" \
    "$BASE_DIR/github-repos/hpl-gpu" \
    "HPL GPU-Accelerated Version"

# HPCG
clone_repo \
    "https://github.com/hpcg-benchmark/hpcg.git" \
    "$BASE_DIR/github-repos/hpcg" \
    "HPCG Benchmark Official Repo"

clone_repo \
    "https://github.com/NVIDIA/nvidia-hpcg.git" \
    "$BASE_DIR/github-repos/nvidia-hpcg" \
    "NVIDIA Optimized HPCG"

# OSU Micro-Benchmarks
clone_repo \
    "https://github.com/forresti/osu-micro-benchmarks.git" \
    "$BASE_DIR/github-repos/osu-micro-benchmarks" \
    "OSU MPI Micro-Benchmarks"

# IOR Parallel I/O
clone_repo \
    "https://github.com/hpc/ior.git" \
    "$BASE_DIR/github-repos/ior" \
    "IOR Parallel I/O Benchmark"

# NVIDIA NCCL Tests
clone_repo \
    "https://github.com/NVIDIA/nccl-tests.git" \
    "$BASE_DIR/github-repos/nccl-tests" \
    "NVIDIA NCCL Tests"

# NVIDIA nvbandwidth
clone_repo \
    "https://github.com/NVIDIA/nvbandwidth.git" \
    "$BASE_DIR/github-repos/nvbandwidth" \
    "NVIDIA nvbandwidth Tool"

# Intel MPI Benchmarks
clone_repo \
    "https://github.com/intel/mpi-benchmarks.git" \
    "$BASE_DIR/github-repos/intel-mpi-benchmarks" \
    "Intel MPI Benchmarks"

# RDMA Performance Tests
clone_repo \
    "https://github.com/linux-rdma/perftest.git" \
    "$BASE_DIR/github-repos/perftest" \
    "InfiniBand/RDMA Performance Tests"

# UCX Communication Framework
clone_repo \
    "https://github.com/openucx/ucx.git" \
    "$BASE_DIR/github-repos/ucx" \
    "UCX Communication Framework"

# =============================================================================
# 4. LLM BENCHMARKING TOOLS
# =============================================================================

echo ""
echo "=== LLM Benchmarking Repositories ==="
echo ""

# llm.c (Andrej Karpathy)
clone_repo \
    "https://github.com/karpathy/llm.c.git" \
    "$BASE_DIR/github-repos/llm.c" \
    "llm.c - Minimal LLM Training in C/CUDA"

# nanoGPT
clone_repo \
    "https://github.com/karpathy/nanoGPT.git" \
    "$BASE_DIR/github-repos/nanoGPT" \
    "nanoGPT - Simplest GPT Training Repo"

# Megatron-LM (NVIDIA)
clone_repo \
    "https://github.com/NVIDIA/Megatron-LM.git" \
    "$BASE_DIR/github-repos/Megatron-LM" \
    "NVIDIA Megatron-LM Large-Scale Training"

# DeepSpeed
clone_repo \
    "https://github.com/microsoft/DeepSpeed.git" \
    "$BASE_DIR/github-repos/DeepSpeed" \
    "Microsoft DeepSpeed Optimization Library"

# DeepSpeed Examples
clone_repo \
    "https://github.com/microsoft/DeepSpeedExamples.git" \
    "$BASE_DIR/github-repos/DeepSpeedExamples" \
    "DeepSpeed Examples and Benchmarks"

# vLLM
clone_repo \
    "https://github.com/vllm-project/vllm.git" \
    "$BASE_DIR/github-repos/vllm" \
    "vLLM - High-Throughput LLM Inference"

# TensorRT-LLM
clone_repo \
    "https://github.com/NVIDIA/TensorRT-LLM.git" \
    "$BASE_DIR/github-repos/TensorRT-LLM" \
    "NVIDIA TensorRT-LLM Inference SDK"

# Flash Attention
clone_repo \
    "https://github.com/Dao-AILab/flash-attention.git" \
    "$BASE_DIR/github-repos/flash-attention" \
    "Flash Attention - Fast & Memory-Efficient Attention"

# AutoGPTQ Quantization
clone_repo \
    "https://github.com/AutoGPTQ/AutoGPTQ.git" \
    "$BASE_DIR/github-repos/AutoGPTQ" \
    "AutoGPTQ - 4-bit Quantization"

# AWQ Quantization
clone_repo \
    "https://github.com/mit-han-lab/llm-awq.git" \
    "$BASE_DIR/github-repos/llm-awq" \
    "AWQ - Activation-aware Weight Quantization"

# LM Evaluation Harness
clone_repo \
    "https://github.com/EleutherAI/lm-evaluation-harness.git" \
    "$BASE_DIR/github-repos/lm-evaluation-harness" \
    "EleutherAI LM Evaluation Harness"

# Hugging Face Optimum Benchmark
clone_repo \
    "https://github.com/huggingface/optimum-benchmark.git" \
    "$BASE_DIR/github-repos/optimum-benchmark" \
    "Hugging Face Optimum Benchmark"

# =============================================================================
# 5. CLUSTER CONFIGURATION EXAMPLES
# =============================================================================

echo ""
echo "=== Cluster Configuration Repositories ==="
echo ""

# Ansible for HPC
clone_repo \
    "https://github.com/stackhpc/ansible-slurm-appliance.git" \
    "$BASE_DIR/github-repos/ansible-slurm-appliance" \
    "Ansible Slurm Appliance"

# Slurm Examples
clone_repo \
    "https://github.com/ubccr/ccr-examples.git" \
    "$BASE_DIR/github-repos/slurm-examples" \
    "Slurm Best Practice Examples"

# OpenMPI Examples
clone_repo \
    "https://github.com/open-mpi/ompi.git" \
    "$BASE_DIR/github-repos/openmpi" \
    "OpenMPI Source Repository"

# AMD HPC Training Examples
clone_repo \
    "https://github.com/amd/HPCTrainingExamples.git" \
    "$BASE_DIR/github-repos/AMD-HPC-Training" \
    "AMD HPC Training Examples"

# AMD Lab Notes
clone_repo \
    "https://github.com/amd/amd-lab-notes.git" \
    "$BASE_DIR/github-repos/AMD-Lab-Notes" \
    "AMD GPU Programming Lab Notes"

# NVIDIA Multi-GPU Examples
clone_repo \
    "https://github.com/NVIDIA/multi-gpu-programming-models.git" \
    "$BASE_DIR/github-repos/nvidia-multi-gpu-examples" \
    "NVIDIA Multi-GPU Programming Models"

# NVIDIA CUDA Samples
clone_repo \
    "https://github.com/NVIDIA/cuda-samples.git" \
    "$BASE_DIR/github-repos/cuda-samples" \
    "NVIDIA CUDA Samples"

# =============================================================================
# 6. COMMUNITY RESOURCES & GUIDES
# =============================================================================

echo ""
echo "=== Community Resources ==="
echo ""

# Download key community guides
download_pdf \
    "https://prace-ri.eu/wp-content/uploads/Best-Practice-Guide_AMD.pdf" \
    "$BASE_DIR/community/best-practice-guide-amd-epyc.pdf" \
    "Best Practice Guide - AMD EPYC"

download_pdf \
    "https://www.olcf.ornl.gov/wp-content/uploads/2019/09/AMD_GPU_HIP_training_20190906.pdf" \
    "$BASE_DIR/community/ornl-amd-gpu-hip-training.pdf" \
    "ORNL AMD GPU HIP Training"

download_pdf \
    "https://www.olcf.ornl.gov/wp-content/uploads/2021/04/SPOCK_Libraries_profiling_JMaia.pdf" \
    "$BASE_DIR/community/ornl-rocm-libraries-profiling.pdf" \
    "ORNL ROCm Libraries & Profiling"

# HPC Networking
download_pdf \
    "https://www.hpcadvisorycouncil.com/events/2012/Switzerland-Workshop/Presentations/Day_3/7_Simula.pdf" \
    "$BASE_DIR/community/hpc-network-topologies-fat-tree-dragonfly.pdf" \
    "HPC Network Topologies: Fat-tree & Dragonfly"

download_html \
    "https://www.admin-magazine.com/HPC/Articles/Useful-NFS-Options-for-Tuning-and-Management" \
    "$BASE_DIR/community/nfs-tuning-for-hpc.md" \
    "NFS Tuning for HPC"

download_html \
    "https://www.open-mpi.org/faq/?category=tuning" \
    "$BASE_DIR/community/openmpi-tuning-faq.md" \
    "OpenMPI Tuning FAQ"

# MLPerf Training Results
download_html \
    "https://mlcommons.org/benchmarks/training/" \
    "$BASE_DIR/community/mlperf-training-benchmarks.md" \
    "MLPerf Training Benchmarks"

# Slurm Configuration Guide
download_html \
    "https://slurm.schedmd.com/quickstart_admin.html" \
    "$BASE_DIR/community/slurm-quickstart-admin.md" \
    "Slurm Quick Start Administrator Guide"

# Create comprehensive README
cat > "$BASE_DIR/hpc-docs-README.md" << 'EOFREADME'
# HPC Documentation Collection

This directory contains comprehensive documentation for HPC computing, downloaded from official sources.

## Directory Structure

```
docs/
├── nvidia/              # NVIDIA CUDA, NCCL, HPC SDK documentation
├── amd/                 # AMD ROCm, RCCL, HIP, Instinct GPU docs
├── github-repos/        # Cloned repositories for benchmarking tools
├── community/           # Community guides and best practices
├── benchmarking/        # HPC benchmarking tools and results
└── llm-benchmarking/    # LLM training and inference benchmarks
```

## Contents Summary

### NVIDIA Documentation (~20 PDFs)
- NCCL Developer Guide & API Reference
- CUDA Programming Guide & Best Practices
- GPUDirect RDMA Documentation
- HPC SDK Release Notes
- cuBLAS, cuSPARSE Library Documentation
- NVSwitch Technical Overview
- Grace Hopper Architecture

### AMD Documentation (~20 PDFs)
- ROCm Installation & Programming Guides
- RCCL Documentation (multiple versions)
- HIP Programming & CUDA Porting Guides
- MI300/MI200 ISA & Architecture Whitepapers
- CDNA 2/3 Architecture Documentation
- rocBLAS, rocFFT Library Documentation
- ROCProfiler & ROCTracer Guides

### GitHub Repositories (~30 repos)
**HPC Benchmarking:**
- STREAM, HPL, HPCG, OSU Micro-Benchmarks, IOR
- NCCL Tests, nvbandwidth, Intel MPI Benchmarks
- RDMA perftest, UCX

**LLM Benchmarking:**
- llm.c, nanoGPT, Megatron-LM
- DeepSpeed, vLLM, TensorRT-LLM
- Flash Attention, AutoGPTQ, AWQ
- LM Evaluation Harness

**Configuration Examples:**
- Ansible Slurm, OpenMPI, CUDA Samples
- AMD HPC Training, Multi-GPU Examples

### Community Resources (~10 guides)
- Best Practice Guides (AMD EPYC, HPC)
- Network Topology Guides (Fat-tree, Dragonfly)
- OpenMPI & Slurm Tuning
- NFS Performance Optimization
- MLPerf Training Benchmarks

## Usage

### For Knowledge Base Ingestion
Upload the entire `docs/` directory to your S3 bucket and trigger ingestion:

```bash
aws s3 sync docs/ s3://your-bucket/ --profile your-profile
```

### For Direct Reference
PDFs and markdown files can be read directly for research and development.

### Repository Structure
GitHub repos include:
- README.md with setup instructions
- Example configuration files
- Benchmark scripts
- Performance tuning guides

## Download Source
Generated by: `scripts/download-hpc-docs.sh`
Download date: $(date '+%Y-%m-%d')

## Key Topics Covered
- GPU Programming (CUDA, HIP, ROCm)
- Collective Communications (NCCL, RCCL)
- HPC Benchmarking (Memory, I/O, MPI)
- LLM Training & Inference Optimization
- Cluster Configuration (Slurm, OpenMPI, UCX)
- Network Optimization (InfiniBand, RoCE, EFA)
- Parallel Filesystems (Lustre, BeeGFS, NFS)
EOFREADME

echo ""
echo "=============================================================="
echo "📊 Download Summary"
echo "=============================================================="

# Count files by category
nvidia_count=$(find "$BASE_DIR/nvidia" -type f 2>/dev/null | wc -l)
amd_count=$(find "$BASE_DIR/amd" -type f 2>/dev/null | wc -l)
repos_count=$(find "$BASE_DIR/github-repos" -maxdepth 1 -type d 2>/dev/null | wc -l)
repos_count=$((repos_count - 1))  # Subtract parent directory
community_count=$(find "$BASE_DIR/community" -type f 2>/dev/null | wc -l)

echo ""
echo "📁 NVIDIA Documentation: $nvidia_count files"
find "$BASE_DIR/nvidia" -type f -name "*.pdf" 2>/dev/null | while read -r file; do
    filename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    echo "   • $filename ($size)"
done

echo ""
echo "📁 AMD Documentation: $amd_count files"
find "$BASE_DIR/amd" -type f -name "*.pdf" 2>/dev/null | while read -r file; do
    filename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    echo "   • $filename ($size)"
done

echo ""
echo "📦 GitHub Repositories: $repos_count repos"
find "$BASE_DIR/github-repos" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | while read -r dir; do
    dirname=$(basename "$dir")
    size=$(du -sh "$dir" | cut -f1)
    echo "   • $dirname ($size)"
done

echo ""
echo "📚 Community Resources: $community_count files"
find "$BASE_DIR/community" -type f 2>/dev/null | while read -r file; do
    filename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    echo "   • $filename ($size)"
done

total_size=$(du -sh "$BASE_DIR" | cut -f1)

echo ""
echo "=============================================================="
echo "✓ Total size: $total_size"
echo "✓ Location: $BASE_DIR/"
echo "✓ README: $BASE_DIR/hpc-docs-README.md"
echo ""

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Download complete!"
echo ""
echo "Next steps:"
echo "1. Review downloaded documentation in $BASE_DIR/"
echo "2. Upload to S3: bash scripts/deploy-docs.sh"
echo "3. Trigger ingestion: bash scripts/sync-kb.sh"
