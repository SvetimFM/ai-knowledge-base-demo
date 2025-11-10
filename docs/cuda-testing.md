# CUDA Testing Methodologies and Frameworks

## Introduction

Testing CUDA applications presents unique challenges due to the parallel nature of GPU execution, asynchronous operations, and the complexity of device memory management. This guide covers comprehensive testing strategies, frameworks, and best practices for ensuring correctness and performance of CUDA applications.

## Unit Testing Strategies for CUDA Kernels

### Challenges in CUDA Testing

1. **Asynchronous Execution**: Kernels execute asynchronously relative to host code
2. **Memory Management**: Separate device and host memory spaces
3. **Race Conditions**: Potential for data races in parallel execution
4. **Non-determinism**: Thread scheduling may vary between runs
5. **Hardware Dependency**: Results may vary across GPU architectures
6. **Error Handling**: Errors may not surface immediately

### Testing Pyramid for CUDA

```
                  /\
                 /  \
               /  E2E \        End-to-End Tests (few)
              /--------\
             / Integr.  \      Integration Tests (some)
            /------------\
           /   Unit Tests \    Unit Tests (many)
          /----------------\
```

### Unit Test Structure

A well-structured CUDA unit test includes:

```cpp
#include <gtest/gtest.h>
#include <cuda_runtime.h>

// Kernel to test
__global__ void vectorAdd(const float* a, const float* b,
                          float* c, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        c[idx] = a[idx] + b[idx];
    }
}

TEST(VectorAddTest, BasicAddition) {
    // Setup
    const int n = 1024;
    const int size = n * sizeof(float);

    // Host memory allocation
    float* h_a = new float[n];
    float* h_b = new float[n];
    float* h_c = new float[n];

    // Initialize test data
    for (int i = 0; i < n; i++) {
        h_a[i] = static_cast<float>(i);
        h_b[i] = static_cast<float>(i * 2);
    }

    // Device memory allocation
    float *d_a, *d_b, *d_c;
    cudaMalloc(&d_a, size);
    cudaMalloc(&d_b, size);
    cudaMalloc(&d_c, size);

    // Copy input data to device
    cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);

    // Execute kernel
    int threadsPerBlock = 256;
    int blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock;
    vectorAdd<<<blocksPerGrid, threadsPerBlock>>>(d_a, d_b, d_c, n);

    // Check for kernel launch errors
    cudaError_t err = cudaGetLastError();
    ASSERT_EQ(err, cudaSuccess) << "Kernel launch failed: "
                                << cudaGetErrorString(err);

    // Wait for kernel to complete
    cudaDeviceSynchronize();

    // Copy result back to host
    cudaMemcpy(h_c, d_c, size, cudaMemcpyDeviceToHost);

    // Verify results
    for (int i = 0; i < n; i++) {
        EXPECT_FLOAT_EQ(h_c[i], h_a[i] + h_b[i])
            << "Mismatch at index " << i;
    }

    // Cleanup
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
    delete[] h_a;
    delete[] h_b;
    delete[] h_c;
}
```

### Testing Edge Cases

```cpp
TEST(VectorAddTest, EmptyVector) {
    const int n = 0;
    float *d_a, *d_b, *d_c;

    // Should handle zero-size gracefully
    vectorAdd<<<1, 1>>>(d_a, d_b, d_c, n);

    cudaError_t err = cudaGetLastError();
    EXPECT_EQ(err, cudaSuccess);
}

TEST(VectorAddTest, SingleElement) {
    const int n = 1;
    float h_a = 5.0f, h_b = 3.0f, h_c;
    float *d_a, *d_b, *d_c;

    cudaMalloc(&d_a, sizeof(float));
    cudaMalloc(&d_b, sizeof(float));
    cudaMalloc(&d_c, sizeof(float));

    cudaMemcpy(d_a, &h_a, sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, &h_b, sizeof(float), cudaMemcpyHostToDevice);

    vectorAdd<<<1, 1>>>(d_a, d_b, d_c, n);
    cudaDeviceSynchronize();

    cudaMemcpy(&h_c, d_c, sizeof(float), cudaMemcpyDeviceToHost);

    EXPECT_FLOAT_EQ(h_c, 8.0f);

    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
}

TEST(VectorAddTest, LargeVector) {
    const int n = 10000000;  // 10 million elements
    // Test large-scale performance and correctness
    // ... implementation
}

TEST(VectorAddTest, UnalignedAccess) {
    const int n = 1023;  // Non-power-of-2
    // Test handling of non-aligned memory access
    // ... implementation
}
```

