# Digest: music and sync, round 1 (accessed 2026-10-03)

- hUGEDriver GBDK usage: export song from hUGETracker as "GBDK .c"; include hUGEDriver.h; `hUGE_init(&song)`; call `hUGE_dosound` "at a regular interval (usually on VBlank, the timer interrupt, or simply in your game's main loop)"; link hUGEDriver.o/lib; enable sound via NR52/NR51/NR50 | github.com/SuperDisk/hUGEDriver README | SuperDisk | repo pushed 2026-08 | high
- hUGETracker and hUGEDriver "are dedicated to the public domain" | same README | high
- Driver effect list includes "6 - Call routine"; patterns are 64 rows of note/instrument/effect | hUGEDriver doc/driver-format.txt | SuperDisk | high
- Exported GBDK song is a plain C source file: arrays of `DN(note, instrument, effect)` rows (e.g. `DN(C_5,1,0x2FF)`) | hUGEDriver gbdk_example/src/sample_song.c | SuperDisk | high
- GBDK example registers the driver with `add_VBL(hUGE_dosound)` inside `__critical` | gbdk_example/src/gbdk_player_example.c | high
- Release v6.1.3 (2024-07-14) zip ships prebuilt `gbdk/hUGEDriver.lib` + `include/hUGEDriver.h` + rgbds asm | release asset listing (downloaded, unzip -l) | high | version
- CI builds that lib with RGBDS v0.6.1 and GBDK 4.1.1 (rgbasm -DGBDK -> rgb2sdas.py -> sdar) | .github/workflows/build.yml | high | version/compat
- Driver repo last commits 2026-08-25, 2026-08-15, 2025-04-25 (newer than last release) | GitHub API commits | high
- untoxa/rhythm: "Rhythm game which is actually a hUGEDriver demo"; MIT; C + GBDK-2020 v4.0 + make; uses hUGEDriver "routines": C handlers called when the special effect is hit, each sets a pending-note bit that the game loop turns into a falling note sprite; created 2020-09, last push 2023-02, 8 stars | github.com/untoxa/rhythm (readme, src/routines.c, src/rhythm.c) | untoxa | high (existence); medium (currency: targets GBDK 4.0)
- GB Studio docs: music routines 0-3 can be triggered from a .uge file via the call routine effect to run scripts in time to music | gbstudio.dev/docs/assets/music/music-huge (search summary only, page not read) | GB Studio | medium
- hUGETracker v1.0.11 2024-12-29 ships a Linux zip; repo pushed 2026-08-25 | GitHub API | high | version
- GBDK docs: hUGEDriver "smaller, more efficient and more versatile than gbt_player" | gbdk.org links and tools | high
- DMG timer selectable 4096 / 262144 / 65536 / 16384 Hz; TIMA overflow reloads TMA and requests interrupt | gbdev.io Pan Docs, Timer and Divider Registers | gbdev | high

Leads / gaps
- Not found: documentation of the binary .uge file format or a command-line .uge -> .c converter (one search, no hits).
- Not verified: prebuilt hUGEDriver.lib (built against GBDK 4.1.1) links cleanly with GBDK 4.5.0.
- Not found: any measured input-latency or timing-jitter figures for C/GBDK rhythm games.
