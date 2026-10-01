# Active Defense Core - System Architecture & Security Model

## 1. Architectural Evolution: In-Place Zero-Allocation Primitive

The core engine was upgraded from a heap-allocated envelope structure to an **In-Place Zero-Allocation Security Primitive**.

### Core Primitive Signature
```c
AD_API int ad_encrypt_and_shred_inplace(
    uint8_t* buffer,
    size_t buffer_len,
    uint64_t* out_latency_us
);
```

## Design PrinciplesZero Dynamic Allocation ($O(1)$ Space Complexity): 

1. The core performs byte transformations directly inside caller-provided memory. No malloc, realloc, or free calls occur inside the critical hot path.
2. Determinism & Fragmentation Immunity: By removing OS heap interaction, execution latency remains deterministic (~19.9 ns) without garbage collection or heap fragmentation spikes.
3. Thread-Safe Hot Path: Each thread operates independently on its local buffer, removing thread locks, mutexes, and atomic contention bottlenecks.

## 2. Compiler Dead-Store Elimination Defenses

To prevent compilers from optimizing away sensitive memory zeroization (Dead-Store Elimination), the engine utilizes platform-native kernel primitives:

```c
/* Cross-Platform Compiler-Proof Zeroization */
#if defined(_WIN32) || defined(_WIN64)
    SecureZeroMemory(buffer, buffer_len);
#elif defined(__STDC_LIB_EXT1__)
    memset_s(buffer, buffer_len, 0, buffer_len);
#else
    explicit_bzero(buffer, buffer_len);
#endif
```

## 3. C-ABI & Cross-Language FFI BindingsThe static (.lib / .a) and dynamic shared (.dll / .so) targets expose a pure C-ABI interface.Native C/C++: Link via activedefense_static with #define AD_STATIC.Python / Foreign Function Interfaces (FFI): Bind via ctypes or cffi pointing to ad_encrypt_and_shred_inplace.