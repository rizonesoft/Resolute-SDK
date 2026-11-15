# The one include a consumer needs. The launcher and every app do this at the
# top of their root CMakeLists.txt, after project():
#
#   include("${CMAKE_SOURCE_DIR}/sdk/cmake/ResoluteSdk.cmake")
#   resolute_sdk_add_libraries()
#
# The include applies the policies in the CONSUMER's directory scope, which is
# why this is an include and not an add_subdirectory: link options, compile
# definitions and job pools set inside a subdirectory never reach the targets
# of the directory that added it.
#
# `sdk/` in a consumer is this repository at the commit the consumer pins in
# its sdk.json, put there by the consumer's scripts/sdk.ps1.

if(DEFINED RESOLUTE_SDK_APPLIED)
    return()
endif()
set(RESOLUTE_SDK_APPLIED TRUE)

get_filename_component(RESOLUTE_SDK_DIR "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

include("${CMAKE_CURRENT_LIST_DIR}/ResolutePlatform.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/ResoluteLinkPolicy.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/ResoluteJobPools.cmake")
# The warning policy is applied per target, because a FetchContent dependency
# is a subdirectory of the build and would inherit anything set at the root.
include("${CMAKE_CURRENT_LIST_DIR}/ResoluteWarnings.cmake")

# The UI library and the icon set, as static libraries: ResoluteUI_static and
# Lucide_static. The binary directories are named, so this works whether the
# SDK sits inside the consumer's source tree or beside it.
macro(resolute_sdk_add_libraries)
    add_subdirectory("${RESOLUTE_SDK_DIR}/shared/resolute-ui" "${CMAKE_BINARY_DIR}/sdk/resolute-ui")
    add_subdirectory("${RESOLUTE_SDK_DIR}/shared/lucide" "${CMAKE_BINARY_DIR}/sdk/lucide")
endmacro()
