# HPC Communication Patterns and Collective Operations

## Introduction

Communication patterns are fundamental building blocks of parallel and distributed computing in HPC (High-Performance Computing) environments. Understanding these patterns, their performance characteristics, and optimal use cases is crucial for designing efficient parallel algorithms and achieving scalability across multiple processors, nodes, and accelerators.

## Point-to-Point Communication

### Overview

Point-to-point communication involves data transfer between two specific processes or ranks. These are the most basic communication primitives in distributed computing.

### Blocking Send/Receive

**Characteristics**:
- Sender blocks until message is sent (or buffered)
- Receiver blocks until message is received
- Guarantees completion before proceeding

**MPI Example**:
```cpp
// Rank 0 sends to Rank 1
int data = 42;
if (rank == 0) {
    MPI_Send(&data, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
}
else if (rank == 1) {
    MPI_Recv(&data, 1, MPI_INT, 0, 0, MPI_COMM_WORLD,
             MPI_STATUS_IGNORE);
}
```

**Use Cases**:
- Simple producer-consumer patterns
- Master-worker task distribution
- Pipeline stages with clear dependencies

**Pitfalls**:
- Can cause deadlocks if not carefully ordered
- May lead to idle time while waiting

### Non-Blocking Send/Receive

**Characteristics**:
- Returns immediately, allowing computation to continue
- Requires explicit wait/test for completion
- Enables overlap of communication and computation

**MPI Example**:
```cpp
MPI_Request request;
MPI_Status status;

if (rank == 0) {
    MPI_Isend(&data, count, MPI_FLOAT, 1, 0,
              MPI_COMM_WORLD, &request);
    // Do other work while sending
    doComputation();
    MPI_Wait(&request, &status);
}
else if (rank == 1) {
    MPI_Irecv(&data, count, MPI_FLOAT, 0, 0,
              MPI_COMM_WORLD, &request);
    // Do other work while receiving
    doComputation();
    MPI_Wait(&request, &status);
}
```

**Use Cases**:
- Overlapping communication with computation
- Multiple simultaneous communications
- Implementing custom collective operations

### Send Modes

| Mode | MPI Function | Behavior |
|------|-------------|----------|
| Standard | MPI_Send | May buffer or synchronize |
| Buffered | MPI_Bsend | Uses user-provided buffer |
| Synchronous | MPI_Ssend | Completes only when receive starts |
| Ready | MPI_Rsend | Requires matching receive already posted |

### Deadlock Avoidance

**Problem Example**:
```cpp
// DEADLOCK: Both ranks waiting to send
if (rank == 0) {
    MPI_Send(sendbuf, count, MPI_INT, 1, 0, MPI_COMM_WORLD);
    MPI_Recv(recvbuf, count, MPI_INT, 1, 0, MPI_COMM_WORLD,
             MPI_STATUS_IGNORE);
}
else if (rank == 1) {
    MPI_Send(sendbuf, count, MPI_INT, 0, 0, MPI_COMM_WORLD);
    MPI_Recv(recvbuf, count, MPI_INT, 0, 0, MPI_COMM_WORLD,
             MPI_STATUS_IGNORE);
}
```

**Solution 1: Reorder operations**:
```cpp
if (rank == 0) {
    MPI_Send(sendbuf, count, MPI_INT, 1, 0, MPI_COMM_WORLD);
    MPI_Recv(recvbuf, count, MPI_INT, 1, 0, MPI_COMM_WORLD,
             MPI_STATUS_IGNORE);
}
else if (rank == 1) {
    MPI_Recv(recvbuf, count, MPI_INT, 0, 0, MPI_COMM_WORLD,
             MPI_STATUS_IGNORE);
    MPI_Send(sendbuf, count, MPI_INT, 0, 0, MPI_COMM_WORLD);
}
```

**Solution 2: Use non-blocking**:
```cpp
MPI_Request requests[2];

MPI_Isend(sendbuf, count, MPI_INT, other_rank, 0,
          MPI_COMM_WORLD, &requests[0]);
MPI_Irecv(recvbuf, count, MPI_INT, other_rank, 0,
          MPI_COMM_WORLD, &requests[1]);

MPI_Waitall(2, requests, MPI_STATUSES_IGNORE);
```

**Solution 3: Use Sendrecv**:
```cpp
MPI_Sendrecv(sendbuf, count, MPI_INT, other_rank, 0,
             recvbuf, count, MPI_INT, other_rank, 0,
             MPI_COMM_WORLD, MPI_STATUS_IGNORE);
```

