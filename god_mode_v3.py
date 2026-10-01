import ctypes
import os
import time
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. โหลด active_defense.dll
dll_path = os.path.abspath("./build/Release/active_defense.dll")
if not os.path.exists(dll_path):
    print(f"[X] Error: {dll_path} not found!")
    exit(1)

c_lib = ctypes.CDLL(dll_path)

# 2. Map C-ABI: int ad_encrypt_and_shred_inplace(uint8_t* buffer, size_t len, uint64_t* out_latency)
c_lib.ad_encrypt_and_shred_inplace.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_uint64)
]
c_lib.ad_encrypt_and_shred_inplace.restype = ctypes.c_int


# 3. Worker Function: Zero-Allocation In-Place Chaos Engine
def god_mode_worker_v3(thread_id, iterations):
    success_count = 0
    failures = 0
    latencies = []
    
    latency_metric = ctypes.c_uint64(0)

    # ⚡ Pre-allocate Mutable C-Arrays ประจำ Thread (Zero Allocation ใน Loop)
    buf_1k = (ctypes.c_uint8 * 1024).from_buffer_copy(b"A" * 1024)
    buf_64k = (ctypes.c_uint8 * (64 * 1024)).from_buffer_copy(b"B" * (64 * 1024))
    buf_256k = (ctypes.c_uint8 * (256 * 1024)).from_buffer_copy(b"C" * (256 * 1024))
    
    buffers = [
        (buf_1k, 1024),
        (buf_64k, 64 * 1024),
        (buf_256k, 256 * 1024)
    ]

    for i in range(iterations):
        c_buf, p_len = buffers[i % 3]
        
        t0 = time.perf_counter_ns()
        # ⚡ ยิงตรงเข้า C-Native In-Place Engine
        res = c_lib.ad_encrypt_and_shred_inplace(c_buf, p_len, ctypes.byref(latency_metric))
        t1 = time.perf_counter_ns()
        
        if res == 0:
            success_count += 1
            latencies.append((t1 - t0) / 1000.0) # แปลงเป็น µs
        else:
            failures += 1

    return success_count, failures, latencies


# 4. Ultra-God Mode Configurations
NUM_THREADS = 128               # 💥 128 Concurrent Threads
OPS_PER_THREAD = 20000          # 20,000 ops ต่อ Thread
TOTAL_OPS = NUM_THREADS * OPS_PER_THREAD # รวมทั้งหมด 2,560,000 Operations!

gc.collect() # Clean Python Heap ก่อนเริ่มวัดค่า RAM
process = psutil.Process(os.getpid())
initial_ram = process.memory_info().rss / (1024 * 1024)

print("=" * 75)
print("☠️️  STARTING ACTIVE DEFENSE CORE - ULTRA-GOD MODE V3 (IN-PLACE ZERO-ALLOCATION) ☠️")
print(f"DLL Target Target    : {dll_path}")
print(f"Concurrent Threads   : {NUM_THREADS} Threads")
print(f"Target Operations    : {TOTAL_OPS:,} ops")
print(f"Execution Strategy   : Zero-Allocation In-Place Memory Masking")
print(f"Initial Process RAM  : {initial_ram:.2f} MB")
print("=" * 75)

global_start = time.perf_counter()

all_latencies = []
total_passed = 0
total_failed = 0

with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(god_mode_worker_v3, t, OPS_PER_THREAD) for t in range(NUM_THREADS)]
    for f in as_completed(futures):
        passed, failed, lats = f.result()
        total_passed += passed
        total_failed += failed
        all_latencies.extend(lats)

global_time = time.perf_counter() - global_start

gc.collect()
final_ram = process.memory_info().rss / (1024 * 1024)
ram_diff = final_ram - initial_ram

all_latencies.sort()
p50 = all_latencies[int(len(all_latencies) * 0.50)]
p95 = all_latencies[int(len(all_latencies) * 0.95)]
p99 = all_latencies[int(len(all_latencies) * 0.99)]

print("\n------------------ GOD MODE V3 RESULTS ------------------")
print(f"Passed Operations    : {total_passed:,} / {TOTAL_OPS:,} ({total_passed/TOTAL_OPS*100:.2f}%)")
print(f"Failed Operations    : {total_failed}")
print(f"Total Time Elapsed   : {global_time:.4f} seconds")
print(f"Real C Throughput    : {total_passed / global_time:,.2f} ops/sec")
print(f"Memory Leak Delta    : {ram_diff:+.2f} MB (Final RAM: {final_ram:.2f} MB)")
print("---------------------------------------------------------")
print("LATENCY PERCENTILES (incl. Python FFI Overhead):")
print(f"  - P50 (Median)      : {p50:.2f} µs")
print(f"  - P95               : {p95:.2f} µs")
print(f"  - P99 (Worst Case)  : {p99:.2f} µs")
print("---------------------------------------------------------")

if total_failed == 0 and abs(ram_diff) < 5.0:
    print("🏆 [ULTRA-GOD MODE V3 PASSED] PERFECT ZERO-LEAK & MAXIMUM C THROUGHPUT!")
else:
    print("❌ [ULTRA-GOD MODE V3 FAILED] Unexpected Memory Overhead Detected!")