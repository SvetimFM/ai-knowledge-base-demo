# HPC Cluster Networking and Topology

## Introduction

High-Performance Computing (HPC) cluster networking is critical for achieving scalable performance in distributed applications. The network fabric interconnecting compute nodes, GPUs, and storage systems can become the primary bottleneck in large-scale parallel computing. This guide covers the major networking technologies, topologies, and optimization strategies used in modern HPC systems.

## InfiniBand Architecture and Features

### Overview

InfiniBand (IB) is the dominant high-performance interconnect technology in HPC clusters, designed specifically for low-latency, high-bandwidth communication between compute nodes.

### Key Features

**1. RDMA (Remote Direct Memory Access)**:
- Direct memory-to-memory transfers without CPU involvement
- Bypasses operating system kernel
- Sub-microsecond latency
- Zero-copy data transfer

**2. Hardware-Based Transport**:
- Protocol implemented in hardware (HCA - Host Channel Adapter)
- Offloads network processing from CPU
- Reliable and unreliable transport modes
- Hardware-based congestion control

**3. Low Latency**:
- Point-to-point latency: < 1 microsecond
- MPI latency: 1-2 microseconds
- Deterministic performance

**4. High Bandwidth**:
- HDR (High Data Rate): 200 Gb/s per port
- NDR (Next Data Rate): 400 Gb/s per port
- XDR (eXtreme Data Rate): 800 Gb/s per port (emerging)
- Aggregated bandwidth with multiple ports

### InfiniBand Generations

| Generation | Speed per Lane | Year | Typical Use |
|------------|---------------|------|-------------|
| SDR | 2.5 Gb/s | 2001 | Legacy |
| DDR | 5 Gb/s | 2005 | Legacy |
| QDR | 10 Gb/s | 2007 | Older clusters |
| FDR | 14 Gb/s | 2011 | Mid-range |
| EDR | 25 Gb/s | 2014 | Common |
| HDR | 50 Gb/s | 2017 | Modern |
| NDR | 100 Gb/s | 2020 | High-end |
| XDR | 200 Gb/s | 2024+ | Future |

**Typical Configurations**:
- 1x: Single lane (rare)
- 4x: Four lanes (most common)
- 12x: Twelve lanes (high-end switches)

Example: HDR200 = 200 Gb/s = 4 lanes × 50 Gb/s

### InfiniBand Architecture Layers

```
┌─────────────────────────────────────┐
│     Application Layer                │
├─────────────────────────────────────┤
│     Upper Layer Protocol             │
│     (MPI, NCCL, Storage)            │
├─────────────────────────────────────┤
│     InfiniBand Verbs API            │
├─────────────────────────────────────┤
│     Transport Layer                  │
│     (RC, UC, UD, RD)                │
├─────────────────────────────────────┤
│     Network Layer                    │
│     (Routing, Forwarding)           │
├─────────────────────────────────────┤
│     Link Layer                       │
│     (Flow Control, Packet)          │
├─────────────────────────────────────┤
│     Physical Layer                   │
│     (Optical/Copper cables)         │
└─────────────────────────────────────┘
```

### Transport Modes

**1. Reliable Connection (RC)**:
- Connection-oriented
- Reliable, ordered delivery
- Most common for HPC
- Used by MPI

**2. Unreliable Connection (UC)**:
- Connection-oriented
- No reliability guarantees
- Lower overhead
- Streaming applications

**3. Unreliable Datagram (UD)**:
- Connectionless
- Multicast support
- Scalable for many endpoints
- Management traffic

**4. Reliable Datagram (RD)**:
- Connectionless with reliability
- Less common
- Specific use cases

### InfiniBand Verbs API

Basic operations example:

