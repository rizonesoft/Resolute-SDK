# DESIGN.md

The design contract for the Resolute suite. Every surface in the launcher and in every tool is held to this, and it lives here, in the SDK, because the UI library that implements it lives here.

It moved from the Resolute repository on 2026-11-15, when every tool left for its own repository. Section references of the form `D01 T01 §7` name the Resolute plan as it stood at the move; the SDK's own plan in `todo/` re-homes each one as it is worked. A tool's own `DESIGN.md` holds its identity (its icon, colours and banners) and points here for everything else.

This is a **contract, not a roadmap.** It says what is true of a finished surface. Work that makes it true lives in `todo/`, primarily `D01 T01 §7`-`§8` and `D01 T02`. If a rule here is not yet implemented everywhere, that is a gap in the plan, not permission to deviate.

**How it binds.** `todo/README.md` requires every user-facing section to carry a `Fidelity:` block. That block names this file and the house-style contract under `docs/captures/house-style/`. `review-todo-section` compares a rendered surface against both before stamping, and `D07 T01 §3` checks it per tool.

**Why a contract rather than screenshots.** `D00 T02 §3` was written to store captured images and was rewritten on 2026-09-17 when the operator asked what a screenshot proved that the source did not. The geometry, typography and spacing are already constants in the shared controls, so the house style is derived from them and a test fails when the two disagree. That makes drift a failing gate rather than something somebody notices while comparing two images. What a screenshot does prove, that a surface *rendered* rather than was merely specified, belongs to `D01 T02 §5` and the automation tree it builds.

**How to change it.** Edit this file in a commit that says what changed and why, and update the affected captures in the same commit. A deviation that is agreed becomes a rule here; a deviation that is not agreed is a defect. Never fork a rule into a tool.

---

## 1. The premise

Resolute is a suite of separately distributed tools, each in its own repository, that must read as one product.

A user who learns one tool has learned all of them. That is only true if the shared layer owns every surface a user recognizes, and if no tool is allowed to draw its own version of something the library already provides.

The suite this replaces failed exactly here: fourteen copies of one framework produced fourteen About dialogs that drifted, seven tools storing settings in the wrong file, and six that logged nothing. The contract exists so that cannot recur by accident.

**Three rules that override everything else in this file:**

1. **A tool never draws a control the shared library provides.** A second progress bar, result list, About dialog, or message box is a defect, not a shortcut.
2. **A tool never hardcodes a colour, a font size, or a spacing value.** It names a token. Tokens live in the theme; literals do not appear in tool code.
3. **Application icons are the one deliberate exception.** Each tool has its own full-colour application icon and its own identity in the launcher, on the desktop, and in the taskbar, drawn under the guidance in section 14. Everything else is shared.

---

## 2. Rendering

**Direct2D and DirectWrite.** Every surface is vector-rendered. No bitmap-scaled UI, no GDI fallback path for anything a user sees.

This is not an implementation preference: it is what makes the next rule achievable.

**Every surface is correct at every scale.** 100, 125, 150, 200 percent, and whatever comes next. Per-monitor DPI v2 is declared in the manifest, and a window dragged between differently scaled monitors re-lays out rather than re-scales.

Layout is expressed in scalable units. A hardcoded pixel coordinate is a defect, because it produces clipped controls at 150 percent instead of blurry ones.

**Minimum target: Windows 10 1809.** That floor is set by dark mode, per-monitor DPI v2, and Direct2D SVG rendering. Lowering it means giving up all three.

---

## 3. Colour

Colour is never a literal. It is a token resolved from the active theme.

### Token set

| Group | Tokens |
| --- | --- |
| Core | `background`, `surface`, `surfaceHover`, `surfaceActive`, `toolbar`, `text`, `textSecondary`, `border`, `accent`, `statusBar`, `statusBarText` |
| Accent variants | `accentHover`, `accentPressed`, `accentSubtle` |
| Semantic | `success`, `warning`, `error`, `info` |
| Elevation | `surfaceBase`, `surfaceLow`, `surfaceMid`, `surfaceHigh` |
| Overlay | `scrim` |

**Elevation is four levels**, base through high, and it carries meaning: a surface nearer the user sits higher. A dialog is above a panel is above the background.

### Rules

