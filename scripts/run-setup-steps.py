"""Run the commands in docs/setup.md, exactly as written.

Usage: run-setup-steps.py FIRST [LAST]

Runs every command block under the numbered steps FIRST to LAST of
docs/setup.md, in order, and stops at the first that fails, naming the step.
With one number it runs that step alone. "make run" is skipped, because it
opens a window.

This is how GitHub installs the tools and builds the game: by following the
same instructions a person follows. If the instructions are wrong or go out
of date, the build on GitHub fails, so they cannot quietly rot.

Needs only Python's standard library, so it runs before anything is
installed.
"""

import re
import subprocess
import sys
from pathlib import Path

INSTRUCTIONS = Path(__file__).resolve().parent.parent / "docs" / "setup.md"
SKIPPED = {"make run"}


def steps() -> dict[int, tuple[str, list[str]]]:
    """Each numbered step's title and its command blocks, in order."""
    found: dict[int, tuple[str, list[str]]] = {}
    number = None
    # A heading such as "## 3. Install hUGEDriver", any other heading, or a
    # block of shell commands between ```sh and ```.
    pattern = re.compile(r"^## (?:(\d+)\. )?([^\n]*)$|^```sh\n(.*?)^```", re.M | re.S)
    for match in pattern.finditer(INSTRUCTIONS.read_text()):
        if match.group(3) is None:
            number = int(match.group(1)) if match.group(1) else None
            if number is not None:
                found[number] = (match.group(2), [])
        elif number is not None:
            found[number][1].append(match.group(3))
    return found


def main() -> int:
    if len(sys.argv) not in (2, 3) or not all(arg.isdigit() for arg in sys.argv[1:]):
        print(__doc__)
        return 2
    first = int(sys.argv[1])
    last = int(sys.argv[2]) if len(sys.argv) == 3 else first

    found = steps()
    for number in range(first, last + 1):
        if number not in found:
            print(f"FAIL: docs/setup.md has no step {number}")
            return 1
        title, blocks = found[number]
        print(f"=== Step {number}: {title}", flush=True)
        for block in blocks:
            if block.strip() in SKIPPED:
                print(f"--- skipped: {block.strip()}", flush=True)
                continue
            print("--- running:\n" + block, end="", flush=True)
            # -e stops a block at its first failing command, as a person
            # following the instructions would stop.
            result = subprocess.run(["sh", "-e", "-c", block], cwd=INSTRUCTIONS.parent.parent)
            if result.returncode != 0:
                print(f"FAIL: step {number} of docs/setup.md ({title}) failed at the commands above")
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
