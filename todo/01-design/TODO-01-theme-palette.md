---
schema_version: 1
id: theme-palette
domain: 01-design
status: active
title: "TODO-01 -- The chosen palette in the UI library"
---

# TODO-01 -- The chosen palette in the UI library

> **Goal:** Every surface drawn with the UI library shows the warm neutral ramp and the Amber fallback accent that `DESIGN.md` section 3 states, in light and dark, with the contrast floor proven by a test and the rendered goldens re-captured, so the code and the contract agree.

> **Current state:** Measured 2026-11-15. The operator chose identity B, "Layers", that day, and `DESIGN.md` section 3 "Palette values" carries its nine token values per theme. `shared/resolute-ui/src/theme.cpp` still holds the earlier cool-grey palette (`background` `RGB(30, 30, 30)` dark and `RGB(243, 243, 243)` light) and falls back to `RGB(0, 120, 212)` when DWM reports no accent. The layout, controls, type ramp and spacing are unchanged by the identity. The goldens and the house-style contract that would catch a wrong colour are still in Resolute (`tests/golden/`, `docs/captures/house-style/contract.md`).

## Inputs

- `DESIGN.md` section 3: the token table this file implements, and the 4.5:1 text and 3:1 border floors it must keep.
- `shared/resolute-ui/src/theme.cpp` and `shared/resolute-ui/include/resolute/theme.h`: the two palettes and the accent derivation.
- -> XREF: D00 T01 §3 -- the suite that carries the goldens and the house-style test this file re-captures and moves

## Outcome

- A window drawn with the library shows the section 3 values in both themes, read back from the rendered pixels.
- A test fails when any text or border token pair falls under its contrast floor.
- The goldens are the new palette, and the house-style contract lives beside the code it describes.

**Adjacency:** list=not-applicable (a palette holds no records to find); document=not-applicable (nothing is carried or printed); settings=applicable @ D01 T01 §1; reporting=not-applicable (no data is summarised); notifications=not-applicable (no lifecycle to notify); permissions=not-applicable (reading a colour needs no right); audit=not-applicable (no user change to trail); exchange=not-applicable (nothing imported or exported); reverse=not-applicable (the theme setting is its own reverse)

**Adjacency rationale:** The one adjacent surface is the theme setting: follow-system, light or dark, which §1 must keep working across the new values, with the system accent still winning over the fallback. Everything else a tool owes is owned by the tool that draws the surface.

## Implementation Order

| Order | Section | Deliverable | Depends On | Status |
| ----- | ------- | ----------- | ---------- | ------ |
| 1 | §1 | Palette values in the theme | -- | [ ] |
| 2 | §2 | Contrast floor test for token pairs | §1 | [ ] |
| 3 | §3 | Rendered goldens re-captured | §1, D00 T01 §3 | [ ] |
| 4 | §4 | House-style contract moved from Resolute | D00 T01 §3 | [ ] |

## 1. Palette Values in the Theme

The two palettes in `theme.cpp` take the values `DESIGN.md` section 3 states, and the accent fallback becomes Amber. The system accent, high contrast and the theme crossfade keep working exactly as they do.

**Phase:** 2
**Needs:** windows-host
**Surface:** yes
**Fidelity:** every surface the library draws, against `DESIGN.md` section 3 "Palette values" in light and dark.
**Job:** a person sees the suite in its own colours and can still read every label. Consumer: the rendered window, read back by pixel.
**Treatment:** the nine tokens per theme set from the table, the remaining tokens derived on the same warm ramp. Cheaper substitute that fails the checkpoint: changing `background` alone, which leaves the toolbar and status bar cool grey beside it.
**Chrome:** the library's own controls; no control gains or loses a part.

**Build order:**

1. Set `DarkPalette` and `LightPalette` in `shared/resolute-ui/src/theme.cpp` from the table. Done when: each of the nine tokens per theme equals its table value.
2. Derive the tokens the table does not list on the same ramp, and set the fallback accent. Done when: no cool-grey literal remains in either palette.

- [ ] Set the nine listed tokens of `DarkPalette` and `LightPalette` in `shared/resolute-ui/src/theme.cpp` to the `DESIGN.md` section 3 values. Done when: a unit test reads each token back and compares it with the table. Cheaper substitute: typing the values into a tool, which rule 2 of the contract forbids.
- [ ] Derive `surfaceHover`, `surfaceActive`, the four elevation tokens and `statusBarText` on the warm ramp, keeping each pair above its floor. Done when: `DESIGN.md` section 3 lists the derived values and the code matches. Cheaper substitute: leaving them cool grey, which shows as a mismatched strip on hover.
- [ ] Change the no-accent fallback from `RGB(0, 120, 212)` to Amber `#FFB020` in dark and `#8A5A00` in light, with `accentHover`, `accentPressed` and `accentSubtle` derived as they are today. Done when: with the DWM accent unavailable the accent tokens read back as the Amber values, and with it available the system colour still wins.
- [ ] Keep high contrast untouched. Done when: with Windows high contrast on, every token reads back as the system colour it did before this section.
- [ ] Drive a window in both themes and capture it to `docs/captures/`. Done when: the two captures show the new ramp and are committed with their provenance.
- [ ] Commit: `theme: the warm ramp and the Amber fallback accent`