- **Light and dark are both first-class.** Neither is a derived afterthought. Every surface is designed and captured in both.
- **The default is follow-system**, with explicit light and dark available as a setting.
- **Theme changes crossfade** over roughly 300ms. An instant flip is jarring and looks broken.
- **The accent colour comes from the system**, read from DWM, with hover, pressed, and subtle variants derived from it. A user who set their accent expects to see it.
- **High contrast is honoured.** When Windows high contrast is active, system colours win over the palette entirely.
- **Semantic colour is never the only signal.** Success and error carry an icon or a label as well, because red and green alone fail for a meaningful share of users.

### Palette values

Decided 2026-11-15 with the SDK's identity (section 15). The neutral ramp is warm, and Amber is the accent a surface shows when Windows reports no accent colour. `shared/resolute-ui/src/theme.cpp` still carries the earlier cool-grey values: bringing it to this table, with the goldens re-captured, is planned work in `todo/`, and until it lands the code is the gap, not this table.

| Token | Light | Dark |
| --- | --- | --- |
| `background` | `#F6F5F2` | `#17191E` |
| `surface` | `#ECEAE5` | `#1F2228` |
| `toolbar` | `#FCFBF9` | `#23262D` |
| `border` | `#827E76` | `#80858F` |
| `text` | `#17191E` | `#ECEAE5` |
| `textSecondary` | `#56524A` | `#B0B3BA` |
| `statusBar` | `#E8E6E0` | `#1B1D22` |
| `accent` (fallback) | `#8A5A00` | `#FFB020` |
| `accentSubtle` (fallback) | `#F6E7C6` | `#3A3018` |

The layout, the controls, the type ramp, the spacing grid and the motion rules are unchanged by this: the identity changed what the suite is coloured with, not how it is built.
### Contrast floor

- **4.5:1 minimum** for all text (WCAG AA).
- **3:1 minimum** for interactive elements and borders.
- Both themes are checked against these, and a token pair that fails is a defect in the palette, not in the surface using it.

---

## 4. Typography

### Type ramp

| Role | Size |
| --- | ---: |
| Caption | 11px |
| Body | 13px |
| Subtitle | 16px |
| Title | 20px |
| Display | 28px |

Weights: Regular 400, Medium 500, SemiBold 600, Bold 700.

A size outside the ramp is a defect. If a surface needs one, the ramp changes here first.

### Rules

- **`DWRITE_RENDERING_MODE_NATURAL_SYMMETRIC`** for text rendering. ClearType antialiasing where it is appropriate to the surface.
- **Monospace for machine values.** Registry paths, file paths, numbers, hex codes, and anything a user might copy or compare character by character use Cascadia Mono or Consolas. Proportional text for prose.
- **Overflow truncates with an ellipsis**, and truncated text carries a tooltip with the full value. A tooltip on text that is *not* truncated is noise.
- **Machine values are selectable and copyable.** A user reading an error they need to search for should not have to retype it.

---

## 5. Spacing and layout

**A 4px grid.** Every spacing value is a multiple of 4.

| Token | Value |
| --- | ---: |
| `SpacingXS` | 4 |
| `SpacingSM` | 8 |
| `SpacingMD` | 12 |
| `SpacingLG` | 16 |
| `SpacingXL` | 24 |

Larger steps continue the grid: 32, 40, 48.

### Rules

- **Density is a user choice**: Compact, Normal, Spacious, adjusting item heights and padding. Normal is the default.
- **The layout adapts rather than breaking.** The sidebar collapses to icons below roughly 600px width; the toolbar moves overflow into a menu when it cannot fit.
- **A minimum window size is enforced** so no surface can be dragged into incoherence.
- **Window size and position are remembered, per monitor.**
- **Windows 11 snap zones are respected.**
- **Long lists virtualize.** A list that renders a thousand rows it cannot show is a performance defect.
- **Scrolling is smooth**, with scroll indicators that fade in on interaction and out when idle.

---

## 6. Motion

Motion exists to explain a change, never to decorate one.

### Rules

- **One shared animation clock.** Every control subscribes to it. A control running its own timer is a defect.
- **Easing is named, not ad hoc**: `EaseOutCubic`, `EaseOutQuart`, `EaseOutBack`, `EaseInOutQuad`, `Spring`.
- **Durations stay short.** Hover transitions around 120ms, state changes around 150ms, theme crossfade around 300ms. Anything a user waits for is too slow.
- **Selection moves, it does not teleport.** An active indicator slides between positions.
- **Feedback is immediate.** A press responds on mousedown, not on mouseup.
- **Staggering is subtle.** Where items animate in sequence, offsets are around 30ms.

