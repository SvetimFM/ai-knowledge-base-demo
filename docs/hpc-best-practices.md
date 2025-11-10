# HPC Best Practices

## Introduction

High-Performance Computing (HPC) requires careful attention to algorithm design, implementation details, and system configuration to achieve optimal performance and scalability. This guide compiles best practices learned from decades of HPC development, covering scaling strategies, performance optimization, resource utilization, and common pitfalls to avoid.

## Scaling Strategies

### Strong Scaling vs Weak Scaling

**Strong Scaling**:
- **Definition**: Fixed total problem size, increasing number of processors
- **Goal**: Reduce time-to-solution
- **Challenge**: Increasing communication overhead relative to computation

**Ideal Strong Scaling**:
```
Speedup = T_serial / T_parallel = N (linear)
Efficiency = Speedup / N = 1.0 (100%)
```

**Reality**:
```
Amdahl's Law: Speedup ≤ 1 / (S + P/N)
Where: S = serial fraction, P = parallel fraction, N = processors
```

**Example**:
```c
// Problem: Sum array of fixed size N = 10^9 elements
// 1 processor: 10 seconds
// 2 processors: 5.1 seconds (overhead)
// 4 processors: 2.6 seconds
// 8 processors: 1.4 seconds
// 16 processors: 0.8 seconds (diminishing returns)

// Efficiency decreases as processors increase
```

**Weak Scaling**:
- **Definition**: Problem size grows proportionally with number of processors
- **Goal**: Solve larger problems in same time
- **Challenge**: Maintaining constant efficiency as system scales

**Ideal Weak Scaling**:
```
T_parallel(N, P) = T_serial(N/P) = constant
Efficiency = T_serial(N/P) / T_parallel(N, P) = 1.0
```

**Gustafson's Law**:
```
Speedup = N - S × (N - 1)
Where: S = serial fraction, N = processors
```

**Example**:
```c
// Problem: Sum N elements where N = processors × 10^6
// 1 processor: 1M elements, 1 second
// 2 processors: 2M elements, 1.05 seconds
// 4 processors: 4M elements, 1.10 seconds
// 8 processors: 8M elements, 1.15 seconds

// Nearly constant time for proportionally larger problems
```

### Choosing the Right Scaling Strategy

**Use Strong Scaling When**:
- Problem size is fixed (real-world constraint)
- Want to reduce time-to-solution
- Have limited memory per node
- Need results faster

**Use Weak Scaling When**:
- Want to solve larger problems
- Have sufficient memory
- Concerned with throughput
- Modeling scales naturally

### Measuring Scalability

**Strong Scaling Study**:
```bash
# Run with increasing processor counts
for P in 1 2 4 8 16 32 64 128; do
    mpirun -np $P ./application --size=1000000
done

# Plot speedup and efficiency
# Speedup = T_1 / T_P
# Efficiency = Speedup / P
```

**Weak Scaling Study**:
```bash
# Scale problem with processors
for P in 1 2 4 8 16 32 64 128; do
    SIZE=$((P * 1000000))
    mpirun -np $P ./application --size=$SIZE
done

# Time should remain approximately constant
```

### Parallel Efficiency Targets

**Excellent**: > 90% efficiency
**Good**: 70-90% efficiency
**Acceptable**: 50-70% efficiency (for strong scaling at scale)
**Poor**: < 50% efficiency

```c
// Example efficiency calculation
double parallel_time = 2.5;  // seconds with 8 processors
double serial_time = 10.0;   // seconds with 1 processor
int nprocs = 8;

double speedup = serial_time / parallel_time;  // 4.0
double efficiency = speedup / nprocs;          // 0.50 (50%)
```

## Load Balancing Techniques

### Static Load Balancing

**Block Distribution**:
```c
// Divide work into equal contiguous blocks
int local_start = rank * (N / nprocs);
int local_end = (rank + 1) * (N / nprocs);

for (int i = local_start; i < local_end; i++) {
    process_element(i);
}
```

