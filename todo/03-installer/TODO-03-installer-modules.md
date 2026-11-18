---
schema_version: 1
id: installer-modules
domain: 03-installer
status: active
title: "TODO-03 -- Installer modules for programs with extra install steps"
---

# TODO-03 -- Installer modules for programs with extra install steps

> **Goal:** A program that needs more than files and shortcuts (a .NET runtime, a Windows service, a firewall rule, Explorer integration) switches on a tested SDK module in its `installer.json`, with parameters, and writes no installer code. Each module installs, upgrades, uninstalls, runs silently and refuses what it cannot do (portable mode, a missing admin right) in one proven way. A program with a need no module covers adds its own `installer/extra.iss`, which the shared script includes through Inno Setup's event attributes, so modules and the program's own code never fight over `InitializeSetup` and the other event functions.

> **Current state:** Measured 2026-11-18. The shared shape (D03 T01) plans one `installer/Resolute.iss` driven by `installer.json` with no extension point. Planned programs need more: the operator named a .NET 11 runtime and service installs. The operator decided on 2026-11-18, in session: a module library plus a per-program escape hatch; a prerequisite such as the .NET runtime is downloaded only when missing, hash- and signature-checked, never bundled; and the first release carries four modules: .NET runtime, Windows service, firewall rule and Explorer integration.

## Inputs

- `todo/03-installer/TODO-01-installer-shape.md`: the shared script (D03 T01 §6), install modes (D03 T01 §7), upgrade (D03 T01 §8), portable (D03 T01 §9) and silent switches (D03 T01 §10) every module must respect.
- Inno Setup 7.1.1 help: event attributes (`<event('InitializeSetup')>`), `PrepareToInstall`, `DownloadTemporaryFile`, `ISSigTool`, `[Run]`, `[UninstallRun]`, `[Registry]` and `ChangesAssociations`: the source cited for every hook.
- Microsoft's .NET release metadata (`https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/11.0/releases.json`) and the documented install-detection registry keys: the source for the runtime module's pins and its detection.
- Microsoft documentation for the Service Control Manager, `ChangeServiceConfig2` recovery actions, the `INetFwPolicy2` firewall interface and file-association registration (`HKCU\Software\Classes` and `HKLM\Software\Classes`, `SHChangeNotify`): the source for the other three modules.

## Outcome

- `installer.json` takes `"modules": [{"name": "dotnet-runtime", "kind": "desktop", "version": "11.0"}, ...]`, validated per module.
- `installer/modules/<name>/` in the SDK holds each module's `module.json` schema and `module.iss`, with round-trip tests.
- A program's `installer/extra.iss`, when present, is included after the modules and documented in `docs/installer.md`.

**Adjacency:** list=not-applicable (no records are listed); document=not-applicable (nothing is printed); settings=applicable @ D03 T03 §1; reporting=not-applicable (no data is summarised); notifications=applicable @ D03 T03 §3; permissions=applicable @ D03 T03 §1; audit=applicable @ D03 T03 §1; exchange=not-applicable (no data leaves the PC); reverse=applicable @ D03 T03 §1

**Adjacency rationale:** Each module's parameters are its settings, checked by the contract in §1, which also owns the admin-right rule, the uninstall reverse and the Setup log lines every module writes. The one message a person sees outside the wizard pages is the prerequisite download failing, owned by §3.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Module contract and installer.json modules list | D03 T01 §5, D03 T01 §6, D03 T01 §7, D03 T01 §9, D03 T01 §11 | [ ] |
| 2 | §2 | Per-program extra.iss escape hatch | §1 | [ ] |
| 3 | §3 | .NET runtime module, downloaded when missing | §1 | [ ] |
| 4 | §4 | Windows service module | §1 | [ ] |
| 5 | §5 | Firewall rule module | §1 | [ ] |
| 6 | §6 | Explorer integration module | §1 | [ ] |
| 7 | §7 | Modules documented and shown in a pilot | §2, §3, §4, §5, §6 | [ ] |

## 1. Module Contract and installer.json Modules List

One contract every module meets, so the shared script can include any mix of them and each behaves the same in every install mode.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Write the contract and the include mechanism. Done when: a fixture module with no effect is switched on from `installer.json` and its event hooks run.

