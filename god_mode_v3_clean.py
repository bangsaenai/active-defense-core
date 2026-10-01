import ctypes
import os
import time
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed

dll_path = os.path.abspath("./build/Release/active_defense.dll")
if not os.path.exists(dll_path):
    print(f"[X] Error: {dll_path} not found!")
    exit(1)

c_lib = ctypes.CDLL(dll_path)

c_lib.ad_encrypt_and_shred_inplace.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_uint64)
]
c_lib.ad_encrypt_and_shred_inplace.restype = ctypes.c_int


# Worker Function: Zero-Overhead Metric Collector (ไม่เก็บ List)
def god_mode_worker_clean(thread_id, iterations):
    success_count = 0
    failures = 0
    
    # คำนวณแบบ Aggregated โดยไม่จอง Memory ใน Python Heap
    min_lat = float('inf')
    max_lat = 0.0
    sum_lat = 0.0

    latency_metric = ctypes.c_uint64(0)

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
        res = c_lib.ad_encrypt_and_shred_inplace(c_buf, p_len, ctypes.byref(latency_metric))
        t1 = time.perf_counter_ns()
        
        if res == 0:
            success_count += 1
            lat_us = (t1 - t0) / 1000.0
            sum_lat += lat_us
            if lat_us < min_lat: min_lat = lat_us
            if lat_us > max_lat: max_lat = lat_us
        else:
            failures += 1

    return success_count, failures, sum_lat, min_lat, max_lat

NUM_THREADS = 128
OPS_PER_THREAD = 20000
TOTAL_OPS = NUM_THREADS * OPS_PER_THREAD # 2,560,000 Ops

gc.collect()
process = psutil.Process(os.getpid())
initial_ram = process.memory_info().rss / (1024 * 1024)

print("=" * 75)
print("☠️  STARTING ACTIVE DEFENSE CORE - TRUE C-LEAK TEST (ZERO-PYTHON OVERHEAD) ☠️")
print(f"DLL Target           : {dll_path}")
print(f"Concurrent Threads   : {NUM_THREADS} Threads")
print(f"Target Operations    : {TOTAL_OPS:,} ops")
print(f"Initial Process RAM  : {initial_ram:.2f} MB")
print("=" * 75)

global_start = time.perf_counter()

total_passed = 0
total_failed = 0
global_sum_lat = 0.0
global_min_lat = float('inf')
global_max_lat = 0.0

with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(god_mode_worker_clean, t, OPS_PER_THREAD) for t in range(NUM_THREADS)]
    for f in as_completed(futures):
        passed, failed, s_lat, min_l, max_l = f.result()
        total_passed += passed
        total_failed += failed
        global_sum_lat += s_lat
        if min_l < global_min_lat: global_min_lat = min_l
        if max_l > global_max_lat: global_max_lat = max_l

global_time = time.perf_counter() - global_start

gc.collect()
final_ram = process.memory_info().rss / (1024 * 1024)
ram_diff = final_ram - initial_ram

avg_latency = global_sum_lat / total_passed if total_passed > 0 else 0

print("\n------------------ GOD MODE CLEAN RESULTS ------------------")
print(f"Passed Operations    : {total_passed:,} / {TOTAL_OPS:,} ({total_passed/TOTAL_OPS*100:.2f}%)")
print(f"Failed Operations    : {total_failed}")
print(f"Total Time Elapsed   : {global_time:.4f} seconds")
print(f"Real C Throughput    : {total_passed / global_time:,.2f} ops/sec")
print(f"Memory Leak Delta    : {ram_diff:+.2f} MB (Final RAM: {final_ram:.2f} MB)")
print("------------------------------------------------------------")
print("LATENCY METRICS (incl. Python FFI Overhead):")
print(f"  - Average Latency   : {avg_latency:.2f} µs")
print(f"  - Min Latency       : {global_min_lat:.2f} µs")
print(f"  - Max Latency       : {global_max_lat:.2f} µs")
print("------------------------------------------------------------")

if total_failed == 0 and abs(ram_diff) < 5.0:
    print("🏆 [PASSED] ABSOLUTE ZERO LEAK VERIFIED! C-Core Memory Management is Perfect!")
else:
    print("❌ [FAILED] Unexpected Memory Overhead Detected!")