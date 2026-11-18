---
schema_version: 1
id: installed-sdk
domain: 03-installer
status: active
title: "TODO-02 -- The SDK installed on the build machine, found by version"
---

# TODO-02 -- The SDK installed on the build machine, found by version

> **Goal:** A developer installs Resolute-SDK once with its own setup, to `C:\ResoluteSDK` or a folder they choose. Versions sit side by side, the toolchain is downloaded once and shared, and a `bin` folder on the PATH holds the `sdk` command. Every program on the SDK finds the version line its `sdk.json` pins through the `RESOLUTE_SDK` environment variable and CMake's own package search. The `sdk/` clone or junction in every consumer goes away. `RESOLUTE_SDK_DEV` points builds at a working checkout while the SDK itself is being changed. The SDK is released, published and announced through the same Cloudflare update service as every Resolute program. A program's own setup still carries everything it uses from the SDK, so nobody who installs a program ever needs the SDK.

> **Current state:** Measured 2026-11-18. Each consumer's `scripts/sdk.ps1` makes `sdk/` either a clone of Resolute-SDK at the `commit` in `sdk.json`, or a directory junction to the checkout named by `RESOLUTE_SDK_DIR`. On this machine the launcher (`D:\Resolute`) and all 78 tools in `D:\Resolute_Bin` use the junction to `D:\Resolute-SDK`, and their pins name six different commits. The toolchain (`toolchain.json`: llvm-mingw 20260908, CMake 4.4.3, Ninja 1.13.2, Python 3.14.10, sccache 0.19.0; 2.1 GB) is downloaded hash-checked into `reskit/` inside each SDK checkout by `scripts/bootstrap.ps1`. Consumers reach it through `${sourceDir}/sdk/reskit/...` in `CMakePresets.json`, and include the SDK with `include(${CMAKE_SOURCE_DIR}/sdk/cmake/ResoluteSdk.cmake)` and `resolute_sdk_add_libraries()`, compiling the shared code into their own executables. The SDK has no version numbers, no releases and no installer.

The operator decided on 2026-11-18, in session:

