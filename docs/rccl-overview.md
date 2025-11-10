# ROCm Collective Communications Library (RCCL) Overview

## Introduction

ROCm Collective Communications Library (RCCL) is AMD's implementation of collective communication primitives optimized for AMD GPUs. RCCL is designed to be API-compatible with NVIDIA's NCCL, enabling easy portability of distributed GPU applications between NVIDIA and AMD platforms. It provides high-performance multi-GPU and multi-node communication capabilities for AMD Instinct accelerators and Radeon GPUs.

## AMD ROCm Ecosystem Integration

### ROCm Platform Architecture

RCCL is a key component of the ROCm (Radeon Open Compute) platform:

```
ROCm Stack:
├── Applications (PyTorch, TensorFlow, etc.)
├── Communication Libraries (RCCL)
├── Math Libraries (rocBLAS, rocFFT, MIOpen)
├── Runtime (HIP)
├── Compiler (ROCm LLVM)
└── Kernel Driver (KFD)
```

### HIP Runtime Integration

RCCL integrates seamlessly with HIP (Heterogeneous-Interface for Portability):

- **HIP Streams**: RCCL operations execute on HIP streams
- **Memory Model**: Uses HIP memory allocation and management
- **Device Management**: Compatible with HIP device selection
- **Kernel Launch**: RCCL kernels launched via HIP runtime

### AMD Infinity Fabric

RCCL leverages AMD's Infinity Fabric for inter-GPU communication:

- **High Bandwidth**: Up to 200 GB/s per link (MI300 series)
- **Low Latency**: Sub-microsecond GPU-to-GPU communication
- **Scalability**: Supports complex multi-GPU topologies
- **Coherency**: Cache-coherent interconnect for some operations

## Comparison with NCCL

### API Compatibility

RCCL maintains API compatibility with NCCL for easy portability:

```cpp
// Code using RCCL (same as NCCL)
#include <rccl.h>

ncclComm_t comm;
ncclResult_t result;

// Initialize communicator
result = ncclCommInitRank(&comm, nranks, ncclId, rank);

// Perform AllReduce
result = ncclAllReduce(sendbuff, recvbuff, count,
                       ncclFloat, ncclSum, comm, stream);
```

**Key Point**: Most NCCL code can be recompiled for RCCL by simply changing include paths and linking against RCCL libraries.

### Feature Parity

| Feature | NCCL | RCCL | Notes |
|---------|------|------|-------|
| AllReduce | Yes | Yes | Full support |
| Broadcast | Yes | Yes | Full support |
| Reduce | Yes | Yes | Full support |
| AllGather | Yes | Yes | Full support |
| ReduceScatter | Yes | Yes | Full support |
| Send/Recv | Yes | Yes | Point-to-point operations |
| Group Operations | Yes | Yes | Batch multiple operations |
| GPUDirect RDMA | Yes | Yes | With compatible NICs |
| InfiniBand | Yes | Yes | Full support |
| RoCE | Yes | Yes | RDMA over Ethernet |
| Topology Detection | Yes | Yes | Automatic optimization |

### Performance Characteristics

**Similarities**:
- Ring-based algorithms for bandwidth optimization
- Tree algorithms for latency-sensitive operations
- Topology-aware communication patterns
- Asynchronous execution model

**Differences**:
- RCCL optimized for AMD GPU memory hierarchy
- Different interconnect technologies (Infinity Fabric vs NVLink)
- Platform-specific tuning parameters
- Distinct performance tuning strategies

### Architecture Differences

**Memory Architecture**:
```
NVIDIA (with NCCL):
- Unified memory addressing
- NVLink interconnect
- CUDA memory model

AMD (with RCCL):
- HIP memory model
- Infinity Fabric interconnect
- ROCm memory management
```

**Communication Path**:
- **NCCL**: GPU → NVLink/PCIe → GPU
- **RCCL**: GPU → Infinity Fabric/PCIe → GPU

## Supported Operations and Features

### Collective Operations

#### AllReduce
```cpp
ncclResult_t ncclAllReduce(
    const void* sendbuff,
    void* recvbuff,
    size_t count,
    ncclDataType_t datatype,
    ncclRedOp_t op,
    ncclComm_t comm,
    hipStream_t stream
);
```

