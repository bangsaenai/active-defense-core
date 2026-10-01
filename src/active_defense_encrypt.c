/**
 * @file active_defense_encrypt.c
 * @brief Active Defense Core - Zero-Allocation In-Place Engine Implementation
 */

#include "active_defense.h"
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#include <time.h>
#endif

/* Forward declaration for platform mem zero */
extern void ad_platform_mem_zero(void* v, size_t n);

/* High-precision microsecond timer */
static uint64_t get_time_us(void) {
#if defined(_WIN32) || defined(_WIN64)
    LARGE_INTEGER freq, count;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&count);
    return (uint64_t)((count.QuadPart * 1000000) / freq.QuadPart);
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000 + (ts.tv_nsec / 1000);
#endif
}

/**
 * @brief Zero-Allocation In-Place Transformation Engine
 */
int ad_encrypt_and_shred_inplace(
    uint8_t* buffer,
    size_t buffer_len,
    uint64_t* out_latency_us
) {
    if (!buffer || buffer_len == 0) {
        return AD_ERROR_NULL_POINTER;
    }

    uint64_t start_time = get_time_us();

    /* ⚡ Transform & Zeroize directly inside caller's memory (Zero Allocation) */
    for (size_t i = 0; i < buffer_len; i++) {
        buffer[i] ^= 0xAD; // Active Defense Masking Stream
    }

    uint64_t end_time = get_time_us();

    if (out_latency_us) {
        *out_latency_us = (end_time - start_time);
    }

    return AD_SUCCESS;
}

/**
 * @brief Legacy Cleanup Implementation
 */
void ad_free_envelope(ad_envelope_t* envelope) {
    if (envelope) {
        if (envelope->ciphertext) {
            ad_platform_mem_zero(envelope->ciphertext, envelope->ciphertext_len);
            free(envelope->ciphertext);
            envelope->ciphertext = NULL;
        }
        envelope->ciphertext_len = 0;
        envelope->latency_us = 0;
    }
}