import ctypes
import os
import time
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Load active_defense.dll
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


# =========================================================================
# TEST 1: Boundary & Edge Case Protections (0 Byte, Null Pointer, 128MB)
# =========================================================================
def run_boundary_edge_cases():
    print("\n[STAGE 1] Testing Edge Cases & Extreme Payload Sizes...")
    latency = ctypes.c_uint64(0)
    
    # 1.1 Null Pointer Test
    res_null = c_lib.ad_encrypt_and_shred_inplace(None, 1024, ctypes.byref(latency))
    assert res_null == -1, f"Failed Null Guard: got {res_null}"
    print("  [✓] Null Pointer Protection: PASSED (Returned AD_ERROR_NULL_POINTER)")

    # 1.2 Zero Byte Test
    dummy_buf = (ctypes.c_uint8 * 16)()
    res_zero = c_lib.ad_encrypt_and_shred_inplace(dummy_buf, 0, ctypes.byref(latency))
    assert res_zero == -1, f"Failed Zero Byte Guard: got {res_zero}"
    print("  [✓] Zero-Length Buffer Guard: PASSED (Returned AD_ERROR_NULL_POINTER)")

    # 1.3 Single Byte Test (1 Byte Edge Case)
    one_byte_buf = (ctypes.c_uint8 * 1)(0xFF)
    res_one = c_lib.ad_encrypt_and_shred_inplace(one_byte_buf, 1, ctypes.byref(latency))
    assert res_one == 0 and one_byte_buf[0] == (0xFF ^ 0xAD), "1-Byte Transform Failed"
    print("  [✓] Single Byte Payload (1 Byte): PASSED")

    # 1.4 Heavy Payload Test (128 MB In-Place Memory Masking)
    print("  [...] Allocating 128 MB RAM Buffer for Massive Stress Test...")
    heavy_size = 128 * 1024 * 1024 # 128 MB
    heavy_buf = (ctypes.c_uint8 * heavy_size)()
    
    t0 = time.perf_counter()
    res_heavy = c_lib.ad_encrypt_and_shred_inplace(heavy_buf, heavy_size, ctypes.byref(latency))
    t1 = time.perf_counter()
    
    assert res_heavy == 0, "128MB Heavy Payload Failed"
    elapsed_ms = (t1 - t0) * 1000.0
    throughput_gbps = (heavy_size / (1024 * 1024 * 1024)) / (t1 - t0)
    print(f"  [✓] Heavy Payload (128 MB Single Pass): PASSED in {elapsed_ms:.2f} ms ({throughput_gbps:.2f} GB/s Rate)")


# =========================================================================
# TEST 2: Extreme Concurrency (512 Threads) & 10,000,000 Operations
# =========================================================================
def worker_heavy_concurrency(thread_id, iterations):
    success_count = 0
    failures = 0
    sum_lat = 0.0
    latency_metric = ctypes.c_uint64(0)

    # Reusable local buffer per thread
    buf = (ctypes.c_uint8 * 4096)(0xAB) # 4KB
    p_len = 4096

    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        res = c_lib.ad_encrypt_and_shred_inplace(buf, p_len, ctypes.byref(latency_metric))
        t1 = time.perf_counter_ns()
        
        if res == 0:
            success_count += 1
            sum_lat += (t1 - t0) / 1000.0
        else:
            failures += 1

    return success_count, failures, sum_lat


def run_massive_concurrency_test():
    NUM_THREADS = 512            # 💥 512 Concurrent Threads
    OPS_PER_THREAD = 19532       # ~10,000,000 Operations
    TOTAL_OPS = NUM_THREADS * OPS_PER_THREAD

    gc.collect()
    process = psutil.Process(os.getpid())
    ram_start = process.memory_info().rss / (1024 * 1024)

    print("\n" + "=" * 75)
    print(f"[STAGE 2] Testing Extreme Concurrency (512 Threads & {TOTAL_OPS:,} Ops)...")
    print("=" * 75)

    global_start = time.perf_counter()
    total_passed = 0
    total_failed = 0
    global_sum_lat = 0.0

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(worker_heavy_concurrency, t, OPS_PER_THREAD) for t in range(NUM_THREADS)]
        for f in as_completed(futures):
            passed, failed, s_lat = f.result()
            total_passed += passed
            total_failed += failed
            global_sum_lat += s_lat

    global_time = time.perf_counter() - global_start

    gc.collect()
    ram_end = process.memory_info().rss / (1024 * 1024)
    ram_diff = ram_end - ram_start

    avg_lat = global_sum_lat / total_passed if total_passed > 0 else 0

    print("\n---------------- EXTREME CONCURRENCY RESULTS ----------------")
    print(f"Passed Operations    : {total_passed:,} / {TOTAL_OPS:,} ({total_passed/TOTAL_OPS*100:.2f}%)")
    print(f"Failed Operations    : {total_failed}")
    print(f"Total Time Elapsed   : {global_time:.4f} seconds")
    print(f"Real C Throughput    : {total_passed / global_time:,.2f} ops/sec")
    print(f"Memory Leak Delta    : {ram_diff:+.2f} MB (Final RAM: {ram_end:.2f} MB)")
    print(f"Average Latency      : {avg_lat:.2f} µs (incl. Python FFI Overhead)")
    print("-------------------------------------------------------------")

    if total_failed == 0 and abs(ram_diff) < 5.0:
        print("🏆 [PASSED] ABSOLUTE C-BINARY EXTREME BOUNDARY VERIFIED!")
    else:
        print("❌ [FAILED] C Binary Failed under Extreme Pressure!")


if __name__ == "__main__":
    print("=========================================================================")
    print("🔥 STARTING C BINARY PHYSICAL BOUNDARY & EXTREME PRESSURE TEST 🔥")
    print("=========================================================================")
    run_boundary_edge_cases()
    run_massive_concurrency_test()