**Cyclic Distribution**:
```c
// Distribute elements in round-robin fashion
for (int i = rank; i < N; i += nprocs) {
    process_element(i);
}
```

**Block-Cyclic Distribution**:
```c
// Combine block and cyclic for better load balance
int block_size = 100;
for (int block = rank; block < N/block_size; block += nprocs) {
    int start = block * block_size;
    int end = start + block_size;
    for (int i = start; i < end; i++) {
        process_element(i);
    }
}
```

### Dynamic Load Balancing

**Work Queue Pattern**:
```c
// Master-worker with dynamic task assignment
if (rank == 0) {
    // Master: Distribute tasks on demand
    int task = 0;
    int active_workers = nprocs - 1;

    // Send initial tasks
    for (int w = 1; w < nprocs; w++) {
        MPI_Send(&task, 1, MPI_INT, w, WORK_TAG,
                 MPI_COMM_WORLD);
        task++;
    }

    // Distribute remaining tasks
    while (active_workers > 0) {
        int result;
        MPI_Status status;
        MPI_Recv(&result, 1, MPI_INT, MPI_ANY_SOURCE,
                 MPI_ANY_TAG, MPI_COMM_WORLD, &status);

        if (task < num_tasks) {
            // Send more work
            MPI_Send(&task, 1, MPI_INT, status.MPI_SOURCE,
                     WORK_TAG, MPI_COMM_WORLD);
            task++;
        } else {
            // No more work, terminate worker
            MPI_Send(NULL, 0, MPI_INT, status.MPI_SOURCE,
                     DONE_TAG, MPI_COMM_WORLD);
            active_workers--;
        }
    }
} else {
    // Worker: Request and process tasks
    while (1) {
        int task;
        MPI_Status status;
        MPI_Recv(&task, 1, MPI_INT, 0, MPI_ANY_TAG,
                 MPI_COMM_WORLD, &status);

        if (status.MPI_TAG == DONE_TAG) break;

        // Process task
        int result = process_task(task);

        // Send result back
        MPI_Send(&result, 1, MPI_INT, 0, RESULT_TAG,
                 MPI_COMM_WORLD);
    }
}
```

**Work Stealing**:
```c
// Each process maintains local queue
// Steal work from neighbors when idle

typedef struct {
    Task* tasks;
    int size;
    int capacity;
    pthread_mutex_t lock;
} WorkQueue;

void* worker_thread(void* arg) {
    WorkQueue* local_queue = (WorkQueue*)arg;

    while (!done) {
        Task task;

        // Try to get local work
        pthread_mutex_lock(&local_queue->lock);
        if (local_queue->size > 0) {
            task = pop_task(local_queue);
            pthread_mutex_unlock(&local_queue->lock);
            process_task(task);
        } else {
            pthread_mutex_unlock(&local_queue->lock);

            // Try to steal from neighbors
            bool stolen = false;
            for (int neighbor = 0; neighbor < num_neighbors; neighbor++) {
                if (try_steal_task(neighbor, &task)) {
                    process_task(task);
                    stolen = true;
                    break;
                }
            }

            if (!stolen) {
                // No work available, sleep briefly
                usleep(100);
            }
        }
    }
}
```

### Load Imbalance Detection

**Timing Analysis**:
```c
// Measure load imbalance
double start = MPI_Wtime();

// Do work
compute_local_work();

double end = MPI_Wtime();
double local_time = end - start;

// Gather times from all processes
double max_time, min_time, avg_time;
MPI_Reduce(&local_time, &max_time, 1, MPI_DOUBLE,
           MPI_MAX, 0, MPI_COMM_WORLD);
MPI_Reduce(&local_time, &min_time, 1, MPI_DOUBLE,
           MPI_MIN, 0, MPI_COMM_WORLD);
MPI_Reduce(&local_time, &avg_time, 1, MPI_DOUBLE,
           MPI_SUM, 0, MPI_COMM_WORLD);

if (rank == 0) {
    avg_time /= nprocs;
    double imbalance = (max_time - min_time) / avg_time;
    printf("Load imbalance: %.2f%%\n", imbalance * 100);

    // Imbalance > 10% indicates problem
    if (imbalance > 0.1) {
        printf("WARNING: Significant load imbalance detected!\n");
    }
}
```