- [ ] Write `installer/modules/README.md`: a module is `module.json` (parameters as JSON Schema, plus `requiresAdmin` and `allowsPortable`) and `module.iss` (sections and `[Code]` whose event handlers all carry `<event('...')>` attributes, procedures and functions alike, with the signatures the help gives; a function such as `InitializeSetup` or `PrepareToInstall` combines with the others as Inno Setup documents, so any one can refuse). Done when: the file states each rule with the Inno Setup help reference, and a fixture with two attributed `InitializeSetup` functions compiles and either can abort.
- [ ] Extend `installer/installer.schema.json` (D03 T01 §5) with `modules`, and `scripts/installer_config.py` to validate each entry against its module's `module.json`. Done when: an unknown module or a bad parameter exits 2 naming both.
- [ ] Generate `#include` lines and `/D` parameter defines for each enabled module in `scripts/package.ps1`, in the order listed. Done when: the fixture module's include appears in the ISCC preprocessor output.
- [ ] Force all-users mode when any enabled module has `requiresAdmin`, by compiling with `PrivilegesRequired=admin` and an empty `PrivilegesRequiredOverridesAllowed` (D03 T01 §7), so neither the dialog nor `/CURRENTUSER` can choose per-user. Done when: a fixture with a `requiresAdmin` module never offers per-user, and `/VERYSILENT /CURRENTUSER` still installs for all users. Cheaper substitute: hiding the dialog only, which leaves the switch open.
- [ ] Hide the portable choice and refuse `/PORTABLE=1` when any enabled module has `allowsPortable: false` (D03 T01 §9). Done when: the switch exits with the documented code naming the module.
- [ ] Require every module to undo itself in `[UninstallRun]` or an uninstall event, and to log one `module <name>: <action>` line per action to the Setup log. Done when: the fixture's install and uninstall logs show its lines.
- [ ] Record what each module created (service names, rule ids, registry keys) in `{app}\installer-state.json`, and on upgrade remove whatever the old state lists that the new release no longer declares, including a whole module dropped from `installer.json`. Done when: upgrading the fixture to a release without its firewall module removes the rule. Cheaper substitute: cleaning up only at uninstall, which leaves a dropped module's changes live for the life of the program.
- [ ] Add `scripts/tests/test_installer_modules.py` for validation, ordering and the admin and portable rules. Done when: it passes.
- [ ] Commit: `installer: the module contract`

**Test checkpoint:** `python -m unittest scripts.tests.test_installer_modules` passes, and fails when a module with `requiresAdmin` still offers per-user mode.

## 2. Per-Program extra.iss Escape Hatch

A program with a one-off need writes its own installer code, in the same shape as a module, without forking the shared script.

**Phase:** 5
**Needs:** none
**Surface:** no

**Build order:**

1. Include `installer/extra.iss` from the consumer when it exists. Done when: a fixture `extra.iss` adds a file and an event hook that runs beside the modules' hooks.

- [ ] Include the consumer's `installer/extra.iss` after every module in `installer/Resolute.iss`, through a `/D ExtraIss=` define set by `scripts/package.ps1` only when the file exists. Done when: a consumer without the file builds unchanged.
- [ ] Refuse a bare event function in `extra.iss` (one without `<event('...')>`) in `scripts/package.ps1` before compiling. Done when: a fixture with a bare `InitializeSetup` fails naming the line. Cheaper substitute: letting ISCC's duplicate-identifier error surface, which names neither the file nor the rule.
- [ ] Let `extra.iss` declare `requiresAdmin` and `allowsPortable` in a leading comment block read by `scripts/package.ps1`, applied as for modules. Done when: a fixture declaring `requiresAdmin` forces all-users mode.
- [ ] Add the cases to `scripts/tests/test_installer_modules.py`. Done when: they pass.
- [ ] Commit: `installer: the per-program extra.iss`

**Test checkpoint:** `python -m unittest scripts.tests.test_installer_modules` passes the escape-hatch cases, and fails when a bare event function is accepted.

## 3. .NET Runtime Module, Downloaded When Missing

A program built on .NET gets its runtime installed by its own setup, only when the PC lacks it, from Microsoft, verified.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** the Installing page while the runtime downloads and installs, and the failure message offline, on Windows 11.
**Job:** a person installs a .NET program without knowing what .NET is. Consumer: the wizard and silent installs.
**Treatment:** a progress line "Installing the .NET 11 Desktop Runtime" with Inno Setup's download progress; on failure, one message naming what is missing and the download page. Cheaper substitute that fails: bundling the runtime, which the operator ruled out on 2026-11-18, or telling the person to install it first.
**Chrome:** Inno Setup's Installing page and its download page.

**Build order:**

1. Write `installer/modules/dotnet-runtime/`. Done when: on a PC without the runtime it is installed, and with it nothing is downloaded.