### Reduced motion is not optional

When `SPI_GETCLIENTAREAANIMATION` reports that animation is disabled, **all motion stops.** Not shortened: stopped. States still change, they change instantly.

This is an accessibility requirement, not a preference. Motion sensitivity is real and the system setting is the user telling you directly.

---

## 7. Iconography

- **Lucide for interface glyphs**, rendered as SVG through Direct2D so they are sharp at every scale. Never a bitmap icon set per size.
- **Icons take their colour from the theme**, through the icon colour tokens. An icon with a baked-in colour breaks in the other theme.
- **An icon is never the only label** for a destructive or ambiguous action. Pair it with text.
- **Application icons are per-tool assets** and are explicitly outside this rule: a tool's icon is never a Lucide glyph. Section 14 says how they are drawn.

---

## 8. Window chrome

- **Rounded corners** on Windows 11, via `DWMWA_WINDOW_CORNER_PREFERENCE`.
- **Backdrop material** via `DWMWA_SYSTEMBACKDROP_TYPE`, and a border colour matched to the theme.
- **A custom caption** drawn with Direct2D, so the title bar is part of the window rather than a system-coloured strip above it. Drag regions are hit-tested properly, and the window controls match the theme.
- **Taskbar integration is used where it means something**: progress on long operations, and nothing decorative.

---

## 9. Accessibility

This section is a floor, not an aspiration. A surface that fails it is not finished.

- **Every feature is reachable by keyboard.** No mouse-only action exists anywhere in the suite.
- **Tab order is logical and predictable**, following visual order.
- **Focus is always visible**: a 2px accent ring with 1px offset on the keyboard-focused element. Focus that cannot be seen is focus that does not exist.
- **Custom controls expose UI Automation.** A custom-drawn control that reports nothing to a screen reader is invisible to the people who most need it, and every control in this suite is custom-drawn.
- **Status changes are announced** through `UiaRaiseNotificationEvent`. A repair that finished silently did not finish for a screen reader user.
- **Hit targets are at least 24x24px** at 100 percent DPI, and 48x48px where touch is supported.
- **Reduced motion is honoured**, per section 6.
- **High contrast is honoured**, per section 3.
- **Colour is never the sole carrier of meaning**, per section 3.

---

## 10. Performance

A system utility that feels slow undermines its own claim to be fixing your machine.

- **Startup is fast enough to feel instant.** A tool the user launched from a launcher should not make them wait twice.
- **Brushes and text formats are pooled**, created once and reused across frames.
- **Repaints are scoped** to the region that actually changed.
- **Static control content is cached** as bitmaps and composited.
- **Render targets are GPU-backed.**
- **The UI thread never blocks.** Long work reports progress and stays responsive, and a surface that freezes during its own main action is a defect regardless of how fast the work is.

---

## 11. Content and tone

The interface is read as much as it is looked at.

- **Say what happened, per item.** "Done" tells a user nothing. Repaired, already correct, skipped, refused, or failed, each with a reason, tells them everything.
- **Name what a destructive action will affect** before asking for confirmation: what, how many, and how large. A generic "are you sure" is not a confirmation.
- **State plainly when something cannot be undone**, on the surface, before the user commits, not in the documentation afterwards.
- **A refusal names the action and what it needed.** "Access denied" is not a message; "Cannot take ownership of C:\Windows\System32: this action needs administrator rights" is.
- **Every string resolves from a language pack.** A hardcoded user-facing string is a defect, because this suite ships in up to 35 languages.
- **Write for someone whose machine is broken.** They are not in a mood for cleverness.

---

## 12. What this contract does not specify

Saying so keeps silence from reading as an oversight.

- **The content of any individual tool's main view.** The contract governs shared surfaces, tokens, and behaviour. What `ComIntRep` puts in its content area is `ComIntRep`'s business.
- **Application icons**, per section 7.
- **Exact palette values.** Those live in the theme implementation, which is the single source. This file governs the token set and the contrast floor, not the hex codes.
- **Pixel-level layout.** The captures under `docs/captures/house-style/` are the visual reference. Where this file and a capture disagree, this file wins and the capture is restaked.

---

## 13. Relationship to the AutoIt suite

`resolute_au3/` is the behavioural specification for the port and is **not** a visual reference.

