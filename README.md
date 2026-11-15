# Resolute-SDK

**The shared foundation of the Resolute suite: one UI library, one toolchain and one set of build rules, pinned by commit by the launcher and by every tool.**

Resolute is Rizonesoft's suite of Windows system utilities. Each tool lives in its own repository and ships as one standalone executable. What they share lives here, once, so that no tool carries a private copy of it.

## What is in it?

| Path | What it is |
| --- | --- |
| `shared/resolute-ui/` | The Direct2D UI library every surface is drawn with. Namespace `rui::`, include prefix `resolute/`, static library `ResoluteUI_static` |
| `shared/lucide/` | The icon set, embedded into each executable. Static library `Lucide_static` |
| `cmake/ResoluteSdk.cmake` | The one include a consumer needs. It applies everything below |
| `cmake/ResolutePlatform.cmake` | C++23 and the Windows 10 1809 floor |
| `cmake/ResoluteLinkPolicy.cmake` | A fully static runtime, ThinLTO for Release and reproducible binaries |
| `cmake/ResoluteWarnings.cmake` | The warning policy, applied per target, warnings as errors |
| `cmake/ResoluteJobPools.cmake` | Ninja job pools sized to the machine's memory |
| `toolchain.json` | The pinned toolchain: llvm-mingw, CMake, Ninja, CPython and sccache, each with its URL and SHA-256 |
| `scripts/bootstrap.ps1` | Downloads the pinned toolchain into `reskit/`, hash-checked. Nothing is installed system-wide |
| `scripts/cpp-env.ps1` | Reports every toolchain component and fails by name when one is missing or is not the pin |
| `scripts/toolchain-latest.ps1` | Says whether a pin has fallen behind upstream. It never changes a pin |

## How does a tool use it?

A consumer names the SDK in one file, `sdk.json`, by repository and full commit hash. Its `scripts/sdk.ps1` puts that commit at `sdk/` inside the consumer, and its root `CMakeLists.txt` includes one file:

```cmake
project(MyTool LANGUAGES CXX RC)

include("${CMAKE_SOURCE_DIR}/sdk/cmake/ResoluteSdk.cmake")
resolute_sdk_add_libraries()

add_executable(MyTool WIN32 src/main.cpp)
resolute_set_warnings(MyTool)
target_link_libraries(MyTool PRIVATE ResoluteUI_static Lucide_static)
```

`sdk/` is either a clone at the pinned commit, which is what CI and a fresh machine get, or a link to a checkout the developer already has, named by the `RESOLUTE_SDK_DIR` environment variable. With the link, one checkout and one toolchain serve every tool on the machine.

A tool takes a newer SDK by changing the commit in its `sdk.json`, and nothing else. Until it does, it builds against exactly what it was tested with.

## Quick start

On Windows 10 or 11 x64 with Git and PowerShell 7:

```powershell
git clone https://github.com/rizonesoft/Resolute-SDK.git
cd Resolute-SDK
pwsh scripts/bootstrap.ps1     # downloads the pinned toolchain into reskit/, hash-checked
pwsh scripts/cpp-env.ps1       # reports what resolved
```

The SDK is built as part of a consumer today. Its own standalone build and test run are planned work in [`todo/`](todo/): until they land, the UI library's test suite runs from the [Resolute](https://github.com/rizonesoft/Resolute) launcher repository against the SDK commit it pins.

## Status

Extracted from the Resolute repository on 2026-11-15, when every tool moved to its own repository. The framework (startup, settings, logging, localization, update, About) and the repair contract (diagnose, result list, restore record, undo) are planned here and not yet built.

## License

MIT. See [`LICENSE`](LICENSE). The Lucide icons under `shared/lucide/icons/` are ISC licensed, copyright Lucide Icons and Contributors: see [`shared/lucide/LICENSE-lucide.txt`](shared/lucide/LICENSE-lucide.txt) and [`shared/lucide/icons/SOURCES.md`](shared/lucide/icons/SOURCES.md) for which files are Lucide's and which are the suite's own.
