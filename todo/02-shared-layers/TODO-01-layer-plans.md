---
schema_version: 1
id: layer-plans
domain: 02-shared-layers
status: active
title: "TODO-01 -- The framework and repair contract come home"
---

# TODO-01 -- The framework and repair contract come home

> **Goal:** The two shared layers every tool is waiting for, the framework and the repair contract, are planned in this repository in full, and the shared material still sitting in Resolute (the reference-data tooling and the AutoIt framework the ports are measured against) has moved here, so a tool's plan can depend on a section that exists.

> **Current state:** Measured 2026-11-15. Neither layer exists in code. Their plans are in `rizonesoft/Resolute` at `840bac79`: `todo/01-framework/` (three files; the plan counts 7 of 33 framework-phase sections done, all of them specification and inventory) and `todo/02-repair-contract/TODO-01-repair-contract.md`. They name paths under `src/framework/` and `src/repair/` in Resolute, which is now the launcher only. The reference-data tooling (`tools/refdata/`, `scripts/refdata-embed.py`, `scripts/refdata-verify.py`, `cmake/ResoluteRefdata.cmake`, `docs/reference-data.md`) and the AutoIt framework (`resolute_au3/SDK/Includes/`, `SDK/Concrete/ReBar/`, `SDK/Resources/`) are still in Resolute.

## Inputs

- `D:\Resolute\todo\01-framework\TODO-01-framework-core.md`, `TODO-02-*.md`, `TODO-03-framework-surfaces.md` and `D:\Resolute\todo\02-repair-contract\TODO-01-repair-contract.md`: the sections, their checkpoints and their review records, which are the known information this file turns into plan files here.
- `D:\Resolute\AGENTS.md` "The source layout": the file-per-concern layout the framework and the repair contract were given (`App`, `ToolDescriptor`, `Settings`, `Logging`, `Localization`, `Update`, `Elevation`, `Crash`, `SingleInstance`, `CommandLine`, `ui/AboutDialog`, `ui/Preferences`; `RepairItem`, `RepairRun`, `ResultList`, `RestoreRecord`, `Transcript`).
- `D:\Resolute\docs\plans\2026-11-15-app-split.md`: the split's tracker and the rule that a moved section is marked `Moved:` where it came from.

## Outcome

- `todo/03-framework/` and `todo/04-repair-contract/` hold validated plan files covering every open section of Resolute's two domains, with paths under `framework/` and `repair/` in this repository.
- The reference-data tooling builds and passes its checks from here, and a tool embeds a dataset through the SDK.
- The AutoIt framework sits under `reference/au3-sdk/` as the frozen specification, and Resolute carries none of the four.

**Adjacency:** all=not-applicable (this file authors plans and moves tooling and reference material; the surfaces the layers will have are declared by the plan files §1 and §2 author)

**Adjacency rationale:** The framework owns settings, logging, update and About, and the repair contract owns the result list, the transcript and undo. Those adjacency lines belong to the files this one authors, where each key gets a real owner, not to the authoring step.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Framework plan authored from Resolute's domain 01 | -- | [ ] |
| 2 | §2 | Repair contract plan authored from Resolute's domain 02 | §1 | [ ] |
| 3 | §3 | Reference-data tooling moved from Resolute | -- | [ ] |
| 4 | §4 | AutoIt framework reference moved from Resolute | -- | [ ] |

## 1. Framework Plan Authored From Resolute's Domain 01

The framework is every tool's startup, settings, logging, localization, update check, elevation guard, crash handler, single-instance guard, command line, About and Preferences. Its plan was written in Resolute against a tree that no longer holds tools. This section authors it here through `create-todo`, one file per subject, so each tool's plan can name the framework section it waits on.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Inventory Resolute's `todo/01-framework/` sections with their state in `docs/layer-plans.md`. Done when: every section is listed as done, open or superseded by the split.
2. Author `todo/03-framework/TODO-NN-*.md` for the open ones. Done when: `validate` passes and every open section has a home here.

- [ ] Write `docs/layer-plans.md` listing every section of Resolute's `todo/01-framework/` at `840bac79` with its title, its state and the file here that will own it. Done when: the section count equals `python scripts/todo-graph.py query stats` for that domain in Resolute, quoted.
- [ ] Author `todo/03-framework/TODO-01-framework-core.md` through the `create-todo` skill: lifecycle and startup order, the tool descriptor, settings, logging, localization, update, elevation, crash, single instance and command line, each its own section with paths under `framework/`. Done when: `python scripts/todo-graph.py validate` exits 0 with the file present. Cheaper substitute: one section named "the framework", which is the umbrella the format refuses.
- [ ] Author `todo/03-framework/TODO-02-framework-surfaces.md`: the About dialog and the Preferences host, each `Surface: yes` with its Fidelity, Job, Treatment and Chrome lines against `DESIGN.md`. Done when: `validate` exits 0 and every control of both surfaces is owned by a section.
- [ ] Carry each done section's evidence: record in `docs/layer-plans.md` the Resolute commit and review record of every section already stamped there. Done when: each done section names its commit and its record path.
- [ ] Mark every open section of Resolute's `todo/01-framework/` `Moved:` to this repository, in a Resolute commit. Done when: Resolute's `python scripts/todo-graph.py validate` exits 0 and `query stats` counts them as moved.
- [ ] Commit: `plan: the framework is planned where it will be built`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0 here with `todo/03-framework/` present, and `python scripts/todo-graph.py query stats` shows its sections as open.

## 2. Repair Contract Plan Authored From Resolute's Domain 02

The repair contract is what the repair tools share and nothing else does: the diagnose pass, the result list with per-item status, the transcript, the restore record and undo, with one log line per action. It consumes the framework, so its plan is authored after §1.

