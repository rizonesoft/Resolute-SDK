---
schema_version: 1
id: installer-shape
domain: 03-installer
status: active
title: "TODO-01 -- One installer shape for every Windows program"
---

# TODO-01 -- One installer shape for every Windows program

> **Goal:** Every Windows program that pins Resolute-SDK (the launcher, the 78 tools in `D:\Resolute_Bin` and any other desktop program built on the SDK) ships one installer built from one shared Inno Setup script in the SDK. It shows a shared suite frame carrying that program's own icon, wordmark and accent in light and dark, installs per user by default with an all-users choice, upgrades in place keeping settings, offers a portable extract, runs silently for scripts and winget, and the program itself notifies (never downloads) when a newer release exists. A program adopts all of it with one `installer.json` and an `sdk.json` bump.

> **Current state:** Measured 2026-11-18. The SDK has no installer code, no `installer/` folder and no Inno Setup pin in `toolchain.json`; Inno Setup is not installed on the build host. Every tool already has `brand/<tool>.ico`, `brand/<tool>-icon.svg` and light and dark wordmarks built by `brand/brandkit.py`. The only prior art is `D:\Resolute-Classic\Resolute_setup.iss` (Inno Setup 5 era, `WizardStyle=modern`, one `WizardSmallImageFile` BMP, `Uninstallable = no`, copied from a Notepad3 script). The operator chose on 2026-11-18: Inno Setup branded (not a custom `resolute-ui` installer, WiX or MSIX); a shared frame with each tool's brand and a setup badge on the setup icon (no bespoke art per tool); per-user default with an all-users option; and silent switches with winget, a portable option, in-place upgrade and an update check that only notifies. The operator set the engine to the latest Inno Setup, 7.1.1 (2026-10-28), which carries PNG wizard images (6.5.2), `WizardStyle=modern dynamic` with `*DynamicDark` image and colour directives and the `windows11` style (6.6.0), `WizardBackImageFile` with `WizardBackColor` (6.7.0), the `stellar` style and a 64-bit Setup through `SetupArchitecture=x64` (7.0.0), and the long-form `ISCC` options such as `--quiet` and `--messages-jsonl` (7.1.0), per https://jrsoftware.org/files/is7-whatsnew.htm.

## Inputs