## Memory Management in Distributed Systems

### Memory Hierarchy Awareness

**Cache-Friendly Data Layout**:
```c
// BAD: Array of structures (poor cache locality)
struct Particle {
    double x, y, z;
    double vx, vy, vz;
    double mass;
};
Particle particles[N];

// Access x coordinates (scattered in memory)
for (int i = 0; i < N; i++) {
    sum += particles[i].x;  // Cache misses
}

// GOOD: Structure of arrays (good cache locality)
struct ParticleArray {
    double* x;
    double* y;
    double* z;
    double* vx;
    double* vy;
    double* vz;
    double* mass;
};

// Access x coordinates (contiguous in memory)
for (int i = 0; i < N; i++) {
    sum += particles.x[i];  // Cache hits
}
```

**Data Alignment**:
```c
// Align to cache line boundaries (64 bytes typical)
#define CACHE_LINE_SIZE 64

// Use posix_memalign for aligned allocation
double* data;
posix_memalign((void**)&data, CACHE_LINE_SIZE,
               N * sizeof(double));

// Or use compiler directives
double data[N] __attribute__((aligned(CACHE_LINE_SIZE)));
```

### NUMA-Aware Allocation

**First-Touch Policy**:
```c
// Allocate memory
double* data = malloc(N * sizeof(double));

// Initialize in parallel (first-touch)
#pragma omp parallel for
for (int i = 0; i < N; i++) {
    data[i] = 0.0;  // Page allocated on local NUMA node
}

// Now use data (already on correct NUMA nodes)
#pragma omp parallel for
for (int i = 0; i < N; i++) {
    data[i] = compute(data[i]);
}
```

**Explicit NUMA Binding**:
```bash
# Bind MPI ranks to NUMA nodes
mpirun --map-by numa:PE=8 ./application

# Or use numactl
for rank in 0 1 2 3; do
    numactl --cpunodebind=$rank --membind=$rank \
        ./application &
done
```

### Memory Pooling

**Custom Allocator**:
```c
typedef struct {
    void* pool;
    size_t size;
    size_t used;
    pthread_mutex_t lock;
} MemoryPool;

MemoryPool* create_memory_pool(size_t size) {
    MemoryPool* pool = malloc(sizeof(MemoryPool));
    pool->pool = malloc(size);
    pool->size = size;
    pool->used = 0;
    pthread_mutex_init(&pool->lock, NULL);
    return pool;
}

void* pool_alloc(MemoryPool* pool, size_t size) {
    pthread_mutex_lock(&pool->lock);

    if (pool->used + size > pool->size) {
        pthread_mutex_unlock(&pool->lock);
        return NULL;  // Pool exhausted
    }

    void* ptr = (char*)pool->pool + pool->used;
    pool->used += size;

    pthread_mutex_unlock(&pool->lock);
    return ptr;
}

// Use pool for frequent allocations
MemoryPool* pool = create_memory_pool(1024 * 1024 * 1024);  // 1GB

for (int i = 0; i < num_iterations; i++) {
    void* buffer = pool_alloc(pool, buffer_size);
    // Use buffer
    // No individual free needed
}
```

### GPU Memory Management

**Unified Memory**:
```cpp
// CUDA Unified Memory
float* data;
cudaMallocManaged(&data, N * sizeof(float));

// Access from CPU
for (int i = 0; i < N; i++) {
    data[i] = i;
}

// Access from GPU
kernel<<<blocks, threads>>>(data, N);

cudaFree(data);
```

**Pinned Memory for Transfers**:
```cpp
// Faster CPU-GPU transfers with pinned memory
float* h_data;
cudaMallocHost(&h_data, N * sizeof(float));  // Pinned

float* d_data;
cudaMalloc(&d_data, N * sizeof(float));

// Fast transfer
cudaMemcpy(d_data, h_data, N * sizeof(float),
           cudaMemcpyHostToDevice);

cudaFree(d_data);
cudaFreeHost(h_data);
```

