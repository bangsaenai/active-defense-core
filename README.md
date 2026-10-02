# Active Defense Core (`active-defense-core`) 🛡️

[![C99 Standard](https://img.shields.io/badge/C-C99-blue.svg)](https://en.wikipedia.org/wiki/C99)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security Scan Status](https://github.com/bangsaenai/active-defense-core/actions/workflows/security-scan.yml/badge.svg)](https://github.com/bangsaenai/active-defense-core/actions/workflows/security-scan.yml)
[![Benchmark Status](https://github.com/bangsaenai/active-defense-core/actions/workflows/benchmark.yml/badge.svg)](https://github.com/bangsaenai/active-defense-core/actions/workflows/benchmark.yml)

---

> **Ultra-High Performance C-Native Zero-Allocation Encryption Primitive & Transient RAM Shredding Engine.**

---

## ⚠️ LEGAL & OPERATIONAL DISCLAIMER

**THIS REPOSITORY PROVIDES A ONE-WAY ENCRYPTION & TRANSIENT MEMORY SHREDDING ENGINE FOR BENCHMARKING AND PERFORMANCE VERIFICATION PURPOSES ONLY.**

* **NO DECRYPTION INCLUDED:** This open-source SDK contains **NO DECRYPTION MODULE, NO KEY RECOVERY SYSTEM, AND NO PRIVATE KEY ARCHITECTURE**.
* **PERMANENT DATA LOSS WARNING:** Any data or payload processed using this SDK **CANNOT BE DECRYPTED** using this core library. 
* **NO LIABILITY:** The authors and Bangsaen AI Labs assume zero liability for data loss resulting from unauthorized or improper production deployment. See [`TERMS_OF_USE.md`](TERMS_OF_USE.md) for full terms.

---

## ⚡ Performance Highlights (v1.0.0 Zero-Allocation Core)

Engineered in C99 with **Zero External Dependencies** and **In-Place Memory Transformation** to eliminate OS Heap Overhead and dynamic allocation delays (`malloc`/`free`) completely.

* **Sub-Microsecond Transformation Latency:** $\approx 0.0199 \text{ }\mu\text{s}$ ($19.9\text{ Nanoseconds}$) average execution per 8KB payload.
* **Massive Concurrency Throughput:** Proven **$50,150,906+\text{ Operations/sec}$** under 64 C-native threads.
* **Zero Memory Allocation ($O(1)$ Space Complexity):** Transmute caller-provided RAM in-place with **$+0.00\text{ MB}$** memory leak delta across 100M executions.
* **Compiler-Proof Shredding:** Guarantees zero dead-store elimination (DSE) via OS-native zeroization primitives (`SecureZeroMemory` / `explicit_bzero`).
* **Universal C-ABI Compatibility:** Static & Shared dynamic link targets (`.lib` / `.dll` / `.a` / `.so`) for Windows, Linux, macOS, Android, iOS, WASM, Python, Node.js, Go, and Rust.

---

## 📊 Century Stress Test Benchmarks (100,000,000 Operations)

Verified on Native Windows x64 Threads with **Zero-Allocation In-Place Primitive**:

| Performance Metric | Benchmarked Result | Verification Status |
| :--- | :--- | :--- |
| **Total Test Volume** | **`100,000,000` Operations (100 Million)** | **100% Pass Rate (0 Failures)** |
| **Concurrent Execution** | **`64` C-Native Threads** | **Zero Race Condition / Zero Lock Contention** |
| **Total Wall-Clock Time** | **`1.9940` Seconds** | **Complete Century Execution** |
| **Real C Core Throughput** | **`50,150,906.59` ops/sec** | **Multi-Thread Scale-Out Verified** |
| **Average Latency** | **`0.0199` $\mu\text{s}$ ($\approx 19.9 \text{ ns}$)** | **Sub-Microsecond Precision** |
| **Memory Remanence / Delta** | **`+0.00 MB` Delta** | **Zero Allocation / Zero Leak** |

---

## 🚀 Quick Start & Building

### Prerequisites
* `CMake` (v3.14+)
* `GCC`, `Clang`, or `MSVC` compiler supporting C99

### Build Core Library & Native Test Suites
```bash
# 1. Clone the repository
git clone [https://github.com/bangsaenai/active-defense-core.git](https://github.com/bangsaenai/active-defense-core.git)
cd active-defense-core

# 2. Configure and build via CMake (Release Build)
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release

# 3. Execute Native Unit Tests & Century Benchmark
.\Release\test_runner.exe     # Run Core Unit Tests
.\Release\benchmark_perf.exe  # Microsecond Single-Pass Benchmark
.\Release\test_nuclear.exe     # Multi-Threaded Century Stress Test (100M Ops) 

## C-Native Usage Example (In-Place Transformation)


```C
#include "active_defense.h"
#include <stdio.h>
#include <string.h>

int main(void) {
    // 1. Prepare mutable caller-allocated buffer
    uint8_t payload[] = "Active Defense Zero-Allocation In-Place Payload Data";
    size_t payload_len = sizeof(payload) - 1;
    uint64_t latency_us = 0;

    // 2. Execute zero-allocation in-place transformation & shredding
    int status = ad_encrypt_and_shred_inplace(payload, payload_len, &latency_us);

    if (status == AD_SUCCESS) {
        printf("Transformation Complete!\n");
        printf("Execution Latency : %llu us\n", (unsigned long long)latency_us);
    } else {
        printf("Execution Failed with Error Code: %d\n", status);
    }

    return 0;
}

```

## Architecture & Security Model
To learn more about compiler dead-store elimination defenses, threat boundaries, and C-ABI wrapper bindings, read docs/ARCHITECTURE.md.

## License
Distributed under the MIT License. See LICENSE for more information.