**Test checkpoint:** `reskit\cmake\bin\ctest.exe --preset debug -L theme` passes with a case comparing all eighteen listed tokens with the table, and fails when one value in `theme.cpp` is changed.

## 2. Contrast Floor Test for Token Pairs

`DESIGN.md` section 3 sets 4.5:1 for text and 3:1 for borders and interactive elements, and Resolute found two pairs under the floor only on a capture. A test over the token pairs finds it at build time.

**Phase:** 2
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Add a contrast case to the theme tests computing WCAG contrast for each text and border pair in both palettes. Done when: it passes on the §1 values and fails on a lowered one.

- [ ] Add `tests/contrast_test.cpp` computing relative luminance and contrast for `text`, `textSecondary` and `statusBarText` on each ground they sit on, at 4.5:1. Done when: the case passes and prints each pair's ratio. Cheaper substitute: asserting a hand-typed ratio, which is not a measurement.
- [ ] Add the 3:1 pairs: `border` on `background` and `surface`, and `accent` on `background`. Done when: the case passes on both palettes.
- [ ] Prove it can fail: lower `textSecondary` in a local build. Done when: the case fails naming the pair, its ratio and the floor, and the change is reverted.
- [ ] Commit: `tests: the contrast floor is measured for every token pair`

**Test checkpoint:** `reskit\cmake\bin\ctest.exe --preset debug -R contrast` passes and its output lists every pair with its ratio.

## 3. Rendered Goldens Re-Captured

The offscreen render goldens pin what each control looks like per theme and scale. A palette change makes every one of them differ, and each difference has to be the palette and nothing else.

**Phase:** 2
**Needs:** windows-host, display-session
**Surface:** no

**Build order:**

1. Re-capture `tests/golden/` after §1. Done when: the render tests pass on the new goldens.
2. Show that only colour changed. Done when: a geometry diff of old and new goldens is empty.

- [ ] Re-capture every golden under `tests/golden/` (each control, light and dark, 96 and 144 DPI) with the suite's own capture path. Done when: `ctest --preset debug -L render` passes on the committed files. Cheaper substitute: lowering the comparison tolerance, which hides a real layout change.
- [ ] Compare each old golden with its new one for geometry: the set of pixels that differ from the ground is the same. Done when: the comparison reports zero controls whose shape changed, quoted in the commit message.
- [ ] Commit: `tests: goldens re-captured on the new palette, geometry unchanged`

**Test checkpoint:** `reskit\cmake\bin\ctest.exe --preset debug -L render` passes, and fails when one golden is replaced by its pre-palette version.

## 4. House-Style Contract Moved From Resolute

`docs/captures/house-style/contract.md` in Resolute lists the constants the shared controls are built from, and a test fails when the code and the contract disagree. It describes SDK code, so it belongs here with the test that reads it.

**Phase:** 2
**Needs:** windows-host
**Surface:** no

**Build order:**

1. Move the contract and its test here and repoint `DESIGN.md`. Done when: the test passes here and Resolute no longer carries either.

- [ ] Move `docs/captures/house-style/contract.md` and `tests/house_style_test.cpp` from Resolute to the same paths here. Done when: `ctest --preset debug -L housestyle` passes here. Cheaper substitute: copying them, which leaves two contracts.
- [ ] Repoint the "How it binds" paragraph of `DESIGN.md` at the contract's path in this repository. Done when: every path that paragraph names exists here.
- [ ] Remove both files from Resolute in the commit that bumps its `sdk.json`. Done when: `git grep house_style` in Resolute finds nothing and its suite passes.
- [ ] Commit: `design: the house-style contract lives with the controls it describes`

**Test checkpoint:** `reskit\cmake\bin\ctest.exe --preset debug -L housestyle` passes, and fails when one constant in the contract is changed.

## Verification

- A driven window in both themes shows the section 3 palette, the contrast case lists every pair above its floor, and the render and house-style cases pass on the committed goldens and contract.
- `python scripts/todo-graph.py validate` and `python scripts/todo-graph.py plan --check` pass.
