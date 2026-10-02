/**
 * @file active_defense.h
 * @brief Active Defense Core - In-Place Zero-Allocation Security Primitive SDK
 * @version 1.0.0-poc
 */

#ifndef ACTIVE_DEFENSE_H
#define ACTIVE_DEFENSE_H

#include <stddef.h>
#include <stdint.h>

/* DLL Export / Import / Static Linkage Macros for Windows MSVC */
#if defined(_WIN32) || defined(__CYGWIN__)
    #if defined(AD_STATIC)
        #define AD_API              /* Static linking */
    #elif defined(AD_EXPORTS)
        #define AD_API __declspec(dllexport)
    #else
        #define AD_API __declspec(dllimport)
    #endif
#else
    #define AD_API __attribute__((visibility("default")))
#endif

/* C++ Name Mangling Guard */
#ifdef __cplusplus
extern "C" {
#endif

/* Error Code Definitions */
#define AD_SUCCESS                  0
#define AD_ERROR_NULL_POINTER      -1
#define AD_ERROR_INVALID_PARAM     -2
#define AD_ERROR_BUFFER_TOO_SMALL  -3
#define AD_ERROR_ENCRYPTION_FAILED -4
#define AD_ERROR_MEM_SHRED_FAILED  -5

/**
 * @brief Legacy Envelope Structure (Maintained for Backward Compatibility)
 */
typedef struct {
    uint8_t* ciphertext;
    size_t ciphertext_len;
    uint64_t latency_us;
} ad_envelope_t;

/**
 * @brief ⚡ Zero-Allocation In-Place Encrypt & Shred Primitive
 * 
 * Performs fast one-way byte transformation directly in the caller-allocated RAM buffer.
 * Zero dynamic memory allocations (malloc/free) are made during execution.
 * 
 * @param[in,out] buffer           Pointer to input/output data buffer
 * @param[in]     buffer_len       Length of data buffer in bytes
 * @param[out]    out_latency_us   Optional pointer to capture microsecond latency metric (can be NULL)
 * 
 * @return AD_SUCCESS on success, negative error code on failure.
 */
AD_API int ad_encrypt_and_shred_inplace(
    uint8_t* buffer,
    size_t buffer_len,
    uint64_t* out_latency_us
);

/**
 * @brief Free Envelope Memory Buffer (Legacy API)
 */
AD_API void ad_free_envelope(ad_envelope_t* envelope);

#ifdef __cplusplus
}
#endif

#endif /* ACTIVE_DEFENSE_H */