```c
#include <infiniband/verbs.h>

// Open device
struct ibv_context *context;
struct ibv_device **dev_list = ibv_get_device_list(NULL);
context = ibv_open_device(dev_list[0]);

// Create protection domain
struct ibv_pd *pd = ibv_alloc_pd(context);

// Register memory region
void *buffer = malloc(BUFFER_SIZE);
struct ibv_mr *mr = ibv_reg_mr(pd, buffer, BUFFER_SIZE,
                                IBV_ACCESS_LOCAL_WRITE |
                                IBV_ACCESS_REMOTE_WRITE |
                                IBV_ACCESS_REMOTE_READ);

// Create completion queue
struct ibv_cq *cq = ibv_create_cq(context, CQ_SIZE, NULL, NULL, 0);

// Create queue pair
struct ibv_qp_init_attr qp_init_attr = {
    .send_cq = cq,
    .recv_cq = cq,
    .qp_type = IBV_QPT_RC,
    .cap = {
        .max_send_wr = 10,
        .max_recv_wr = 10,
        .max_send_sge = 1,
        .max_recv_sge = 1
    }
};
struct ibv_qp *qp = ibv_create_qp(pd, &qp_init_attr);

// Post RDMA write
struct ibv_sge sge = {
    .addr = (uint64_t)buffer,
    .length = BUFFER_SIZE,
    .lkey = mr->lkey
};

struct ibv_send_wr wr = {
    .wr_id = 0,
    .sg_list = &sge,
    .num_sge = 1,
    .opcode = IBV_WR_RDMA_WRITE,
    .send_flags = IBV_SEND_SIGNALED,
    .wr.rdma = {
        .remote_addr = remote_addr,
        .rkey = remote_key
    }
};

struct ibv_send_wr *bad_wr;
ibv_post_send(qp, &wr, &bad_wr);

// Poll completion
struct ibv_wc wc;
while (ibv_poll_cq(cq, 1, &wc) == 0);

// Cleanup
ibv_destroy_qp(qp);
ibv_destroy_cq(cq);
ibv_dereg_mr(mr);
ibv_dealloc_pd(pd);
ibv_close_device(context);
free(buffer);
```

### GPUDirect RDMA with InfiniBand

GPUDirect RDMA enables direct data transfer between GPU memory and InfiniBand HCA:

```
Traditional Path:
GPU Memory → CPU Memory → Network Adapter

GPUDirect RDMA Path:
GPU Memory → Network Adapter (direct)
```

**Benefits**:
- Reduced latency (eliminates CPU copies)
- Lower CPU utilization
- Higher effective bandwidth
- Essential for multi-node GPU communication

**Configuration**:
```bash
# Load nvidia-peermem module
modprobe nvidia-peermem

# Verify GPUDirect support
nvidia-smi topo -m

# Check NCCL configuration
export NCCL_IB_DISABLE=0
export NCCL_NET_GDR_LEVEL=3  # Enable GPUDirect RDMA
export NCCL_NET_GDR_READ=1   # Enable GPUDirect read
```

**Verification**:
```bash
# Test GPUDirect RDMA performance
ib_write_bw -d mlx5_0 -a -F --report_gbits \
    -q 1 --use_cuda=0 <remote_host>
```

## AWS Elastic Fabric Adapter (EFA)

### Overview

Elastic Fabric Adapter (EFA) is Amazon's custom network interface designed for HPC and ML workloads on AWS EC2 instances. It provides RDMA-like performance in the cloud.

### Key Features

**1. Low Latency**:
- Sub-10 microsecond inter-instance latency
- OS-bypass capabilities
- Hardware-based transport

**2. Scalability**:
- Designed for thousands of instances
- No physical switches to manage
- Elastic bandwidth scaling

**3. MPI Support**:
- Compatible with major MPI implementations
- Intel MPI, Open MPI, MVAPICH
- Transparent to applications

**4. libfabric Integration**:
- Uses libfabric API
- OFI (OpenFabrics Interfaces) compatible
- Portable across fabrics

### EFA vs Traditional InfiniBand