### Floating-Point Comparison

```cpp
// Custom comparison for floating-point tests
bool almostEqual(float a, float b, float epsilon = 1e-5f) {
    return std::fabs(a - b) < epsilon;
}

TEST(MatrixMultiplyTest, NumericalAccuracy) {
    // ... setup and kernel execution

    for (int i = 0; i < n; i++) {
        EXPECT_TRUE(almostEqual(result[i], expected[i], 1e-4f))
            << "Values differ at index " << i
            << ": " << result[i] << " vs " << expected[i];
    }
}

// For more complex numerical validation
TEST(FFTTest, ParsevalsTheorem) {
    // Verify energy conservation in FFT
    float input_energy = 0.0f, output_energy = 0.0f;

    for (int i = 0; i < n; i++) {
        input_energy += input[i] * input[i];
    }

    // After FFT
    for (int i = 0; i < n; i++) {
        output_energy += output[i].real() * output[i].real() +
                        output[i].imag() * output[i].imag();
    }

    EXPECT_NEAR(input_energy, output_energy / n, 1e-3f);
}
```

## Validation Frameworks and Tools

### Google Test for CUDA

Google Test is the most widely used C++ testing framework and works well with CUDA:

**Setup** (CMakeLists.txt):
```cmake
cmake_minimum_required(VERSION 3.18)
project(CUDATests CUDA CXX)

enable_testing()
find_package(GTest REQUIRED)
find_package(CUDA REQUIRED)

include_directories(${GTEST_INCLUDE_DIRS})

# Add CUDA test executable
add_executable(cuda_tests
    test_vector_add.cu
    test_matrix_multiply.cu
    test_reduction.cu
)

set_target_properties(cuda_tests PROPERTIES
    CUDA_SEPARABLE_COMPILATION ON
    CUDA_ARCHITECTURES "70;75;80;86"
)

target_link_libraries(cuda_tests
    ${GTEST_LIBRARIES}
    pthread
)

# Register tests
gtest_discover_tests(cuda_tests)
```

**Running Tests**:
```bash
mkdir build && cd build
cmake ..
make
ctest --verbose

# Or run directly
./cuda_tests --gtest_filter=VectorAddTest.*
```

### CUDA-Memcheck

CUDA-Memcheck detects memory access errors and race conditions:

```bash
# Run with memory checker
cuda-memcheck ./cuda_tests

# Check for race conditions
cuda-memcheck --tool racecheck ./cuda_tests

# Check for initialization errors
cuda-memcheck --tool initcheck ./cuda_tests

# Check for synchronization issues
cuda-memcheck --tool synccheck ./cuda_tests
```

**Example Output**:
```
========= CUDA-MEMCHECK
========= Invalid __global__ write of size 4
=========     at 0x00000148 in vectorAdd
=========     by thread (1023,0,0) in block (0,0,0)
=========     Address 0x7f8a34000000 is out of bounds
=========
```

### Compute Sanitizer

Modern replacement for cuda-memcheck (CUDA 11.3+):

```bash
# Memory check
compute-sanitizer --tool memcheck ./cuda_tests

# Race detection
compute-sanitizer --tool racecheck ./cuda_tests

# Initialization check
compute-sanitizer --tool initcheck ./cuda_tests

# Synchronization check
compute-sanitizer --tool synccheck ./cuda_tests
```

### NVIDIA Nsight Compute

Command-line profiling and testing:

```bash
# Profile specific kernel
ncu --kernel-name vectorAdd ./cuda_tests

# Check for performance issues
ncu --set full --import-source yes ./cuda_tests

# Generate report
ncu --export report ./cuda_tests
ncu --import report.ncu-rep
```

### Custom Test Harness