- **Layout:** versions side by side under `C:\ResoluteSDK` (a folder of the operator's choice at install time).
- **Version cap:** SDK releases are numbered `MAJOR.MINOR.PATCH`. A program pins a minor line (`"1.4"`) and builds with that line's installed patch; a patch release replaces the previous patch of its line in place (a plan detail added after review, so patches never pile up). Each release's rollout moves every program to the new line together, and `sdk prune` removes lines no program on the machine pins, so one or two lines are installed in practice.
- **Toolchain:** a small installer; the pinned toolchain is downloaded hash-checked into a shared store that every SDK version pinning the same component uses.
- **Scope:** machine-wide: one admin prompt, `RESOLUTE_SDK` and the `bin` PATH entry are set for the machine.
- **SDK development:** `RESOLUTE_SDK_DEV` names a checkout that builds use instead of the installed version, with no link on disk. The operator called the junctions "facky".
- **Distribution:** the SDK is published like every Resolute program, to the Cloudflare update service (`D:\Updates`).
- **Programs carry the SDK:** a program's distribution includes everything it uses from the SDK (operator: "when a tool is distributed, the SDK is bundled with the tool").

## Inputs

- `scripts/sdk.ps1` in each consumer, and `sdk.json`: the pin and the clone-or-junction logic this file replaces.
- `toolchain.json` and `scripts/bootstrap.ps1`: the pinned, hash-checked components that move into the shared store.
- `cmake/ResoluteSdk.cmake`: what a consumer includes today, and what the package config wraps.
- CMake documentation for `find_package` config mode, the `<PackageName>*/` search entries, `CMAKE_FIND_PACKAGE_SORT_ORDER`, `write_basic_package_version_file(COMPATIBILITY SameMinorVersion)` and `CMAKE_TOOLCHAIN_FILE` (https://cmake.org/cmake/help/latest/command/find_package.html): the source cited for every resolution rule.
- `todo/03-installer/TODO-01-installer-shape.md`: the shared installer (D03 T01 §6), packaging (D03 T01 §11) and the Updates feed contract (D03 T01 §13) the SDK's own setup uses.
- `D:\Updates` (private `rizonesoft/Updates`): the feed and download service the SDK is published to.

## Outcome

- `C:\ResoluteSDK\` holds `sdk\ResoluteSDK-<line>\` per installed minor line (its newest patch), `toolchain\<component>-<version>\` per downloaded component, and `bin\` on the machine PATH, with `RESOLUTE_SDK` set for the machine.
- A consumer builds from a clean clone with no `sdk/` folder, no junction and no `RESOLUTE_SDK_DIR`, against the newest installed version of its pinned line, and fails by name when that line is missing.
- `sdk list`, `sdk install <line>`, `sdk prune`, `sdk which` and `sdk doctor` manage and explain what is installed.
- A packaged program installs and runs on a PC with no SDK installed.

**Adjacency:** list=applicable @ D03 T02 §5; document=not-applicable (nothing is printed or exported beyond the SDK's own files); settings=applicable @ D03 T02 §7; reporting=applicable @ D03 T02 §5; notifications=applicable @ D03 T02 §13; permissions=applicable @ D03 T02 §6; audit=applicable @ D03 T02 §6; exchange=applicable @ D03 T02 §12; reverse=applicable @ D03 T02 §6

**Adjacency rationale:** The list and report are `sdk list` and `sdk doctor`, owned by §5. The one setting is the dev override, §7. Permissions are the machine-wide install and its admin prompt, and the reverse is its uninstaller with the Inno Setup log as the trail, both §6. Exchange is the release archive and feed published to the update service, §12. The notification is the notice that a newer SDK release exists, §13.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | SDK version numbers and release tags | -- | [ ] |
| 2 | §2 | Installed layout and the CMake package config | §1 | [ ] |
| 3 | §3 | Shared toolchain store | §2 | [ ] |
| 4 | §4 | Root toolchain file that picks the pinned line | §2, §3 | [ ] |
| 5 | §5 | The sdk command in bin | §2, §3 | [ ] |
| 6 | §6 | SDK setup: machine-wide, side by side, variables | §3, §5, D03 T01 §6, D03 T01 §11 | [ ] |
| 7 | §7 | Dev override to a working checkout | §4 | [ ] |
| 8 | §8 | Consumers find the SDK by version line | §4, §7 | [ ] |
| 9 | §9 | CI gets the pinned line from the release archive | §8, §12 | [ ] |
| 10 | §10 | A packaged program carries what it uses | §8, D03 T01 §11 | [ ] |
| 11 | §11 | Junctions and RESOLUTE_SDK_DIR retired | §8 | [ ] |
| 12 | §12 | SDK release published to the update service | §1, §6, D03 T01 §13 | [ ] |
| 13 | §13 | Notice when a newer SDK release exists | §5, §12 | [ ] |
| 14 | §14 | Every consumer moved to the installed SDK | §9, §10, §11 | [ ] |
| 15 | §15 | Release rollout moves every consumer to a new line | §12, §14 | [ ] |

## 1. SDK Version Numbers and Release Tags

The SDK gets real version numbers, so a program can pin a line instead of a commit and an installed folder can say what it holds.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Add `VERSION` and the release tag rule. Done when: `git describe` and `VERSION` agree on a tagged commit.

- [ ] Add `VERSION` at the root holding `1.0.0`, read by `cmake/ResoluteSdk.cmake` into `RESOLUTE_SDK_VERSION`. Done when: a configure prints `Resolute-SDK 1.0.0`. Cheaper substitute: deriving the version from the commit count, which differs between clones.
- [ ] Write the numbering rule in `docs/sdk-install.md`: a patch release never changes what a consumer must write; anything that does is a minor or major release, named in `CHANGELOG.md`. Done when: the rule and three examples are in the file.
- [ ] Add `scripts/sdk-version.py check` failing when `VERSION` is not newer than the last `v*` tag on a commit that changes `shared/`, `cmake/` or `toolchain.json`. Done when: a changed `shared/` file with an unchanged `VERSION` exits 1 naming `VERSION`.
- [ ] Add `scripts/tests/test_sdk_version.py` covering newer, equal and older versions. Done when: it passes.
- [ ] Commit: `sdk: version numbers and release tags`

**Test checkpoint:** `python -m unittest scripts.tests.test_sdk_version` passes, and fails when the comparison treats `1.10.0` as older than `1.9.0`.

## 2. Installed Layout and the CMake Package Config

Each installed version is a CMake package, so `find_package(ResoluteSDK 1.4 CONFIG)` picks the newest `1.4.x` with no resolver of our own.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Write the package config and version files. Done when: two fake installs `1.4.1` and `1.4.3` and a consumer asking for `1.4` configure against `1.4.3`.

- [ ] Write `cmake/ResoluteSDKConfig.cmake`, which includes `ResoluteSdk.cmake` from its own folder and sets `ResoluteSDK_ROOT`. Done when: `find_package(ResoluteSDK CONFIG)` from a consumer defines `resolute_sdk_add_libraries`.
- [ ] Generate `ResoluteSDKConfigVersion.cmake` with `write_basic_package_version_file(... COMPATIBILITY SameMinorVersion)` from `VERSION`. Done when: asking for `1.4` refuses an installed `1.5.0` and accepts `1.4.0` to `1.4.x`. Cheaper substitute: `AnyNewerVersion`, which lets a consumer build against a line it never pinned.
- [ ] Fix the installed layout as `<root>\sdk\ResoluteSDK-<line>\`, one folder per minor line: a patch release replaces the previous patch of its line in place (§6), so patches never pile up. CMake's `<prefix>/<name>*/` search finds every line with `CMAKE_PREFIX_PATH=<root>\sdk`. Done when: the fixture with lines `1.3` and `1.4` and a consumer asking for `1.4` configures against `1.4`.
- [ ] Write the layout into `docs/sdk-install.md`, including what is not in an installed version: `reskit/`, `.git`, `todo/`, `docs/reviews/`. Done when: the doc lists each folder and its owner.
- [ ] Add `scripts/tests/test_sdk_package.py` configuring a fixture consumer against fake installs `1.3`, `1.4` and an incompatible newer `1.5`. Done when: it passes.
- [ ] Commit: `sdk: installed layout and CMake package config`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_sdk_package` passes, and fails when `SameMinorVersion` is changed to `AnyNewerVersion` (the `1.5` install is then chosen).

## 3. Shared Toolchain Store

The 2.1 GB toolchain is downloaded once per component version into a store every installed SDK version shares.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Teach `scripts/bootstrap.ps1` a store root. Done when: two SDK versions pinning the same CMake share one `toolchain\cmake-4.4.3\`.

- [ ] Add `-Store <root>\toolchain` to `scripts/bootstrap.ps1`, unpacking each `toolchain.json` component into `<component>-<version>\`, hash-checked as today. Done when: a run writes `cmake-4.4.3\bin\cmake.exe` and a second run with the same pins downloads nothing. Cheaper substitute: one `reskit/` per installed version, which costs 2 GB per version.
- [ ] Stage each component in `<store>\.staging\` and rename it into place only after its hash checks, never deleting an existing component first (today's replacement removes the destination before moving, `scripts/bootstrap.ps1`). Done when: a download killed half way leaves the store's existing components working.
- [ ] Serialize store changes with a lock file `<store>\.lock`, so two setups or `sdk install` runs never write at once. Done when: a second concurrent run waits, then finds the component present and downloads nothing.
- [ ] Write `toolchain.cmake` into each installed version, naming the store paths of its pinned compiler, `windres`, `sccache` and Ninja. Done when: it contains no `reskit` path.
- [ ] Keep `reskit/` as the store for a working checkout when no store root is given. Done when: `bootstrap.ps1` in `D:\Resolute-SDK` with no argument behaves as before.
- [ ] Move the Inno Setup component that D03 T01 §1 adds into the store like the others. Done when: `toolchain\innosetup-7.1.1\ISCC.exe` exists after a store run.
- [ ] Add `scripts/tests/test_toolchain_store.py` with a fake component archive. Done when: it passes, and fails when a hash mismatch still unpacks.
- [ ] Commit: `toolchain: a shared store for installed SDK versions`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_toolchain_store` passes, including a case that a second SDK version pinning the same component writes nothing.

## 4. Root Toolchain File That Picks the Pinned Line

The compiler must be chosen before `project()`, so a toolchain file at the root of the install reads the consumer's pinned line and hands over to that version's `toolchain.cmake`.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Write `ResoluteToolchain.cmake` installed at `<root>\`. Done when: a consumer preset with `"toolchainFile": "$env{RESOLUTE_SDK}/ResoluteToolchain.cmake"` compiles with the pinned line's clang.

- [ ] Write `cmake/ResoluteToolchain.cmake`, which on the top-level run reads `version` from `${CMAKE_SOURCE_DIR}/sdk.json`, resolves the line's folder once into `RESOLUTE_SDK_RESOLVED_DIR`, and includes its `toolchain.cmake`. Done when: the fixture consumer pinned to `1.4` gets the `1.4` line's compiler path.
- [ ] Pass `RESOLUTE_SDK_RESOLVED_DIR` to compiler probes through `CMAKE_TRY_COMPILE_PLATFORM_VARIABLES`, and use it, not `sdk.json`, inside a `try_compile` project (CMake toolchains manual). Done when: a fixture with `check_cxx_source_compiles` configures.
- [ ] Set `ResoluteSDK_DIR` from the resolved folder on every configure, overriding a cached value, so a reconfigure after installing a patch or clearing the dev override follows the change. Done when: a fixture build tree reconfigured after the override is cleared names the installed line.
- [ ] Fail with one message naming the line, the root searched and the command `sdk install <line>` when no matching version is installed. Done when: a fixture pinned to `9.9` stops configure with that text.
- [ ] Print `Resolute-SDK <version> from <path>` once per configure. Done when: the line appears in the configure output.
- [ ] Add the cases to `scripts/tests/test_sdk_package.py`. Done when: it passes.
- [ ] Commit: `sdk: root toolchain file picks the pinned line`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_sdk_package` passes the missing-line case, and fails when the message no longer names `sdk install`.

## 5. The sdk Command in bin

One command manages and explains the installed SDK, so nobody browses `C:\ResoluteSDK` by hand.

**Phase:** 5
**Needs:** windows-host
**Surface:** yes
**Fidelity:** the command's output in Windows Terminal, PowerShell 7 and cmd.
**Job:** a developer sees what is installed, adds a line, removes unused versions and finds out why a build cannot find the SDK. Consumer: the developer at a terminal.
**Treatment:** plain aligned text, one line per item, exit code 0 or 1. Cheaper substitute that fails: telling people to read folder names.
**Chrome:** none; console output.

**Build order:**

1. Write `bin/sdk.ps1` with `bin/sdk.cmd` calling it. Done when: each subcommand runs from cmd and PowerShell.

- [ ] Write `sdk list`: each installed version with its size and the consumers on this machine pinning its line, then each toolchain component and the versions using it. Done when: it lists the fixture installs and their users.
- [ ] Write `sdk which [<folder>]`: the version and path the folder's `sdk.json` resolves to, or the dev override when set. Done when: it prints the same path `ResoluteToolchain.cmake` picks.
- [ ] Write `sdk env [<folder>] [-Json]`: the resolved SDK folder and the store paths of CMake, Ninja, Python, sccache, the compiler and `ISCC.exe`, for build scripts that must start CMake itself (a toolchain file cannot choose the CMake that reads it). Done when: `-Json` output names an existing file for each tool.
- [ ] Write `sdk install <line>`: looks up the newest non-yanked release of that line in the signed `resolute-sdk` feed (D:\Updates feed `lines`), downloads it, checks its SHA-256 against the signed feed before running anything, and installs it silently, elevating once. Done when: `sdk install 1.4` works after stable has moved to `1.5`, and a download with a wrong digest never starts setup.
- [ ] Write `sdk prune`: removes every line and toolchain component no consumer pins, where the consumer roots are the machine's registered list (`HKLM\Software\Rizonesoft\ResoluteSDK\ConsumerRoots`, set in setup and by `sdk roots add`). It lists what it would remove and asks. Done when: the fixture's unpinned `1.3` is removed and `1.4` stays. Cheaper substitute: deleting all but the newest, which breaks a consumer pinned one line back.
- [ ] Refuse to prune when no consumer root is registered, when any root is missing or unreadable, or when a scan did not finish, and never remove the newest installed line. Done when: each fixture case removes nothing and names the reason.
- [ ] Write `sdk doctor`: checks `RESOLUTE_SDK`, the PATH entry, every installed version's files and every store component's hash, and names each fault with its fix. Done when: a removed `clang.exe` is named with `sdk install <line>` as the fix.
- [ ] Add `scripts/tests/test_sdk_command.py` driving each subcommand against a temp root. Done when: it passes.
- [ ] Commit: `sdk: the sdk command`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_sdk_command` passes, and fails when `prune` removes a pinned line or runs with an unreadable consumer root.

## 6. SDK Setup: Machine-Wide, Side by Side, Variables

The SDK's own setup, built with the shared installer shape, installs one version beside any others and sets the machine variables.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** the setup wizard and the installed state on Windows 11: folders, the machine variables, the Add/Remove Programs entry per version.
**Job:** a developer gets a working SDK with one setup. Consumer: the wizard and `sdk install`.
**Treatment:** the D03 T01 frame with the SDK's own brand, `PrivilegesRequired=admin`, a folder page defaulting to `C:\ResoluteSDK` only on the first install. Cheaper substitute that fails: a zip and a README asking for manual variables.
**Chrome:** Inno Setup's wizard; Welcome, folder (first install only), Ready, Installing (with the toolchain download's progress), Finished.

**Build order:**

1. Write `installer/sdk/installer.json` and the SDK's `[Code]`. Done when: the setup installs `1.0.0` beside a fake `0.9.0` and both stay.

- [ ] Give each minor line one fixed `AppId` GUID, recorded once in `installer/sdk/lines.json` (the SDK's exception to D03 T01 §5's one GUID per program), so a patch upgrades its line in place and lines install and uninstall independently (help: `AppId`). Done when: installing `1.4.1` over `1.4.0` leaves one entry `Resolute SDK 1.4`, beside `Resolute SDK 1.3`.
- [ ] Install the root files (`ResoluteToolchain.cmake`, `bin\`) with `Flags: sharedfile` so they stay until the last line is uninstalled (help: `[Files]` `sharedfile`). Done when: uninstalling either of two lines, in either order, leaves the other compiling.
- [ ] Write the root files only when the setup's version is newer than `RootVersion` in `HKLM\Software\Rizonesoft\ResoluteSDK`, through a `Check:` function, and record the new `RootVersion`, since Inno Setup replaces unversioned files regardless of age. Done when: installing `1.4` after `1.5` leaves the `1.5` root files in place and both lines build.
- [ ] Record the root in `HKLM\Software\Rizonesoft\ResoluteSDK\Root` and read it from there, never from the process environment; ask for the folder only when it is absent. Done when: a second line goes to the recorded root with no folder page, and a different `RESOLUTE_SDK` in the setup's own environment is ignored.
- [ ] Set the root's ACL at install: Administrators and SYSTEM full control, Users read and execute, inheritance from `C:\` removed, because a new folder in the root of `C:` inherits Modify for Authenticated Users and a writable `bin` on the machine PATH would let any user plant code others run. Refuse a chosen folder that a non-administrator can write, or whose any parent folder a non-administrator could rename or replace, after resolving junctions in the path. Done when: `icacls <root>` shows exactly those entries, a standard user cannot create a file in `bin`, and a protected folder under a user-writable parent is refused. Cheaper substitute: inheriting the drive root's permissions.
- [ ] Set `RESOLUTE_SDK` and add `<root>\bin` to the machine `Path` in `[Registry]` with `ChangesEnvironment=yes` (help: `ChangesEnvironment`), adding the entry once and removing only that entry later. Done when: a new terminal sees both with no sign-out, and unrelated `Path` entries are unchanged after install and uninstall.
- [ ] Register the consumer roots on a Finished-page field (default the drive holding the first consumer found, else none), stored as the machine's `ConsumerRoots`. Done when: `sdk prune` reads them back.
- [ ] Run the toolchain download on the Installing page through `bootstrap.ps1 -Store`, failing the setup with the component's name when it fails. Done when: an offline install stops naming the first component, and a silent one exits non-zero.
- [ ] Remove only that line's folder on uninstall, and the variables, `bin` and the toolchain store only with the last line. Done when: uninstalling `1.3` leaves `1.4` working.
- [ ] Offer "Remove versions nothing uses" on the Finished page only when consumer roots are registered, running `sdk prune` with its refusals (§5), never touching the line just installed. Done when: ticking it removes the fixture's unpinned line and keeps the new one.
- [ ] Add the cases to `scripts/tests/test_installer_roundtrip.py` as elevated-only cases. Done when: they pass on an elevated host.
- [ ] Commit: `installer: the SDK's own setup`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the SDK cases on an elevated host (both uninstall orders, the ACL read-back, `Path` entries preserved), and fails when uninstalling one line removes `RESOLUTE_SDK`.

## 7. Dev Override to a Working Checkout

While the SDK itself is changing, a program builds against the checkout with no link on disk.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Honour `RESOLUTE_SDK_DEV` in `ResoluteToolchain.cmake` and the package search. Done when: with it set to `D:\Resolute-SDK`, a consumer builds from the checkout and its `reskit/`.

- [ ] Make `ResoluteToolchain.cmake` use `$ENV{RESOLUTE_SDK_DEV}` first, with the checkout's `reskit/` as the toolchain. Done when: `sdk which` and configure both name the checkout.
- [ ] Set `ResoluteSDK_DIR` to `$ENV{RESOLUTE_SDK_DEV}/cmake` when the override is set (CMake's own `<PackageName>_DIR`). Done when: `find_package` loads the checkout's config.
- [ ] Print `Resolute-SDK DEV from <path> (RESOLUTE_SDK_DEV)` on every configure, and refuse the override in `scripts/package.ps1 -Publish`. Done when: a publish with the override set exits 1 naming it. Cheaper substitute: allowing it, which ships a program built from unreleased SDK code.
- [ ] Document setting and clearing it in `docs/sdk-install.md`. Done when: both commands are in the file.
- [ ] Add the cases to `scripts/tests/test_sdk_package.py`. Done when: they pass.
- [ ] Commit: `sdk: RESOLUTE_SDK_DEV for working on the SDK`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_sdk_package` passes the override cases, and fails when the publish refusal is removed.

## 8. Consumers Find the SDK by Version Line

A consumer names a line in `sdk.json` and the installed SDK does the rest.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write the consumer template and its migration. Done when: the fixture consumer builds with no `sdk/` folder.

- [ ] Change the `sdk.json` format to `{"version": "1.4"}`, keeping `repository` for CI, and drop `commit`. Done when: the schema in `docs/sdk-install.md` matches.
- [ ] Replace the consumer `CMakeLists.txt` include with `find_package(ResoluteSDK ${line} REQUIRED CONFIG)` and `resolute_sdk_add_libraries()`. Done when: the fixture configures.
- [ ] Replace every `${sourceDir}/sdk/reskit/...` in the consumer `CMakePresets.json` with `"toolchainFile": "$env{RESOLUTE_SDK}/ResoluteToolchain.cmake"`. Done when: the presets contain no `sdk/` path.
- [ ] Reduce the consumer `scripts/sdk.ps1` to `sdk which` plus `-Check`, failing when the pinned line is not installed. Done when: it no longer clones or links anything. Cheaper substitute: keeping the clone path as a fallback, which leaves two ways to get the SDK.
- [ ] Change every build entry point that starts tools itself (the launcher's `scripts/build.ps1` finds CMake, Ninja, Python and sccache under `sdk\reskit` and passes compiler paths explicitly) to take them from `sdk env -Json`. Done when: `rg "sdk[\\/]reskit"` finds nothing in the consumer template or the launcher.
- [ ] Point `brand/build.py` at the installed brand kit through `sdk which`. Done when: `python brand/build.py --check` works with no `sdk/` folder.
- [ ] Point `scripts/package.ps1` (D03 T01 §11) at the store's `ISCC.exe` and the version's `installer/Resolute.iss`. Done when: packaging the fixture finds both through the resolver.
- [ ] Add `scripts/tests/test_sdk_consumer.py` running `sdk.ps1 -Check` and configure in a fixture consumer with no `sdk/` folder, with the line installed and uninstalled. Done when: it passes.
- [ ] Commit: `sdk: consumers find the SDK by version line`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_sdk_consumer` passes, and fails when the consumer preset still names `sdk/reskit`.

## 9. CI Gets the Pinned Line from the Release Archive

A GitHub runner has no installer session, so it unpacks the same release archive the setup carries.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Write the CI step. Done when: a workflow run on a consumer builds against the pinned line from a clean runner.

- [ ] Make the release archive (§12) a relocatable root: `ResoluteToolchain.cmake`, `bin\` and `sdk\ResoluteSDK-<line>\`, with no toolchain inside. Done when: unpacked anywhere, `bin\sdk.cmd doctor` names only the missing store.
- [ ] Add `scripts/sdk-ci.ps1` that finds the pinned line's newest release in the signed feed, downloads the archive, checks its SHA-256 against the signed feed before unpacking, unpacks it under the runner's temp, runs `bootstrap.ps1 -Store`, and exports `RESOLUTE_SDK` and the `bin` path through `GITHUB_ENV` and `GITHUB_PATH`. Done when: a later step in the same job runs `sdk which`.
- [ ] Cache the root and store per line with `actions/cache` keyed on the archive's SHA-256 from the signed feed, which already identifies the `toolchain.json` inside it. Done when: a second clean runner restores both without fetching the archive or any component.
- [ ] Add the step to the consumer workflow template. Done when: the template names `sdk-ci.ps1` before configure.
- [ ] Add `scripts/tests/test_sdk_ci.py` running `sdk-ci.ps1` on a local fixture feed and archive, with a cache miss, then a corrupted archive. Done when: the good archive configures a fixture consumer and the corrupted one is refused before any file is unpacked.
- [ ] Commit: `ci: the pinned SDK line from the release archive`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_sdk_ci` passes, and fails when the digest check runs after unpacking.

## 10. A Packaged Program Carries What It Uses

Nobody installing a program installs the SDK: everything the program uses from it is in the program's own setup.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. List the SDK's runtime files and copy them at packaging. Done when: the fixture's setup installs and runs on a profile with no SDK.

- [ ] Keep linking the shared code statically through `resolute_sdk_add_libraries()`, and write `runtime-files.json` in each installed version naming every file a program needs at run time (none today). Done when: the file exists and `scripts/package.ps1` reads it.
- [ ] Copy each listed runtime file into the setup's `[Files]` in `scripts/package.ps1`. Done when: a fixture runtime file appears in `{app}`.
- [ ] Add a packaging check that the built executable imports no DLL from the SDK root or the store. Done when: a fixture linked to a store DLL fails packaging naming it. Cheaper substitute: trusting the static link, which a dynamic MinGW runtime breaks unseen.
- [ ] Add a round-trip case that installs the fixture's setup and starts it with `RESOLUTE_SDK` unset and the root renamed. Done when: it starts and exits 0.
- [ ] Commit: `installer: programs carry what they use from the SDK`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the no-SDK case, and fails when the executable is linked against a DLL in the store.

## 11. Junctions and RESOLUTE_SDK_DIR Retired

The old way goes away entirely, so there is one way to find the SDK.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Remove the link mode and the variable. Done when: no consumer and no script mentions `RESOLUTE_SDK_DIR`.

- [ ] Remove the clone and junction code from the consumer `scripts/sdk.ps1` template and from `scripts/start-run.ps1`. Done when: `rg RESOLUTE_SDK_DIR` finds nothing in the SDK.
- [ ] Add `scripts/sdk-unlink.ps1` that removes a consumer's `sdk/` only when it is a junction, deleting the link and never its target (`[System.IO.Directory]::Delete` on the link, non-recursive). Done when: run on a fixture junction, the link is gone and the target's files are all still there. Cheaper substitute: `Remove-Item -Recurse`, which can follow the link into the SDK checkout.
- [ ] Make `scripts/sdk-unlink.ps1` leave a cloned `sdk/` in place and name it for the developer to delete. Done when: a fixture clone is left and reported.
- [ ] Record each removed junction's target in `<consumer>\.git\sdk-unlink.json` and add `-Restore` to put it back. Done when: a fixture junction removed and restored points at the same target.
- [ ] Add `scripts/tests/test_sdk_unlink.py` making a temp junction and a temp clone. Done when: it passes.
- [ ] Commit: `sdk: retire the junction and RESOLUTE_SDK_DIR`

**Test checkpoint:** `python -m unittest scripts.tests.test_sdk_unlink` passes: the junction is removed with the target's file count unchanged and the clone is left; it fails when the unlink recurses into the target.

## 12. SDK Release Published to the Update Service

An SDK release is built, signed and published like any program, with the archive CI uses beside the setup.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Add the SDK as a product of the update service. Done when: `package.ps1 -Publish -Channel stable -WhatIf` in the SDK prints the setup and the archive uploads for product `resolute-sdk`.

- [ ] Tag the release `v<VERSION>` (the first is `v1.0.0`, once §2 to §6 have landed) and push the tag. Done when: `git ls-remote --tags origin v1.0.0` prints it.
- [ ] Build `dist/ResoluteSDK-<version>-Setup.exe` with `scripts/package.ps1`, from a tagged commit only. Done when: an untagged commit refuses to package naming `VERSION`.
- [ ] Build `dist/ResoluteSDK-<version>.zip`, the relocatable root of §9. Done when: its file list equals an installed root's minus the store.
- [ ] Publish both through the Updates repository's `scripts/publish.py` as product `resolute-sdk`, the archive with `--file`, and the feed's `lines` entry for the release's minor line naming its newest patch; the toolchain pins stay in the archive's `toolchain.json`. Done when: the feed at `https://updates.rizonesoft.com/v1/resolute-sdk/stable/feed.json` lists the release under both `version` and `lines`.
- [ ] Add a `docs/sdk-install.md` release checklist: bump `VERSION`, `CHANGELOG.md`, tag, package, publish, roll out (§15). Done when: the checklist is in the file.
- [ ] Commit: `sdk: releases published to the update service`

**Test checkpoint:** `pwsh scripts/package.ps1 -Publish -Channel stable -WhatIf` in the SDK exits 0 listing both files, and exits 1 on an untagged commit.

## 13. Notice When a Newer SDK Release Exists

The developer learns a newer SDK exists without any program installing it on its own.

**Phase:** 5
**Needs:** none
**Surface:** yes
**Fidelity:** the line printed by `sdk list`, `sdk doctor` and the configure step in a terminal.
**Job:** a developer sees that a newer line or patch is out, and the command to get it. Consumer: the developer at a terminal.
**Treatment:** one line, at most once a day, from the signed stable feed; never downloads. Cheaper substitute that fails: an automatic upgrade, which the operator ruled out for programs on 2026-11-18.
**Chrome:** none; console output.

**Build order:**

1. Add the check to `bin/sdk.ps1` and `ResoluteToolchain.cmake`. Done when: with a fixture feed newer than the installed version, both print the notice once.

- [ ] Fetch and verify the `resolute-sdk` feed at most once a day per user, caching the answer and the time of the last attempt, failed ones included, under `%LOCALAPPDATA%\ResoluteSDK\feed.json`, since the install root is read-only to users. Skip the check inside compiler probes. Done when: two offline configures by a standard user within the day make one request.
- [ ] Print `Resolute-SDK <new> is available: sdk install <line>` from `sdk list`, `sdk doctor` and configure. Done when: the fixture shows the line.
- [ ] Stay silent offline, on a failed signature and when `RESOLUTE_SDK_NO_UPDATE_CHECK=1`. Done when: each fixture case prints nothing and logs one line.
- [ ] Commit: `sdk: notice when a newer release exists`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_sdk_command` passes the notice cases, and fails when a tampered feed still prints a notice.

## 14. Every Consumer Moved to the Installed SDK

The launcher and every tool build against the installed SDK, and no junction is left on the machine.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/sdk-migrate.py` and run it. Done when: every consumer pins a line, has no `sdk/` and passes its brand check.

- [ ] Write `scripts/sdk-migrate.py` applying §8's changes to a consumer. Done when: a dry run lists each consumer under the registered roots with its current commit and the line it would pin.
- [ ] Install the first release with its own setup on this machine. Done when: `sdk doctor` exits 0.
- [ ] Migrate the launcher first, in its working copy with the junction still in place, then build it through its own entry point (`scripts/build.ps1`) with `sdk/` renamed aside. Unlink with `sdk-unlink.ps1` only after that build passes, then commit and push. Done when: `D:\Resolute` builds in Release with no `sdk/` folder and `git status -sb` reads `## main...origin/main`. Cheaper substitute: unlinking first, which leaves the launcher unbuildable if the new path fails.
- [ ] Migrate every `D:\Resolute_Bin\<Tool>` the same way: change, check (`sdk.ps1 -Check`, `brand/build.py --check`) with `sdk/` renamed aside, unlink, commit, push. A consumer whose check fails keeps its junction and is reported. Done when: every tool is clean, pushed and has no `sdk/`, or is named in the report.
- [ ] Remove the user variable `RESOLUTE_SDK_DIR` once every consumer has moved. Done when: `[Environment]::GetEnvironmentVariable('RESOLUTE_SDK_DIR','User')` is empty.
- [ ] Commit: `sdk: migrate every consumer to the installed SDK`

**Test checkpoint:** `python scripts/sdk-migrate.py --check` exits 0 reporting every consumer on a line with no junction, and exits 1 naming any consumer that still has `sdk/`.

## 15. Release Rollout Moves Every Consumer to a New Line

Each SDK release moves every program to the new line together, so only one or two versions are ever installed.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/sdk-rollout.py`. Done when: after a fixture release `1.5.0`, a dry run lists each consumer moving from `1.4` to `1.5`.

- [ ] Write `scripts/sdk-rollout.py <line>` with a preflight that, for every consumer, sets the new line in a scratch copy, rebuilds its brand assets and runs its quick checks against the installed line, changing no repository. Done when: the preflight reports every consumer pass or fail. Cheaper substitute: a hand loop per release, which leaves programs behind.
- [ ] Run the preflight with `RESOLUTE_SDK_DEV` cleared, asserting that each consumer resolves to the installed line's folder, and build the launcher through its own entry point (`scripts/build.ps1`) before the first push. Done when: a fixture run with the override set still checks against the installed line and prints its path.
- [ ] Push nothing when any consumer fails the preflight, and name each failure. Done when: a fixture with one failing consumer leaves every repository unchanged.
- [ ] After a clean preflight, commit and push each consumer, writing the intended old and new commits to `%LOCALAPPDATA%\ResoluteSDK\rollout\<line>.jsonl` before each push and marking it done after, so an interrupted run resumes where it stopped. Done when: a fixture run killed between a push and its mark resumes, sees the remote already moved and finishes the rest.
- [ ] Run `sdk prune` only after every consumer's remote pin is confirmed on the new line. Done when: the old line is removed from the fixture root only then.
- [ ] Add `scripts/tests/test_sdk_rollout.py` with three fixture consumers, one with a failing check, and an interrupted run. Done when: it passes.
- [ ] Commit: `sdk: release rollout to every consumer`

**Test checkpoint:** `python -m unittest scripts.tests.test_sdk_rollout` passes, and fails when a failing preflight still pushes any consumer.

## Verification

- A clean Windows 11 machine runs the SDK setup once and then builds any consumer from a clean clone with no `sdk/` folder.
- Two SDK lines install side by side, `sdk prune` keeps only what consumers pin, and a program's setup runs on a PC with no SDK.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
