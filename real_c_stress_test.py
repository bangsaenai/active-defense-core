import ctypes
import os
import time
from concurrent.futures import ThreadPoolExecutor

# 1. โหลด active_defense.dll
dll_path = os.path.abspath("./build/Release/active_defense.dll")
if not os.path.exists(dll_path):
    print(f"[X] Error: {dll_path} not found! Please build CMake first.")
    exit(1)

c_lib = ctypes.CDLL(dll_path)

# 2. นิยาม Structure ad_envelope_t ใน Python ให้ตรงกับ C Header
class AdEnvelope(ctypes.Structure):
    _fields_ = [
        ("ciphertext", ctypes.POINTER(ctypes.c_uint8)),
        ("ciphertext_len", ctypes.c_size_t),
        ("latency_us", ctypes.c_uint64)
    ]

# 3. กำหนด Argument / Return Types ของ C Functions
# int ad_encrypt_and_shred(const uint8_t* payload, size_t payload_len, ad_envelope_t* envelope)
c_lib.ad_encrypt_and_shred.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(AdEnvelope)
]
c_lib.ad_encrypt_and_shred.restype = ctypes.c_int

# void ad_free_envelope(ad_envelope_t* envelope)
c_lib.ad_free_envelope.argtypes = [ctypes.POINTER(AdEnvelope)]
c_lib.ad_free_envelope.restype = None


# 4. Thread Worker: เรียกใช้งาน C Function และ Shred Memory จริง
def c_native_worker(thread_id, iterations):
    # เตรียม 1KB Sample Data
    sample_data = b"Bangsaen AI Labs Active Defense Payload " * 25 # 1000 bytes
    payload_len = len(sample_data)
    
    # แปลง Python bytes -> C uint8 Array
    c_payload = (ctypes.c_uint8 * payload_len).from_buffer_copy(sample_data)
    
    success_count = 0
    envelope = AdEnvelope()

    for _ in range(iterations):
        # เรียก C Engine: เข้ารหัส + Kernel Zeroization ใน RAM
        res = c_lib.ad_encrypt_and_shred(c_payload, payload_len, ctypes.byref(envelope))
        if res == 0: # AD_SUCCESS
            success_count += 1
            # คืน Memory Heap ใน C
            c_lib.ad_free_envelope(ctypes.byref(envelope))

    return success_count

# 5. Execute Multi-threaded C-FFI Stress Test
NUM_THREADS = 16
OPS_PER_THREAD = 50000
TOTAL_OPS = NUM_THREADS * OPS_PER_THREAD

print("=" * 65)
print(f"🔥 REAL C-NATIVE DLL MULTI-THREADED STRESS TEST 🔥")
print(f"DLL Target      : {dll_path}")
print(f"Total Threads   : {NUM_THREADS}")
print(f"Total Operations: {TOTAL_OPS:,} ops")
print("=" * 65)

start_time = time.perf_counter()

with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(c_native_worker, t, OPS_PER_THREAD) for t in range(NUM_THREADS)]
    total_passed = sum(f.result() for f in futures)

total_time = time.perf_counter() - start_time
throughput = total_passed / total_time
avg_latency = (total_time / total_passed) * 1_000_000

print("\n---------------- STRESS TEST RESULTS ----------------")
print(f"Passed Operations  : {total_passed:,} / {TOTAL_OPS:,}")
print(f"Total Time Elapsed : {total_time:.4f} seconds")
print(f"Real C Throughput  : {throughput:,.2f} ops/sec")
print(f"Average Latency    : {avg_latency:.2f} µs (including Python FFI overhead)")
print("-----------------------------------------------------")