## Collective Communication Patterns

### AllReduce

**Operation**: Every process contributes data, reduction is performed, and all processes receive the result.

**Visual Representation**:
```
Before:  P0: [1]    P1: [2]    P2: [3]    P3: [4]
After:   P0: [10]   P1: [10]   P2: [10]   P3: [10]  (Sum)
```

**MPI Implementation**:
```cpp
float local_sum = computeLocalSum(data);
float global_sum;

MPI_Allreduce(&local_sum, &global_sum, 1, MPI_FLOAT,
              MPI_SUM, MPI_COMM_WORLD);

// All ranks now have global_sum
```

**Reduction Operations**:
- `MPI_SUM`: Addition
- `MPI_PROD`: Multiplication
- `MPI_MAX`: Maximum value
- `MPI_MIN`: Minimum value
- `MPI_MAXLOC`: Maximum and its location
- `MPI_MINLOC`: Minimum and its location
- `MPI_LAND`: Logical AND
- `MPI_LOR`: Logical OR

**Performance**:
- **Complexity**: O(log N) latency, O(N) bandwidth
- **Optimized implementations**: Ring, recursive doubling, rabenseifner
- **Message size matters**: Small messages use tree, large use ring

**Use Cases**:
- Computing global sums, averages, norms
- Finding global maximum/minimum
- Synchronizing convergence criteria
- Distributed gradient averaging (deep learning)

**Example - Convergence Check**:
```cpp
bool local_converged = checkLocalConvergence();
bool global_converged;

MPI_Allreduce(&local_converged, &global_converged, 1,
              MPI_C_BOOL, MPI_LAND, MPI_COMM_WORLD);

if (global_converged) {
    // All processes have converged
    break;
}
```

### Broadcast

**Operation**: One process (root) sends identical data to all other processes.

**Visual Representation**:
```
Before:  P0: [1,2,3]    P1: [?]    P2: [?]    P3: [?]
After:   P0: [1,2,3]    P1: [1,2,3]    P2: [1,2,3]    P3: [1,2,3]
```

**MPI Implementation**:
```cpp
float data[100];

if (rank == 0) {
    // Initialize data on root
    initializeData(data);
}

// Broadcast from root (rank 0) to all
MPI_Bcast(data, 100, MPI_FLOAT, 0, MPI_COMM_WORLD);

// All ranks now have the data
```

**Performance**:
- **Complexity**: O(log N) for both latency and bandwidth
- **Algorithm**: Typically uses binary tree
- **Optimization**: Pipelined for large messages

**Use Cases**:
- Broadcasting input parameters
- Distributing model weights
- Sharing configuration data
- Synchronizing random seeds

**Example - Parameter Broadcasting**:
```cpp
struct SimulationParams {
    double dt;
    int max_iterations;
    double tolerance;
};

SimulationParams params;

if (rank == 0) {
    // Read from file or command line
    params = readParameters();
}

// Broadcast to all processes
MPI_Bcast(&params, sizeof(SimulationParams), MPI_BYTE, 0,
          MPI_COMM_WORLD);
```

### Reduce

**Operation**: All processes contribute data, reduction is performed, and only root receives the result.

**Visual Representation**:
```
Before:  P0: [1]    P1: [2]    P2: [3]    P3: [4]
After:   P0: [10]   P1: [2]    P2: [3]    P3: [4]  (Only P0 has sum)
```

**MPI Implementation**:
```cpp
float local_result = computeLocalResult();
float global_result;

MPI_Reduce(&local_result, &global_result, 1, MPI_FLOAT,
           MPI_SUM, 0, MPI_COMM_WORLD);

if (rank == 0) {
    // Only root has global_result
    printf("Global result: %f\n", global_result);
}
```

**Performance**:
- **Complexity**: O(log N) latency
- **Algorithm**: Binary tree reduction
- **Bandwidth**: Only root receives full data

**Use Cases**:
- Collecting statistics to master process
- Aggregating results for output
- Computing total energy, error norms
- Performance metric collection

**Relationship to AllReduce**:
```
AllReduce = Reduce + Broadcast
```

### Scatter

**Operation**: Root process distributes different portions of data to all processes.

**Visual Representation**:
```
Before:  P0: [A,B,C,D]    P1: [?]    P2: [?]    P3: [?]
After:   P0: [A]          P1: [B]    P2: [C]    P3: [D]
```

