# Digest: field of toolchains, round 1 (accessed 2026-10-03)

Claims (claim | source | publisher | pub_date | confidence | class)
- GBDK-2020 latest stable is 4.5.0, published 2025-12-28; prebuilt linux64 and linux-arm64 tarballs; repo pushed 2026-09-30; 2306 stars | api.github.com/repos/gbdk-2020/gbdk-2020 (+/releases) | GitHub API | 2025-12 | high | version
- 4.4.0 published 2025-05-19, 4.3.0 2024-03-15 (roughly 7-14 month cadence) | same | GitHub API | high | ecosystem
- RGBDS latest v1.0.4 published 2026-09-22; pushed 2026-10-02; 1657 stars; MIT; assembly toolchain (rgbasm/rgblink/rgbfix/rgbgfx) | api.github.com/repos/gbdev/rgbds | GitHub API | 2026-09 | high | version
- GB Studio latest v4.3.2 2026-06-22; 9412 stars; Linux AppImage/deb/rpm; TypeScript; MIT | api.github.com/repos/chrismaltby/gb-studio | GitHub API | 2026-06 | high | version
- ZGB (C engine on GBDK): last release v2023.0 2023-08-18, last push 2024-08-01 -> stale | api.github.com/repos/Zal0/ZGB | GitHub API | high | ecosystem
- CrossZGB (fork under gbdk-2020 org): v2026.1 2026-03-13, pushed 2026-09-18, 73 stars | api.github.com/repos/gbdk-2020/CrossZGB | GitHub API | high | ecosystem
- gbdev.io resources lists compilers: RGBDS, ASMotor, wla-dx, GBDK ("powered by an updated version of the SDCC toolchain"), Turbo Rascal, Wiz, gbforth, gbasm-rs, tniASM, llvm-gbz80/clang-gbz80, gbdk-go; engines ZGB, Retr0 GB | gbdev.io/resources.html | gbdev | undated | medium | landscape
- GBDK docs: install = download release and unzip; build examples with `make`; start from `template_` projects in examples | gbdk.org/docs/api/docs_getting_started.html | GBDK-2020 | undated (current docs) | high
- GBDK coding guidelines: prefer 8-bit unsigned; no floats; avoid mul/div/mod non-power-of-2; prefer globals over locals; no recursion; use vsync() to idle between frames; wrap ISR-shared vars in __critical; performance-critical functions in asm | gbdk.org/docs/api/docs_coding_guidelines.html | GBDK-2020 | high
- GBDK docs tool list: hUGETracker/hUGEDriver "work with GBDK and RGBDS... smaller, more efficient and more versatile than gbt_player"; CBT-FX; VGM2GBSFX; GBT Player; Emulicious "source level debugging" + VS Code debug adapter; BGB; romusage; GBDK GitHub Action Builder; png2asset | gbdk.org/docs/api/docs_links_and_tools.html | GBDK-2020 | high
- CBT-FX repo archived (2022); gbt-player last release 2022-05, pushed 2026-01 | GitHub API | high | ecosystem
- hUGETracker v1.0.11 2024-12-29 with Linux zip; pushed 2026-08-25; hUGEDriver v6.1.3 2024-07-14, pushed 2026-08-26 | GitHub API | high | version
- Emulicious VS Code debugger extension v1.3.0 2023-11-06 | GitHub API | high

Note: a WebFetch summary of the GBDK releases page gave 2024 dates; GitHub API contradicts (2025). API taken as authoritative.

Leads: llvm-gbz80 status unknown (repo not located); GB Studio as wildcard (visual, C engine underneath); PyBoy for headless agent testing.
Not found: any second maintained C compiler for the Game Boy besides SDCC/GBDK.
