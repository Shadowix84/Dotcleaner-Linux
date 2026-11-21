#!/bin/sh
#
# End-to-end test on macOS with REAL cards: creates exFAT and FAT32 disk
# images, mounts them like SD cards, cleans them and ejects them.
# Also checks that the Mac's own APFS disk is refused.
#
# Usage (macOS only): sh tests/macos_card.sh

set -u

HERE=$(cd "$(dirname "$0")" && pwd -P)
SCRIPT="$HERE/../dotcleaner.sh"
WORK=$(mktemp -d "${TMPDIR:-/tmp}/dotcleaner-mac.XXXXXX") || exit 1
FAIL=0

ok() { printf '  ok    %s\n' "$1"; }
ko() { printf '  FAIL  %s\n' "$1"; FAIL=1; }
check() { _d=$1; shift; if "$@"; then ok "$_d"; else ko "$_d"; fi; }

[ "$(uname -s)" = Darwin ] || { echo "macOS only"; exit 0; }

for FS in ExFAT "MS-DOS FAT32"; do
  NAME=DCTEST
  IMG="$WORK/card-$(printf '%s' "$FS" | tr -dc 'A-Za-z0-9').dmg"
  printf '\n== %s card ==\n' "$FS"
  hdiutil create -quiet -size 64m -fs "$FS" -volname "$NAME" "$IMG" || { ko "create $FS image"; continue; }
  hdiutil attach -quiet "$IMG" || { ko "mount $FS image"; continue; }
  V="/Volumes/$NAME"

  mkdir -p "$V/roms/gba" "$V/__MACOSX/roms" "$V/bios"
  printf 'rom'  >"$V/roms/gba/Pokemon Emerald.gba"
  printf 'save' >"$V/roms/gba/Pokemon Emerald.srm"
  printf 'bios' >"$V/bios/gba_bios.bin"
  printf 'x'    >"$V/roms/gba/._Pokemon Emerald.gba"
  printf 'x'    >"$V/roms/gba/.DS_Store"
  printf 'x'    >"$V/__MACOSX/roms/._x"
  printf 'keep' >"$V/roms/gba/Game._beta.gba"

  DOTCLEANER_LANG=en NO_COLOR=1 sh "$SCRIPT" -n "$V" </dev/null; RC=$?
  check "$FS: dry run accepted (not refused as a Mac disk)" [ "$RC" -eq 0 ]
  check "$FS: dry run deleted nothing" [ -e "$V/roms/gba/._Pokemon Emerald.gba" ]

  DOTCLEANER_LANG=en NO_COLOR=1 sh "$SCRIPT" -y "$V" </dev/null; RC=$?
  check "$FS: clean exit code 0" [ "$RC" -eq 0 ]
  check "$FS: ._ file deleted" [ ! -e "$V/roms/gba/._Pokemon Emerald.gba" ]
  check "$FS: .DS_Store deleted" [ ! -e "$V/roms/gba/.DS_Store" ]
  check "$FS: __MACOSX deleted" [ ! -e "$V/__MACOSX" ]
  check "$FS: ROM kept" [ -f "$V/roms/gba/Pokemon Emerald.gba" ]
  check "$FS: save kept" [ -f "$V/roms/gba/Pokemon Emerald.srm" ]
  check "$FS: BIOS kept" [ -f "$V/bios/gba_bios.bin" ]
  check "$FS: Game._beta.gba kept" [ -f "$V/roms/gba/Game._beta.gba" ]

  DOTCLEANER_LANG=en NO_COLOR=1 sh "$SCRIPT" -y -e "$V" </dev/null; RC=$?
  sleep 2
  check "$FS: -e ejects the card" [ ! -d "$V" ]
  [ -d "$V" ] && hdiutil detach -quiet -force "$V"
done

printf '\n== Mac disk (APFS) ==\n'
mkdir -p "$WORK/apfs"; printf 'x' >"$WORK/apfs/._x"
DOTCLEANER_LANG=en NO_COLOR=1 sh "$SCRIPT" -y "$WORK/apfs" </dev/null; RC=$?
check "APFS folder refused (exit 1)" [ "$RC" -eq 1 ]
check "APFS folder untouched" [ -e "$WORK/apfs/._x" ]

rm -rf "$WORK"
[ "$FAIL" -eq 0 ] && printf '\nmacOS card tests OK\n'
exit "$FAIL"
