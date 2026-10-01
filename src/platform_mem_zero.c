/**
 * @file platform_mem_zero.c
 * @brief Cross-platform secure memory zeroization primitive (Kernel Level)
 */

#include <stddef.h>
#include <stdint.h>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#define _GNU_SOURCE
#include <string.h>
#endif

/**
 * @brief Securely zeroes memory to prevent sensitive data remanence in RAM.
 * Ensures the zeroing operation is not optimized away by the compiler.
 */
void ad_platform_mem_zero(void* v, size_t n) {
    if (v == NULL || n == 0) return;

#if defined(_WIN32) || defined(_WIN64)
    /* Windows Kernel SecureZeroMemory */
    SecureZeroMemory(v, n);
#elif defined(__STDC_LIB_EXT1__)
    /* C11 Annex K memset_s */
    memset_s(v, n, 0, n);
#elif defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__) || defined(__APPLE__)
    /* BSD/Apple explicit_bzero */
    explicit_bzero(v, n);
#elif defined(__linux__) && defined(__GLIBC__) && (__GLIBC__ > 2 || (__GLIBC__ == 2 && __GLIBC_MINOR__ >= 25))
    /* Modern Linux explicit_bzero */
    explicit_bzero(v, n);
#else
    /* Volatile Pointer Fallback (Guaranteed No Compiler Optimization Removal) */
    volatile uint8_t* p = (volatile uint8_t*)v;
    while (n--) {
        *p++ = 0;
    }
#endif
}