## Profiling and Performance Analysis Tools

### Timing and Instrumentation

**Basic Timing**:
```c
#include <time.h>

// CPU timing
clock_t start = clock();
compute();
clock_t end = clock();
double cpu_time = ((double)(end - start)) / CLOCKS_PER_SEC;

// Wall clock timing (better for parallel)
#include <sys/time.h>

struct timeval start, end;
gettimeofday(&start, NULL);
compute();
gettimeofday(&end, NULL);

double elapsed = (end.tv_sec - start.tv_sec) +
                 (end.tv_usec - start.tv_usec) / 1e6;
```

**MPI Timing**:
```c
// MPI_Wtime for distributed timing
double start = MPI_Wtime();

compute();
MPI_Barrier(MPI_COMM_WORLD);  // Synchronize

double end = MPI_Wtime();
double local_time = end - start;

// Collect statistics
double max_time, min_time, avg_time;
MPI_Reduce(&local_time, &max_time, 1, MPI_DOUBLE,
           MPI_MAX, 0, MPI_COMM_WORLD);
MPI_Reduce(&local_time, &avg_time, 1, MPI_DOUBLE,
           MPI_SUM, 0, MPI_COMM_WORLD);

if (rank == 0) {
    avg_time /= nprocs;
    printf("Time - Min: %.3f, Max: %.3f, Avg: %.3f\n",
           min_time, max_time, avg_time);
}
```

### Performance Profiling Tools

**GNU gprof**:
```bash
# Compile with profiling
gcc -pg -O2 application.c -o application

# Run application
./application

# Generate profile
gprof application gmon.out > profile.txt

# Analyze hotspots
less profile.txt
```

**perf (Linux)**:
```bash
# Record performance data
perf record -g ./application

# View report
perf report

# Specific events
perf stat -e cache-misses,cache-references,instructions,cycles \
    ./application

# Hardware counters
perf stat -e L1-dcache-load-misses,L1-dcache-loads \
    ./application
```

**Intel VTune**:
```bash
# Hotspots analysis
vtune -collect hotspots ./application

# Memory access analysis
vtune -collect memory-access ./application

# Threading analysis
vtune -collect threading ./application

# View GUI
vtune-gui
```

**NVIDIA Nsight Systems**:
```bash
# Profile CUDA application
nsys profile --stats=true ./cuda_application

# Generate detailed report
nsys profile -o report ./cuda_application

# View in GUI
nsys-ui report.qdrep
```

**NVIDIA Nsight Compute**:
```bash
# Profile specific kernel
ncu --kernel-name myKernel ./cuda_application

# Full metrics
ncu --set full --import-source yes ./cuda_application

# Memory analysis
ncu --metrics l1tex__m_sectors_pipe_lsu_mem_global_op_ld \
    ./cuda_application
```

**TAU (Tuning and Analysis Utilities)**:
```bash
# Instrument with TAU
tau_cc.sh -tau_options=-optCompInst application.c

# Run
./a.out

# Generate profiles
pprof

# View with ParaProf
paraprof
```

**Score-P and Scalasca**:
```bash
# Instrument with Score-P
scorep mpicc -O2 application.c -o application

# Run and trace
mpirun -np 8 ./application

# Analyze with Scalasca
scalasca -analyze mpirun -np 8 ./application

# View results
scalasca -examine scorep_*
```

### Communication Profiling

**MPI Profiling Interface (PMPI)**:
```c
// Wrapper for MPI_Send
int MPI_Send(const void *buf, int count, MPI_Datatype datatype,
             int dest, int tag, MPI_Comm comm) {
    double start = MPI_Wtime();

    // Call actual MPI_Send
    int ret = PMPI_Send(buf, count, datatype, dest, tag, comm);

    double end = MPI_Wtime();
    record_send_time(end - start, count);

    return ret;
}
```

