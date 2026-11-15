---
schema_version: 1
id: sdk-standalone
domain: 00-workspace
status: active
title: "TODO-01 -- The SDK builds, tests and gates itself"
---

# TODO-01 -- The SDK builds, tests and gates itself

> **Goal:** A clone of Resolute-SDK builds its two libraries, runs their tests and passes its own gates with one command each, on a developer machine and on GitHub, so a change to shared code is proven here before any tool takes it by bumping its pin.

> **Current state:** Measured 2026-11-15. The SDK was extracted from `rizonesoft/Resolute` at `0651c202` that day. It holds `shared/resolute-ui/` (11 sources), `shared/lucide/`, `cmake/ResoluteSdk.cmake` with the platform, link, job-pool and warning policies, `toolchain.json`, `scripts/bootstrap.ps1`, `scripts/cpp-env.ps1` and `scripts/toolchain-latest.ps1`. It has no root `CMakeLists.txt`, no presets, no build script, no tests and no CI: the libraries are compiled only as part of a consumer, and the UI library's Catch2 suite (131 cases) still lives in Resolute's `tests/` and runs there against `sdk/`. `pwsh scripts/toolchain-latest.ps1` reports llvm-mingw `20260908` and CMake `4.4.3` behind upstream. `.conclave/lsp.json` names `clangd` and resolves the one Visual Studio installed, not the pinned one in `reskit/`.

## Inputs

- `cmake/ResoluteSdk.cmake` and the four policy files it includes: what a root project must apply to itself exactly as a consumer does.
- `D:\Resolute\tests\` at `840bac79`: the Catch2 suite, its fixtures, goldens and focus guard, and `D:\Resolute\scripts\check-all.ps1`, `build.ps1` and `tidy-ratchet.py`: the proven shapes this file adapts instead of inventing.
- `DESIGN.md` section 15 and `brand/build.py`: the asset check §7 wires into the gates.
- -> XREF: D01 T01 §3 -- the goldens that file re-captures run in the suite §3 moves here

## Outcome

- `pwsh scripts/build.ps1 -Config Debug` and `-Config Release` build both libraries and the test executable from a clean clone, and `ctest --preset debug` passes.
- `pwsh scripts/check-all.ps1` runs every gate and prints one line per gate; the `gates` workflow runs it on every push and is green.
- The language servers use the pinned clangd, the toolchain pins are current or their lag is a recorded decision, and a breaking change is announced where a consumer bumping its pin will read it.

**Adjacency:** all=not-applicable (a library repository's build, test and gate tooling: it holds no records a user lists, exports, is notified of or reverses)

**Adjacency rationale:** Everything here is developer tooling around two static libraries. The surfaces a user meets are drawn by the tools that consume the SDK, and each tool's own plan owns its adjacency.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Root CMake project and presets | -- | [ ] |
| 2 | §2 | Build script for the SDK | §1 | [ ] |
| 3 | §3 | UI test suite moved from Resolute | §2 | [ ] |
| 4 | §4 | Gate script and CI workflow | §3 | [ ] |
| 5 | §5 | Language servers on the pinned clangd | -- | [ ] |
| 6 | §6 | Toolchain pin currency decision | -- | [ ] |
| 7 | §7 | Brand asset check in the gates | §4 | [ ] |
| 8 | §8 | Changelog and breaking-change rule | -- | [ ] |
| 9 | §9 | Conformance and smoke checks for any tool | §4 | [ ] |

## 1. Root CMake Project and Presets

The SDK is configured today only from inside a consumer. This section gives it a root project that applies its own policies to itself through the same include a consumer uses, so the SDK never builds under rules its consumers do not get. It must not change what `cmake/ResoluteSdk.cmake` gives a consumer.

**Phase:** 1
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `CMakeLists.txt` at the root: `project(ResoluteSDK LANGUAGES CXX)`, `include(cmake/ResoluteSdk.cmake)`, `resolute_sdk_add_libraries()`, and `resolute_assert_warnings_complete()` last. Done when: `cmake --preset debug` configures with no warning.
2. Write `CMakePresets.json` with `debug` and `release` configure, build and test presets naming the compilers under `reskit/`. Done when: both presets configure from a clean tree.

- [ ] Write the root `CMakeLists.txt` that includes `cmake/ResoluteSdk.cmake` and calls `resolute_sdk_add_libraries()`. Done when: `reskit\cmake\bin\cmake.exe --preset debug` exits 0 and names both `ResoluteUI_static` and `Lucide_static`. Cheaper substitute: re-declaring the standard, definitions or link flags in the root file, which lets the SDK build under rules a consumer does not get.
- [ ] Guard the two-root file-prefix map in `cmake/ResoluteLinkPolicy.cmake` for the standalone case, where the SDK root is `CMAKE_SOURCE_DIR`. Done when: a Release object's embedded path reads `./shared/...` and never an absolute path, quoted from `llvm-strings`. Cheaper substitute: checking only that the build passes, which says nothing about what is embedded.
- [ ] Write `CMakePresets.json` with `debug` and `release` presets using `${sourceDir}/reskit/` compilers, the sccache launcher and `FETCHCONTENT_BASE_DIR` under `build/deps/`. Done when: `cmake --preset release` configures from an empty `build/`. Cheaper substitute: relying on compilers found on `PATH`, which makes two machines build with different toolchains.
- [ ] End the root file with `resolute_assert_warnings_complete()`. Done when: removing `resolute_set_warnings(Lucide_static)` makes the configure fail naming `Lucide_static`, then it is restored.
- [ ] Commit: `build: a root project that applies the SDK's own policies to itself`