```cpp
// test_harness.h
#ifndef TEST_HARNESS_H
#define TEST_HARNESS_H

#include <cuda_runtime.h>
#include <iostream>
#include <string>

class CUDATestHarness {
public:
    CUDATestHarness(const std::string& name) : test_name(name) {
        cudaGetDevice(&device);
        cudaGetDeviceProperties(&prop, device);
        std::cout << "Running " << test_name
                  << " on " << prop.name << std::endl;
    }

    ~CUDATestHarness() {
        // Ensure all operations complete
        cudaDeviceSynchronize();

        // Check for any errors
        cudaError_t err = cudaGetLastError();
        if (err != cudaSuccess) {
            std::cerr << "CUDA error in " << test_name << ": "
                      << cudaGetErrorString(err) << std::endl;
        }
    }

    template<typename T>
    T* allocateDevice(size_t count) {
        T* ptr;
        cudaError_t err = cudaMalloc(&ptr, count * sizeof(T));
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaMalloc failed");
        }
        allocated_ptrs.push_back(ptr);
        return ptr;
    }

    template<typename T>
    T* allocateHost(size_t count) {
        T* ptr;
        cudaError_t err = cudaMallocHost(&ptr, count * sizeof(T));
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaMallocHost failed");
        }
        host_ptrs.push_back(ptr);
        return ptr;
    }

    void cleanup() {
        for (void* ptr : allocated_ptrs) {
            cudaFree(ptr);
        }
        for (void* ptr : host_ptrs) {
            cudaFreeHost(ptr);
        }
        allocated_ptrs.clear();
        host_ptrs.clear();
    }

private:
    std::string test_name;
    int device;
    cudaDeviceProp prop;
    std::vector<void*> allocated_ptrs;
    std::vector<void*> host_ptrs;
};

#endif
```

## Performance Benchmarking Approaches

### Timing CUDA Operations

```cpp
// Using CUDA events for accurate timing
cudaEvent_t start, stop;
cudaEventCreate(&start);
cudaEventCreate(&stop);

cudaEventRecord(start);

// Launch kernel
myKernel<<<gridSize, blockSize>>>(args);

cudaEventRecord(stop);
cudaEventSynchronize(stop);

float milliseconds = 0;
cudaEventElapsedTime(&milliseconds, start, stop);

std::cout << "Kernel execution time: " << milliseconds << " ms" << std::endl;

cudaEventDestroy(start);
cudaEventDestroy(stop);
```

### Benchmark Framework Integration

```cpp
#include <benchmark/benchmark.h>

static void BM_VectorAdd(benchmark::State& state) {
    int n = state.range(0);
    int size = n * sizeof(float);

    float *d_a, *d_b, *d_c;
    cudaMalloc(&d_a, size);
    cudaMalloc(&d_b, size);
    cudaMalloc(&d_c, size);

    int threadsPerBlock = 256;
    int blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock;

    for (auto _ : state) {
        vectorAdd<<<blocksPerGrid, threadsPerBlock>>>(d_a, d_b, d_c, n);
        cudaDeviceSynchronize();
    }

    state.SetItemsProcessed(state.iterations() * n);
    state.SetBytesProcessed(state.iterations() * n * 3 * sizeof(float));

    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
}

BENCHMARK(BM_VectorAdd)
    ->Arg(1024)
    ->Arg(1024 * 1024)
    ->Arg(1024 * 1024 * 10)
    ->Unit(benchmark::kMillisecond);

BENCHMARK_MAIN();
```

### Performance Metrics

```cpp
struct PerformanceMetrics {
    float execution_time_ms;
    float bandwidth_gb_s;
    float gflops;
    size_t memory_used_bytes;
    float occupancy_percent;

    void print() const {
        std::cout << "Performance Metrics:\n"
                  << "  Execution Time: " << execution_time_ms << " ms\n"
                  << "  Bandwidth: " << bandwidth_gb_s << " GB/s\n"
                  << "  GFLOPS: " << gflops << "\n"
                  << "  Memory Used: " << memory_used_bytes / (1024*1024) << " MB\n"
                  << "  Occupancy: " << occupancy_percent << "%\n";
    }
};

PerformanceMetrics measureKernelPerformance(
    void (*kernel)(float*, float*, float*, int),
    int n, int threadsPerBlock) {

    PerformanceMetrics metrics;

    // Measure execution time
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    float *d_a, *d_b, *d_c;
    size_t size = n * sizeof(float);
    cudaMalloc(&d_a, size);
    cudaMalloc(&d_b, size);
    cudaMalloc(&d_c, size);

    metrics.memory_used_bytes = size * 3;

    int blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock;

    cudaEventRecord(start);
    kernel<<<blocksPerGrid, threadsPerBlock>>>(d_a, d_b, d_c, n);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    cudaEventElapsedTime(&metrics.execution_time_ms, start, stop);

    // Calculate bandwidth (3 arrays: 2 reads, 1 write)
    float bytes_transferred = size * 3;
    metrics.bandwidth_gb_s = bytes_transferred /
                            (metrics.execution_time_ms * 1e6);

    // Calculate GFLOPS (1 FLOP per element)
    metrics.gflops = (n / (metrics.execution_time_ms * 1e6));

    // Calculate occupancy
    cudaOccupancyMaxActiveBlocksPerMultiprocessor(
        &blocksPerGrid, kernel, threadsPerBlock, 0);

    int device;
    cudaGetDevice(&device);
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, device);

    int maxThreadsPerSM = prop.maxThreadsPerMultiProcessor;
    int activeThreadsPerSM = blocksPerGrid * threadsPerBlock;
    metrics.occupancy_percent = 100.0f * activeThreadsPerSM / maxThreadsPerSM;

    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
    cudaEventDestroy(start);
    cudaEventDestroy(stop);

    return metrics;
}
```

