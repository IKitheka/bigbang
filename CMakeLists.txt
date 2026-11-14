cmake_minimum_required(VERSION 3.20)

project(BigBangSimulation
    VERSION 1.0
    LANGUAGES C CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(OpenGL REQUIRED)
find_package(glfw3 3.3 REQUIRED)
find_package(glm CONFIG REQUIRED)

include(FetchContent)

FetchContent_Declare(
    glad
    GIT_REPOSITORY https://github.com/Dav1dde/glad.git
    GIT_TAG v2.0.8
    SOURCE_SUBDIR cmake
)

FetchContent_MakeAvailable(glad)

glad_add_library(glad_gl_core_33
    REPRODUCIBLE
    API gl:core=3.3
)

add_executable(bigbang
    src/main.cpp
    src/Shader.cpp
    src/HDRFramebuffer.cpp
    src/BloomEffect.cpp
    src/PngWriter.cpp
)

target_include_directories(bigbang PRIVATE include)

target_link_libraries(bigbang PRIVATE
    OpenGL::GL
    glfw
    glm::glm
    glad_gl_core_33
)

target_compile_definitions(bigbang PRIVATE
    PROJECT_ROOT="${CMAKE_SOURCE_DIR}"
)

target_compile_options(bigbang PRIVATE
    -Wall
    -Wextra
    -Wpedantic
)

# M0: deterministic timeline and PNG tests have no OpenGL or Blender dependency.
include(CTest)
if(BUILD_TESTING)
    add_executable(m0_native_tests
        tests/test_native_m0.cpp
        src/PngWriter.cpp
    )
    target_include_directories(m0_native_tests PRIVATE include)
    target_compile_options(m0_native_tests PRIVATE -Wall -Wextra -Wpedantic)
    add_test(NAME m0_native_clock_png COMMAND m0_native_tests)
endif()