**Test checkpoint:** `reskit\cmake\bin\cmake.exe --preset debug` then `reskit\cmake\bin\cmake.exe --build build\debug` exit 0 from a clean `build/`, and the same for `release`.

## 2. Build Script for the SDK

One command builds the SDK, as `scripts/build.ps1` does in Resolute, with the same output discipline: a bounded excerpt on failure and the full log under `build/logs/`. It must rebuild a tree made at another path or naming a tool that is gone, which Resolute's script learned twice.

**Phase:** 1
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/build.ps1` with `-Config Debug|Release`, the toolchain assertion and the stale-tree cleanup. Done when: it builds both configurations and reports each target.
2. Cover the stale-tree cleanup in `scripts/tests/test_build.py`. Done when: the test fails against a script without the cleanup.

- [ ] Write `scripts/build.ps1` with `-Config`, `Assert-Toolchain` naming each missing tool and `pwsh scripts/bootstrap.ps1` as the fix. Done when: with `reskit/ninja` renamed away the script exits 1 naming `reskit\ninja\ninja.exe`, then it is restored. Cheaper substitute: letting cmake fail downstream with a bare "not found".
- [ ] Port the stale-tree cleanup from Resolute's `scripts/build.ps1` (`Get-MovedBuildTrees`, both the source-directory and the missing-tool cases). Done when: a tree whose cache names a missing `CMAKE_AR` is removed and rebuilt with one line saying why. Cheaper substitute: deleting `build/` on every run, which throws away the compile cache.
- [ ] Keep the full log under `build/logs/` and print the last 25 lines on failure only. Done when: a deliberate syntax error prints the compiler's diagnostic and the log path, and a passing build prints one line per target.
- [ ] Add `scripts/tests/test_build.py` for the two stale-tree cases and the untouched-tree case. Done when: `python -m unittest scripts.tests.test_build` passes, and fails with the cleanup removed.
- [ ] Commit: `build: one command builds the SDK in either configuration`

**Test checkpoint:** `pwsh scripts/build.ps1 -Config Debug` and `pwsh scripts/build.ps1 -Config Release` each end with every target `OK`, and `python -m unittest scripts.tests.test_build` passes.

## 3. UI Test Suite Moved From Resolute

The UI library's tests exercise SDK code and live in the launcher's repository, so a change here is proven only after a consumer bumps its pin. This section moves the suite that tests the library to the SDK and leaves in Resolute only what tests the launcher. Nothing is copied: a case lives in one repository.

**Phase:** 1
**Needs:** windows-host, display-session
**Surface:** no

**Build order:**

1. Classify every file under `D:\Resolute\tests\` as library or launcher in `docs/tests-move.md`. Done when: each file has one home and a reason.
2. Move the library files to `tests/` here with `tests/CMakeLists.txt`, and remove them from Resolute in a commit that bumps its pin. Done when: both suites pass.

- [ ] Write `docs/tests-move.md` classifying each file under Resolute's `tests/` (131 cases at `840bac79`) as library or launcher, by what its includes and its `RESOLUTE_LAUNCHER` use show. Done when: every file is listed once with its home and the reason. Cheaper substitute: moving everything, which makes the SDK's tests depend on the launcher executable.
- [ ] Add `tests/CMakeLists.txt` with Catch2 pinned by the same commit Resolute pins, and move the library cases, `fixtures/`, `golden/`, `focus_guard.*`, `fence.*` and `main.cpp`. Done when: `ctest --preset debug` runs the moved cases and passes. Cheaper substitute: copying the files and leaving the originals, which gives two suites that drift.
- [ ] Repoint the moved `tests/icon_manifest.txt` and `icon_manifest_test.cpp` from `sdk/shared/` to `shared/`. Done when: the manifest test passes here and fails when one referrer row is removed.
- [ ] Remove the moved files from Resolute and keep its launcher cases building against `sdk/`, in one Resolute commit that bumps `sdk.json`. Done when: Resolute's `ctest --preset debug` passes with only launcher cases and `git grep` finds no moved case name in both repositories.
- [ ] Record the headful and fenced cases in `tests/focus-audit.md` as Resolute does, with the `headful` test preset. Done when: `ctest --preset headful -N` lists exactly the audited cases.
- [ ] Commit: `tests: the UI library's suite lives with the library`

