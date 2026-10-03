# Digest: surrounding tools, round 1 (accessed 2026-10-03)

- Emulicious: runs on Windows, Linux, Raspberry Pi OS, macOS, "any other operating system supporting Java SE"; free to use (open-source status not stated); emulates GB, GBC, SMS, GG, MSX; debugger with breakpoints/watchpoints, source loading, profiler, tracer, coverage, remote debugging, VS Code integration; footer date 2026-03-19 | emulicious.net | Calindro | 2026-03 | high
- Emulicious Debugger VS Code extension v1.3.0 2023-11-06, repo last push 2023-11 | GitHub API Calindro/emulicious-debugger | high | ecosystem
- GBDK docs: Emulicious debug adapter gives C source-level debugging in VS Code; `-Wf--max-allocs-per-node0` helps stepping; romusage reports bank usage; "GBDK GitHub Action Builder" exists for CI | gbdk.org links and tools | high
- Forum: pass `-Wf--debug -Wl-m -Wl-w -Wl-y` via lcc for debug info; ROM and CDB in project root | gbdev.gg8.se forum (search summary) | low-medium
- PyBoy: Game Boy emulator in Python; `pip install pyboy`; headless; API for button presses, `tick()`, screen image (PIL), memory reads; aimed at bots/RL; 5213 stars; pushed 2026-10-02; GitHub release v2.7.1 2026-05-05; PyPI shows 2.7.0, requires Python >=3.9 | github.com/Baekalfen/PyBoy + pypi.org | high (API), version mismatch noted
- PyBoy accuracy and sound support: not stated in what was read.
- GBDK ships `png2asset` (PNG to C conversion; 4.5.0 added metafile option) | GBDK release notes via releases page | medium
- GBDK ROM/MBC: 32K ROM-only needs no MBC; "For most projects we recommend MBC5"; flags `-Wm-yt<N>`, `-Wm-yo<N>`, `-Wm-ya<N>`, `-autobank` | gbdk.org docs_rombanking_mbcs | high
- SameBoy v1.0.3 2026-03-04: release assets are macOS/iOS/Windows only (no Linux binary in release) | GitHub API | high
- mGBA 0.10.5 2025-03-09 has Linux AppImage | GitHub API | high