**mpiP**:
```bash
# Link with mpiP
mpicc -O2 application.c -o application -lmpiP -lunwind

# Run (generates mpiP output automatically)
mpirun -np 8 ./application

# View report
less application.*.mpiP
```

## Common Pitfalls and Solutions

### Pitfall 1: Unnecessary Synchronization

**Problem**:
```c
// BAD: Frequent barriers
for (int iter = 0; iter < num_iters; iter++) {
    compute_local();
    MPI_Barrier(MPI_COMM_WORLD);  // Expensive!
}
```

**Solution**:
```c
// GOOD: Remove unnecessary barriers
for (int iter = 0; iter < num_iters; iter++) {
    compute_local();
    // No barrier needed if no dependencies
}

// Only synchronize when necessary
MPI_Barrier(MPI_COMM_WORLD);
```

### Pitfall 2: Small Message Overhead

**Problem**:
```c
// BAD: Many small messages
for (int i = 0; i < N; i++) {
    MPI_Send(&data[i], 1, MPI_DOUBLE, dest, i, comm);
}
```

**Solution**:
```c
// GOOD: Batch into fewer large messages
MPI_Send(data, N, MPI_DOUBLE, dest, tag, comm);

// Or use derived datatypes
MPI_Datatype strided_type;
MPI_Type_vector(N, 1, stride, MPI_DOUBLE, &strided_type);
MPI_Type_commit(&strided_type);
MPI_Send(data, 1, strided_type, dest, tag, comm);
MPI_Type_free(&strided_type);
```

### Pitfall 3: False Sharing

**Problem**:
```c
// BAD: False sharing between threads
int counters[NUM_THREADS];  // Adjacent in memory

#pragma omp parallel
{
    int tid = omp_get_thread_num();
    for (int i = 0; i < N; i++) {
        counters[tid]++;  // False sharing!
    }
}
```

**Solution**:
```c
// GOOD: Pad to avoid false sharing
struct PaddedCounter {
    int value;
    char pad[CACHE_LINE_SIZE - sizeof(int)];
};

struct PaddedCounter counters[NUM_THREADS];

#pragma omp parallel
{
    int tid = omp_get_thread_num();
    for (int i = 0; i < N; i++) {
        counters[tid].value++;
    }
}
```

### Pitfall 4: Serialized I/O

**Problem**:
```c
// BAD: Sequential I/O
for (int rank = 0; rank < nprocs; rank++) {
    if (my_rank == rank) {
        FILE* f = fopen("output.txt", "a");
        fprintf(f, "Data from rank %d\n", rank);
        fclose(f);
    }
    MPI_Barrier(MPI_COMM_WORLD);
}
```

**Solution**:
```c
// GOOD: MPI-IO for parallel I/O
MPI_File fh;
MPI_File_open(MPI_COMM_WORLD, "output.txt",
              MPI_MODE_CREATE | MPI_MODE_WRONLY,
              MPI_INFO_NULL, &fh);

MPI_Offset offset = rank * sizeof(double) * local_size;
MPI_File_write_at(fh, offset, local_data, local_size,
                  MPI_DOUBLE, MPI_STATUS_IGNORE);

MPI_File_close(&fh);
```

### Pitfall 5: Insufficient Error Checking

**Problem**:
```c
// BAD: No error checking
cudaMalloc(&d_data, size);
kernel<<<grid, block>>>(d_data);
cudaMemcpy(h_data, d_data, size, cudaMemcpyDeviceToHost);
```

**Solution**:
```c
// GOOD: Check all CUDA calls
cudaError_t err;

err = cudaMalloc(&d_data, size);
if (err != cudaSuccess) {
    fprintf(stderr, "cudaMalloc failed: %s\n",
            cudaGetErrorString(err));
    exit(1);
}

kernel<<<grid, block>>>(d_data);

err = cudaGetLastError();
if (err != cudaSuccess) {
    fprintf(stderr, "Kernel launch failed: %s\n",
            cudaGetErrorString(err));
    exit(1);
}

err = cudaMemcpy(h_data, d_data, size, cudaMemcpyDeviceToHost);
if (err != cudaSuccess) {
    fprintf(stderr, "cudaMemcpy failed: %s\n",
            cudaGetErrorString(err));
    exit(1);
}
```