| Feature | InfiniBand | EFA |
|---------|-----------|-----|
| Environment | On-premises | AWS Cloud |
| Management | Physical infrastructure | Fully managed |
| Latency | <1 μs | ~5-10 μs |
| Bandwidth | Up to 800 Gb/s | Up to 400 Gb/s |
| Scalability | Limited by switches | Virtually unlimited |
| GPUDirect | Full support | GPUDirect RDMA support |
| Cost model | CapEx | OpEx (pay-per-use) |

### EFA-Enabled Instance Types

**Compute Optimized**:
- C5n.18xlarge: 100 Gbps EFA
- C6i instances with EFA support

**General Purpose**:
- M5n instances: Up to 100 Gbps
- M6i instances: EFA support

**GPU Instances**:
- P4d.24xlarge: 4x 100 Gbps EFA (400 Gbps aggregate)
- P3dn.24xlarge: 100 Gbps EFA
- P5.48xlarge: 3200 Gbps network bandwidth

**HPC Optimized**:
- Hpc6a: AMD EPYC with EFA
- Hpc7a: Latest AMD with EFA

### Setting Up EFA

**1. Security Group Configuration**:
```bash
# Create security group allowing all traffic within group
aws ec2 create-security-group \
    --group-name efa-sg \
    --description "Security group for EFA"

# Allow all traffic from same security group
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol all \
    --source-group sg-xxxxx
```

**2. Install EFA Driver**:
```bash
# Download and install EFA installer
curl -O https://efa-installer.amazonaws.com/aws-efa-installer-latest.tar.gz
tar -xf aws-efa-installer-latest.tar.gz
cd aws-efa-installer
sudo ./efa_installer.sh -y

# Verify installation
fi_info -p efa
```

**3. MPI Configuration**:
```bash
# Open MPI with EFA
mpirun --map-by ppr:8:node \
    --mca btl ^openib,tcp \
    --mca pml ^cm \
    --mca mtl ofi \
    --mca mtl_ofi_provider_include efa \
    ./mpi_application
```

**4. NCCL with EFA**:
```bash
# Install AWS OFI NCCL plugin
git clone https://github.com/aws/aws-ofi-nccl.git
cd aws-ofi-nccl
./autogen.sh
./configure --with-libfabric=/opt/amazon/efa
make && sudo make install

# Run with NCCL
export LD_LIBRARY_PATH=/opt/amazon/efa/lib:$LD_LIBRARY_PATH
export FI_PROVIDER=efa
export NCCL_DEBUG=INFO

mpirun -np 16 --hostfile hosts \
    --mca pml ^cm --mca btl tcp,self \
    --mca btl_tcp_if_exclude lo,docker0 \
    ./nccl_test
```

### EFA Performance Optimization

**1. Instance Placement**:
```bash
# Use placement groups for lower latency
aws ec2 create-placement-group \
    --group-name hpc-cluster \
    --strategy cluster

# Launch instances in placement group
aws ec2 run-instances \
    --placement GroupName=hpc-cluster \
    --instance-type p4d.24xlarge \
    ...
```

**2. Network Interface Tuning**:
```bash
# Increase socket buffer sizes
sudo sysctl -w net.core.rmem_max=268435456
sudo sysctl -w net.core.wmem_max=268435456

# Optimize for low latency
sudo ethtool -C ens5 rx-usecs 0
sudo ethtool -C ens5 tx-usecs 0
```

**3. Process Binding**:
```bash
# Bind processes to NUMA nodes
numactl --cpunodebind=0 --membind=0 ./application
```

## Network Topologies

### Fat-Tree Topology

**Structure**:
```
         ┌──────────────────┐
         │  Core Switches   │  Layer 3
         └────┬──────┬──────┘
              │      │
      ┌───────┴──┬───┴───────┐
      │          │            │
   ┌──┴──┐   ┌──┴──┐    ┌───┴─┐
   │Aggr1│   │Aggr2│    │Aggr3│  Layer 2
   └──┬──┘   └──┬──┘    └──┬──┘
      │         │           │
   ┌──┴──┐   ┌─┴───┐    ┌──┴──┐
   │ToR1 │   │ToR2 │    │ToR3 │  Layer 1
   └──┬──┘   └──┬──┘    └──┬──┘
      │         │           │
    Nodes     Nodes       Nodes
```

