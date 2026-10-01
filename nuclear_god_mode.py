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

c_lib.ad_encrypt_and_shred_inplace.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_uint64)
]
c_lib.ad_encrypt_and_shred_inplace.restype = ctypes.c_int


# 2. Worker Function: Massive Concurrency & Data Integrity Validation
def nuclear_worker(thread_id, iterations):
    success_count = 0
    failures = 0
    corruptions = 0
    sum_lat = 0.0
    latency_metric = ctypes.c_uint64(0)

    # Payload Template ขนาด 8KB สำหรับเค้น L1/L2 Cache
    payload_len = 8192
    raw_data = bytes([i % 256 for i in range(payload_len)])
    
    # Pre-allocated Mutable Thread Buffer
    buf = (ctypes.c_uint8 * payload_len).from_buffer_copy(raw_data)

    for i in range(iterations):
        t0 = time.perf_counter_ns()
        
        # Pass 1: Encrypt/Mask In-Place
        res1 = c_lib.ad_encrypt_and_shred_inplace(buf, payload_len, ctypes.byref(latency_metric))
        
        # Pass 2: Re-apply In-Place (XOR 0xAD ซ้ำอีกรอบเพื่อ Decode กลับเป็นค่าเดิม)
        res2 = c_lib.ad_encrypt_and_shred_inplace(buf, payload_len, ctypes.byref(latency_metric))
        
        t1 = time.perf_counter_ns()

        if res1 == 0 and res2 == 0:
            # ⚡ Verification: เช็กว่า Data ถูกคืนค่ากลับมาสมบูรณ์ $100\%$ หรือไม่
            if bytes(buf) == raw_data:
                success_count += 1
            else:
                corruptions += 1 # เกิด Data Race/Memory Overwrite สลับ Thread
            sum_lat += (t1 - t0) / 1000.0
        else:
            failures += 1

    return success_count, failures, corruptions, sum_lat


# 3. Nuclear Configurations
NUM_THREADS = 1024               # 💥 1,024 Concurrent Threads!
OPS_PER_THREAD = 48828           # ~50,000,000 Operations
TOTAL_OPS = NUM_THREADS * OPS_PER_THREAD

gc.collect()
process = psutil.Process(os.getpid())
ram_start = process.memory_info().rss / (1024 * 1024)

print("=" * 80)
print("☢️  STARTING ACTIVE DEFENSE CORE - NUCLEAR GOD MODE (LEVEL 5 STRESS) ☢️")
print(f"DLL Target Target    : {dll_path}")
print(f"Concurrent Threads   : {NUM_THREADS} Threads")
print(f"Target Operations    : {TOTAL_OPS:,} ops (50 Million Ops)")
print(f"Verification Mode    : Double-Pass In-Place XOR Integrity Validation")
print(f"Initial Process RAM  : {ram_start:.2f} MB")
print("=" * 80)

global_start = time.perf_counter()

total_passed = 0
total_failed = 0
total_corruptions = 0
global_sum_lat = 0.0

with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(nuclear_worker, t, OPS_PER_THREAD) for t in range(NUM_THREADS)]
    for f in as_completed(futures):
        passed, failed, corrupt, s_lat = f.result()
        total_passed += passed
        total_failed += failed
        total_corruptions += corrupt
        global_sum_lat += s_lat

global_time = time.perf_counter() - global_start

gc.collect()
ram_end = process.memory_info().rss / (1024 * 1024)
ram_diff = ram_end - ram_start

avg_lat = global_sum_lat / (total_passed * 2) if total_passed > 0 else 0

print("\n------------------ NUCLEAR GOD MODE RESULTS ------------------")
print(f"Passed Operations    : {total_passed:,} / {TOTAL_OPS:,} ({total_passed/TOTAL_OPS*100:.2f}%)")
print(f"API Execution Errors : {total_failed}")
print(f"Data Corruptions     : {total_corruptions} (Memory Integrity Failures)")
print(f"Total Time Elapsed   : {global_time:.4f} seconds")
print(f"Real C Throughput    : {(total_passed * 2) / global_time:,.2f} transforms/sec")
print(f"Memory Leak Delta    : {ram_diff:+.2f} MB (Final RAM: {ram_end:.2f} MB)")
print(f"Average Pass Latency : {avg_lat:.2f} µs (incl. Double-Pass & FFI Overhead)")
print("--------------------------------------------------------------")

if total_failed == 0 and total_corruptions == 0 and abs(ram_diff) < 10.0:
    print("👑 [NUCLEAR GOD MODE PASSED] IMMORTAL C-BINARY! Unstoppable Speed & Absolute Integrity!")
else:
    print("💥 [NUCLEAR GOD MODE FAILED] System Failure Detected under Extreme Pressure!")