- `DESIGN.md`: the suite's design contract; section 17 is the installer contract §2 recorded, exact to the unit.
- `docs/captures/installer/reference/`: `make_reference.py`, the reference implementation of section 17, and the PNGs and `.ico` it writes for MemBoost, Firemin and Sleep and Wake Diagnostics. §3 and §4 must reproduce them pixel for pixel.
- `docs/installer.md`: the adoption guide; each section below updates the part it builds.
- `brand/brandkit.py`: the asset builder every repository runs; §3 and §4 extend it.
- `toolchain.json` and `scripts/bootstrap.ps1`: the pin format and the hash-checked download that §1 follows.
- `D:\Resolute-Classic\Resolute_setup.iss`: prior art for directives and messages only; nothing is copied without reading it.
- Inno Setup help for the pinned version (`ISCC.exe` ships `ISetup.chm`; online at https://jrsoftware.org/ishelp/): the source cited for every directive, image size and command-line switch.
- Signing material stays in each program's private repository or local config, never in this public MIT repository (see `D:\Resolute-Classic` leaving out `SDK/Signing`).

## Outcome

- `scripts/package.ps1` in a consumer builds `<Tool>-<version>-Setup.exe` from that consumer's `installer.json` and `brand/`, with no per-tool `.iss` file.
- The setup wizard shows the shared frame with the tool's icon, wordmark and accent, and follows the Windows light or dark setting.
- Install, upgrade, uninstall, portable extract and the silent forms all leave a read-back state (files, shortcuts, the Add/Remove Programs entry) that a test checks.
- A winget manifest is generated per release, and an installed program shows a notice when the release feed names a newer version.

**Adjacency:** list=not-applicable (an installer holds no records to find); document=not-applicable (nothing is printed or carried beyond the setup file itself); settings=applicable @ D03 T01 §14; reporting=not-applicable (no data is summarised); notifications=applicable @ D03 T01 §14; permissions=applicable @ D03 T01 §7; audit=applicable @ D03 T01 §6; exchange=applicable @ D03 T01 §12; reverse=applicable @ D03 T01 §6

**Adjacency rationale:** The reverse of an install is its uninstaller, owned by §6, and the Inno Setup log (`/LOG`) is the diagnostic trail. Permissions are the per-user and all-users modes and the elevation each needs, owned by §7. Exchange is the winget manifest, §12. The one setting and the one notice are the update check: on by default, switchable off, notify only, owned by §14.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Inno Setup pinned in the toolchain | -- | [ ] |
| 2 | §2 | Installer frame approved in DESIGN.md | -- | [ ] |
| 3 | §3 | Wizard images built from each tool's brand | §2 | [ ] |
| 4 | §4 | Setup icon with the setup badge | §2 | [ ] |
| 5 | §5 | Per-program installer.json schema | -- | [ ] |
| 6 | §6 | Shared Inno script: install, uninstall, shortcuts | §1, §3, §4, §5 | [ ] |
| 7 | §7 | Per-user default with an all-users choice | §6 | [ ] |
| 8 | §8 | In-place upgrade that keeps settings | §6 | [ ] |
| 9 | §9 | Portable extract option | §6 | [ ] |
| 10 | §10 | Silent install and uninstall proven | §7, §8, §9 | [ ] |
| 11 | §11 | Packaging script and signing hook | §6 | [ ] |
| 12 | §12 | winget manifest per release | §10, §11 | [ ] |
| 13 | §13 | Release feed format and host | -- | [ ] |
| 14 | §14 | Notify-only update check in the UI library | §13 | [ ] |
| 15 | §15 | MemBoost pilot, end to end | §10, §11, §12, §14, §17 | [ ] |
| 16 | §16 | Rollout to every consumer | §15 | [ ] |
| 17 | §17 | Setup warns when a newer version exists | §6, §13 | [ ] |

## 1. Inno Setup Pinned in the Toolchain

The compiler is pinned like every other build tool, so a clean clone builds the same installer without a system-wide install.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Add an `innosetup` component to `toolchain.json` at 7.1.1. Done when: `scripts/bootstrap.ps1` downloads it hash-checked into `reskit/innosetup/`.
2. Teach `scripts/cpp-env.ps1` to report it. Done when: it fails by name when `ISCC.exe` is missing or off the pin.

- [ ] Add the `innosetup` entry to `toolchain.json` with version `7.1.1`, the jrsoftware.org URL, `sha256` and `bytes` taken from a real download, `dir` `innosetup` and `probe` `ISCC.exe`. Done when: the entry validates under the existing format. Cheaper substitute: a pin with no hash, which `toolchain.json`'s own comment refuses.
- [ ] Extend `scripts/bootstrap.ps1` to unpack the Inno Setup installer into `reskit/innosetup/` without touching the registry or Program Files (`/PORTABLE=1 /DIR=... /VERYSILENT /CURRENTUSER`, per the Inno Setup help for setup command-line parameters). Done when: `reskit\innosetup\ISCC.exe` exists and no `Inno Setup 6` uninstall key is written. Cheaper substitute: requiring a system install, which the bootstrap forbids.
- [ ] Add the component to `scripts/cpp-env.ps1` and `scripts/toolchain-latest.ps1`. Done when: `cpp-env.ps1` prints the Inno Setup version and `toolchain-latest.ps1` says whether 7.1.1 is behind.
- [ ] Commit: `toolchain: pin Inno Setup 7.1.1`

**Test checkpoint:** `pwsh scripts/cpp-env.ps1` exits 0 and lists `innosetup 7.1.1`; renaming `reskit\innosetup\ISCC.exe` makes it exit non-zero naming `innosetup`.

## 2. Installer Frame Approved in DESIGN.md

The operator approves design in session, by multiple choice with the recommendation first, from comparison boards. This section produces the boards and records the chosen frame in the contract, so §3 and §4 build to a decision rather than a guess.

**Phase:** 5
**Needs:** none
**Surface:** yes
**Fidelity:** the welcome, ready, progress and finish pages of a real Inno Setup 7.1.1 wizard, light and dark, at 100% and 200% scale.
**Job:** a person sees which program they are installing and that it belongs to the suite. Consumer: the wizard window.
**Treatment:** a shared frame (style, background, layout) with the tool's icon, wordmark and accent as the only per-tool parts. Cheaper substitute that fails: one generic image for every tool, which the operator ruled out on 2026-11-18.
**Chrome:** Inno Setup's own wizard controls and buttons; nothing is drawn over them.

**Decision:** the operator chose frame A, Graphite panel, and setup-icon badge 1, Graphite arrow, on 2026-11-18 from real 7.1.1 wizards for MemBoost and Firemin (captures in `docs/captures/installer/`). `DESIGN.md` section 17 records it.

**Build order:**

1. Render three or four frame candidates on two sample tools as boards in `docs/captures/installer/`. Done when: each board shows all four pages in both themes.
2. Record the chosen frame as a new `DESIGN.md` section. Done when: it names the `WizardStyle`, every image directive with its pixel sizes per scale, the colours, and which parts come from the tool's brand.

- [x] Build candidate frames from Inno Setup directives: `WizardStyle` (`modern dynamic` with a built-in style such as `windows11`), `WizardImageFile`, `WizardSmallImageFile`, `WizardBackImageFile`, `WizardBackColor`, their `DynamicDark` forms and `WizardImageOpacity` (all per the 7.1.1 help). Done when: each candidate compiles and runs on the host. Cheaper substitute: mock-ups drawn outside Inno Setup, which do not show what the engine can really do.
- [x] Capture every page of each candidate for MemBoost and one more tool in light and dark to `docs/captures/installer/`. Done when: the boards exist with their provenance.
- [x] Ask the operator which frame, in session, recommendation first. Done when: the answer is recorded in this section's body with the date and `owner-decision` is removed from Needs.
- [x] Write the chosen frame into `DESIGN.md` with exact image sizes per DPI read from the Inno Setup help for the pinned version. Done when: `python scripts/design-lint.py` passes on it.
- [x] Make section 17 exact enough to build 1:1: geometry, the long-name and credit fitting rules, the per-size viewBox, badge geometry, file names and the `[Setup]` block, with a reference renderer and reference PNGs. Done when: the references render at every listed size with no pixel off, and the longest name (Sleep and Wake Diagnostics) fits on two lines.
- [x] Commit: `design: the installer frame`

**Test checkpoint:** `python scripts/design-lint.py` exits 0 and `DESIGN.md` contains the installer section naming every image directive and size the boards used.

## 3. Wizard Images Built from Each Tool's Brand

The wizard images come out of `brandkit.py` like every other brand asset, so a tool's installer art changes when its icon does and never drifts.

**Phase:** 5
**Needs:** none
**Surface:** yes
**Fidelity:** the images at the sizes `DESIGN.md` records in §2, light and dark.
**Job:** the wizard shows the tool's own icon, wordmark and accent. Consumer: the `[Setup]` image directives in §6.
**Treatment:** generated PNGs from `brand/<tool>-icon.svg`, the wordmarks and the accent. Cheaper substitute that fails: hand-exported images committed per tool.
**Chrome:** none; these are image assets.

**Build order:**

1. Add an installer target to `brand/brandkit.py`. Done when: a run writes `brand/installer/` with every image §2 names, in both themes and every listed scale.

- [ ] Port the side panel and header icon from `docs/captures/installer/reference/make_reference.py` into `brand/brandkit.py`, called from `app_assets` so `build.py` and `build.py --check` cover `brand/installer/` (`DESIGN.md` 17.2, 17.3, 17.6), with one SVG per size on its own viewBox (17.2) and `WizardImageStretch=no` in §6. Done when: `brand/installer/` holds every file at its exact listed pixel size. Cheaper substitute: three sizes left to Setup to stretch, which blurred and distorted the icon in the first board (operator, 2026-11-18), or one 164 by 314 drawing scaled by width, which comes out a pixel tall at five of the seven sizes.
- [ ] Add an `accent` argument to `app_assets` (`DESIGN.md` 17.4), falling back to the first colour of the detailed drawing. Done when: MemBoost and Firemin get `#0284C7` and `#EA580C` with no `accent` given, and a given `accent` wins.
- [ ] Add `scripts/tests/test_brandkit_installer.py` comparing brandkit's side panels and header icons for the three reference tools with the reference PNGs pixel for pixel, checking every size, and checking a three-line name fails by name. Done when: it passes, and fails when one unit of 17.2 changes in the builder without the references.
- [ ] Commit: `brand: installer images from each tool's brand`

**Test checkpoint:** `python -m unittest scripts.tests.test_brandkit_installer` passes and fails when one image size is altered.

## 4. Setup Icon with the Setup Badge

The setup file must not look like the program in a Downloads folder. A small badge on the tool's own icon marks it as the installer.

**Phase:** 5
**Needs:** none
**Surface:** yes
**Fidelity:** `brand/installer/<tool>-setup.ico` at every `brandkit.ICO_SIZES` frame (16 to 256 px), beside `brand/<tool>.ico` in Explorer.
**Job:** a person tells the setup file from the program at a glance. Consumer: `SetupIconFile` in §6.
**Treatment:** the tool icon with the badge §2 approves, rendered per size. Cheaper substitute that fails: the plain tool icon.
**Chrome:** none.

**Build order:**

1. Add a setup-icon target to `brand/brandkit.py`. Done when: it writes `<tool>-setup.ico` with every listed size.

- [ ] Port badge 1 from the reference script into `brandkit.py` with the geometry in `DESIGN.md` 17.5, drawn per frame on the detailed or small drawing. Done when: the 16 px frame keeps the badge legible. Cheaper substitute: scaling the 256 px frame down, which loses the badge at 16 px.
- [ ] Add the setup icon to `scripts/tests/test_brandkit_installer.py`: every `ICO_SIZES` frame present, and the 256, 32 and 16 px frames equal to the reference `setup-<size>.png` pixel for pixel. Done when: it fails if a size is missing or the badge moves.
- [ ] Commit: `brand: setup icon with the setup badge`

**Test checkpoint:** `python -m unittest scripts.tests.test_brandkit_installer` passes with a case reading every frame size from the `.ico`.

## 5. Per-Program installer.json Schema

One small file per program says what differs: name, identifiers, executable, shortcuts. Everything else is the shared shape.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Write `installer/installer.schema.json` and a validator. Done when: a valid file passes and each missing or malformed field is refused by name.

- [ ] Define the fields in `installer/installer.schema.json`: `name`, `appId` (a GUID, fixed for the life of the program), `exe`, `publisher`, `homepage`, `wingetId`, `feedUrl`, optional `startMenu` and `desktopShortcut`. Done when: the schema documents each field in one line.
- [ ] Add `scripts/installer_config.py` loading and validating a consumer's `installer.json`, reading the version from the built executable. Done when: an invalid file exits 2 naming the field. Cheaper substitute: reading the version from `installer.json`, which drifts from the binary.
- [ ] Add `scripts/tests/test_installer_config.py` with a valid fixture and one fixture per refusal. Done when: it passes.
- [ ] Commit: `installer: the per-program installer.json`

**Test checkpoint:** `python -m unittest scripts.tests.test_installer_config` passes, and fails when the `appId` check is removed.

## 6. Shared Inno Script: Install, Uninstall, Shortcuts

One `.iss` in the SDK, driven by defines from `installer.json` and the brand images, builds every program's setup. It installs the executable, creates shortcuts, registers the uninstaller and the Add/Remove Programs entry, and logs.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** the installed state on Windows 11: files, Start menu shortcut, Add/Remove Programs entry with the tool icon, and the uninstaller removing all of it.
**Job:** a person installs and later removes the program cleanly. Consumer: the wizard and Settings > Apps.
**Treatment:** the §2 frame, `SetupIconFile` from §4, `UninstallDisplayIcon` pointing at the installed executable. Cheaper substitute that fails: `Uninstallable=no` as in the classic script.
**Chrome:** Inno Setup's wizard; welcome, ready, progress and finish pages only, no license or components page.

**Build order:**

1. Write `installer/Resolute.iss`. Done when: ISCC builds a setup for a fixture program from defines alone.
2. Prove install and uninstall on the host. Done when: a test reads back every file, shortcut and registry value and finds none after uninstall.

- [ ] Write `installer/Resolute.iss` taking `AppName`, `AppId`, `AppVersion`, `AppExe` and the image paths as `/D` defines. Done when: `ISCC.exe --messages-jsonl` compiles it for the fixture with no warning entries. Cheaper substitute: a per-tool copy of the script.
- [ ] Set the `[Setup]` frame directives exactly as `DESIGN.md` 17.1 lists them, and only those. Done when: a capture of the fixture wizard at 100% and 200% shows the side panel equal to its `side-202.png` and `side-430.png` pixel for pixel (17.8), in light and dark.
- [ ] Set `SetupArchitecture=x64` so Setup is 64-bit and `ArchitecturesAllowed` and `ArchitecturesInstallIn64BitMode` default to `x64compatible` (7.0.0, help: `SetupArchitecture`), with no Pascal use of the removed `EnableFsRedirection`. Done when: the uninstall key is written to the 64-bit view and `Setup.exe` is a PE32+ image. Cheaper substitute: a 32-bit Setup relying on file-system redirection.
- [ ] Add `scripts/tests/test_installer_roundtrip.py` installing the fixture silently into a temp per-user location, reading back files, the shortcut and the `Uninstall\<AppId>_is1` key, then uninstalling and checking each is gone, with every started process tree killed on timeout. Done when: it passes, and fails if the uninstaller leaves the executable.
- [ ] Commit: `installer: the shared Inno Setup script`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes, and fails when `[UninstallDelete]` or the `[Icons]` entry is removed.

## 7. Per-User Default with an All-Users Choice

Installs go to `%LOCALAPPDATA%\Programs\<Tool>` with no admin prompt by default; an all-users install to Program Files is one choice or switch away.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** the Inno Setup install-mode dialog, and both installed states.
**Job:** a person installs without admin rights, or for every user of the PC. Consumer: the wizard and `/CURRENTUSER` and `/ALLUSERS`.
**Treatment:** `PrivilegesRequired=lowest` with `PrivilegesRequiredOverridesAllowed=dialog commandline` (help: `PrivilegesRequiredOverridesAllowed`), `DefaultDirName={autopf}\{#AppName}`. Cheaper substitute that fails: `PrivilegesRequired=admin`.
**Chrome:** Inno Setup's own mode dialog.

**Build order:**

1. Set the privilege directives in `installer/Resolute.iss`. Done when: a default run writes under `%LOCALAPPDATA%\Programs` and HKCU, and `/ALLUSERS` writes under Program Files and HKLM.

- [ ] Set `PrivilegesRequired`, `PrivilegesRequiredOverridesAllowed` and `{autopf}`, `{autoprograms}` paths in `installer/Resolute.iss`. Done when: both modes read back correctly.
- [ ] Extend `scripts/tests/test_installer_roundtrip.py` with the per-user case and an elevated all-users case marked to run only when the session is elevated. Done when: the per-user case runs everywhere and the all-users case runs on an elevated host.
- [ ] Commit: `installer: per-user by default, all-users on request`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the per-user case without elevation, and fails if `PrivilegesRequired=admin` is set.

## 8. In-Place Upgrade That Keeps Settings

Running a newer setup over an installed version closes the running program, replaces it in the same folder and keeps the user's settings.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** no

**Build order:**

1. Configure upgrade behaviour in `installer/Resolute.iss`. Done when: installing version N+1 over N leaves one Add/Remove Programs entry at N+1 and the settings file unchanged.

- [ ] Rely on the fixed `AppId` from `installer.json` and set `UsePreviousAppDir=yes`, `CloseApplications=force` and `RestartApplications=yes` (help: `CloseApplications`). Done when: a running fixture is closed and restarted by the upgrade.
- [ ] Refuse a downgrade unless `/ALLOWDOWNGRADE` is passed, in a `[Code]` `InitializeSetup` check against the installed `DisplayVersion`. Done when: running N over N+1 shows a refusal and changes nothing.
- [ ] Keep settings out of the install folder's delete lists, and leave them on uninstall unless the user ticks "remove settings". Done when: the round-trip test reads the settings file back after an upgrade. Cheaper substitute: storing settings in the install folder.
- [ ] Add the upgrade and downgrade cases to `scripts/tests/test_installer_roundtrip.py`. Done when: they pass.
- [ ] Commit: `installer: in-place upgrade that keeps settings`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the upgrade case, and fails if `AppId` is derived from the version.

## 9. Portable Extract Option

Each program is already one standalone executable, so the installer offers "portable": copy the files to a chosen folder with no shortcuts, registry or uninstaller.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** a choice on the welcome or directory page, and the extracted folder.
**Job:** a person runs the program from a USB stick or a folder of their choice. Consumer: the wizard and `/PORTABLE=1`.
**Treatment:** a `[Code]` choice that skips `[Icons]`, `[Registry]` and the uninstaller (`Uninstallable` as a scripted check, help: `Uninstallable`). Cheaper substitute that fails: a separate zip that bypasses the installer frame.
**Chrome:** one radio pair: "Install" (default) and "Portable".

**Build order:**

1. Add the portable path to `installer/Resolute.iss`. Done when: a portable run writes only the program files to the chosen folder.

- [ ] Add the portable choice and the `/PORTABLE=1` switch in `[Code]`. Done when: the choice appears and the switch selects it silently.
- [ ] Add a portable case to `scripts/tests/test_installer_roundtrip.py` asserting no `Uninstall` key and no shortcut. Done when: it passes.
- [ ] Commit: `installer: portable extract`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the portable case, and fails if `[Icons]` runs in portable mode.

## 10. Silent Install and Uninstall Proven

Scripted and fleet installs need every mode to run with no window and a meaningful exit code.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Document and test the switch set. Done when: `docs/installer.md` lists each switch and the tests run each one.

- [ ] Complete the switch table in `docs/installer.md` (it lists `/VERYSILENT`, `/SUPPRESSMSGBOXES`, `/NORESTART`, `/CURRENTUSER`, `/ALLUSERS`, `/DIR=`, `/PORTABLE=1`, `/LOG=`, `/ALLOWDOWNGRADE` and the uninstaller's switches) with exit codes, citing the Inno Setup help, and drop its "nothing is built yet" status line once §15 lands. Done when: every switch in the file is exercised by a test.
- [ ] Add silent cases to `scripts/tests/test_installer_roundtrip.py` checking exit code 0 and no visible window. Done when: they pass.
- [ ] Commit: `installer: silent switches documented and proven`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes all silent cases.

## 11. Packaging Script and Signing Hook

A consumer runs one command to get its setup file. Signing is a hook the consumer fills from its own private config; the SDK holds no key.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/package.ps1`. Done when: in a consumer it builds the release executable's setup into `dist/`.

- [ ] Write `scripts/package.ps1` that validates `installer.json` (§5), runs `brandkit.py` for the installer images (§3, §4) and calls `reskit\innosetup\ISCC.exe --quiet --messages-jsonl` on `sdk/installer/Resolute.iss` and fails on any error or warning line. Done when: it writes `dist/<Tool>-<version>-Setup.exe`.
- [ ] Add an optional `SignTool` hook read from an environment variable or the consumer's untracked `signing.local.json`, applied to setup and uninstaller (help: `SignTool`, `SignedUninstaller`). Done when: with no hook set the build succeeds unsigned and says so in one line. Cheaper substitute: a certificate path in the SDK.
- [ ] Add `scripts/tests/test_package.py` packaging the fixture. Done when: it passes and the output's version matches the executable.
- [ ] Commit: `installer: package.ps1 and the signing hook`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_package` passes, and fails if the version is read from anywhere but the executable.

## 12. winget Manifest per Release

Each release produces a winget manifest set from `installer.json` and the built setup, ready to submit.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/winget-manifest.py`. Done when: it writes a version, installer and locale manifest for the fixture that `winget validate` accepts.

- [ ] Write `scripts/winget-manifest.py` emitting the current winget manifest schema with `InstallerType: inno`, both `Scope` values, the SHA-256 of the setup and the release URL. Done when: `winget validate --manifest dist\winget\...` passes.
- [ ] Add `scripts/tests/test_winget_manifest.py`. Done when: it passes and fails when the hash does not match the file.
- [ ] Commit: `installer: winget manifest per release`

**Test checkpoint:** `winget validate --manifest <generated folder>` exits 0, and `python -m unittest scripts.tests.test_winget_manifest` passes.

## 13. Release Feed Format and Host

The operator decided on 2026-11-18: feeds and setup downloads are served from a Cloudflare Worker and R2 at `https://updates.rizonesoft.com`, run by the private `rizonesoft/Updates` repository (`D:\Updates`, `todo/00-service/TODO-01-update-service.md`), with an Ed25519 signed feed and `stable` and `beta` channels. This section makes the SDK speak that contract and publish to it.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Vendor the v1 feed schema and the public key, and publish from `package.ps1`. Done when: a fixture build validates its feed against the vendored schema and calls the publisher in dry-run.

- [ ] Copy `schema/feed-v1.schema.json` and `keys/feed-ed25519.pub` from the Updates repository into `installer/feed/`, recording their source commit in `installer/feed/SOURCE`. Done when: both files and the commit are present. Cheaper substitute: a second hand-written schema in the SDK that drifts.
- [ ] Set `feedUrl` in `installer.json` to `https://updates.rizonesoft.com/v1/<product>/<channel>/feed.json`, with `<channel>` filled at run time. Done when: `scripts/installer_config.py` refuses any other host.
- [ ] Add `-Publish` and `-Channel stable|beta` to `scripts/package.ps1`, calling the Updates repository's `scripts/publish.py` after a successful build. Done when: `-Publish -WhatIf` prints the upload it would make.
- [ ] Commit: `installer: the Updates feed contract and publish step`

**Test checkpoint:** `python -m unittest scripts.tests.test_package` passes with a case validating a written feed against `installer/feed/feed-v1.schema.json`, and fails when `feedUrl` names another host.

## 14. Notify-Only Update Check in the UI Library

An installed program checks its feed at most once a day and shows a notice with a link to the release page when a newer version exists. It never downloads or installs anything (operator, 2026-11-18).

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** a non-modal notice in a real tool window, light and dark.
**Job:** a person learns a newer version exists and can open its page. Consumer: the tool window.
**Treatment:** a quiet notice with "View release" and "Dismiss", once per new version; a setting "Check for updates" on by default. Cheaper substitute that fails: a modal dialog on start, or downloading the setup.
**Chrome:** the library's own notice control.

**Build order:**

1. Add the check and the notice to `shared/resolute-ui`. Done when: with a fixture feed newer than the build the notice shows, and with it equal or older nothing shows.

- [ ] Add `rui::UpdateCheck` fetching `feedUrl` and its `.sig` over HTTPS with WinHTTP on a background thread, at most once per 24 hours, silent on any network or parse failure. Done when: an offline run shows nothing and logs one line.
- [ ] Verify the feed's Ed25519 signature against the public key embedded from `installer/feed/feed-ed25519.pub`, and open only `releaseUrl` values on `rizonesoft.com`. Done when: a tampered fixture feed shows no notice and logs the refusal. Cheaper substitute: trusting HTTPS alone.
- [ ] Add an "Update channel" setting (`Stable` default, `Beta`) beside "Check for updates". Done when: switching to Beta reads the beta feed, read back after restart.
- [ ] When the running version is listed in `yanked`, show the notice with the yank reason even if it was dismissed. Done when: a fixture with the running version yanked shows the reason.
- [ ] Add the notice and the "Check for updates" setting, persisted with the tool's other settings. Done when: turning it off stops the request, read back from settings after restart.
- [ ] Open `releaseUrl` in the default browser on "View release" and remember a dismissed version. Done when: a dismissed version never shows again and a newer one does.
- [ ] Add unit tests for version comparison, throttling and dismissal. Done when: `ctest -L update` passes and fails if a download path is added.
- [ ] Commit: `ui: notify-only update check`

**Test checkpoint:** `reskit\cmake\bin\ctest.exe --preset debug -L update` passes, including a case that the check makes exactly one GET to `feedUrl` and writes no file outside settings.

## 15. MemBoost Pilot, End to End

One real tool goes through the whole shape before the other programs adopt it.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** `D:\Resolute_Bin\MemBoost` built, packaged, installed, upgraded, notified, uninstalled on Windows 11.
**Job:** the operator sees the finished installer on a real tool. Consumer: the operator.
**Treatment:** MemBoost's own `installer.json` and brand, nothing pilot-specific in the SDK. Cheaper substitute that fails: the test fixture standing in for a real tool.
**Chrome:** the §2 frame.

**Build order:**

1. Adopt the shape in MemBoost. Done when: `scripts/package.ps1` in MemBoost writes a setup, and each mode works on the host.

- [ ] Add `installer.json` to `D:\Resolute_Bin\MemBoost` and bump its `sdk.json` to the SDK commit carrying §1 to §14. Done when: `pwsh scripts/package.ps1` writes `dist/MemBoost-<version>-Setup.exe`.
- [ ] Install, upgrade, run portable, and uninstall MemBoost, capturing each wizard page in light and dark to `docs/captures/installer/memboost/`. Done when: the captures pass the `DESIGN.md` 17.8 check.
- [ ] Show the operator the captures. Done when: their approval or changes are recorded here with the date.
- [ ] Commit: `installer: MemBoost pilot`

**Test checkpoint:** in `D:\Resolute_Bin\MemBoost`, `pwsh scripts/package.ps1` exits 0 and the SDK's round-trip test passes against the MemBoost setup.

## 16. Rollout to Every Consumer

After the pilot, every program that pins the SDK adopts the installer the same way.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `scripts/installer-rollout.py`. Done when: it writes `installer.json` for each consumer from its existing metadata and bumps `sdk.json`, then each repository packages.

- [ ] Write `scripts/installer-rollout.py` that generates `installer.json` (new fixed `appId` per program, recorded once) for the launcher, every `D:\Resolute_Bin\<Tool>` and every other repository whose `sdk.json` pins this SDK. Done when: a dry run lists each repository and the file it would write.
- [ ] Run it, package each repository, commit and push each, checking `git status -sb` reads `## main...origin/main`. Done when: every consumer has a setup in `dist/` and a clean tree.
- [ ] Commit: `installer: rollout script`

**Test checkpoint:** `python scripts/installer-rollout.py --check` exits 0, reporting every consumer with a valid `installer.json` and an `sdk.json` at or past the installer commit.

## 17. Setup Warns When a Newer Version Exists

An old setup file someone kept still installs, but its welcome page first says a newer version exists, with a link. It never downloads (operator, 2026-11-18).

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** the welcome page of a real setup built from an older fixture version, light and dark.
**Job:** a person installing an old copy learns a newer one exists and can get it. Consumer: the wizard.
**Treatment:** one line and a "Get the latest" link on the welcome page when the stable feed's version is newer; nothing when offline or when the feed fails verification. Cheaper substitute that fails: a modal message box, or downloading the newer setup.
**Chrome:** Inno Setup's welcome page with one added label and link.

**Build order:**

1. Add the check to `[Code]` in `installer/Resolute.iss`. Done when: a setup older than the fixture feed shows the line and a current one does not.

- [ ] Fetch the stable feed with the `DownloadTemporaryFile` support function (help: `DownloadTemporaryFile`) in `InitializeWizard`, with a 3-second timeout. Done when: an offline run starts the wizard with no delay beyond the timeout and no message.
- [ ] Verify the feed's signature with ISSigTool's Ed25519 support or a bundled verifier before trusting it. Done when: a tampered fixture feed shows no line. Cheaper substitute: trusting HTTPS alone.
- [ ] Add the label and the link to the welcome page, opening `releaseUrl` on `rizonesoft.com` only. Done when: the round-trip test sees the label on an old build. A `/VERYSILENT` run never fetches. Cheaper substitute: a check that also runs in silent installs and delays scripted deployments.
- [ ] Add old-build, current-build, offline and silent cases to `scripts/tests/test_installer_roundtrip.py`. Done when: they pass.
- [ ] Commit: `installer: setup warns when a newer version exists`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the four cases, and fails when the signature check is removed.

## Verification

- A clean clone of any consumer runs `pwsh scripts/package.ps1` and gets a branded, signed-if-configured setup whose install, upgrade, portable, silent and uninstall modes pass the round-trip test.
- The installed program shows an update notice from its feed and never downloads.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