**Characteristics**:
- Full bisection bandwidth
- Non-blocking for upward traffic
- Scalable to thousands of nodes
- Cost-effective

**Pros**:
- Excellent for all-to-all communication
- Predictable performance
- Most common in HPC

**Cons**:
- Cable complexity increases with scale
- Requires careful design
- Cost increases with bisection bandwidth

### Dragonfly Topology

**Structure**:
- High-radix routers
- Groups of routers fully connected internally
- All-to-all inter-group connections
- Reduced diameter

```
Group 1           Group 2           Group 3
┌─────────┐      ┌─────────┐      ┌─────────┐
│ R1──R2  │──────│ R5──R6  │──────│ R9──R10 │
│  │\ /│  │      │  │\ /│  │      │  │\ /│  │
│  │ X │  │      │  │ X │  │      │  │ X │  │
│ R3──R4  │──────│ R7──R8  │──────│ R11─R12 │
└─────────┘      └─────────┘      └─────────┘
     │                │                │
   Nodes            Nodes            Nodes
```

**Characteristics**:
- Minimal diameter (2 hops typical)
- Cost-effective at large scale
- Excellent for random traffic
- Load balancing critical

**Pros**:
- Lower cost than fat-tree at scale
- Good performance for many patterns
- Used in large supercomputers

**Cons**:
- Performance depends on load balancing
- Adversarial traffic patterns possible
- Complex routing algorithms

### Torus Topology

**2D Torus**:
```
n0──n1──n2──n3──n0
│   │   │   │   │
n4──n5──n6──n7──n4
│   │   │   │   │
n8──n9──n10─n11─n8
│   │   │   │   │
n0──n1──n2──n3──n0
```

**3D Torus**: Extension to three dimensions

**Characteristics**:
- Direct connections to neighbors
- Wrap-around connections
- Regular, symmetric structure
- Bounded degree

**Pros**:
- Excellent for nearest-neighbor communication
- Predictable performance
- Simple routing
- Good for stencil computations

**Cons**:
- Poor for all-to-all patterns
- Diameter increases with size
- Bisection bandwidth limitations

**Use Cases**:
- Molecular dynamics
- Climate modeling
- Structured grid applications
- Any application with spatial locality

## RDMA and GPUDirect

### RDMA Fundamentals

**Traditional Network Communication**:
```
Application → System Call → Kernel → Network Stack → NIC
(Multiple context switches, CPU overhead, memory copies)
```

**RDMA Communication**:
```
Application → User-space library → NIC
(Zero-copy, kernel bypass, low latency)
```

### RDMA Operations

**1. RDMA Write**:
```c
// Write local buffer to remote memory
ibv_post_send(qp, &write_wr, &bad_wr);
// Remote side doesn't need to be notified
```

**2. RDMA Read**:
```c
// Read remote memory into local buffer
ibv_post_send(qp, &read_wr, &bad_wr);
// Fetches data without remote CPU involvement
```

**3. RDMA Send/Receive**:
```c
// Traditional two-sided operation
// Receiver must post receive buffer
ibv_post_recv(qp, &recv_wr, &bad_wr);
// Sender sends data
ibv_post_send(qp, &send_wr, &bad_wr);
```

**4. RDMA Atomic**:
```c
// Atomic operations on remote memory
// Compare-and-swap, fetch-and-add
ibv_post_send(qp, &atomic_wr, &bad_wr);
```

### GPUDirect Technologies

**GPUDirect Peer-to-Peer (P2P)**:
- Direct GPU-to-GPU transfers within same PCIe root complex
- No CPU or system memory involvement
- Bandwidth limited by PCIe

