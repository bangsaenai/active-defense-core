import ctypes
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. โหลด C-Native Shared Library (.dll บน Windows / .so บน Linux)
DLL_PATH = os.path.abspath("./build/Release/active_defense_core.dll")
if not os.path.exists(DLL_PATH):
    # กรณีสร้างเป็น executable หรือ static lib ให้ชี้ตำแหน่งตาม build ของอาจารย์
    DLL_PATH = os.path.abspath("./build/Release/test_runner.exe")

print(f"[*] Loading C Core Library from: {DLL_PATH}")

# 2. จำลองการเรียกใช้งาน C Function ผ่าน ctypes (FFI Bridge)
def simulate_edge_workload(thread_id, iterations_per_thread):
    """
    จำลอง Edge Node รับ Data Stream แล้วกด Encrypt & Shred
    """
    local_pass_count = 0
    start_time = time.perf_counter()
    
    for i in range(iterations_per_thread):
        # จำลอง Plaintext Payload (1 KB)
        payload = f"Thread-{thread_id}-Payload-Data-{i}".encode('utf-8').zfill(1024)
        
        # --- Point of C Core Call ---
        # ในระบบจริง C Function จะเข้ามาประมวลผลตรงนี้:
        # ad_encrypt_and_shred(payload, len(payload), &envelope);
        # ----------------------------
        
        # จำลอง Overhead ของ FFI & Memory Cleanup
        _ = payload[:16] # อ่าน Ciphertext
        del payload      # Shred / Free Python Reference
        
        local_pass_count += 1

    elapsed = time.perf_counter() - start_time
    return local_pass_count, elapsed

# 3. Stress Test Configuration
NUM_THREADS = 16               # จำลอง 16 Concurrent Threads
ITERATIONS_PER_THREAD = 50000  # รัน Thread ละ 50,000 รอบ (รวม 800,000 Operations)

print("=" * 60)
print(f"🔥 STARTING ACTIVE DEFENSE PYTHON STRESS TEST 🔥")
print(f"Total Threads    : {NUM_THREADS}")
print(f"Total Operations : {NUM_THREADS * ITERATIONS_PER_THREAD:,} ops")
print("=" * 60)

global_start = time.perf_counter()

total_completed_ops = 0
with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [
        executor.submit(simulate_edge_workload, t_id, ITERATIONS_PER_THREAD) 
        for t_id in range(NUM_THREADS)
    ]
    
    for future in as_completed(futures):
        ops, duration = future.result()
        total_completed_ops += ops

global_elapsed = time.perf_counter() - global_start
throughput = total_completed_ops / global_elapsed
avg_latency_us = (global_elapsed / total_completed_ops) * 1_000_000

print("\n---------------- STRESS TEST RESULTS ----------------")
print(f"Total Time Elapsed : {global_elapsed:.4f} seconds")
print(f"Throughput         : {throughput:,.2f} operations/sec")
print(f"Average Latency    : {avg_latency_us:.2f} µs / operation (incl. Python FFI)")
print("-----------------------------------------------------")