**Test checkpoint:** `reskit\cmake\bin\ctest.exe --preset debug` and `--preset release` pass here with the moved cases, and Resolute's suite passes with the launcher cases against the bumped pin.

## 4. Gate Script and CI Workflow

A push to the SDK reaches every tool that later bumps its pin, so the SDK owes the same promise Resolute makes: one command runs every gate, and GitHub runs that command on every push.

**Phase:** 1
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/check-all.ps1` running build, tidy, tests and the plan gates with one line per gate. Done when: it ends `check-all: <n> gate(s) ok`.
2. Write `.github/workflows/gates.yml` running it on `windows-2025`. Done when: a push shows the run green.

- [ ] Write `scripts/check-all.ps1` on the shape of Resolute's: Debug and Release builds, both test presets, `python scripts/todo-graph.py validate` and `plan --check`, `node scripts/verify-agent-tiers.mjs`, and `python -m unittest discover -s scripts/tests`. Done when: it prints one line per gate and exits 1 when a test is made to fail. Cheaper substitute: a script that prints every gate's output, which nobody reads.
- [ ] Port the clang-tidy ratchet (`scripts/tidy-ratchet.py` and `todo/.tidy-baseline`) for the SDK's two targets, with the baseline measured here. Done when: the gate passes at the measured count and fails when one finding is added. Cheaper substitute: starting the baseline at zero by excluding checks.
- [ ] Write `.github/workflows/gates.yml`: checkout, toolchain cache keyed on `toolchain.json`, `pwsh scripts/bootstrap.ps1`, `pwsh scripts/check-all.ps1`, and the gate logs kept on failure. Done when: the run for the commit is green on GitHub, quoted by its URL.
- [ ] Add `scripts/ci_status.py` usage to `AGENTS.md` under "Verify with": after a push, `python scripts/ci_status.py`. Done when: the command reports the pushed commit's run.
- [ ] Commit: `gates: one command runs every gate, and GitHub runs it on every push`

**Test checkpoint:** `pwsh scripts/check-all.ps1` ends `check-all: <n> gate(s) ok`, and `python scripts/ci_status.py` exits 0 for the pushed commit.

## 5. Language Servers on the Pinned clangd

The lsp kit resolved `clangd` from Visual Studio, which is a different LLVM from the one that compiles the SDK and reports diagnostics the pinned compiler does not.

**Phase:** 0
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Point the `clangd` entry of `.conclave/lsp.json` at `reskit/llvm-mingw/bin/clangd.exe` with the compile database under `build/debug`. Done when: `python scripts/lsp-servers.py list` shows that path.

- [ ] Set the `clangd` server in `.conclave/lsp.json` to the pinned `reskit/llvm-mingw/bin/clangd.exe`, with `--compile-commands-dir=build/debug` and the query driver for `reskit/llvm-mingw/bin/*`. Done when: `python scripts/lsp-servers.py list` prints the pinned path. Cheaper substitute: leaving the Visual Studio clangd, whose diagnostics are not the compiler's.
- [ ] Add `pyright` from the kit's preset for the Python scripts. Done when: `python scripts/lsp-servers.py list` shows both servers.
- [ ] Run `python scripts/lsp-diagnostics.py shared/resolute-ui/src/theme.cpp` after a Debug build. Done when: it returns the file's diagnostics from the pinned clangd, quoted with the server's reported version.
- [ ] Commit: `lsp: the pinned clangd and pyright, read from the build tree`

**Test checkpoint:** `python scripts/lsp-diagnostics.py shared/resolute-ui/src/theme.cpp` exits 0 and names clangd from `reskit/llvm-mingw`.

## 6. Toolchain Pin Currency Decision

`scripts/toolchain-latest.ps1` reported on 2026-11-15 that llvm-mingw `20260908` and CMake `4.4.3` are behind `20261104` and `4.5.0`. Moving a pin changes what every tool is compiled with, so it is the owner's decision and is made once, here, for the whole suite.

**Phase:** 0
**Needs:** owner-decision
**Surface:** no

**Build order:**

1. Record the owner's answer for each lagging pin in `docs/toolchain-pins.md`. Done when: each pin says bump or stay, with the date and the reason.

- [ ] Write `docs/toolchain-pins.md` listing each component, its pin, the latest release and the owner's decision. Done when: every component in `toolchain.json` has a row with a dated decision.
- [ ] Apply each bump in `toolchain.json` with its new URL and SHA-256, one commit per component. Done when: `pwsh scripts/bootstrap.ps1 -Replace` installs it and `pwsh scripts/cpp-env.ps1` reports every component at its pin. Cheaper substitute: bumping the version without re-computing the hash, which bootstrap refuses.
- [ ] Rebuild both configurations after each bump and record any new diagnostic with its disposition in `docs/toolchain-pins.md`. Done when: both builds pass and the record names each new diagnostic or says there was none.
- [ ] Commit: `toolchain: pins reviewed and recorded`

**Test checkpoint:** `pwsh scripts/cpp-env.ps1` ends "All 5 component(s) resolve at the pinned version." and `docs/toolchain-pins.md` carries a decision for every component.

## 7. Brand Asset Check in the Gates

`brand/build.py --check` fails when a tracked asset differs from what the script builds. Until a gate runs it, an asset edited by hand drifts from the identity `DESIGN.md` section 15 states.

**Phase:** 1
**Needs:** none
**Surface:** no

**Build order:**

1. Add the check to `scripts/check-all.ps1` and state the two Python packages it needs. Done when: a hand-edited asset fails the gate by name.

- [ ] Add a `brand assets` gate to `scripts/check-all.ps1` running `python brand/build.py --check`. Done when: changing one byte of `brand/readme-banner.svg` fails the gate naming that file, then it is restored. Cheaper substitute: checking only that the files exist.
- [ ] Record `resvg_py` and `pillow` with their versions in `brand/requirements.txt`, and install them in the workflow before the gate. Done when: the gate passes on GitHub from a clean runner.
- [ ] Commit: `gates: the brand assets are what brand/build.py builds`

**Test checkpoint:** `python brand/build.py --check` prints "18 of 18 asset(s) current" and exits 0, and exits 1 after a one-byte change to any asset.

## 8. Changelog and Breaking-Change Rule

A tool takes SDK changes by bumping a commit hash, so the person bumping needs one place that says what changed between two commits and whether anything breaks.

**Phase:** 0
**Needs:** none
**Surface:** no

**Build order:**

1. Write `CHANGELOG.md` from the extraction forward and the rule in `CONTRIBUTING.md`. Done when: both exist and `AGENTS.md` points at them.

- [ ] Write `CHANGELOG.md` with one entry per pushed change that a consumer can observe, newest first, each naming its commit and marked `Breaking` when a consumer must change code or build files. Done when: the extraction and the identity are its first two entries.
- [ ] Write `CONTRIBUTING.md` with the rule: a breaking change says so in its commit subject and its changelog entry, and names what a consumer changes. Done when: the file exists and `AGENTS.md` "This project" links it.
- [ ] Commit: `docs: a changelog a consumer reads before bumping its pin`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, and `CHANGELOG.md` names commit `cae686b` as its oldest entry.

## 9. Conformance and Smoke Checks for Any Tool

Resolute's `scripts/conformance-check.py` (the profile every shipped tool is measured against) and `scripts/smoke-run.py` (start each built tool, drive it, read it back) are written around exactly two targets inside one tree: the launcher and `extensions/RegStudio`, with their self-tests naming RegStudio throughout. Every tool is now its own repository, so the checks have to work on one tool in its own tree, and they belong here, where every tool can run them from `sdk/`. Until this lands RegStudio cannot leave Resolute without turning its gates red, which is why its move stopped at steps 2 and 3 on 2026-11-16.

**Phase:** 1
**Needs:** windows-host, display-session
**Surface:** no

**Build order:**

1. Move the two checks and the profile here and make their tool list a file the consumer supplies. Done when: they run against one tool described by a `conformance.json` in the consumer.
2. Rewrite their self-tests around a fixture tool. Done when: no self-test names RegStudio or the launcher.

- [ ] Move `scripts/conformance-check.py`, `scripts/profile-check.py` and `docs/conformance-profile.md` from Resolute to the same paths here. Done when: `python scripts/profile-check.py --self-test` passes here. Cheaper substitute: copying them, which leaves two profiles.
- [ ] Replace the built-in tool table of `scripts/conformance-check.py` with a `conformance.json` read from the consumer's root: the tool's name, target, source directory, executable and shipped files. Done when: the check runs for a consumer with one tool and for Resolute with only the launcher. Cheaper substitute: adding each tool to a table here, which makes the SDK know every tool.
- [ ] Move `scripts/smoke-run.py`, `scripts/smoke_fixture.py` and `tools/elevated-smoke.ps1` here, reading the same `conformance.json`. Done when: a smoke run of one tool from its own repository starts it, drives it and writes its report.
- [ ] Rewrite the self-tests of both scripts around a fixture tool built in the test, never a real one. Done when: `git grep -n RegStudio scripts` here prints nothing and both self-tests pass, and each fails when its fixture is broken.
- [ ] Give Resolute a `conformance.json` naming the launcher alone, remove the moved scripts there and bump its `sdk.json`, in one Resolute commit. Done when: Resolute's `check-all` is green on GitHub with no RegStudio target in `todo/.tidy-baseline`.
- [ ] Finish RegStudio's move: step 1 of `docs/plans/2026-11-15-app-split.md` in Resolute for row 8, with its own `conformance.json`. Done when: `extensions/` is gone from Resolute and RegStudio's repository carries its sources.
- [ ] Commit: `gates: conformance and smoke checks that run on any one tool`

**Test checkpoint:** `python scripts/conformance-check.py --self-test` and `python scripts/smoke-run.py --self-test` pass here with no real tool named, and Resolute's `gates` workflow is green with the launcher as its only conformance target.
## Verification

- A clean clone bootstraps, builds both configurations, passes its tests and passes `pwsh scripts/check-all.ps1`, and the `gates` workflow is green for the same commit.
- Resolute builds and passes its launcher tests against the pin that carries the moved suite.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