- [ ] Define parameters `kind` (`runtime`, `desktop`, `aspnet`) and `version` (a major.minor line such as `11.0`) in `module.json`, with `requiresAdmin: true` and `allowsPortable: false`. Done when: `installer_config.py` refuses `kind: "sdk"`.
- [ ] Detect an installed runtime of the line from the version value names under `SOFTWARE\dotnet\Setup\InstalledVersions\x64\sharedfx\<framework>` in the 32-bit registry view (`HKLM32`), where Microsoft's installer records x64 runtimes too, matching the framework, x64 and the exact `major.minor`. Done when: the check is true with `11.0.x` installed by Microsoft's own installer, and false with only `10.0.x` present.
- [ ] Pin the installer URL, size and SHA-256 per line in `installer/modules/dotnet-runtime/pins.json`, written by `scripts/dotnet-pins.py`, which downloads the file once, checks it against the SHA-512 in Microsoft's `releases.json`, and records the SHA-256 it computes (Inno Setup's `DownloadTemporaryFile` checks SHA-256 only). Done when: the script refreshes the pin for `11.0`, refuses a file whose SHA-512 differs, and records the release date.
- [ ] Download with `DownloadTemporaryFile` and the pinned SHA-256 only when detection fails, then check the file's Authenticode signature is valid and its signer is Microsoft Corporation before running it. Done when: a tampered fixture download is refused and nothing runs, and a present runtime with the network off installs with no request. Cheaper substitute: trusting HTTPS alone.
- [ ] Run the installer with `/install /quiet /norestart`, treating exit 3010 as success with a restart owed, which Setup's Finished page reports (help: `NeedRestart`). Done when: a fixture 3010 shows the restart prompt.
- [ ] Fail offline with one message, and exit `/VERYSILENT` with a documented code naming the module in the log. Done when: an offline silent run exits with that code.
- [ ] Never remove the runtime on uninstall, and log why. Done when: uninstalling the fixture leaves the runtime and logs `module dotnet-runtime: shared runtime left in place`.
- [ ] Add elevated round-trip cases with and without the runtime present. Done when: they pass.
- [ ] Commit: `installer: the .NET runtime module`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the runtime cases on an elevated host, and fails when a download with the wrong SHA-512 is run.

## 4. Windows Service Module

A program that runs as a service has it registered, configured, stopped for upgrades and removed by its setup.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `installer/modules/service/`. Done when: a fixture service is installed running, survives an upgrade and is gone after uninstall.

- [ ] Define parameters `name`, `displayName`, `description`, `exe`, `args`, `account` (`LocalService` default, `NetworkService`, `LocalSystem`), `start` (`auto`, `delayed`, `manual`) and `recovery` (restart delays), with `requiresAdmin: true` and `allowsPortable: false`. Done when: `installer_config.py` refuses a `name` with spaces.
- [ ] Before touching an existing service of that name, check its image path is inside `{app}` and that `installer-state.json` lists it; otherwise refuse with a message naming the service. Done when: a fixture with a same-name service owned by another program is refused and that service keeps running.
- [ ] Stop the service in a `PrepareToInstall` event before files are replaced, waiting up to 30 seconds, because `CloseApplications` does not stop services (help: `PrepareToInstall`), and remember that it was running. Done when: an upgrade of a running fixture service replaces its executable with no reboot.
- [ ] Save the service's whole configuration (`QueryServiceConfig` and `QueryServiceConfig2`: path, arguments, account, start type, recovery) before changing it. Done when: the saved copy reads back every field.
- [ ] When the install is cancelled or fails after the stop, restore the saved configuration and then restart the service if it was running, from `DeinitializeSetup` when the install did not complete. Done when: a fixture failing after the configuration change leaves the old service running with its original settings.
- [ ] Create or update the service with the Service Control Manager API from `[Code]`, and set recovery with `ChangeServiceConfig2`. Done when: `sc qc` and `sc qfailure` read back every parameter.
- [ ] Start the service after install unless `start` is `manual`. Done when: `sc query` reads `RUNNING`.
- [ ] Stop and delete the service on uninstall before files are removed. Done when: `sc query <name>` reports it does not exist.
- [ ] Add elevated round-trip cases for install, upgrade and uninstall. Done when: they pass.
- [ ] Commit: `installer: the Windows service module`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the service cases on an elevated host (install, upgrade, cancel after stop, foreign same-name service), and fails when the upgrade does not stop the service first.

## 5. Firewall Rule Module

A program that listens or connects gets exactly its own firewall rule, removed with it.

**Phase:** 5
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Write `installer/modules/firewall/`. Done when: the fixture rule exists after install and not after uninstall.