**MPI Implementation**:
```cpp
float* sendbuf;  // Only meaningful on root
float recvbuf[100];

if (rank == 0) {
    sendbuf = new float[nprocs * 100];
    // Initialize data to distribute
    initializeData(sendbuf);
}

MPI_Scatter(sendbuf, 100, MPI_FLOAT,
            recvbuf, 100, MPI_FLOAT,
            0, MPI_COMM_WORLD);

// Each process now has its portion
processLocalData(recvbuf);

if (rank == 0) delete[] sendbuf;
```

**Performance**:
- **Complexity**: O(N) for both latency and bandwidth
- **Total data sent**: N elements distributed
- **Bandwidth intensive**: Root must send to all

**Use Cases**:
- Distributing work items
- Partitioning arrays for parallel processing
- Load distribution in data parallelism
- Initializing distributed data structures

### Gather

**Operation**: Root process collects data from all processes.

**Visual Representation**:
```
Before:  P0: [A]    P1: [B]    P2: [C]    P3: [D]
After:   P0: [A,B,C,D]    P1: [B]    P2: [C]    P3: [D]
```

**MPI Implementation**:
```cpp
float sendbuf[100];
float* recvbuf;

// Each process has local data
computeLocalData(sendbuf);

if (rank == 0) {
    recvbuf = new float[nprocs * 100];
}

MPI_Gather(sendbuf, 100, MPI_FLOAT,
           recvbuf, 100, MPI_FLOAT,
           0, MPI_COMM_WORLD);

if (rank == 0) {
    // Process collected data
    processGatheredData(recvbuf);
    delete[] recvbuf;
}
```

**Performance**:
- **Complexity**: O(N) bandwidth
- **Inverse of Scatter**: Same performance characteristics
- **Bottleneck**: Root must receive from all

**Use Cases**:
- Collecting results for output
- Assembling distributed data
- Gathering performance metrics
- Centralized post-processing

### AllGather

**Operation**: Every process collects data from all processes.

**Visual Representation**:
```
Before:  P0: [A]    P1: [B]    P2: [C]    P3: [D]
After:   P0: [A,B,C,D]    P1: [A,B,C,D]    P2: [A,B,C,D]    P3: [A,B,C,D]
```

**MPI Implementation**:
```cpp
float sendbuf[100];
float recvbuf[nprocs * 100];

// Each process has local data
computeLocalData(sendbuf);

MPI_Allgather(sendbuf, 100, MPI_FLOAT,
              recvbuf, 100, MPI_FLOAT,
              MPI_COMM_WORLD);

// All processes now have all data
processCompleteData(recvbuf);
```

**Performance**:
- **Complexity**: O(N * nprocs) total data movement
- **Algorithm**: Recursive doubling or ring
- **Expensive**: Every process receives N * nprocs data

**Use Cases**:
- Particle methods needing global view
- Global state synchronization
- Distributed hash table updates
- Consensus algorithms

**Relationship**:
```
AllGather = Gather + Broadcast
```

### ReduceScatter

**Operation**: Reduction is performed and different portions of the result are distributed to processes.

**Visual Representation**:
```
Before:  P0: [1,2,3,4]    P1: [5,6,7,8]    P2: [9,10,11,12]
Reduce:  [15,18,21,24]  (element-wise sum)
After:   P0: [15]    P1: [18]    P2: [21]    P3: [24]
```

**MPI Implementation**:
```cpp
float sendbuf[total_size];
float recvbuf[local_size];

// Initialize send buffer
initializeData(sendbuf);

int recvcounts[nprocs];
for (int i = 0; i < nprocs; i++) {
    recvcounts[i] = local_size;
}

MPI_Reduce_scatter(sendbuf, recvbuf, recvcounts, MPI_FLOAT,
                   MPI_SUM, MPI_COMM_WORLD);

// Each process has its portion of reduced data
```

**Performance**:
- **Complexity**: Similar to AllReduce
- **Efficient**: Combines reduction and distribution
- **Bandwidth optimal**: Data scattered during reduction

**Use Cases**:
- Distributed matrix operations
- Sharded optimizer updates (ZeRO)
- Parallel FFT algorithms
- Distributed gradient computation

**Relationship**:
```
AllReduce = ReduceScatter + AllGather
ReduceScatter = Reduce + Scatter
```

### AllToAll

**Operation**: Each process sends different data to every other process (complete exchange).

**Visual Representation**:
```
Before:  P0: [A0,A1,A2,A3]    P1: [B0,B1,B2,B3]    P2: [C0,C1,C2,C3]
After:   P0: [A0,B0,C0]       P1: [A1,B1,C1]       P2: [A2,B2,C2]
         (column 0)            (column 1)            (column 2)
```