Those windows are not DPI-aware, have no dark mode, and predate every rule in this file. Ports are 1:1 on behaviour and deliberately not on pixels. Reproducing an AutoIt window faithfully would freeze the defects this contract exists to remove.

---

## 14. Application icons

Each tool's icon is its own: full colour, drawn for that tool in its own repository, and never a Lucide glyph. Decided by the operator on 2026-11-15: the icons are not set on a shared tile. What they share is how they are constructed, so eighty of them read as one family in a taskbar without looking alike.

- **Free-standing.** The object is the silhouette. There is no rounded-square tile, plate or badge behind it, and each tool's outline is its own. The drawing fills an 80-unit box centred on a 96-unit grid.
- **Its own object.** The picture is the thing the tool acts on or the result it produces, chosen so it is recognisable without the name: a keyhole shield for Ownership, a drive for Drive Repair. Not an abstract mark, and not a letter. One exception is approved: Busview's mark is the letter B drawn as a chip package (operator, 2026-11-17).
- **Its own colour.** Each tool has one signature hue in two or three tones (light face, mid face, dark face) and at most one second hue as a highlight. Amber is the SDK's and the launcher's and is not a tool's signature hue.
- **One construction.** No outlines and no drop shadows. Depth comes from faces lit from the upper left: the face toward the light is the lightest tone, and a face may carry a gradient within the tool's hue. Every corner is rounded, three units at least, so no edge reads as sharp. (The earlier "flat faces, no gradients" rule was removed by the operator on 2026-11-17.)
- **Legible on both grounds.** With no tile, the icon sits directly on a light or a dark taskbar. Its tones stay in the middle of the lightness range (no face darker than `#1F1F1F` or lighter than `#F0F0F0`), and a cut-out shows the ground through it. It is checked on both grounds at 16 pixels before it ships.
- **Two drawings.** A detailed drawing for 40 pixels and up, and a simplified one below that with fewer parts and larger openings. Every size in the `.ico` is rendered from the vector, never scaled from a bitmap: 16, 20, 24, 32, 40, 48, 64, 96, 128 and 256.
- **Built by a script.** A tool's `brand/build.py` describes its icon, name, tagline and colours, and `sdk/brand/brandkit.py` writes the SVG sources, PNG renders, `.ico`, wordmarks, README banner and social preview from that, with the suite's fonts. `python brand/build.py --check` fails when a tracked asset differs from what the script builds.

The SDK's own mark (section 15) keeps its tile: it is a repository's mark, not a tool on a taskbar.
## 15. Identity of the SDK

Direction B, "Layers", chosen by the operator on 2026-11-15. Three stacked plates, the top one amber: what every tool stands on.

| Name | Value | Use |
| --- | --- | --- |
| Graphite | `#17191E` | The icon's ground and the dark ground of banners |
| Graphite raised | `#2A2E36` | The icon's ground when it sits on Graphite |
| Slate | `#717B8C` | The middle plate (`#8A93A3` on a dark ground) |
| Slate low | `#3B414D` | The lowest plate (`#4A515E` on a dark ground) |
| Amber | `#FFB020` | The top plate and the SDK chip on dark |
| Amber ink | `#7A4E00` | Amber for text and lines on a light ground, where Amber itself fails contrast |
| Paper | `#F6F5F2` | The light ground and text on dark |

Type: Sora Bold for the name, Inter for everything a person reads at length. Both are in `brand/fonts/` under the SIL Open Font License. The interface itself uses the system's Segoe UI Variable, as section 4 says.

The assets are in `brand/`, all written by `python brand/build.py` (`--check` fails when one differs from what the script builds):

| File | What it is |
| --- | --- |
| `resolute-sdk-icon.svg`, `-512.png`, `-256.png`, `-192.png`, `-64.png`, `-48.png` | The icon, detailed drawing |
| `resolute-sdk-icon-small.svg`, `-32.png`, `-16.png` | The icon's small drawing: two plates |
| `resolute-sdk.ico` | The Windows icon, ten sizes from 16 to 256 |
| `resolute-sdk-wordmark-light.svg`, `.png`, `-dark.svg`, `.png` | The icon with the name and the SDK chip |
| `readme-banner.svg`, `.png` | The README banner, 1280 by 320 |
| `social-preview.svg`, `.png` | The repository's social preview, 1280 by 640 |

Rules: the mark is never recoloured, stretched or set on a photograph; the plates keep their order and the top one is always Amber; the name is always "Resolute" with the SDK chip, never "ResoluteSDK".