## Debugging CUDA Applications

### Printf Debugging

```cpp
__global__ void debugKernel(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    // Print from specific thread
    if (idx == 0) {
        printf("Block (%d,%d,%d), Thread (%d,%d,%d)\n",
               blockIdx.x, blockIdx.y, blockIdx.z,
               threadIdx.x, threadIdx.y, threadIdx.z);
    }

    if (idx < n) {
        // Conditional debugging
        if (data[idx] < 0) {
            printf("Warning: Negative value %f at index %d\n",
                   data[idx], idx);
        }
    }
}
```

### Assertion in Kernels

```cpp
__global__ void assertKernel(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    if (idx < n) {
        // Assert condition
        assert(data[idx] >= 0.0f && "Data must be non-negative");
        assert(idx < n && "Index out of bounds");
    }
}

// Enable device-side assertions
// Compile with: nvcc -G -g kernel.cu
```

### NVIDIA Nsight Debugger

```bash
# Debug with nsight
cuda-gdb ./cuda_application

# Set breakpoint in kernel
(cuda-gdb) break vectorAdd

# Run until breakpoint
(cuda-gdb) run

# Examine thread state
(cuda-gdb) info cuda threads
(cuda-gdb) cuda thread 0
(cuda-gdb) print idx
(cuda-gdb) print data[idx]

# Step through kernel
(cuda-gdb) next
```

### Error Checking Macros

```cpp
#define CUDA_CHECK(call) \
do { \
    cudaError_t error = call; \
    if (error != cudaSuccess) { \
        fprintf(stderr, "CUDA error at %s:%d: %s\n", \
                __FILE__, __LINE__, cudaGetErrorString(error)); \
        exit(EXIT_FAILURE); \
    } \
} while(0)

#define CUDA_CHECK_KERNEL() \
do { \
    cudaError_t error = cudaGetLastError(); \
    if (error != cudaSuccess) { \
        fprintf(stderr, "CUDA kernel launch error at %s:%d: %s\n", \
                __FILE__, __LINE__, cudaGetErrorString(error)); \
        exit(EXIT_FAILURE); \
    } \
    error = cudaDeviceSynchronize(); \
    if (error != cudaSuccess) { \
        fprintf(stderr, "CUDA kernel execution error at %s:%d: %s\n", \
                __FILE__, __LINE__, cudaGetErrorString(error)); \
        exit(EXIT_FAILURE); \
    } \
} while(0)

// Usage
CUDA_CHECK(cudaMalloc(&d_data, size));
myKernel<<<grid, block>>>(d_data);
CUDA_CHECK_KERNEL();
```

## Common Testing Patterns and Anti-Patterns

### Good Patterns

#### 1. Fixture Classes for Setup/Teardown

```cpp
class CUDATest : public ::testing::Test {
protected:
    void SetUp() override {
        cudaGetDevice(&device);
        cudaGetDeviceProperties(&prop, device);

        // Allocate common resources
        cudaMalloc(&d_buffer, BUFFER_SIZE);
    }

    void TearDown() override {
        cudaFree(d_buffer);
        cudaDeviceReset();
    }

    int device;
    cudaDeviceProp prop;
    void* d_buffer;
    static constexpr size_t BUFFER_SIZE = 1024 * 1024;
};

TEST_F(CUDATest, TestWithFixture) {
    // d_buffer is already allocated
    // Use fixture resources
}
```

#### 2. Parameterized Tests

```cpp
class VectorSizeTest : public ::testing::TestWithParam<int> {};

TEST_P(VectorSizeTest, VectorAddDifferentSizes) {
    int n = GetParam();
    // Test with different vector sizes
}

INSTANTIATE_TEST_SUITE_P(
    VectorSizes,
    VectorSizeTest,
    ::testing::Values(1, 10, 100, 1000, 10000, 1000000)
);
```

#### 3. Reference Implementation Comparison

```cpp
void referenceCPU(const float* a, const float* b, float* c, int n) {
    for (int i = 0; i < n; i++) {
        c[i] = a[i] + b[i];
    }
}

TEST(CorrectnessTest, CompareWithReference) {
    // Run GPU version
    // Run CPU reference
    // Compare results

    for (int i = 0; i < n; i++) {
        EXPECT_FLOAT_EQ(gpu_result[i], cpu_result[i]);
    }
}
```