## Resource Utilization Optimization

### CPU Utilization

**Hybrid MPI+OpenMP**:
```c
// Use MPI between nodes, OpenMP within nodes
int provided;
MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);

MPI_Comm_rank(MPI_COMM_WORLD, &rank);
MPI_Comm_size(MPI_COMM_WORLD, &size);

// Compute with OpenMP
#pragma omp parallel for
for (int i = 0; i < local_size; i++) {
    local_data[i] = compute(local_data[i]);
}

// Communicate with MPI
MPI_Allreduce(local_data, global_data, local_size,
              MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);

MPI_Finalize();
```

**Process Binding**:
```bash
# OpenMPI process and thread binding
mpirun --map-by socket:PE=4 --bind-to core \
       --report-bindings ./application

# Intel MPI
mpirun -genv I_MPI_PIN=1 -genv I_MPI_PIN_DOMAIN=socket \
       ./application

# SLURM
srun --cpu-bind=cores --threads-per-core=1 ./application
```

### GPU Utilization

**Kernel Occupancy**:
```cpp
// Query occupancy
int blockSize = 256;
int minGridSize, gridSize;

cudaOccupancyMaxPotentialBlockSize(&minGridSize, &blockSize,
                                    myKernel, 0, 0);

// Launch with optimal configuration
gridSize = (N + blockSize - 1) / blockSize;
myKernel<<<gridSize, blockSize>>>(data, N);
```

**Stream Concurrency**:
```cpp
// Multiple streams for kernel concurrency
cudaStream_t streams[NUM_STREAMS];
for (int i = 0; i < NUM_STREAMS; i++) {
    cudaStreamCreate(&streams[i]);
}

// Launch kernels on different streams
for (int i = 0; i < NUM_STREAMS; i++) {
    int offset = i * chunk_size;
    kernel<<<grid, block, 0, streams[i]>>>(&data[offset], chunk_size);
}

// Synchronize all streams
for (int i = 0; i < NUM_STREAMS; i++) {
    cudaStreamSynchronize(streams[i]);
    cudaStreamDestroy(streams[i]);
}
```

### Network Utilization

**Communication Overlap**:
```c
// Overlap computation and communication
MPI_Request request;

// Start non-blocking communication
MPI_Iallreduce(sendbuf, recvbuf, count, MPI_DOUBLE,
               MPI_SUM, MPI_COMM_WORLD, &request);

// Do independent work while communicating
compute_independent_work();

// Wait for communication to complete
MPI_Wait(&request, MPI_STATUS_IGNORE);

// Use result
process_result(recvbuf);
```

**Multi-Rail Networks**:
```bash
# Utilize multiple network interfaces
export NCCL_IB_HCA=mlx5_0,mlx5_1,mlx5_2,mlx5_3
export NCCL_SOCKET_IFNAME=ib0,ib1,ib2,ib3

# OpenMPI with multiple rails
mpirun --mca btl_openib_if_include mlx5_0,mlx5_1 \
       ./application
```

## Conclusion

Achieving high performance in HPC requires attention to many details:

1. **Understand scaling**: Know when to use strong vs weak scaling
2. **Balance load**: Use appropriate load balancing strategies
3. **Manage memory**: Be aware of hierarchy and NUMA effects
4. **Profile regularly**: Measure before optimizing
5. **Avoid common pitfalls**: Synchronization, false sharing, small messages
6. **Utilize resources**: CPU, GPU, network - all matter
7. **Think holistically**: Co-design algorithm and implementation
8. **Test at scale**: Performance characteristics change with scale

By following these best practices and continuously measuring and optimizing, you can achieve excellent performance and scalability in your HPC applications. Remember that optimization is an iterative process - profile, identify bottlenecks, optimize, and repeat.
