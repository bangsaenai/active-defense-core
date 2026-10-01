#include "active_defense.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#include <pthread.h>
#endif

#define NUM_THREADS 64               // 64 High-Performance Threads
#define TOTAL_TARGET_OPS 100000000   // ⚡ 100,000,000 Operations (ร้อยล้านรอบ!)
#define OPS_PER_THREAD (TOTAL_TARGET_OPS / NUM_THREADS)
#define PAYLOAD_SIZE 8192            // 8 KB Payload per pass

typedef struct {
    int thread_id;
    uint64_t passed_ops;
    uint64_t failed_ops;
} thread_args_t;

#if defined(_WIN32) || defined(_WIN64)
DWORD WINAPI nuclear_worker(LPVOID lpParam) {
#else
void* nuclear_worker(void* lpParam) {
#endif
    thread_args_t* args = (thread_args_t*)lpParam;
    
    uint8_t* buffer = (uint8_t*)malloc(PAYLOAD_SIZE);
    if (!buffer) {
        args->failed_ops = OPS_PER_THREAD;
        return 0;
    }

    for (size_t i = 0; i < PAYLOAD_SIZE; i++) {
        buffer[i] = (uint8_t)(i % 256);
    }

    uint64_t latency = 0;
    for (uint64_t i = 0; i < OPS_PER_THREAD; i++) {
        int res = ad_encrypt_and_shred_inplace(buffer, PAYLOAD_SIZE, &latency);
        if (res == AD_SUCCESS) {
            args->passed_ops++;
        } else {
            args->failed_ops++;
        }
    }

    free(buffer);
    return 0;
}

int main(void) {
    printf("========================================================================\n");
    printf("  CENTURY STRESS TEST (PURE C-NATIVE 100 MILLION OPS)                  \n");
    printf("========================================================================\n");
    printf("Target Operations   : %d ops (100 MILLION)\n", TOTAL_TARGET_OPS);
    printf("Concurrent Threads  : %d Threads\n", NUM_THREADS);
    printf("Payload Size        : %d Bytes (8 KB)\n\n", PAYLOAD_SIZE);

    thread_args_t args[NUM_THREADS];
#if defined(_WIN32) || defined(_WIN64)
    HANDLE threads[NUM_THREADS];
#endif

    printf("Executing 100,000,000 Pure C Operations across threads...\n");

#if defined(_WIN32) || defined(_WIN64)
    LARGE_INTEGER freq, start, end;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&start);

    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].thread_id = i;
        args[i].passed_ops = 0;
        args[i].failed_ops = 0;
        threads[i] = CreateThread(NULL, 0, nuclear_worker, &args[i], 0, NULL);
    }

    WaitForMultipleObjects(NUM_THREADS, threads, TRUE, INFINITE);

    QueryPerformanceCounter(&end);
    double elapsed_sec = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;
    for (int i = 0; i < NUM_THREADS; i++) CloseHandle(threads[i]);
#endif

    uint64_t total_passed = 0;
    uint64_t total_failed = 0;
    for (int i = 0; i < NUM_THREADS; i++) {
        total_passed += args[i].passed_ops;
        total_failed += args[i].failed_ops;
    }

    printf("\n------------------ CENTURY C-NATIVE RESULTS ------------------\n");
    printf("Passed Operations   : %llu / %d (%.2f%%)\n", 
            (unsigned long long)total_passed, TOTAL_TARGET_OPS, ((double)total_passed / TOTAL_TARGET_OPS) * 100.0);
    printf("Failed Operations   : %llu\n", (unsigned long long)total_failed);
    printf("Total Elapsed Time  : %.4f seconds\n", elapsed_sec);
    printf("Real C Throughput   : %.2f ops/sec\n", total_passed / elapsed_sec);
    printf("Avg Execution Latency: %.4f us\n", (elapsed_sec * 1000000.0) / total_passed);
    printf("--------------------------------------------------------------\n");

    return 0;
}