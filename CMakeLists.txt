cmake_minimum_required(VERSION 3.14)
project(active_defense_core VERSION 1.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Optimization Flags for High-Performance C-Core
if(MSVC)
    add_compile_options(/W4 /O2)
else()
    add_compile_options(-Wall -Wextra -O3)
endif()

# Include Directories
include_directories(include)

# =========================================================================
# 1. Build Static Core Library (.lib / .a) สำหรับ C/C++ Native Projects
# =========================================================================
add_library(activedefense_static STATIC
    src/active_defense_encrypt.c
    src/platform_mem_zero.c
)
target_include_directories(activedefense_static PUBLIC include)
set_target_properties(activedefense_static PROPERTIES OUTPUT_NAME "active_defense_static")

# =========================================================================
# 2. Build Shared Core Library (.dll / .so) สำหรับ Python/FFI Stress Test
# =========================================================================
add_library(activedefense_shared SHARED
    src/active_defense_encrypt.c
    src/platform_mem_zero.c
    exports.def
)
target_include_directories(activedefense_shared PUBLIC include)
target_compile_definitions(activedefense_shared PRIVATE AD_EXPORTS) 
set_target_properties(activedefense_shared PROPERTIES OUTPUT_NAME "active_defense")

# =========================================================================
# 3. Build Performance Benchmark Executable (Link กับ Static Core)
# =========================================================================
add_executable(benchmark_perf tests/benchmark_perf.c)
target_link_libraries(benchmark_perf PRIVATE activedefense_static)

# =========================================================================
# 4. Build Unit Test Executable (Link กับ Static Core)
# =========================================================================
add_executable(test_runner tests/test_runner.c)
target_link_libraries(test_runner PRIVATE activedefense_static)

# =========================================================================
# 5. Build Pure C-Native Nuclear Runner (Link กับ Static Core)
# =========================================================================
add_executable(test_nuclear tests/test_nuclear.c)
target_link_libraries(test_nuclear PRIVATE activedefense_static)

# ⚡ ปิด Macro __declspec(dllimport) สำหรับ Native Executables ทั้งหมด
target_compile_definitions(benchmark_perf PRIVATE AD_STATIC)
target_compile_definitions(test_runner PRIVATE AD_STATIC)
target_compile_definitions(test_nuclear PRIVATE AD_STATIC)