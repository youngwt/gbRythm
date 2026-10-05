#!/bin/sh
# Converts every PNG given into C for the Game Boy background, one after
# another, giving each image the next free tile numbers.
#
# Usage: convert-images.sh PNG2ASSET OUTPUT_DIR IMAGE.png...
#
# The background can use 256 tile numbers. The text font has the lower half,
# so images share 128 to 255. Each image starts where the one before ended,
# which is why they are converted together and in a fixed order: the order
# the names are given in.

FIRST_TILE=128
TILE_LIMIT=256

png2asset=$1
output_dir=$2
shift 2

next_tile=$FIRST_TILE
for png in "$@"; do
    name=$(basename "$png" .png)
    out="$output_dir/$name.c"

    # The image's C file is compiled to build/NAME.o, the same object file
    # a source file of that name would use.
    if [ -e "src/$name.c" ]; then
        echo "error: $png and src/$name.c share a name; rename the image." >&2
        exit 1
    fi

    # -map exports a background image: a set of 8x8 tiles plus a map saying
    # which tile goes where. This writes both the .c and its .h.
    # -noflip keeps mirrored tiles separate; the original Game Boy cannot
    # flip background tiles.
    # png2asset exits 0 even when it reports an error such as too many
    # colours, so its output is kept in a log and checked.
    "$png2asset" "$png" -map -tile_origin "$next_tile" -noflip -o "$out" > "$out.log" 2>&1
    status=$?
    cat "$out.log"
    if grep -qi "error" "$out.log"; then
        exit 1
    fi
    # The converter can also stop without a message; it crashes on some
    # images with more than four colours.
    if [ "$status" -ne 0 ]; then
        echo "error: the image converter failed on $png without saying why (exit status $status). Check the image uses only the Game Boy's four shades." >&2
        exit 1
    fi

    # A fifth shade in a tile of its own is not reported as an error: the
    # converter quietly makes a second palette, which only the Game Boy
    # Color has. One palette means the image fits the four shades.
    palettes=$(sed -n "s/^#define ${name}_PALETTE_COUNT \([0-9][0-9]*\).*/\1/p" "$output_dir/$name.h")
    if [ "$palettes" != "1" ]; then
        echo "error: $png uses more than four shades; the original Game Boy has only four." >&2
        exit 1
    fi

    # The converter numbers the shades it finds from lightest to darkest, so
    # an image that skips one of the four is shown with the others shifted:
    # with no white, its lightest shade is drawn as white. Every image must
    # therefore use all four. The palette in the generated C lists them, with
    # the last repeated when there are fewer.
    shades=$(grep -A1 "${name}_palettes\[" "$out" | grep -o 'RGB8([^)]*)' | sort -u | wc -l)
    if [ "$shades" -ne 4 ]; then
        echo "error: $png uses $shades of the Game Boy's four shades; it must use all four (white, light grey, dark grey, black), or the ones it has are shown shifted." >&2
        exit 1
    fi

    count=$(sed -n "s/^#define ${name}_TILE_COUNT \([0-9][0-9]*\).*/\1/p" "$output_dir/$name.h")
    if [ -z "$count" ]; then
        echo "error: could not read the tile count of $png from $output_dir/$name.h." >&2
        exit 1
    fi

    if [ $((next_tile + count)) -gt "$TILE_LIMIT" ]; then
        echo "error: tile space ran out at $png: it needs $count tiles and $((TILE_LIMIT - next_tile)) are left of the $((TILE_LIMIT - FIRST_TILE)) that images share." >&2
        exit 1
    fi
    next_tile=$((next_tile + count))
done