**GPUDirect RDMA**:
- Direct transfer between GPU memory and network adapter
- Eliminates CPU copies
- Requires compatible NIC and driver support

**GPUDirect Storage**:
- Direct path between GPU and storage
- Useful for data-intensive workflows
- Reduces CPU bottlenecks

### Enabling GPUDirect RDMA

**Prerequisites**:
- CUDA-aware MPI or NCCL
- Compatible InfiniBand/RoCE adapter
- nvidia-peermem kernel module

**Configuration**:
```bash
# Check GPU topology
nvidia-smi topo -m

# Load peermem module
sudo modprobe nvidia-peermem

# Verify GPUDirect capability
cat /sys/kernel/mm/memory_peers/nv_mem/version

# NCCL configuration
export NCCL_IB_DISABLE=0
export NCCL_NET_GDR_LEVEL=3
export NCCL_NET_GDR_READ=1
export NCCL_IB_GID_INDEX=3  # RoCE
```

**Testing**:
```bash
# Test bandwidth with GPUDirect
ib_write_bw -d mlx5_0 -a --use_cuda=0 <remote_host>

# NCCL test
./nccl-tests/build/all_reduce_perf -b 8 -e 128M -f 2 -g 8
```

## Network Performance Optimization

### Bandwidth Optimization

**1. Large Message Sizes**:
```c
// Use large buffers to amortize latency
#define OPTIMAL_SIZE (4 * 1024 * 1024)  // 4 MB

// Avoid many small messages
for (int i = 0; i < n; i++) {
    MPI_Send(&small_buf[i], 1, MPI_INT, dest, tag, comm);  // BAD
}

// Batch into larger messages
MPI_Send(small_buf, n, MPI_INT, dest, tag, comm);  // GOOD
```

**2. Non-Blocking Operations**:
```c
// Overlap multiple transfers
MPI_Request requests[N];
for (int i = 0; i < N; i++) {
    MPI_Isend(buffers[i], size, MPI_BYTE, dests[i],
              tags[i], comm, &requests[i]);
}
MPI_Waitall(N, requests, MPI_STATUSES_IGNORE);
```

**3. Pipeline Communication**:
```c
// Stream large data in chunks
for (int chunk = 0; chunk < num_chunks; chunk++) {
    MPI_Isend(&data[chunk * chunk_size], chunk_size,
              MPI_BYTE, dest, chunk, comm, &requests[chunk]);
}
```

### Latency Optimization

**1. Eager Protocol**:
```bash
# Increase eager message threshold
export MPI_EAGER_LIMIT=65536  # OpenMPI
export MPICH_EAGER_MAX_MSG_SIZE=65536  # MPICH
```

**2. Progress Threads**:
```bash
# Enable asynchronous progress
export MPICH_ASYNC_PROGRESS=1
```

**3. Polling vs Blocking**:
```c
// Polling for low latency (uses CPU)
while (!flag) {
    MPI_Test(&request, &flag, &status);
}

// Blocking for CPU efficiency
MPI_Wait(&request, &status);
```

### Multi-Rail Configuration

**Using Multiple NICs**:
```bash
# OpenMPI with multiple IB ports
mpirun --mca btl_openib_if_include mlx5_0,mlx5_1 \
       ./application

# NCCL with multiple NICs
export NCCL_IB_HCA=mlx5_0,mlx5_1
export NCCL_SOCKET_IFNAME=ib0,ib1
```

### Bandwidth and Latency Tradeoffs

**Latency-Sensitive Applications**:
- Small message sizes
- Frequent synchronization
- Fine-grained parallelism
- Optimize for: Message rate, latency

**Bandwidth-Sensitive Applications**:
- Large data transfers
- Bulk communication
- Coarse-grained parallelism
- Optimize for: Throughput, message size

### Network Monitoring

