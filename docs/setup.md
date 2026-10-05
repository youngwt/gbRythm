# Setting up and understanding gbRythm

gbRythm is a rhythm game for the original Game Boy: a song plays, a note falls for each note of the tune, and you press the matching button as it lands.

This document does two jobs. Steps 1 to 9 take a fresh checkout to a built ROM, an automatic check of it, and playing and debugging it in an emulator. The sections after them explain how the game works, for someone new to the Game Boy: start with "How to play". Run every command from the repository root.

GitHub follows steps 1 to 5 itself on every push, running the commands exactly as they are written here, and then builds and checks the game. So if you change a command in those steps, the next push tests it.

Everything is installed into `tools/`, a folder inside the repository that git ignores. Nothing is installed system-wide, because SteamOS keeps its system partition read-only and wipes changes to it on OS updates. To start again, delete `tools/` and repeat these steps. The one thing you lose is `tools/emulicious/Emulicious.ini`, where Emulicious keeps its settings such as key bindings; copy it out first if you have changed them.

## What you need already

- `make`, `curl`, `tar`, `unzip` and `sha256sum`, which SteamOS provides.
- [`uv`](https://docs.astral.sh/uv/), which manages the Python environment. Check with `uv --version`.

These must be reachable from the terminal you use. The VS Code Flatpak terminal has its own PATH, so check there if that is where you work.

## 1. Install GBDK-2020 (the compiler)

GBDK-2020 turns C source into a Game Boy ROM. It bundles the SDCC compiler, an assembler, a linker and the Game Boy libraries, with `lcc` as the single command that drives them. The version is pinned to 4.5.0 so every build uses the same compiler.

Download the Linux release:

```sh
mkdir -p tools
curl -sSL -o tools/gbdk-linux64.tar.gz https://github.com/gbdk-2020/gbdk-2020/releases/download/4.5.0/gbdk-linux64.tar.gz
```

Check the download is the file the GBDK project published. This catches a corrupt or tampered download before you run it; it must print `OK`:

```sh
echo "d7857a5f6d135ee4c249043ca26aad9f2ec8ab5d4106d97720d404114f42605c  tools/gbdk-linux64.tar.gz" | sha256sum -c -
```

Unpack it and remove the archive. The archive contains one folder, `gbdk/`, so this creates `tools/gbdk/`:

```sh
tar -xzf tools/gbdk-linux64.tar.gz -C tools
rm tools/gbdk-linux64.tar.gz
```

Confirm the compiler runs; it prints a version line dated 2025/12/28:

```sh
tools/gbdk/bin/lcc -v
```

## 2. Install PyBoy (the headless emulator)

PyBoy is a Game Boy emulator controlled from Python. It can run a ROM with no window, which lets an agent run the game and look at the screen without a person present.

Create a Python environment inside `tools/`. A separate environment keeps PyBoy and its dependencies out of the system Python and inside the folder you can delete:

```sh
uv venv tools/venv
```

`uv` uses the system's Python (3.13 here) for the environment, and downloads one itself if it finds none.

Install PyBoy, Pillow and NumPy at pinned versions. Pillow is the image library PyBoy uses to hand over the screen as a picture. NumPy handles grids of numbers; PyBoy needs it, and the check uses it to search the screen for an image:

```sh
uv pip install --python tools/venv/bin/python pyboy==2.7.0 pillow==12.3.0 numpy==2.5.3
```

`uv` may warn that hardlinking is not supported across filesystems. That is harmless: it copies the files instead.

## 3. Install hUGEDriver (the music driver)

The Game Boy has no way to play a music file. A program makes sound by writing numbers to the sound hardware many times a second, and a music driver is the code that does this for you: you give it a song as a table of notes, call it once per frame, and it plays the next step. hUGEDriver is the one GBDK's documentation describes as smaller and more versatile than the alternative. It comes as a ready-built library that the build links into the ROM, plus a header file the C program includes. The version is pinned to 6.1.3.

Download it and check it is the file that was published; the check must print `OK`:

```sh
curl -sSL -o tools/hugedriver.zip https://github.com/SuperDisk/hUGEDriver/releases/download/v6.1.3/hUGEDriver-6.1.3.zip
echo "587f108681d49104349d8f9ea4db4be5fbeca70b09d66a3037db767b2e1c2c82  tools/hugedriver.zip" | sha256sum -c -
```

Unpack it into its own folder and remove the archive. The archive has no top folder of its own, so `-d` names one:

```sh
mkdir -p tools/hugedriver
unzip -q tools/hugedriver.zip -d tools/hugedriver
rm tools/hugedriver.zip
```

The build uses two files from it: `tools/hugedriver/gbdk/hUGEDriver.lib`, the library, and `tools/hugedriver/include/hUGEDriver.h`, the header. The `rgbds/` folder is the same driver for a different toolchain and is not used.

## 4. Build the ROM

```sh
make
```

This converts each image in `assets/` to C (see "Adding or changing an image" below), compiles `src/*.c`, links in the music driver, and writes the ROM to `build/gbrythm.gb`. The `Makefile` calls the compiler by its path in `tools/gbdk`, so it does not matter what is on your PATH. If a compile fails, `make` stops with the compiler's message, which names the file and line.

`make clean` deletes `build/`.

## 5. Run the headless check

```sh
make check
```

This builds the ROM if needed and plays it in PyBoy with no window. The emulator runs much faster than a real Game Boy, so the whole check takes about six seconds.

**First it presses Start and lets the song play twice**, with no other presses. It waits a second and a half before the first Start, leaves the results showing for ten seconds, then presses Start again. In every frame it records what is on the screen and what sound was made. Afterwards it:

1. finds the lane markers, the count words, the digits and the `PRESS START` prompt on the screen, from the PNGs in `assets/`;
2. confirms nothing fell and nothing played before Start;
3. works out which notes were played, and the frame each one started;
4. follows the falling notes, `assets/falling.png`, down the screen above each marker, frame by frame;
5. compares the frame each note landed on a marker with the frame its sound started, and the marker it landed on with the one its pitch belongs to;
6. confirms the song ended: the `RESULTS` heading appeared, the music stopped without the tune starting again, and it stayed silent, with nothing falling, until Start;
7. reads the counts off the results, which with no presses must be every note a miss;
8. confirms the second Start cleared the counts and that the second play had the same notes and the same results.

**Then it plays the song thirteen more times with scripted button presses**, pressing Start first each time, and reads the PERFECT, GOOD and MISS counts off the results:

| Presses | Every note should be |
|---|---|
| none | a miss |
| on the frame the note lands; 3 frames late; 3 early | perfect |
| 4 frames late; 7 late; 7 early | good |
| 8 frames late | a miss, with the press ignored |
| the wrong lane's button as each note lands, and the right button well after it has gone | a miss, with nothing else counted |
| every lane button held down throughout | a miss |
| on time, with Start pressed again in the middle of the song | perfect: Start changes nothing |
| lane buttons only before Start and on the results | a miss: they change nothing |
| on time, in two plays one after the other | perfect, in both plays |

It prints `PASS` and exits 0 when all of that holds. The message gives the numbers and lists the notes heard. It saves the screen, five seconds in, to `build/screenshot-play.png`.

It prints `FAIL` and exits non-zero, saying which, if:

- the ROM is missing, the screen is blank, or one of the images is not on screen;
- a note fell or music played before Start was pressed;
- the song did not end with its results, sound came back after the last note, or anything happened while the results were showing;
- the second play did not start from zero or did not match the first;
- no sound was produced, or the sound never changed note enough to be a tune (at least three different notes);
- the number of notes that landed differs from the number heard: a note sounded with nothing falling, or the reverse;
- a note landed more than two frames, a thirtieth of a second, before or after its sound;
- a note landed on the wrong marker for its pitch, for example `note 2 (G4) landed on assets/lane_2_up.png, but its pitch G belongs on assets/lane_3_right.png`;
- a falling note did not move the same distance every frame, which is what would happen if the game ran too slowly to keep up;
- any way of pressing gave the wrong counts, for example `with presses 4 frames late, the 35 notes should score 0 perfect, 35 good, 0 miss but the screen shows 35 perfect, 0 good, 0 miss`.

The check knows neither the tune nor where anything is drawn. It finds everything by looking for the PNGs on the screen, reads the counts by matching digits, and gets the notes from the sound. So after you edit the song, an image, or the layout, there is nothing else to update. What it is told is the game's design, on purpose, so that a ROM which departs from it fails: which pitch belongs to which button and marker, in the `Makefile` as `CHECK_ARGS`, and the two timing windows, at the top of `scripts/check_rom.py`.

The check finds the end of the song by watching for the `RESULTS` heading, so a longer or shorter song needs no change to it.

**How it hears.** Nothing is played out loud. The emulator works out the sound for each frame as a list of numbers, all zero when silent. A plain Game Boy tone switches between off and on at a steady rate, and how fast it switches is the pitch, so the check measures that rate in each frame and names the nearest musical note. A new note starts when the pitch changes, when sound follows silence, or when the same pitch suddenly gets louder again. The check ignores the first second, because the ROM makes a short blip about half a second after starting even with no music. The note names are the usual ones, where D4 is the D just above middle C.

**How it sees.** It compares the Game Boy's four shades, not exact colours, because the emulator's greys differ slightly from the PNG's. A falling note is a sprite, and the white parts of a sprite are see-through, so only its other pixels are compared.

PyBoy prints a warning about "SDL2 binaries from pysdl2-dll". It is informational and can be ignored.

Open the screenshot to see what the ROM drew, a few seconds into the song: notes on their way down, the five lane markers, and below them the latest judgement and the three counts.

## 6. Install Java (to run Emulicious)

Steps 6 to 9 set up an emulator with a window, so you can play the ROM and step through its C source. Building and `make check` do not need them.

Emulicious, the emulator installed in the next step, is a Java program, and SteamOS has no Java. This step unpacks a Java runtime into `tools/`. It is Eclipse Temurin 21, a free build of Java, in its "JRE" form, which runs Java programs and leaves out the developer tools.

Download it and check it is the file that was published; the check must print `OK`:

```sh
curl -sSL -o tools/java.tar.gz "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jre_x64_linux_hotspot_21.0.12.1_1.tar.gz"
echo "2413149700df0f7d440500a84a8f764c535f21e5a5e87d38328b64eec2c5b500  tools/java.tar.gz" | sha256sum -c -
```

Unpack it and remove the archive. The archive's top folder has the version in its name, so `--strip-components=1` drops that folder and puts the contents straight into `tools/java/`, a path that stays the same when the version changes:

```sh
mkdir -p tools/java
tar -xzf tools/java.tar.gz -C tools/java --strip-components=1
rm tools/java.tar.gz
```

Confirm it runs; it prints a version starting `21.0.12`:

```sh
tools/java/bin/java -version
```

## 7. Install Emulicious (the emulator with a debugger)

Emulicious is a Game Boy emulator with a window, and it has a debugger that VS Code can drive. PyBoy stays the emulator for automated checks; Emulicious is the one you look at.

Download it:

```sh
curl -sSL -o tools/emulicious.zip "https://emulicious.net/download/emulicious/?wpdmdl=205"
```

Emulicious publishes only its latest version, at one address, so there is no version number to pin. The checksum below is for the release dated 2026-03-27, downloaded 2026-10-04. It must print `OK`:

```sh
echo "6e1c6d511014033bbc2668360a0194389a5bad2bf6c5ffd0fe093b84da33c0fc  tools/emulicious.zip" | sha256sum -c -
```

If it prints `FAILED`, Emulicious has most likely released a new version. Check the date at https://emulicious.net/, and if there is a newer release, carry on and then update the checksum and date in this file. The debugging steps below were only tested with the 2026-03-27 release.

Unpack it and remove the archive:

```sh
mkdir -p tools/emulicious
unzip -q tools/emulicious.zip -d tools/emulicious
rm tools/emulicious.zip
```

## 8. Play the ROM

```sh
make run
```

This builds the ROM if needed and opens it in an Emulicious window. Emulicious's Options menu shows which keys act as the Game Boy's buttons and lets you change them.

**If the game suddenly runs many times too fast, music included, it is Emulicious's turbo.** Emulicious has a shortcut that switches turbo on and off, and its release notes say it is the Space key unless you change it. If the key you use for a Game Boy button is also that shortcut, every press of it flips turbo, so every other play races through in a second or two. The game is not at fault: other emulators play it at normal speed, and so does Emulicious when the game is started without a key press. This happened here on 2026-10-05 with the key used for Start, and remapping Start cured it. Change one of the two bindings in Emulicious's Options menu, or untick Turbo in its menu when it happens.

`make run` starts Java through `scripts/java-host.sh` instead of directly. The reason is the VS Code Flatpak: programs started from its terminal run in a sandbox that has no X11 display, and Java needs one to open a window. The script asks Flatpak to start Java on the host, outside the sandbox, with `flatpak-spawn --host`. Outside a Flatpak it just runs Java.

## 9. Step through the C source in VS Code

This lets you stop the running ROM on a line of C and look at the variables.

Install the Emulicious Debugger extension, version 1.3.0. VS Code offers it when you open this folder, because `.vscode/extensions.json` recommends it, or install it from the terminal:

```sh
code --install-extension emulicious.emulicious-debugger@1.3.0
```

Then:

1. Open `src/game.c` and click to the left of a line number to set a breakpoint, shown as a red dot. The line `falling_active[i] = 1;` is a good first one: it runs each time a note starts to fall.
2. Press F5.
3. An Emulicious window opens with the ROM showing `PRESS START`. Press Start in it, and the first note starts to fall.
4. VS Code stops on that line. The Variables panel and hovering over `read_row` or `row_note` show their values. F10 steps to the next line and F5 continues.

What F5 does is set out in `.vscode/launch.json`, with the build step in `.vscode/tasks.json`:

- It first runs `make debug`, which builds a second ROM in `build/debug/`. That build adds two compiler flags. `-debug` writes `gbrythm.cdb`, the file that tells the debugger which machine code came from which line of C. `-Wf--max-allocs-per-node0` turns off an optimisation that reorders code, so stepping follows the source line by line. The second flag makes the code bigger and slower, so the debug ROM is kept separate: the ROM that `make check` tests is always the normal one.
- It then starts Emulicious through `scripts/java-host.sh`, for the reason given in step 8, and connects to it on port 58870.

The extension tries to connect every tenth of a second and by default gives up after 25 tries, which a slow start of Java can exceed. `.vscode/settings.json` raises that to 100, about ten seconds. If F5 still reports that it could not connect, press F5 again.

## How to play

Open the ROM with `make run`, or in any Game Boy emulator: the file is `build/gbrythm.gb`.

1. The screen shows `PRESS START`. Press Start.
2. The first verse of "Amazing Grace" plays. For each note of the tune a note falls down one of five lanes. Each lane ends in a marker showing its button:

   | Lane | Marker | Button |
   |---|---|---|
   | 1 | left arrow | Left |
   | 2 | up arrow | Up |
   | 3 | right arrow | Right |
   | 4 | B | B |
   | 5 | A | A |

3. Press a lane's button as its note lands on the marker, which is the moment you hear it. The word under the markers tells you how you did: `PERFECT`, `GOOD`, or `MISS` if the note got past you. The three counts below keep score.
4. The song lasts about half a minute and has 35 notes. When it ends, `RESULTS` appears and your counts stay on screen. Press Start to play again.

Things worth knowing as a player:

- The lanes follow the tune's pitch: the lowest note is on the left and the highest on the right, so the notes move across the lanes the way the melody rises and falls.
- You cannot fail, and there is no penalty for pressing when no note is near.
- The Down and Select buttons do nothing.
- If everything suddenly runs many times too fast in Emulicious, see the note on turbo under step 8.

The sections below explain how each part works and where to change it: "How the falling notes work", "How judging works", "How a play starts and ends", and "How the music works".

## Adding or changing an image

The Game Boy cannot display a picture file. Its screen is built from 8×8 pixel squares called tiles, and a program supplies two things: the tiles themselves, and a map saying which tile goes at each position. GBDK's `png2asset` tool turns a PNG into exactly that pair, written as C.

The build runs it for you. Every `assets/NAME.png` becomes `build/NAME.c` and `build/NAME.h`, and the C program includes `NAME.h` to get the tiles (`NAME_tiles`), the map (`NAME_map`) and the sizes. The generated files are build output: they are not committed and are never edited by hand. To change what is on screen, edit the PNG and run `make`; it notices the PNG changed and reconverts it.

An image must fit what the original Game Boy can show:

- **Width and height are multiples of 8 pixels**, because the screen is made of 8×8 tiles.
- **At most four shades.** The original Game Boy has four: white, light grey, dark grey and black. Use `#FFFFFF`, `#AAAAAA`, `#555555` and `#000000`.
- **Use all four shades.** The converter numbers the shades it finds from lightest to darkest, so an image that skips one is shown with the others shifted: with no white, for example, its lightest shade is drawn as white. One pixel of each shade is enough. The grey line under every marker and word in this game is partly there for this.
- **No larger than the screen**, which is 160×144 pixels.

If an image breaks any of the first three rules, `make` stops and prints an error naming the image. The converter is not much help here: it exits successfully even when it reports an error, it accepts a fifth shade without complaint when that shade sits in a tile of its own, it says nothing about a missing shade, and on some images with too many colours it simply crashes. `scripts/convert-images.sh` checks for each of these. The converter's full output is kept in `build/NAME.c.log`.

**Several images.** Background tiles are numbered 0 to 255. The lower half is kept for the Game Boy's built-in text font, which this game no longer uses, so images share numbers 128 to 255: 128 tiles between them. The build hands these out for you. `scripts/convert-images.sh` converts the images in alphabetical order and starts each one where the one before ended, so any number of images can be on screen together without overwriting each other, and you never type a tile number. Today there are twelve images using 45 tiles between them: the digits, the falling note, the five lane markers and five words or phrases. The C program reads each image's start from `NAME_TILE_ORIGIN`.

Because the numbers depend on the images before, changing any PNG reconverts all of them. Two things stop the build with a message:

- **Tile space ran out.** The images together need more than 128 tiles. The message names the image that did not fit. Identical tiles within one image are stored once, so plain areas cost little; a large detailed picture costs a lot.
- **An image shares a name with a C source file**, such as `assets/main.png` beside `src/main.c`. Both would compile to the same file in `build/`, so rename the image.

Moving objects, called sprites, use a separate set of tiles and are not covered here.

## How the falling notes work

The play screen is `src/game.c`. Five markers sit in a row near the bottom of the screen, one for each button, and a note falls for each note of the tune, landing on a marker as the note sounds.

**The five lanes.** A note's pitch decides which lane it falls in, lowest on the left:

| Lane | Marker | Button | Note |
|---|---|---|---|
| 1 | left arrow | Left | D |
| 2 | up arrow | Up | E |
| 3 | right arrow | Right | G |
| 4 | B | B | A |
| 5 | A | A | B |

The same pitch falls in the same lane in every octave, so the high D of "like me" shares lane 1 with the low D. Mind the names: the note A falls on the B button's lane, and the note B on the A button's. The tune uses exactly these five pitches. A note of any other pitch has no lane and nothing falls for it, which `make check` reports as a note heard with nothing falling.

In `src/game.c` the mapping is the table `lane_of_pitch`, with one entry for each of the twelve pitches in an octave, and `lane_x` says how far across the screen each lane is.

**Background and sprites.** The Game Boy draws two kinds of picture. The background is a grid of tiles that stays put: the markers, words and counts are background. A sprite is a single small picture that can be placed anywhere, pixel by pixel, on top of the background: each falling note is a sprite. Sprites can use the same tiles as background images, so the falling note comes from a PNG in `assets/` like any other image. Wherever the PNG is white, a sprite is see-through.

**Where the notes come from.** There is no list of falling notes. The game reads the song itself, the same rows in `src/song.c` that the music driver plays, and drops a note from the top whenever a row starts one. A row that uses the silent instrument is a rest and drops nothing. If a pattern ends early with the pattern-break effect, the reader follows it, just as the driver does.

**How they arrive in time.** A note needs time to fall, so the game cannot wait until it hears the note. Instead the reader gets a head start: it begins reading the song one second before the music begins. A note is dropped when the reader reaches its row, falls for exactly one second, and lands as the music reaches the same row. That one second is `LEAD_FRAMES` in `src/game.c`, 60 frames, and a note falls 2 pixels every frame. It starts just above the top edge of the screen, out of sight.

**One clock.** The Game Boy tells the program each time it finishes drawing a frame, sixty times a second. Two things happen on that signal, in `game_frame`: the frame is counted, and the music driver is run. The rest of the game then deals with each counted frame in turn. If the game were ever slow and missed one, it does two steps the next time, so the falling notes cannot slip behind the music. The music starts and stops on exact frame counts, not on when the game gets round to it, so a slower build of the same code keeps the same time.

**Changing it.** Edit the song and the falling notes follow, with nothing else to change; `make check` will report the new count. To make notes fall for longer or faster, change `LEAD_FRAMES` and `FALL_SPEED` together so that one multiplied by the other is still the distance a note travels, 120 pixels.


## How judging works

Press a lane's button as its note reaches the marker. The game grades the press by how close it was:

| Judgement | The press was | In time |
|---|---|---|
| PERFECT | within 3 frames of the note landing, early or late | a twentieth of a second either side |
| GOOD | within 7 frames | about an eighth of a second either side |
| MISS | not made by 7 frames after landing | |

The latest judgement is shown under the markers, and below it the three running counts.

- **A press counts once**, on the frame the button goes down. Holding a button does nothing more.
- **A note is judged once.** A judged note disappears. A note nobody presses carries on a little way past its marker, while a late press could still count, and then becomes a miss.
- **Stray presses are ignored.** A press with no note within the good window in that lane does nothing: not a miss, no penalty. That includes pressing the wrong lane's button.
- **If two notes in a lane are both within reach**, the press goes to the one nearest its marker.
- **You cannot fail.** The song always plays to the end, and misses are only counted.
- **The score starts again with each play.** Pressing Start sets the three counts to zero and clears the latest judgement.

**Distance is time.** Notes fall at a steady 2 pixels a frame, so the game does not time presses. It measures how far the note is from its marker: 6 pixels is 3 frames, 14 pixels is 7.

**What you see is a frame behind.** The game moves a sprite and the Game Boy shows the move one frame later than it shows changes to the background. So when a note looks as if it is on its marker, the game already has it one step further down, and it judges against that. Without this allowance every press would be judged a frame late. You may notice the same lag the other way: a judged note vanishes one frame after its word and count change.

**Changing the windows.** `PERFECT_FRAMES` and `GOOD_FRAMES` are near the top of `src/game.c`. The same two numbers are at the top of `scripts/check_rom.py`, which tests the edges of each window; change both together, or `make check` will fail and tell you which press was judged differently.

**The words and digits are images**, drawn from PNGs in `assets/` like the markers, not the Game Boy's built-in text. That is what lets `make check` read the counts off the screen. Each count is kept as two separate digits, because dividing by ten to display a number is slow on this hardware. It stops at 99.

## How a play starts and ends

The game is always doing one of three things: waiting, playing, or showing the results.

- **Waiting.** When the ROM opens it shows `PRESS START` and does nothing else. No note falls and no music plays.
- **Playing.** Start clears the score, removes the prompt, and begins the song. The first note starts to fall at once and the music begins a second later, as it lands. Pressing Start again during the song does nothing.
- **Results.** The song plays once. When its last row has played, the music stops, and once the last note has been judged a `RESULTS` heading and the prompt appear. The three counts stay where they were during play: they are the results, and they add up to the number of notes in the song. Start plays again from the beginning.

Lane buttons do nothing while waiting or on the results.

**How the game knows the song is over.** The reader, which runs a second ahead of the music, adds up how long each row lasts as it goes. When it reaches the end of the song's last pattern it knows how many frames the song takes, and tells the music to stop after exactly that many. The music then switches the sound hardware off and is no longer run; once more and the driver would start the tune again, which `make check` listens for.

**The results are not a separate screen.** They are the play screen with a heading, so the counts are drawn one way only.

## How the music works

This section explains the music from scratch. The song itself is `src/song.c`, and its comments repeat the details beside the code.

**The sound hardware.** The Game Boy has four sound channels, each a simple tone generator, and their outputs are mixed together:

| Channel | What it makes | Typical use |
|---|---|---|
| 1 | A square wave: a plain beep. Its pitch can also slide | Melody |
| 2 | A square wave | Harmony or a second melody |
| 3 | A short wave shape that the program supplies | Bass, softer tones |
| 4 | Noise: a hiss | Drums |

A program makes a note by writing a pitch and a volume to a channel. Nothing plays a tune on its own: to play music, something has to write the next note at the right moment, over and over.

**The music driver.** That something is the driver, hUGEDriver. The C program hands it a song and arranges for it to be called once per frame, sixty times a second. Each call, the driver works out whether it is time for the next step of the song and writes to the channels if so. In `src/main.c` this is three lines that switch the sound hardware on, then `hUGE_init` to hand over the song and `add_VBL` to have the driver called every frame.

**The song file.** A song is a table of notes, in the same form the hUGETracker editor would write. It is plain C, so it can be written and changed as text; this one was written by hand.

- A **pattern** is 64 rows. Each row is `DN(note, instrument, effect)`. A note is a name such as `G_5`, or `___` to leave the channel as it is, so a note keeps sounding until another replaces it. The driver steps through the rows one at a time.
- Each channel plays its own pattern, and the four are stepped through together. Here channel 1 plays `melody` and the other three play `silence`, a pattern of empty rows.
- The **order** lists which pattern each channel plays at each step of the song. This song has three steps: `melody_1`, `melody_2`, `melody_3`.
- An **effect** on a row changes how the song plays. None is used in this song. One worth knowing is `D01`, pattern break, which ends a pattern early: a pattern is always 64 rows, and this skips the ones a tune does not need. The falling notes follow it correctly.
- An **instrument** says how a note sounds: its starting volume, how it fades, and its wave shape. Instrument 1 starts at full volume and fades slowly. A row cannot say "stop", so instrument 2, which has no volume, is used as a rest.
- The **tempo** is how many frames each row lasts. At 10, a row is a sixth of a second.

**Reading the melody.** "Amazing Grace" has three beats to the bar. In this file one beat is four rows, so a half note is eight rows, an eighth note is two, and a dotted quarter note is six. The song is the whole first verse, 35 notes in 192 rows, which is three patterns exactly:

| Words | Notes |
|---|---|
| Amazing grace, how sweet the sound, | D G B G B A G E D |
| that saved a wretch like me. | D G B G B A D (the D above) |
| I once was lost, but now am found, | B D B D B G D E G G E D (the first two Ds are the D above) |
| was blind but now I see. | D G B G B A G |

Where a word is sung on two notes, such as "-zing" and "once", both are in the file. A note still sounding when a pattern ends carries on into the next, as "now" does between the second and third.

In four places two neighbouring notes are the same pitch, for example "sound" and "that", both D. On the Game Boy you hear the second one start, because each note begins at full volume and fades. The headless check counts them as two notes, by the jump in loudness, but its printed list of notes heard shows each such pair once.

One trap: the driver names octaves one higher than usual. Its `D_5` sounds as the D just above middle C, which most music, and the headless check, calls D4.

**Changing the tune.** Edit a note name in `src/song.c` and run `make check`. The check prints the notes it heard, so the change shows up there without anyone listening: changing `E_5` to `Fs5` turns `... G4 E4 D4` into `... G4 F#4 D4`. To change the speed, change the tempo number at the bottom of the file. To hear it, run `make run`.

**What is not here yet.** One channel, one verse, no drums and no sound effects.

## Everyday commands

Once the tools are installed, these are all you need. Run them from the repository root.

| Command | What it does |
|---|---|
| `make` | Builds the ROM, `build/gbrythm.gb` |
| `make check` | Builds, then runs the ROM with no window and reports `PASS` or `FAIL` |
| `make run` | Builds, then opens the ROM in Emulicious to play |
| `make debug` | Builds the debug ROM in `build/debug/`; F5 in VS Code does this for you |
| `make check-debug` | Runs the same check on the debug ROM, the one F5 runs |
| `make clean` | Deletes `build/` |

## Where things are

| Path | What it is | In git? |
|---|---|---|
| `src/` | C source for the ROM | yes |
| `assets/` | PNG images shown by the ROM: the lane markers, the falling note, the words and the digits | yes |
| `Makefile` | Build and check commands | yes |
| `src/game.c` | The game: waiting for Start, the lanes, the falling notes, judging, the counts and the results | yes |
| `src/song.c` | The song, the first verse of "Amazing Grace", as a table of notes | yes |
| `scripts/check_rom.py` | The headless check, one function for each thing it checks | yes |
| `scripts/screen.py`, `scripts/sound.py` | The check's helpers for reading the screen and the sound | yes |
| `scripts/run-setup-steps.py` | Runs the commands of the numbered steps in this document, as written; GitHub uses it | yes |
| `.github/workflows/build.yml` | Tells GitHub to build and check the game on every push | yes |
| `scripts/convert-images.sh` | Converts the images to C and hands out their tile numbers | yes |
| `scripts/java-host.sh` | Starts Java on the host so it can open a window | yes |
| `.vscode/` | VS Code debug configuration | yes |
| `tools/gbdk/` | GBDK-2020 4.5.0 | no |
| `tools/venv/` | Python environment with PyBoy | no |
| `tools/hugedriver/` | hUGEDriver 6.1.3, the music driver | no |
| `tools/java/` | Java runtime, Temurin 21 | no |
| `tools/emulicious/` | Emulicious | no |
| `build/` | The ROM, screenshots, C generated from images, and compiler output | no |
| `build/debug/` | The debug ROM and its `.cdb` debug symbols | no |

## What was found

These questions were open when the work was planned. These are the answers, found on 2026-10-04.

**Which Java does Emulicious need, and can it open a window from the VS Code Flatpak?** Emulicious's `ReadMe.txt` says "Java 6 or newer", so any current Java works; Temurin 21, a long-term-support release, was chosen. Java unpacked inside the repository runs in the sandbox, but cannot open a window there: started from the Flatpak terminal, Emulicious fails with `HeadlessException: No X11 DISPLAY variable was set`, and setting `DISPLAY=:0` by hand fails with "Authorization required". Started on the host with `flatpak-spawn --host`, the same Java and the same files run without that error. So Java must launch on the host, which is what `scripts/java-host.sh` does. One trap: in the sandbox Emulicious still opens its debugger port even though it has no window, so a successful connection does not prove the window appeared.

**Does the Emulicious VS Code debugger extension, last released 2023-11, still work?** Version 1.3.0 installs without complaint on VS Code 1.139.1 from the marketplace. The extension is small: it starts Emulicious and hands VS Code the port, and Emulicious itself does the debugging, so the extension's age matters less than Emulicious's, which was last released 2026-03-27 and lists remote-debugger fixes in its `WhatsNew.txt`. The check that matters needs a person: on 2026-10-04 the user set a breakpoint in `src/main.c`, pressed F5, and reported that it worked. So yes, it still works.

**Does hUGEDriver's ready-built library work with GBDK 4.5.0?** Yes. The worry was that release 6.1.3 was built in 2024 against GBDK 4.1.1, three versions older than the one used here. Found on 2026-10-04: the driver's own example program and song compile and link against the library with GBDK 4.5.0 with no errors or warnings, and run in PyBoy producing sound in 185 of the first 240 frames. The proof ROM then linked the same library and plays its own song. Nothing had to be rebuilt, so the driver's source and the RGBDS assembler it needs are not installed.

**Can PyBoy hear sound?** Yes. With sound emulation switched on it exposes each frame's sound as numbers, which is what the headless check reads. Whether what it produces matches a real Game Boy has not been compared.

**Does the game fit in 32K, and can it keep up at 60 frames a second?** Yes to both, so far. Found on 2026-10-05 with the song's notes falling in one lane: `tools/gbdk/bin/romusage build/gbrythm.gb` reports 6,921 bytes used of 32,768, about a fifth. For speed, the headless check follows every falling note for 1,500 frames and each one moved exactly 2 pixels in every frame; a game that fell behind would show a note standing still and then jumping, and when that was forced on purpose the check caught it. This is measured in the PyBoy emulator, not on a real Game Boy, and with no judging yet. With five lanes the figures were 7,357 bytes and the same steady 2 pixels. With judging added, and the built-in text routines no longer used, it was 5,641 bytes; notes still move steadily while judgements and counts are being drawn. The finished first playable, with the whole verse, Start and the results, is 6,531 bytes, about a fifth of the space.

**Do the notes land in time?** Yes. With the whole verse, all 35 notes in each of the check's two plays land within one frame of their sound starting.

**Does the build and check work on a machine that has never seen the project?** Yes. On 2026-10-05 GitHub followed steps 1 to 5 of this document on a fresh Ubuntu machine, built the ROM and passed both headless checks, in 24 seconds. PyBoy, which until then had only run on the Steam Deck, needed no change. A push with the check broken on purpose failed at step 5, as it should.

One question is still open: whether PyBoy's picture matches Emulicious's closely enough to trust the headless check. It is a parked ticket in `_bmad-output/backlog/`.
