/**
 * @file test_runner.c
 * @brief Automated Unit Test Suite for Active Defense C-Core Primitives
 */

#include "active_defense.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

static void test_null_pointer_guard(void) {
    printf("[TEST] Testing Null Pointer Guards... ");
    uint64_t latency = 0;
    int status = ad_encrypt_and_shred_inplace(NULL, 100, &latency);
    assert(status == AD_ERROR_NULL_POINTER);
    printf("PASSED\n");
}

static void test_encryption_and_latency(void) {
    printf("[TEST] Testing In-Place Encryption Execution and Microsecond Latency... ");
    
    // สร้าง Mutable Buffer สำหรับ In-Place Transformation
    char sample_data[] = "Bangsaen AI Labs Active Defense C-Core Payload Test";
    size_t len = strlen(sample_data);
    
    // สำเนาข้อมูลเดิมไว้เปรียบเทียบหลัง Transform
    char original_data[128];
    memcpy(original_data, sample_data, len);

    uint64_t latency_us = 0;
    int status = ad_encrypt_and_shred_inplace((uint8_t*)sample_data, len, &latency_us);

    assert(status == AD_SUCCESS);

    // ตรวจสอบว่าข้อมูลใน Buffer ถูก Transform (ไม่เหมือนเดิมแล้ว)
    assert(memcmp(sample_data, original_data, len) != 0);

    printf("PASSED (Latency: %llu µs)\n", (unsigned long long)latency_us);
}

int main(void) {
    printf("=====================================================\n");
    printf("     RUNNING ACTIVE DEFENSE C-CORE UNIT TESTS        \n");
    printf("=====================================================\n");

    test_null_pointer_guard();
    test_encryption_and_latency();

    printf("=====================================================\n");
    printf(" [SUCCESS] ALL UNIT TESTS PASSED SUCCESSFULLY!       \n");
    printf("=====================================================\n");

    return 0;
}