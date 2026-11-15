# The language standard and the Windows floor, in one file, for the launcher and
# every app.
#
# Moved here from Resolute's root CMakeLists.txt on 2026-11-15, when each tool
# left for its own repository: a block every repository retypes is the
# fourteen-copies failure arriving one repository at a time.

if(DEFINED RESOLUTE_PLATFORM_APPLIED)
    return()
endif()
set(RESOLUTE_PLATFORM_APPLIED TRUE)

# ── Standards ────────────────────────────────────────────────
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_SCAN_FOR_MODULES OFF)

# ── Platform requirements ────────────────────────────────────
# The runtime floor is Windows 10 1809 (build 17763), set in ONE place and
# inherited by every target. D00 T01 §1 records why 1809 and not older: dark
# mode, per-monitor DPI v2 as the suite uses it, and Direct2D SVG rendering.
#
# WINVER and _WIN32_WINNT carry only "Windows 10" (0x0A00); the RELEASE is
# carried by NTDDI_VERSION. Each executable's manifest declares the same floor
# to the loader. Both have to agree or one of them is a comment rather than a
# contract.
add_compile_definitions(
    WINVER=0x0A00
    _WIN32_WINNT=0x0A00
    NTDDI_VERSION=0x0A000006
    UNICODE
    _UNICODE
    NOMINMAX
    WIN32_LEAN_AND_MEAN
)