### Anti-Patterns to Avoid

#### 1. Not Checking Errors

```cpp
// BAD: No error checking
cudaMalloc(&d_data, size);
kernel<<<grid, block>>>(d_data);
cudaMemcpy(h_data, d_data, size, cudaMemcpyDeviceToHost);

// GOOD: Check every call
CUDA_CHECK(cudaMalloc(&d_data, size));
kernel<<<grid, block>>>(d_data);
CUDA_CHECK_KERNEL();
CUDA_CHECK(cudaMemcpy(h_data, d_data, size, cudaMemcpyDeviceToHost));
```

#### 2. Forgetting to Synchronize

```cpp
// BAD: No synchronization
kernel<<<grid, block>>>(d_data);
cudaMemcpy(h_data, d_data, size, cudaMemcpyDeviceToHost);
// May copy before kernel completes!

// GOOD: Synchronize or use blocking operations
kernel<<<grid, block>>>(d_data);
cudaDeviceSynchronize();
cudaMemcpy(h_data, d_data, size, cudaMemcpyDeviceToHost);
```

#### 3. Memory Leaks in Tests

```cpp
// BAD: Resource leaks
TEST(BadTest, LeaksMemory) {
    float* d_data;
    cudaMalloc(&d_data, size);
    // Test logic
    // FORGOT TO FREE!
}

// GOOD: RAII or explicit cleanup
TEST(GoodTest, NoLeaks) {
    float* d_data;
    cudaMalloc(&d_data, size);

    // Test logic

    cudaFree(d_data);  // Always cleanup
}
```

#### 4. Testing Too Many Things at Once

```cpp
// BAD: Complex test with multiple responsibilities
TEST(BadTest, DoesEverything) {
    // Tests allocation, kernel, memory transfer, math, etc.
    // Hard to debug which part failed
}

// GOOD: Separate focused tests
TEST(AllocationTest, AllocatesCorrectly) { /* ... */ }
TEST(KernelTest, ComputesCorrectly) { /* ... */ }
TEST(TransferTest, CopiesCorrectly) { /* ... */ }
```

## CI/CD Integration for CUDA Tests

### GitHub Actions Example

```yaml
name: CUDA Tests

on: [push, pull_request]

jobs:
  cuda-tests:
    runs-on: ubuntu-latest
    container:
      image: nvidia/cuda:12.0.0-devel-ubuntu22.04

    steps:
    - uses: actions/checkout@v3

    - name: Install dependencies
      run: |
        apt-get update
        apt-get install -y cmake libgtest-dev

    - name: Build tests
      run: |
        mkdir build && cd build
        cmake ..
        make -j$(nproc)

    - name: Run tests
      run: |
        cd build
        ./cuda_tests --gtest_output=xml:test_results.xml

    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: build/test_results.xml
```

### GitLab CI Example

```yaml
stages:
  - build
  - test

cuda-build:
  stage: build
  image: nvidia/cuda:12.0.0-devel-ubuntu22.04
  script:
    - mkdir build && cd build
    - cmake ..
    - make -j$(nproc)
  artifacts:
    paths:
      - build/

cuda-test:
  stage: test
  image: nvidia/cuda:12.0.0-runtime-ubuntu22.04
  dependencies:
    - cuda-build
  script:
    - cd build
    - ./cuda_tests
  tags:
    - gpu
```

### Docker Testing Environment

```dockerfile
FROM nvidia/cuda:12.0.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgtest-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN mkdir build && cd build && cmake .. && make

CMD ["./build/cuda_tests"]
```

## Conclusion

Comprehensive testing of CUDA applications requires a multi-layered approach combining unit tests, integration tests, performance benchmarks, and debugging tools. Key takeaways:

1. **Use established frameworks**: Google Test, Google Benchmark
2. **Check every CUDA operation**: Never skip error checking
3. **Validate with reference implementations**: CPU versions for correctness
4. **Profile before optimizing**: Use nsight tools to identify bottlenecks
5. **Test edge cases**: Empty inputs, single elements, large datasets
6. **Automate testing**: Integrate with CI/CD pipelines
7. **Use appropriate tools**: Compute Sanitizer for memory errors, debuggers for logic
8. **Separate concerns**: Unit test kernels independently from integration

By following these methodologies and leveraging the available frameworks and tools, you can ensure your CUDA applications are correct, performant, and maintainable.