**MPI Implementation**:
```cpp
float sendbuf[nprocs * chunk_size];
float recvbuf[nprocs * chunk_size];

// Prepare data for each destination
for (int i = 0; i < nprocs; i++) {
    prepareDataForRank(&sendbuf[i * chunk_size], i);
}

MPI_Alltoall(sendbuf, chunk_size, MPI_FLOAT,
             recvbuf, chunk_size, MPI_FLOAT,
             MPI_COMM_WORLD);

// Process received data from all ranks
```

**Performance**:
- **Complexity**: O(N * nprocs) most expensive collective
- **Bandwidth**: All-to-all bisection bandwidth limited
- **Scalability**: Challenging at large scale

**Use Cases**:
- Matrix transpose in distributed algorithms
- FFT transpose phases
- Particle redistribution
- Graph algorithms (vertex redistribution)

**Optimizations**:
- Use `MPI_Alltoallv` for variable-size messages
- Consider sparse communication patterns
- Implement staged communication for large systems

## Blocking vs Non-Blocking Communication

### Blocking Collectives

**Characteristics**:
- Simple to use and understand
- Synchronization point
- Ensures completion before returning
- May lead to idle time

**Example**:
```cpp
// Blocking AllReduce
MPI_Allreduce(&sendbuf, &recvbuf, count, MPI_FLOAT,
              MPI_SUM, MPI_COMM_WORLD);

// Guaranteed to be complete here
processResult(recvbuf);
```

### Non-Blocking Collectives (MPI 3.0+)

**Characteristics**:
- Prefix `I` (e.g., `MPI_Iallreduce`)
- Returns immediately with request handle
- Enables overlap with computation
- Requires explicit wait for completion

**Example**:
```cpp
MPI_Request request;

// Start non-blocking AllReduce
MPI_Iallreduce(&sendbuf, &recvbuf, count, MPI_FLOAT,
               MPI_SUM, MPI_COMM_WORLD, &request);

// Do independent computation while communicating
doIndependentWork();

// Wait for communication to complete
MPI_Wait(&request, MPI_STATUS_IGNORE);

// Now safe to use recvbuf
processResult(recvbuf);
```

**Comparison**:

| Aspect | Blocking | Non-Blocking |
|--------|----------|--------------|
| Simplicity | Simple | More complex |
| Overlap potential | None | High |
| Resource usage | Lower | Higher (buffers) |
| Performance | Good for sync | Better for async |
| Error handling | Immediate | Deferred to wait |

## Communication Scheduling and Overlap

### Computation-Communication Overlap

**Pattern 1: Double Buffering**:
```cpp
float buffer[2][SIZE];
MPI_Request requests[2];
int current = 0;

// Start first communication
MPI_Iallreduce(buffer[current], buffer[current], SIZE,
               MPI_FLOAT, MPI_SUM, comm, &requests[current]);

for (int iter = 1; iter < max_iters; iter++) {
    int next = 1 - current;

    // Compute next iteration while previous communicates
    compute(buffer[next]);

    // Start communication for next iteration
    MPI_Iallreduce(buffer[next], buffer[next], SIZE,
                   MPI_FLOAT, MPI_SUM, comm, &requests[next]);

    // Wait for previous communication
    MPI_Wait(&requests[current], MPI_STATUS_IGNORE);

    // Use previous result
    processResult(buffer[current]);

    current = next;
}
```

**Pattern 2: Pipelined Communication**:
```cpp
const int num_chunks = 4;
MPI_Request requests[num_chunks];

// Start all communications
for (int i = 0; i < num_chunks; i++) {
    MPI_Isend(&data[i * chunk_size], chunk_size, MPI_FLOAT,
              dest, tag, comm, &requests[i]);
}

// Do computation while communicating
doComputation();

// Wait for all to complete
MPI_Waitall(num_chunks, requests, MPI_STATUSES_IGNORE);
```

**Pattern 3: Progressive Communication**:
```cpp
// Communicate ready chunks progressively
for (int chunk = 0; chunk < num_chunks; chunk++) {
    // Compute chunk
    computeChunk(data, chunk);

    // Immediately start sending
    MPI_Isend(&data[chunk * chunk_size], chunk_size,
              MPI_FLOAT, dest, chunk, comm, &requests[chunk]);
}

// Continue with other work
doOtherWork();

// Wait for all sends to complete
MPI_Waitall(num_chunks, requests, MPI_STATUSES_IGNORE);
```