- [ ] Define parameters `name`, `program` (default the main executable), `direction` (`in`, `out`), `protocol`, `ports` and `profiles`, with `requiresAdmin: true` and `allowsPortable: false`. Done when: `installer_config.py` refuses ports outside 1 to 65535.
- [ ] Add each rule through `INetFwPolicy2` from `[Code]` with a product-scoped unique name, `Rizonesoft.<appId>.<rule key>`, recorded in `installer-state.json`, replacing only that name on upgrade. Done when: the rule's application and port filters (`Get-NetFirewallApplicationFilter`, `Get-NetFirewallPortFilter`) read back the executable, protocol and ports, once.
- [ ] Remove only the rules `installer-state.json` lists on uninstall, never by group or display name. Done when: the fixture's rules are gone and a foreign rule seeded with the same group survives.
- [ ] Add elevated round-trip cases. Done when: they pass.
- [ ] Commit: `installer: the firewall rule module`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the firewall cases on an elevated host, and fails when uninstall removes the seeded foreign rule or an upgrade leaves two rules.

## 6. Explorer Integration Module

Context menu entries and file associations are registered for the install mode and removed cleanly.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** File Explorer's right-click menu (with "Show more options" on Windows 11) and the Open with list, per user and all users.
**Job:** a person reaches the program from Explorer. Consumer: File Explorer.
**Treatment:** classic verbs under `Software\Classes` in HKCU or HKLM by install mode, a ProgID per file type, `ChangesAssociations=yes` (help: `ChangesAssociations`). Cheaper substitute that fails: a shell extension DLL, which needs Explorer restarts and crashes Explorer when it fails.
**Chrome:** Explorer's own menus.

**Build order:**

1. Write `installer/modules/explorer/`. Done when: the fixture verb and association appear for the install mode and are gone after uninstall.

- [ ] Define parameters `verbs` (label, target `*`, `Directory`, `Directory\Background` or an extension, and the argument line) and `associations` (extension, ProgID, description, icon), with `requiresAdmin: false` and `allowsPortable: false`. Done when: `installer_config.py` refuses a verb with no label.
- [ ] Write verbs and ProgIDs in `[Registry]` under `HKA\Software\Classes` so the install mode picks HKCU or HKLM (help: `HKA`), with `uninsdeletekey` only on keys the program owns (its ProgID and each verb's own subkey) and `uninsdeletevalue` for its value under a shared key such as `.<ext>\OpenWithProgids`. Done when: a per-user install writes only under HKCU, and uninstalling leaves a second fixture program's values under the same extension.
- [ ] Register associations as Open with candidates without taking the default, which Windows reserves for the person. Done when: the fixture extension lists the program in Open with and its previous default is unchanged.
- [ ] Notify the shell with `ChangesAssociations=yes` and restart nothing. Done when: the verb appears without signing out.
- [ ] Add round-trip cases for both modes, the all-users one elevated. Done when: they pass.
- [ ] Commit: `installer: the Explorer integration module`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the Explorer cases, including an upgrade that drops a verb while a second program shares the extension, and fails when uninstall leaves the ProgID or removes the other program's value.

## 7. Modules Documented and Shown in a Pilot

The guide explains every module and the escape hatch, and one real setup proves a mix of modules together.

**Phase:** 5
**Needs:** windows-host, display-session
**Surface:** yes
**Fidelity:** a fixture program's real setup with the .NET runtime, service and firewall modules on Windows 11, every page in light and dark.
**Job:** the operator sees a program with extra install steps install, upgrade and uninstall end to end. Consumer: the operator.
**Treatment:** the D03 T01 frame; the modules add only progress lines. Cheaper substitute that fails: testing each module alone, which misses ordering between them.
**Chrome:** Inno Setup's wizard.

**Build order:**

1. Write the guide section and run the pilot. Done when: the guide covers each module and the captures are shown to the operator.

- [ ] Add a "Modules" section to `docs/installer.md`: each module's parameters with an example, the admin and portable rules, and how to write `extra.iss`. Done when: every parameter in every `module.json` appears in the guide.
- [ ] Build a fixture setup with three modules and capture install, upgrade and uninstall to `docs/captures/installer/modules/`. Done when: the captures exist with their provenance.
- [ ] Show the operator the captures. Done when: their approval or changes are recorded here with the date.
- [ ] Commit: `installer: modules documented and piloted`

**Test checkpoint:** `bosun run -- python -m unittest scripts.tests.test_installer_roundtrip` passes the combined three-module case on an elevated host.

## Verification

- A program switches on any mix of the four modules in `installer.json` and its setup installs, upgrades, uninstalls and runs silently with each, writing no installer code of its own.
- A program's `extra.iss` runs beside the modules without clashing event functions.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