**Supported Reduction Operations**:
- `ncclSum`: Summation
- `ncclProd`: Product
- `ncclMax`: Maximum value
- `ncclMin`: Minimum value
- `ncclAvg`: Average (RCCL 2.10+)

**Data Types**:
- `ncclInt8`, `ncclUint8`
- `ncclInt32`, `ncclUint32`
- `ncclInt64`, `ncclUint64`
- `ncclFloat16` (half precision)
- `ncclFloat32` (single precision)
- `ncclFloat64` (double precision)
- `ncclBfloat16` (brain float)

#### Broadcast
```cpp
ncclResult_t ncclBroadcast(
    const void* sendbuff,
    void* recvbuff,
    size_t count,
    ncclDataType_t datatype,
    int root,
    ncclComm_t comm,
    hipStream_t stream
);
```

#### AllGather
```cpp
ncclResult_t ncclAllGather(
    const void* sendbuff,
    void* recvbuff,
    size_t sendcount,
    ncclDataType_t datatype,
    ncclComm_t comm,
    hipStream_t stream
);
```

#### ReduceScatter
```cpp
ncclResult_t ncclReduceScatter(
    const void* sendbuff,
    void* recvbuff,
    size_t recvcount,
    ncclDataType_t datatype,
    ncclRedOp_t op,
    ncclComm_t comm,
    hipStream_t stream
);
```

#### Send/Recv
```cpp
ncclResult_t ncclSend(
    const void* sendbuff,
    size_t count,
    ncclDataType_t datatype,
    int peer,
    ncclComm_t comm,
    hipStream_t stream
);

ncclResult_t ncclRecv(
    void* recvbuff,
    size_t count,
    ncclDataType_t datatype,
    int peer,
    ncclComm_t comm,
    hipStream_t stream
);
```

### Group Operations

Batch multiple operations for improved efficiency:

```cpp
ncclGroupStart();

// Multiple operations executed as a group
ncclAllReduce(buff1, buff1, count1, ncclFloat, ncclSum, comm, stream);
ncclBroadcast(buff2, buff2, count2, ncclFloat, root, comm, stream);
ncclAllGather(buff3, buff4, count3, ncclFloat, comm, stream);

ncclGroupEnd();
```

**Benefits**:
- Reduced launch overhead
- Better scheduling opportunities
- Improved bandwidth utilization
- Deadlock prevention for Send/Recv patterns

## Performance Tuning for AMD GPUs

### GPU-Specific Optimizations

#### Memory Access Patterns

AMD GPUs have distinct memory hierarchy characteristics:

```
Memory Hierarchy:
├── L2 Cache (shared across CUs)
├── L1 Cache (per CU)
├── LDS (Local Data Share)
└── Global Memory (HBM2/HBM3)
```

**Optimization Strategies**:
1. Align buffers to cache line boundaries (128 bytes)
2. Use coalesced memory access patterns
3. Leverage LDS for intermediate reductions
4. Optimize for HBM bandwidth

#### Wavefront Considerations

AMD GPUs use wavefronts (64 threads) vs NVIDIA warps (32 threads):

- **Occupancy**: Optimize for wavefront occupancy
- **Divergence**: Minimize wavefront divergence
- **Scheduling**: Consider wavefront scheduling patterns

### RCCL-Specific Tuning

#### Environment Variables

```bash
# Network interface selection
export NCCL_SOCKET_IFNAME=ib0

# InfiniBand configuration
export NCCL_IB_DISABLE=0
export NCCL_IB_HCA=mlx5_0:1,mlx5_1:1

# Network tuning
export NCCL_NET_GDR_LEVEL=3  # Enable GPUDirect RDMA
export NCCL_NET_GDR_READ=1

# Algorithm selection
export NCCL_ALGO=Ring  # or Tree
export NCCL_PROTO=Simple  # or LL, LL128

# Buffer sizes
export NCCL_BUFFSIZE=4194304  # 4MB

# Debug output
export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=ALL

# Timeout configuration
export NCCL_TIMEOUT=1800

# AMD-specific optimizations
export HSA_FORCE_FINE_GRAIN_PCIE=1
export GPU_MAX_HW_QUEUES=8
```

#### Topology Optimization

Configure RCCL for specific AMD GPU topologies:

```bash
# MI250X (2 GCDs per package)
export NCCL_TOPO_FILE=/opt/rocm/share/rccl/topo/MI250X.xml

# Custom topology
export NCCL_TOPO_FILE=/path/to/custom_topology.xml
```

### Benchmark-Driven Tuning

#### RCCL Performance Tests

```bash
# Clone RCCL tests
git clone https://github.com/ROCmSoftwarePlatform/rccl-tests.git
cd rccl-tests
make

# Run AllReduce benchmark
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 8

# Run all collective benchmarks
./build/all_reduce_perf -g 8
./build/all_gather_perf -g 8
./build/broadcast_perf -g 8
./build/reduce_scatter_perf -g 8
```

#### Performance Metrics

Key metrics to monitor:

1. **Bandwidth**: GB/s achieved vs theoretical maximum
2. **Latency**: Microseconds for operation completion
3. **Efficiency**: Percentage of peak bandwidth utilized
4. **Scalability**: Performance vs number of GPUs

### Multi-GPU System Configuration

#### MI300 Series Optimization

For AMD MI300X accelerators:

```bash
# Enable Infinity Fabric optimizations
export HSA_XNACK=0  # Disable XNACK for performance
export HSA_FORCE_FINE_GRAIN_PCIE=1

# Optimize for 8 GPU configuration
export RCCL_NUM_XGMI_LINKS=16  # MI300X has 16 XGMI links
```

#### MI250/MI250X Optimization

For dual-GCD packages:

```bash
# Each MI250X has 2 GCDs (treated as 2 GPUs)
# Total 8 GCDs in 4-package system

# Optimize XGMI communication
export RCCL_XGMI_ENABLED=1
```

## Installation and Configuration

### Installation from ROCm Repository

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install rccl rccl-dev

# RHEL/CentOS
sudo yum install rccl rccl-devel
```

### Building from Source

```bash
# Clone RCCL repository
git clone https://github.com/ROCmSoftwarePlatform/rccl.git
cd rccl

# Build with ROCm
mkdir build
cd build
CXX=/opt/rocm/bin/hipcc cmake ..
make -j$(nproc)
sudo make install
```

### Verifying Installation

```bash
# Check RCCL version
/opt/rocm/bin/rccl-info

# Verify GPU detection
rocm-smi
rocminfo

# Test basic communication
cd /opt/rocm/share/rccl/tests
./all_reduce_perf -g 2
```

### Integration with MPI

RCCL works seamlessly with MPI for multi-node communication:

```cpp
#include <mpi.h>
#include <rccl.h>
#include <hip/hip_runtime.h>

int main(int argc, char* argv[]) {
    // Initialize MPI
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Set GPU device
    hipSetDevice(rank % num_local_gpus);

    // Create NCCL unique ID
    ncclUniqueId id;
    if (rank == 0) ncclGetUniqueId(&id);
    MPI_Bcast(&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD);

    // Initialize RCCL communicator
    ncclComm_t comm;
    ncclCommInitRank(&comm, size, id, rank);

    // Perform RCCL operations
    float* d_data;
    hipMalloc(&d_data, count * sizeof(float));

    hipStream_t stream;
    hipStreamCreate(&stream);

    ncclAllReduce(d_data, d_data, count, ncclFloat,
                  ncclSum, comm, stream);

    hipStreamSynchronize(stream);

    // Cleanup
    ncclCommDestroy(comm);
    hipStreamDestroy(stream);
    hipFree(d_data);
    MPI_Finalize();

    return 0;
}
```

## Best Practices for AMD GPU Clusters

### 1. Topology-Aware Process Placement

Map MPI ranks to GPUs considering Infinity Fabric topology:

```bash
# Check GPU topology
rocm-smi --showtoponuma

# Use NUMA binding for optimal performance
numactl --cpunodebind=0 --membind=0 ./application
```

### 2. Memory Management

```cpp
// Use pinned memory for faster transfers
float* h_data;
hipHostMalloc(&h_data, size, hipHostMallocDefault);

// Use managed memory when appropriate
float* m_data;
hipMallocManaged(&m_data, size);
```

### 3. Stream Management

```cpp
// Create multiple streams for overlap
hipStream_t compute_stream, comm_stream;
hipStreamCreate(&compute_stream);
hipStreamCreate(&comm_stream);

