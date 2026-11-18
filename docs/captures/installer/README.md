# Installer frame captures

Captured 2026-11-18 on Windows 11 from real Inno Setup 7.1.1 wizards (D03 T01 §2). Frames: `a` Graphite panel (chosen), `b` Accent wash, `c` Quiet float; each for MemBoost and Firemin, light and dark, on the Welcome, Ready and Finished pages. `badges/` holds the three setup-icon badges at 256 pixels beside each program's plain icon; badge 1, Graphite arrow, was chosen.

How they were made: `make_art.py` renders the art from each tool's `brand/build.py` through `brand/brandkit.py`, `preview.iss` builds a preview wizard from it with `/D` defines, and `capture.ps1` compiles each preview, clicks through it and captures each page with `PrintWindow`. These are the decision's record, not the build; D03 T01 §3 and §4 move the art into `brandkit.py`.
