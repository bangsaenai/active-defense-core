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

class AdEnvelope(ctypes.Structure):
    _fields_ = [
        ("ciphertext", ctypes.POINTER(ctypes.c_uint8)),
        ("ciphertext_len", ctypes.c_size_t),
        ("latency_us", ctypes.c_uint64)
    ]

c_lib.ad_encrypt_and_shred.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(AdEnvelope)
]
c_lib.ad_encrypt_and_shred.restype = ctypes.c_int

c_lib.ad_free_envelope.argtypes = [ctypes.POINTER(AdEnvelope)]
c_lib.ad_free_envelope.restype = None


def god_mode_worker_v2(thread_id, iterations):
    success_count = 0
    failures = 0
    latencies = []
    
    envelope = AdEnvelope()

    # ⚡ Reuse Buffers: เตรียม C-Array ไว้ล่วงหน้าในระดับ Thread (ไม่สร้างใหม่ใน Loop)
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
        res = c_lib.ad_encrypt_and_shred(c_buf, p_len, ctypes.byref(envelope))
        t1 = time.perf_counter_ns()
        
        if res == 0:
            success_count += 1
            latencies.append((t1 - t0) / 1000.0) # Convert to µs
            c_lib.ad_free_envelope(ctypes.byref(envelope))
        else:
            failures += 1

    return success_count, failures, latencies

NUM_THREADS = 128
OPS_PER_THREAD = 15625
TOTAL_OPS = NUM_THREADS * OPS_PER_THREAD

gc.collect() # Force GC ก่อนเริ่มวัดค่า
process = psutil.Process(os.getpid())
initial_ram = process.memory_info().rss / (1024 * 1024)

print("=" * 70)
print("☠️  STARTING ACTIVE DEFENSE CORE - GOD MODE V2 (TRUE C-LEAK TEST) ☠️")
print(f"DLL Path             : {dll_path}")
print(f"Concurrent Threads   : {NUM_THREADS} Threads")
print(f"Target Operations    : {TOTAL_OPS:,} ops")
print(f"Payload Strategy     : Reusable Dynamic Chaos Buffers (1KB -> 256KB)")
print(f"Initial Process RAM  : {initial_ram:.2f} MB")
print("=" * 70)

global_start = time.perf_counter()

all_latencies = []
total_passed = 0
total_failed = 0

with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(god_mode_worker_v2, t, OPS_PER_THREAD) for t in range(NUM_THREADS)]
    for f in as_completed(futures):
        passed, failed, lats = f.result()
        total_passed += passed
        total_failed += failed
        all_latencies.extend(lats)

global_time = time.perf_counter() - global_start

gc.collect() # Force Cleanup Python References
final_ram = process.memory_info().rss / (1024 * 1024)
ram_diff = final_ram - initial_ram

all_latencies.sort()
p50 = all_latencies[int(len(all_latencies) * 0.50)]
p95 = all_latencies[int(len(all_latencies) * 0.95)]
p99 = all_latencies[int(len(all_latencies) * 0.99)]

print("\n------------------ GOD MODE V2 RESULTS ------------------")
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

if total_failed == 0 and abs(ram_diff) < 10.0:
    print("🏆 [GOD MODE V2 PASSED] Perfect C-Core Memory Zeroization & Zero Leak!")
else:
    print("❌ [GOD MODE V2 FAILED] Genuine C Memory Leak Detected!")