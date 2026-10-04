#!/bin/sh
# Runs the Java in tools/java, passing every argument through.
#
# Inside the VS Code Flatpak there is no X11 display, so Java cannot open a
# window there. flatpak-spawn --host starts it on the host instead, where the
# display is. The repository is at the same path on both sides, and both share
# one network, so the debugger in VS Code can still reach Emulicious.
# Outside a Flatpak this simply runs Java.

JAVA="$(cd "$(dirname "$0")/.." && pwd)/tools/java/bin/java"

if [ ! -x "$JAVA" ]; then
    echo "Java not found at $JAVA. Follow docs/setup.md." >&2
    exit 1
fi

if [ -e /.flatpak-info ]; then
    # --watch-bus stops Java when the program that started it goes away.
    exec flatpak-spawn --host --watch-bus --directory="$PWD" "$JAVA" "$@"
fi

exec "$JAVA" "$@"
