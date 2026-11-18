# The installer

Every Windows program on the SDK ships one Inno Setup 7.1.1 installer built from one shared script. A program gives it three things: its brand (already in `brand/build.py`), one `installer.json`, and an `sdk.json` pin. The look is fixed by `DESIGN.md` section 17; the work is planned in `todo/03-installer/TODO-01-installer-shape.md` (D03 T01).

**Status, 2026-11-18:** the design is decided and its reference set is rendered. Nothing below is built yet: each part names the D03 T01 section that builds it, and this guide is updated as each one lands.

## What a program gets

- A setup file, `dist/<Tool>-<version>-Setup.exe`, 64-bit, with the Graphite panel frame carrying the tool's icon, name and accent, light or dark with Windows.
- A per-user install by default (`%LOCALAPPDATA%\Programs\<Tool>`, no admin prompt) and an all-users install on request.
- In-place upgrade that keeps settings, a portable extract, silent switches and a winget manifest.
- A notice in the program, and on an old setup's welcome page, when a newer version is published. Nothing ever downloads or installs on its own.

## How the look is built

`brandkit.py` writes the installer art into `brand/installer/` from the same spec that draws the program's icon (D03 T01 §3 and §4). Nobody draws installer art by hand, and no program has its own `.iss` file.

| File | What it is | Where Setup uses it |
| ---- | ---------- | ------------------- |
| `<slug>-side-<width>.png` (7) | the Graphite side panel at 100% to 250% | `WizardImageFile`, Welcome and Finished |
| `<slug>-small-<size>.png` (7) | the icon, square, transparent | `WizardSmallImageFile`, the inner pages |
| `<slug>-setup.ico` | the icon with the setup badge | `SetupIconFile`, the setup file in Explorer |

To change a program's installer look, change its icon or its `accent` in `brand/build.py` and run `python brand/build.py`. To change the frame for every program, change `DESIGN.md` section 17 and the reference script together, re-render the references, then `brandkit.py`; that is a design decision and goes to the operator first.

## Adopting it in a program

1. **Accent.** Add `accent='#RRGGBB'` to the `app_assets(...)` call in `brand/build.py`: the signature hue's mid face (`DESIGN.md` section 14). Without it the builder takes the first colour of the detailed icon.
2. **`installer.json`** at the repository root (D03 T01 §5): `name`, `appId` (a GUID made once and never changed, since upgrades find the old install by it), `exe`, `publisher`, `homepage`, `wingetId`, `feedUrl`, and optional `startMenu` and `desktopShortcut`. The version is read from the built executable, never written here.
3. **Pin the SDK** in `sdk.json` at a commit carrying the installer, then `pwsh scripts/sdk.ps1`.
4. **Build:** `pwsh scripts/package.ps1` (D03 T01 §11) checks `installer.json`, renders the art, compiles `sdk/installer/Resolute.iss` with the pinned `ISCC.exe` and writes the setup to `dist/`. Signing runs only when the program's own untracked `signing.local.json` or environment names a sign tool; the SDK holds no key.
5. **Publish:** `pwsh scripts/package.ps1 -Publish -Channel stable` (D03 T01 §13) uploads the setup and its signed feed entry to `https://updates.rizonesoft.com` through the private Updates service.

`scripts/installer-rollout.py` (D03 T01 §16) does steps 1 to 3 for every program at once after the MemBoost pilot.

## Command-line switches

Inno Setup's own switches, plus one the shared script adds. D03 T01 §10 proves each with a test and adds the exit codes here.

| Switch | Effect |
| ------ | ------ |
| `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART` | install with no window or prompt |
| `/CURRENTUSER` or `/ALLUSERS` | choose the install mode without the dialog |
| `/DIR="path"` | install folder |
| `/PORTABLE=1` | extract only, no shortcuts, registry or uninstaller (added by the shared script) |
| `/LOG="file"` | write Setup's log |
| `/ALLOWDOWNGRADE` | let an older version replace a newer one (added by the shared script) |

The uninstaller, `unins000.exe` in the install folder, takes `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART`.

## Checking a build is 1:1

- **Art:** `brandkit.py`'s output for MemBoost, Firemin and Sleep and Wake Diagnostics must equal `docs/captures/installer/reference/<slug>/` pixel for pixel. `python docs/captures/installer/reference/make_reference.py` re-renders the references from the contract.
- **Wizard:** capture a real setup at 100% and 200% display scale; the side panel in the capture must equal `side-202.png` or `side-430.png` exactly, with the icon in its own proportions, not stretched.
- **Long names:** names up to two lines at 15 units fit the panel. The build fails by name on one that does not, rather than shrinking it further or running off the edge.