// Launch computation on compute stream
kernel<<<grid, block, 0, compute_stream>>>(data);

// Launch communication on comm stream
ncclAllReduce(buffer, buffer, count, ncclFloat,
              ncclSum, comm, comm_stream);
```

### 4. Error Handling

```cpp
ncclResult_t result;

result = ncclAllReduce(sendbuff, recvbuff, count,
                       ncclFloat, ncclSum, comm, stream);

if (result != ncclSuccess) {
    const char* err = ncclGetErrorString(result);
    fprintf(stderr, "RCCL error: %s\n", err);
    // Handle error appropriately
}
```

### 5. Profiling and Debugging

```bash
# Use rocprof for profiling
rocprof --stats ./application

# Enable RCCL debug output
export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=INIT,COLL,NET

# Trace RCCL calls
export NCCL_DEBUG_FILE=/tmp/rccl_trace_%h_%p.log
```

## Common Issues and Troubleshooting

### Issue 1: Poor Performance

**Symptoms**: Low bandwidth, high latency

**Solutions**:
1. Verify Infinity Fabric connectivity: `rocm-smi --showtoponuma`
2. Check for PCIe bottlenecks: Ensure GPUs use full PCIe bandwidth
3. Enable GPUDirect RDMA: `export NCCL_NET_GDR_LEVEL=3`
4. Tune buffer sizes: `export NCCL_BUFFSIZE=8388608`

### Issue 2: Hangs and Deadlocks

**Symptoms**: Application freezes during RCCL operations

**Solutions**:
1. Ensure all ranks call collectives
2. Check for mismatched parameters across ranks
3. Verify network connectivity between nodes
4. Increase timeout: `export NCCL_TIMEOUT=3600`
5. Check for GPU memory issues: `rocm-smi --showmeminfo`

### Issue 3: InfiniBand Issues

**Symptoms**: Slow multi-node performance

**Solutions**:
1. Verify IB connectivity: `ibstatus`
2. Check GPUDirect support: `nvidia-peermem` or AMD equivalent
3. Configure correct IB device: `export NCCL_IB_HCA=mlx5_0:1`
4. Disable IB if causing issues: `export NCCL_IB_DISABLE=1`

### Issue 4: Memory Errors

**Symptoms**: Allocation failures, out of memory errors

**Solutions**:
1. Reduce RCCL buffer size: `export NCCL_BUFFSIZE=2097152`
2. Monitor GPU memory: `rocm-smi --showuse`
3. Use in-place operations when possible
4. Check for memory leaks in application

## Integration with Deep Learning Frameworks

### PyTorch with ROCm

```python
import torch
import torch.distributed as dist

# Initialize process group with NCCL backend (RCCL on AMD)
dist.init_process_group(backend='nccl', init_method='env://')

# Set device
device = torch.device(f'cuda:{rank}')  # HIP runtime via PyTorch
torch.cuda.set_device(device)

# Distributed training
model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[rank])

# All operations automatically use RCCL
tensor = torch.randn(1000, 1000).to(device)
dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
```

### TensorFlow with ROCm

```python
import tensorflow as tf

# Multi-GPU strategy (uses RCCL internally)
strategy = tf.distribute.MultiWorkerMirroredStrategy()

with strategy.scope():
    model = create_model()
    model.compile(optimizer='adam', loss='mse')

# Training automatically uses RCCL for gradient synchronization
model.fit(dataset, epochs=10)
```

## Conclusion

RCCL provides AMD GPU users with high-performance collective communication capabilities comparable to NCCL on NVIDIA platforms. Key advantages include:

1. **API Compatibility**: Easy migration from NVIDIA platforms
2. **Performance**: Optimized for AMD GPU architecture and Infinity Fabric
3. **Integration**: Seamless integration with ROCm ecosystem
4. **Scalability**: Supports large-scale multi-GPU and multi-node deployments
5. **Flexibility**: Works with InfiniBand, RoCE, and standard Ethernet

By understanding RCCL's features, tuning parameters, and best practices, developers can achieve optimal performance for distributed computing workloads on AMD GPU clusters. The combination of RCCL, ROCm, and AMD Instinct accelerators provides a powerful platform for HPC and AI applications.