**InfiniBand Diagnostics**:
```bash
# Check link status
ibstatus

# Monitor performance counters
perfquery mlx5_0 1

# Check topology
ibnetdiscover

# Monitor errors
ibdiagnet

# Performance testing
ib_write_bw -a -d mlx5_0 <remote_host>
ib_read_bw -a -d mlx5_0 <remote_host>
```

**System Monitoring**:
```bash
# Network interface statistics
ifconfig ib0
ethtool -S ib0

# Bandwidth monitoring
iftop -i ib0
nload ib0

# MPI profiling
mpirun -profile=mpi ./application
```

## Bandwidth and Latency Considerations

### Theoretical Limits

**Bandwidth Calculation**:
```
Peak Bandwidth = Link Speed × Encoding Efficiency
Effective Bandwidth ≈ 0.9 × Peak Bandwidth

Example HDR InfiniBand:
Peak: 200 Gb/s = 25 GB/s
Effective: ~22-23 GB/s
```

**Latency Components**:
```
Total Latency = Software Overhead + Serialization + Propagation + Queuing

Software Overhead: 0.5-1 μs (RDMA) or 2-5 μs (TCP)
Serialization: Message_Size / Bandwidth
Propagation: Distance / Speed_of_Light
Queuing: Depends on congestion
```

### Measuring Performance

**Bandwidth Test**:
```c
// MPI bandwidth benchmark
double start = MPI_Wtime();
for (int i = 0; i < iterations; i++) {
    MPI_Send(buffer, size, MPI_BYTE, dest, 0, MPI_COMM_WORLD);
    MPI_Recv(buffer, size, MPI_BYTE, src, 0, MPI_COMM_WORLD,
             MPI_STATUS_IGNORE);
}
double end = MPI_Wtime();

double bandwidth = (2.0 * size * iterations) / (end - start) / 1e9;
printf("Bandwidth: %.2f GB/s\n", bandwidth);
```

**Latency Test**:
```c
// Ping-pong latency test
double start = MPI_Wtime();
for (int i = 0; i < iterations; i++) {
    if (rank == 0) {
        MPI_Send(buffer, 1, MPI_BYTE, 1, 0, MPI_COMM_WORLD);
        MPI_Recv(buffer, 1, MPI_BYTE, 1, 0, MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
    } else {
        MPI_Recv(buffer, 1, MPI_BYTE, 0, 0, MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
        MPI_Send(buffer, 1, MPI_BYTE, 0, 0, MPI_COMM_WORLD);
    }
}
double end = MPI_Wtime();

double latency = (end - start) / (2.0 * iterations) * 1e6;
printf("Latency: %.2f μs\n", latency);
```

### Application Performance Model

**Roofline Model**:
```
Performance = min(Peak_FLOPS, Bandwidth × Arithmetic_Intensity)

Where Arithmetic_Intensity = FLOPs / Bytes_Transferred
```

**Network-Bound Applications**:
- Low arithmetic intensity
- Performance limited by bandwidth/latency
- Examples: Distributed sorting, data analytics

**Compute-Bound Applications**:
- High arithmetic intensity
- Network less critical
- Examples: Matrix multiplication, FFT

## Conclusion

HPC networking is a complex but critical component of high-performance distributed systems. Key takeaways:

1. **Choose the right technology**: InfiniBand for on-premises, EFA for cloud
2. **Understand topology**: Fat-tree for general HPC, specialized for specific workloads
3. **Leverage RDMA**: Essential for low-latency communication
4. **Enable GPUDirect**: Critical for multi-GPU workloads
5. **Optimize for your workload**: Bandwidth vs latency tradeoffs
6. **Monitor and profile**: Identify network bottlenecks
7. **Consider placement**: Topology-aware process placement
8. **Scale appropriately**: Network design affects maximum scale

Modern HPC systems achieve performance through careful co-design of compute, memory, and network subsystems. Understanding these networking technologies and their optimal configurations is essential for achieving scalable performance in distributed HPC applications.