## 16. The tool window

Decided by the operator on 2026-11-15, when the first seven tools each chose it from three layouts. Every tool's main window is the same arrangement, so a person who has used one tool has used them all, and a new feature gets a section instead of crowding the first screen.

```
+---------------------------------------------------------------+
| [icon] Tool name                                    _  []  X  |   caption, drawn by the library
+--------------+------------------------------------------------+
| First        | First                    [ Secondary ] [ Do ]  |   content header: the section's title, then its actions
| Second       +------------------------------------------------+
| Activity     | row                                    state   |
| Settings     | row                                    state   |   the section's content
| About        | row                                    state   |
+--------------+------------------------------------------------+
| what the content shows, in words                              |   status bar
+---------------------------------------------------------------+
```

- **Sidebar on the left.** The tool's own sections first, then Activity, Settings and About, in that order and with those names in every tool. The selected section has the accent indicator, which slides between positions. Below roughly 600 pixels of width the sidebar collapses to icons (section 5).
- **Content on the right.** A header with the section's title on the left and its actions on the right, the primary action last and drawn as the accent button, then the section's content.
- **The first section is the tool.** It opens selected and shows the thing the tool acts on as rows, each with its state as an icon and a word (section 3: colour is never the only signal). The primary action's label is the action that changes the state.
- **Activity is the log made readable.** What the tool did, newest first, one line per action with its time. Every tool has it and it is fed by the same record the log file is.
- **Settings and About are the framework's.** The tool hosts the framework's pages and adds a page of its own only for options its `DESIGN.md` names.
- **A status bar** under both panes says what the content shows, in words.
- **No menu bar, no splash screen and no decoration.** What a menu held lives in a section or in the content header.
- **Graphs** are drawn with the library's chart control, never by a tool. A tool that shows a value over time (memory in use, for example) names the series and the library draws it in the theme's colours, with the values reachable by keyboard and by a screen reader.

A tool's own `DESIGN.md` lists its sections and says what the first one shows. It does not restate this arrangement.

## 17. The installer

Decided by the operator on 2026-11-18 from real Inno Setup 7.1.1 wizards for MemBoost and Firemin, three frames and three badges: frame A, "Graphite panel", and badge 1, "Graphite arrow". Every program's installer is the same frame; only its icon, name, accent and credit change. All of it is written by `brandkit.py` from the program's `brand/build.py`, never drawn by hand (D03 T01 §3 and §4).

- **Style.** `WizardStyle=modern dynamic windows11`: the wizard follows the Windows light or dark setting, on Inno Setup's Windows 11 style.
- **Side panel** (`WizardImageFile`, Welcome and Finished pages). Graphite `#17191E` in both themes, with a radial glow of the program's signature colour at 38% opacity centred a third of the way down. The detailed icon is centred in the upper half at 104 units on the 164 by 314 grid. The name is in Sora Bold in Paper `#F6F5F2` under it, with a 40 by 3 unit rule in the signature colour. The credit is in Inter in `#C3C7CF` at the foot: "A Resolute tool by Rizonesoft", or the program's own credit as `app_assets` takes it. Rendered at every image-area size the Inno Setup 7.1.1 help lists, 202 by 386 at 100% to 534 by 1022 at 250%, and listed together with `WizardImageStretch=no`, so Setup shows each one at its own pixels and an icon is never stretched out of shape.
- **Header icon** (`WizardSmallImageFile`, the inner pages). The detailed icon on a transparent ground, square, at every size the help lists: 58, 77, 97, 116, 124, 143 and 159 pixels (100% to 250%).
- **No background image.** `WizardBackImageFile` stays unset; the page is the style's own ground.
- **Setup file icon** (`SetupIconFile`). The program's icon with a badge on its lower right: a Graphite disc with a Paper down-arrow, cut out of the icon by a ring of the ground. The disc's radius is 19 units on the 96 grid (22 below 40 pixels, with the small drawing), so the badge stays readable at 16 pixels. This is the one place a badge sits on a program's icon (section 14); the installed program keeps its plain icon, and the Add/Remove Programs entry uses the installed program's icon.
- **Pages.** Welcome, Ready, Installing and Finished, plus Inno Setup's own install-mode choice. No licence, components or program-group page.

The comparison board is the artifact the decision was made on; the captures are kept in `docs/captures/installer/`.