### Communication Scheduling Strategies

**Strategy 1: Nearest Neighbor First**:
```cpp
// Prioritize local communication
// 1. Intra-node communication (shared memory)
// 2. Near neighbors (same rack)
// 3. Remote nodes

if (dest_rank_on_same_node) {
    // Fast path
    communicate_via_shared_memory();
} else {
    // Network path
    MPI_Send(...);
}
```

**Strategy 2: Batching Small Messages**:
```cpp
// Combine small messages into larger ones
struct Message {
    float data[MESSAGE_SIZE];
    int dest_rank;
};

std::vector<Message> pending_messages;

// Collect messages
for (/* each small message */) {
    pending_messages.push_back(message);
}

// Send batched
if (pending_messages.size() >= BATCH_SIZE) {
    MPI_Send(pending_messages.data(), ...);
    pending_messages.clear();
}
```

## Performance Characteristics

### Latency and Bandwidth

**Latency (α)**: Time to send zero-byte message
**Bandwidth (β)**: Rate of data transfer

**Communication Time Model**:
```
T_comm = α + n * β
```
where n is message size

**Small Messages**: Latency-dominated
- Use tree algorithms (O(log N) latency)
- Minimize number of messages
- Consider message aggregation

**Large Messages**: Bandwidth-dominated
- Use ring algorithms (optimal bandwidth)
- Pipeline when possible
- Maximize message size

### Scalability Considerations

**Strong Scaling**: Fixed problem size, increasing processors
- Communication overhead increases
- Communication-to-computation ratio grows
- Eventually hits scalability limit

**Weak Scaling**: Problem size grows with processors
- Maintains constant work per processor
- Better scalability potential
- Communication patterns matter more

**Efficiency Formula**:
```
Efficiency = T_serial / (P * T_parallel)
```

### Network Topology Impact

**Impact on Collectives**:

| Topology | Best For | Characteristics |
|----------|----------|-----------------|
| Fat-tree | AllReduce, Broadcast | Bisection bandwidth |
| Torus | Nearest neighbor | Regular structure |
| Dragonfly | Random patterns | High-radix routers |

## When to Use Which Pattern

### Decision Tree

```
Need to share data?
├─ Yes → Need all-to-all sharing?
│   ├─ Yes → Same data?
│   │   ├─ Yes → Use Broadcast
│   │   └─ No → Use AllGather
│   └─ No → Need computation on data?
│       ├─ Yes → All need result?
│       │   ├─ Yes → Use AllReduce
│       │   └─ No → Use Reduce
│       └─ No → Distribute different data?
│           ├─ Yes → Use Scatter
│           └─ No → Use Gather
└─ No → Point-to-point or custom pattern
```

### Pattern Selection Guide

**Use Broadcast when**:
- One process has data needed by all
- Configuration, parameters, small datasets
- Low overhead for moderate-sized data

**Use AllReduce when**:
- Computing global properties (sum, max, min)
- Synchronizing state across all processes
- Most common in iterative algorithms

**Use Scatter/Gather when**:
- Work distribution and result collection
- One process coordinates others
- Data parallelism patterns

**Use AllGather when**:
- All processes need complete global view
- Typically expensive, use sparingly
- Consider if truly necessary

**Use ReduceScatter when**:
- Distributing portions of a global reduction
- More efficient than Reduce + Scatter
- Common in linear algebra operations

**Use AllToAll when**:
- Complete data exchange required
- Matrix transpose, FFT
- Most expensive collective, optimize carefully

**Use Point-to-Point when**:
- Custom communication patterns
- Sparse communication
- Irregular patterns

## Conclusion

Understanding communication patterns and their performance characteristics is essential for efficient HPC application development. Key principles:

1. **Choose the right collective**: Use built-in collectives when possible
2. **Consider message size**: Small messages benefit from trees, large from rings
3. **Overlap when possible**: Non-blocking enables computation overlap
4. **Avoid unnecessary synchronization**: Use asynchronous operations
5. **Minimize communication volume**: Algorithm design is crucial
6. **Understand your topology**: Network characteristics affect performance
7. **Profile and measure**: Use tools to identify communication bottlenecks
8. **Think about scaling**: Design for both strong and weak scaling

By applying these principles and understanding the trade-offs of each communication pattern, you can design algorithms that scale efficiently to large processor counts and achieve high performance on modern HPC systems.