**Phase:** 4
**Needs:** none
**Surface:** no

**Build order:**

1. Author `todo/04-repair-contract/TODO-01-repair-contract.md` from Resolute's file. Done when: `validate` passes and each section names its framework dependency.

- [ ] Author `todo/04-repair-contract/TODO-01-repair-contract.md` through `create-todo`: the item shape, the run loop and pre-flight, the result list, the restore record and undo, and the transcript, with paths under `repair/` and a `Depends On` edge to the framework section each consumes. Done when: `python scripts/todo-graph.py validate` exits 0. Cheaper substitute: copying the Resolute file unchanged, whose paths and cross-references name a tree that no longer exists.
- [ ] Declare the file `frozen: true` where the restore record's format is concerned, with a `Freeze check:` in each section. Done when: `python scripts/todo-graph.py query frozen` lists the file with full coverage.
- [ ] Mark every open section of Resolute's `todo/02-repair-contract/` `Moved:` to this repository, in a Resolute commit. Done when: Resolute's `validate` exits 0.
- [ ] Commit: `plan: the repair contract is planned on top of the framework`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0 with `todo/04-repair-contract/` present, and `python scripts/todo-graph.py query frozen` shows its coverage complete.

## 3. Reference-Data Tooling Moved From Resolute

Reference data (BIOS beep codes first) is authored in a database, exported to committed files and embedded per tool at build time. The embedding rule and its packer are shared build tooling, so they belong here; a tool keeps only its own exported datasets.

**Phase:** 3
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Move the packer, the format module, the CMake rule and the document here. Done when: a consumer embeds a fixture dataset through `sdk/`.
2. Remove them from Resolute with its pin bump. Done when: Resolute's refdata tests pass against the SDK's rule.

- [ ] Move `scripts/refdata-embed.py`, `tools/refdata/refdata_format.py` and `cmake/ResoluteRefdata.cmake` here, and make the rule find its packer beside itself instead of under `CMAKE_SOURCE_DIR`. Done when: `resolute_embed_refdata()` configures from a consumer whose tree has no `scripts/refdata-embed.py`. Cheaper substitute: leaving the paths on `CMAKE_SOURCE_DIR`, which makes every tool carry a copy of the packer.
- [ ] Include `ResoluteRefdata.cmake` from `cmake/ResoluteSdk.cmake`. Done when: a consumer calls `resolute_embed_refdata()` with no include of its own.
- [ ] Move `tools/refdata/refdata.py`, `server.ps1`, `server.json`, `scripts/refdata-verify.py` and `docs/reference-data.md` here. Done when: `python scripts/refdata-verify.py --self-test` and `python scripts/refdata-embed.py --self-test` pass here.
- [ ] Remove the moved files from Resolute and bump its `sdk.json` in one commit. Done when: Resolute's `ctest --preset debug -L refdata` passes and `git ls-files` there lists none of them.
- [ ] Commit: `refdata: the embedding rule and its tooling are the SDK's`

**Test checkpoint:** `python scripts/refdata-embed.py --self-test` and `python scripts/refdata-verify.py --self-test` pass here, and Resolute's refdata test label passes against the bumped pin.

## 4. AutoIt Framework Reference Named

Every ported tool is measured against its AutoIt original, and every original includes the shared AutoIt framework: `ReBar`, the shared includes and the shared resources. Each port carries its own tool's source under `reference/au3/`; the shared part lives once. It was to be copied here. The operator decided otherwise on 2026-11-16: this repository is public and MIT, and the AutoIt tree is GPL with four community includes of unknown licence, so the whole AutoIt suite went to the private `rizonesoft/Resolute-Classic` (`D:\Resolute-Classic`), byte for byte from Resolute at `8fca9fbf`, and no copy is kept here. Resolute keeps the launcher's and the framework's AutoIt source under `resolute_au3/` as its own specification.

**Phase:** 3
**Needs:** none
**Surface:** no

**Build order:**

1. Record in `docs/layer-plans.md` where the AutoIt framework reference is read and how it is cited. Done when: `docs/layer-plans.md` names Resolute-Classic and its five framework folders.

- [ ] Record in `docs/layer-plans.md` where the shared AutoIt framework is read: `SDK/Includes/`, `SDK/UDF/`, `SDK/Templates/`, `SDK/Resources/` and `SDK/Concrete/ReBar/` of Resolute-Classic, cited as path and line at that repository's commit. Done when: the file names the repository, the five folders and the citation form, and says no copy exists here and why. Cheaper substitute: a sentence in a commit message, which a later session cannot find.
- [ ] State the licence rule beside it: the AutoIt source is read for what the suite did, never ported line by line where a community include's licence is unknown (`CompInfo.au3`, `FFLabels.au3`, `GUICtrlFFLabel.au3`, `SSLG.au3`), and nothing GPL is copied into this repository. Done when: the file names those four and the rule.
- [ ] Record that `SDK/Signing/` is in neither repository: it held a test certificate with its private key, left out of Resolute-Classic and removed from Resolute's tree on 2026-11-16, and still visible in Resolute's public history. Done when: the file says so by file name and type, never by content, and says nothing is ever signed with that certificate.
- [ ] Commit: `reference: where the AutoIt framework is read, and why it is not copied here`

**Test checkpoint:** `python scripts/todo-graph.py validate` exits 0, and `docs/layer-plans.md` names Resolute-Classic, the five folders, the citation form, the four includes and the Signing folder.

## Verification

- `todo/03-framework/` and `todo/04-repair-contract/` validate and own every open section Resolute's two domains had, the reference-data self-tests pass here, and Resolute carries none of the moved material.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
