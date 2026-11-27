#!/bin/sh
#
# Test suite for dotcleaner: builds a fake SD card and checks what is
# deleted and, above all, what is kept.
#
# Usage: sh tests/run_tests.sh [SHELL]     (default: sh)
#   e.g. sh tests/run_tests.sh bash
#        sh tests/run_tests.sh "busybox sh"

# Test conditions are written in single quotes on purpose: eval expands them.
# shellcheck disable=SC2016

set -u

HERE=$(cd "$(dirname "$0")" && pwd -P)
SCRIPT="$HERE/../dotcleaner.sh"
SHELL_CMD=${1:-sh}

TMP=$(mktemp -d "${TMPDIR:-/tmp}/dotcleaner-test.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
trap 'rm -rf "$TMP"' EXIT
trap 'exit 1' INT TERM

CARD="$TMP/NO NAME"          # a volume name with a space, like macOS FAT cards
OUT="$TMP/output.txt"
PASS=0
FAIL=0
RC=0

# Tests behave as on an exFAT SD card on every system (on macOS the temp
# folders live on the Mac's own APFS disk, which would trigger safe mode).
DOTCLEANER_FS_TYPE=exfat; export DOTCLEANER_FS_TYPE

ok() { PASS=$((PASS + 1)); printf '  ok    %s\n' "$1"; }
ko() {
  FAIL=$((FAIL + 1)); printf '  FAIL  %s\n' "$1"
  if [ -s "$OUT" ]; then sed -n '1,12s/^/        | /p' "$OUT"; fi    # last output, to debug
}

# check "description" test-command...
check() {
  _desc=$1; shift
  if "$@"; then ok "$_desc"; else ko "$_desc"; fi
}

# run dotcleaner with English messages and no colours; stdin is not a terminal
run() {
  # shellcheck disable=SC2086  # SHELL_CMD may be "busybox sh"
  NO_COLOR=1 $SHELL_CMD "$SCRIPT" "$@" </dev/null >"$OUT" 2>&1
  RC=$?
}

rc_is()    { [ "$RC" -eq "$1" ]; }
out_has()  { grep -q -- "$1" "$OUT"; }
out_has_e(){ grep -Eq -- "$1" "$OUT"; }
exists()   { [ -e "$1" ] || [ -L "$1" ]; }
missing()  { ! exists "$1"; }

all_exist() { for _f in "$@"; do exists "$_f" || return 1; done; }
all_missing() { for _f in "$@"; do missing "$_f" || return 1; done; }

# make_card [DIR] - a realistic SD card full of macOS junk
make_card() {
  C=${1:-$CARD}
  rm -rf "$C"
  mkdir -p "$C/roms/gba" "$C/roms/snes" "$C/roms/psx" "$C/roms/._folder" "$C/bios" \
           "$C/.Spotlight-V100/Store-V2" "$C/.Trashes/501" "$C/.fseventsd" \
           "$C/__MACOSX/roms" "$C/.TemporaryItems/folders.501"
  # games, saves, bios and legit hidden files: must survive
  touch "$C/roms/gba/Pokemon Emerald.gba" "$C/roms/gba/.hidden_save.srm" \
        "$C/roms/snes/Zelda (USA) [!].sfc" "$C/roms/snes/Game._beta.sfc" \
        "$C/roms/snes/it's ok.sfc" "$C/roms/.keep" "$C/bios/gba_bios.bin" \
        "$C/roms/psx/Thumbs.db" "$C/roms/psx/desktop.ini"
  # macOS junk: must go
  touch "$C/roms/gba/._Pokemon Emerald.gba" "$C/roms/gba/.DS_Store" \
        "$C/roms/snes/._Zelda (USA) [!].sfc" "$C/roms/snes/._it's ok.sfc" \
        "$C/.Spotlight-V100/Store-V2/db" "$C/.Trashes/501/old.gba" \
        "$C/.fseventsd/0001" "$C/__MACOSX/roms/._x.gba" "$C/.apdisk" \
        "$C/._.Trashes" "$C/.DS_Store"
  # a symlink to a folder outside the card: must never be followed
  mkdir -p "$TMP/outside"
  touch "$TMP/outside/._secret.gba"
  ln -s "$TMP/outside" "$C/link"
}

keep_list() {
  C=${1:-$CARD}
  set -- "$C/roms/gba/Pokemon Emerald.gba" "$C/roms/gba/.hidden_save.srm" \
         "$C/roms/snes/Zelda (USA) [!].sfc" "$C/roms/snes/Game._beta.sfc" \
         "$C/roms/snes/it's ok.sfc" "$C/roms/.keep" "$C/bios/gba_bios.bin" \
         "$C/roms/._folder" "$C/link" "$TMP/outside/._secret.gba"
  all_exist "$@"
}

junk_gone() {
  C=${1:-$CARD}
  all_missing "$C/roms/gba/._Pokemon Emerald.gba" "$C/roms/gba/.DS_Store" \
              "$C/roms/snes/._Zelda (USA) [!].sfc" "$C/roms/snes/._it's ok.sfc" \
              "$C/.Spotlight-V100" "$C/.Trashes" "$C/.fseventsd" "$C/__MACOSX" \
              "$C/.TemporaryItems" "$C/.apdisk" "$C/._.Trashes" "$C/.DS_Store"
}

junk_there() {
  C=${1:-$CARD}
  all_exist "$C/roms/gba/._Pokemon Emerald.gba" "$C/.Spotlight-V100" "$C/__MACOSX" "$C/.DS_Store"
}

windows_kept() { all_exist "$CARD/roms/psx/Thumbs.db" "$CARD/roms/psx/desktop.ini"; }
windows_gone() { all_missing "$CARD/roms/psx/Thumbs.db" "$CARD/roms/psx/desktop.ini"; }

printf 'dotcleaner tests - shell: %s\n\n' "$SHELL_CMD"

# --- Basics -------------------------------------------------------------------
run --version
check "--version prints the version"        eval 'rc_is 0 && out_has_e "^dotcleaner [0-9]+\.[0-9]+\.[0-9]+$"'
run --help
check "--help prints the usage"             eval 'rc_is 0 && out_has "Usage:"'
run --bogus
check "unknown option -> exit 2"            rc_is 2
run -x
check "unknown short option -> exit 2"      rc_is 2
run
check "no path without a terminal -> exit 2" rc_is 2

# --- Dry run --------------------------------------------------------------------
make_card
run -n "$CARD"
check "dry run: exit 0"                     rc_is 0
check "dry run: nothing deleted"            junk_there
check "dry run: lists the ._ files"         out_has "roms/gba/._Pokemon Emerald.gba"
check "dry run: counts 4 ._ files"          out_has_e "^ +4  \._\* files"
check "dry run: counts 2 .DS_Store"         out_has_e "^ +2  \.DS_Store"
check "dry run: counts 6 system items"      out_has_e "^ +6  macOS system items"
check "dry run: total of 12 items"          out_has "Total: 12 items"
check "dry run: does not list pruned content" eval '! out_has "__MACOSX/roms"'
check "dry run: symlink not followed"       eval '! out_has "_secret"'

# --- Safety without confirmation -------------------------------------------------
run "$CARD"
check "no -y and no terminal -> exit 1"     rc_is 1
check "no -y and no terminal -> nothing deleted" junk_there

# --- Real cleaning ---------------------------------------------------------------
run -y "$CARD"
check "clean: exit 0"                       rc_is 0
check "clean: all macOS junk deleted"       junk_gone
check "clean: games, saves, bios kept"      keep_list
check "clean: Windows files kept without -w" windows_kept
check "clean: reports what was done"        out_has "Done: 12 items deleted"

run -y "$CARD"
check "second run: already clean"           eval 'rc_is 0 && out_has "Already clean"'

run -y -w "$CARD"
check "-w: Windows files deleted"           eval 'rc_is 0 && windows_gone'
check "-w: games still kept"                keep_list

# --- Option handling ---------------------------------------------------------------
make_card
run -yw "$CARD"
check "combined flags -yw"                  eval 'rc_is 0 && junk_gone && windows_gone && keep_list'

make_card
run "$CARD" -y
check "options after the path"              eval 'rc_is 0 && junk_gone && keep_list'

make_card
run -y -- "$CARD"
check "-- ends the options"                 eval 'rc_is 0 && junk_gone'

make_card
run -y -q "$CARD"
check "-q prints nothing on success"        eval 'rc_is 0 && [ ! -s "$OUT" ] && junk_gone'

make_card
run -y -v "$CARD"
check "-v lists the deleted items"          eval 'rc_is 0 && out_has "roms/snes/._Zelda (USA) \[!\].sfc" && junk_gone'

# --- Several cards at once -------------------------------------------------------------
make_card "$TMP/CARD1"; make_card "$TMP/CARD2"
run -y "$TMP/CARD1" "$TMP/CARD2"
check "two cards in one call"               eval 'rc_is 0 && junk_gone "$TMP/CARD1" && junk_gone "$TMP/CARD2"'

# --- Guard rails ----------------------------------------------------------------------
run -y /
check "refuses /"                           eval 'rc_is 1 && out_has "refusing"'

mkdir -p "$TMP/home"; touch "$TMP/home/._x"
HOME_SAVE=${HOME:-}; HOME="$TMP/home"; export HOME
run -y "$TMP/home"
HOME=$HOME_SAVE; export HOME
check "refuses the home folder"             eval 'rc_is 1 && exists "$TMP/home/._x"'

run -y "$TMP/does-not-exist"
check "missing path -> exit 1"              eval 'rc_is 1 && out_has "not found"'

touch "$TMP/a-file"
run -y "$TMP/a-file"
check "file instead of folder -> exit 1"    eval 'rc_is 1 && out_has "not a folder"'

mkdir -p "$TMP/__MACOSX/inner"
run -y "$TMP/__MACOSX"
check "refuses a junk folder as the root"   eval 'rc_is 1 && exists "$TMP/__MACOSX/inner"'

make_card
run -y "$CARD" "$TMP/does-not-exist"
check "one bad path -> exit 1, good one cleaned" eval 'rc_is 1 && junk_gone'

# --- Card's Trash ------------------------------------------------------------------------
make_card
run -n "$CARD"
check "warns before erasing the card's Trash" out_has "Trash holds 1 file"

run -y -k "$CARD"
check "-k keeps the card's Trash"           eval 'rc_is 0 && exists "$CARD/.Trashes/501/old.gba" && missing "$CARD/.Spotlight-V100" && keep_list'
check "-k: no Trash warning"                eval '! out_has "Trash holds"'
make_card; touch "$CARD/.Trashes/501/._old.gba" "$CARD/.Trashes/.DS_Store"; mkdir -p "$CARD/.Trashes/501/__MACOSX"
run -y -k "$CARD"
check "-k: junk names inside the Trash kept" eval 'rc_is 0 && exists "$CARD/.Trashes/501/._old.gba" && exists "$CARD/.Trashes/.DS_Store" && exists "$CARD/.Trashes/501/__MACOSX"'

# --- Mac-formatted drives: safe mode ---------------------------------------------------
make_card
DOTCLEANER_FS_TYPE=apfs; run -y "$CARD"; DOTCLEANER_FS_TYPE=exfat   # (no "VAR=x func": it sticks in some shells)
check "Mac disk: safe mode announced"       eval 'rc_is 0 && out_has "safe mode"'
check "Mac disk: junk files removed"        eval 'missing "$CARD/roms/gba/._Pokemon Emerald.gba" && missing "$CARD/roms/gba/.DS_Store" && missing "$CARD/.apdisk"'
check "Mac disk: __MACOSX removed"          missing "$CARD/__MACOSX"
check "Mac disk: system folders kept"       eval 'exists "$CARD/.Spotlight-V100/Store-V2/db" && exists "$CARD/.Trashes/501/old.gba" && exists "$CARD/.fseventsd/0001" && exists "$CARD/.TemporaryItems"'
check "Mac disk: games kept"                keep_list

# Real detection with simulated macOS tools (uname, stat, mount)
FAKE="$TMP/fakebin"; mkdir -p "$FAKE"
printf '#!/bin/sh\necho Darwin\n' >"$FAKE/uname"
printf '#!/bin/sh\necho disk9s1\n' >"$FAKE/stat"
printf '#!/bin/sh\necho "/dev/disk9s1 on /Volumes/My (Backup) (apfs, local, journaled)"\n' >"$FAKE/mount"
chmod +x "$FAKE/uname" "$FAKE/stat" "$FAKE/mount"
make_card
# shellcheck disable=SC2086
PATH="$FAKE:$PATH" DOTCLEANER_FS_TYPE='' NO_COLOR=1 $SHELL_CMD "$SCRIPT" -y "$CARD" </dev/null >"$OUT" 2>&1; RC=$?
check "detects APFS from mount (safe mode)" eval 'rc_is 0 && out_has "safe mode" && exists "$CARD/.Spotlight-V100" && missing "$CARD/.DS_Store"'
printf '#!/bin/sh\necho "/dev/disk9s1 on /Volumes/EASYROMS (exfat, local, nodev)"\n' >"$FAKE/mount"
make_card
# shellcheck disable=SC2086
PATH="$FAKE:$PATH" DOTCLEANER_FS_TYPE='' NO_COLOR=1 $SHELL_CMD "$SCRIPT" -y "$CARD" </dev/null >"$OUT" 2>&1; RC=$?
check "detects exFAT from mount (full clean)" eval 'rc_is 0 && ! out_has "safe mode" && junk_gone && keep_list'

# --- English only --------------------------------------------------------------------------
make_card
# shellcheck disable=SC2086
LANG=fr_FR.UTF-8 LC_ALL=fr_FR.UTF-8 NO_COLOR=1 $SHELL_CMD "$SCRIPT" -n "$CARD" </dev/null >"$OUT" 2>&1; RC=$?
check "English on a French system"          eval 'rc_is 0 && out_has "Preview only"'
run --lang fr -n "$CARD"
check "no --lang option any more -> exit 2" rc_is 2

# --- Old BusyBox without "find -exec ... {} +" ---------------------------------------------
make_card
DOTCLEANER_NO_EXEC_PLUS=1; export DOTCLEANER_NO_EXEC_PLUS; run -y "$CARD"; unset DOTCLEANER_NO_EXEC_PLUS
check "fallback for old find: junk deleted"  eval 'rc_is 0 && junk_gone && keep_list'

# --- Console mode: launcher started from the console menu (no keyboard, no terminal) ------
# the launcher writes next to itself (dotcleaner.log, gamelist.xml when an icon sits there):
# test a copy, never the one in the repository
mkdir -p "$TMP/launcher"; cp "$HERE/../console/Dotcleaner.sh" "$TMP/launcher/Dotcleaner.sh"
LAUNCHER="$TMP/launcher/Dotcleaner.sh"
make_card
# shellcheck disable=SC2086
DOTCLEANER_CONSOLE_ROOT="$CARD" DOTCLEANER_NO_TTY=1 DOTCLEANER_LOG="$TMP/console.log" NO_COLOR=1 \
  $SHELL_CMD "$LAUNCHER" </dev/null >"$OUT" 2>&1; RC=$?
check "console launcher: cleans the card, no question" eval 'rc_is 0 && junk_gone && keep_list'
check "console launcher: result on screen"   eval 'out_has "12 items deleted" && out_has "Done!"'
check "console launcher: writes dotcleaner.log" grep -q "12 items deleted" "$TMP/console.log"
check "console launcher: lines fit 40 columns" eval '[ "$(grep -v "^      /" "$TMP/console.log" | awk "length > 40" | wc -l)" -eq 0 ]' 
check "console launcher: plain text log"     eval '! grep -q "$(printf "\033")" "$TMP/console.log"'
# shellcheck disable=SC2086
DOTCLEANER_CONSOLE_ROOT='' DOTCLEANER_NO_TTY=1 DOTCLEANER_LOG="$TMP/console.log" NO_COLOR=1 \
  $SHELL_CMD "$LAUNCHER" </dev/null >"$OUT" 2>&1; RC=$?
check "console launcher: no card -> clear message, exit 1" eval 'rc_is 1 && out_has "No ROM card found"'
make_card
run -n "$CARD"
check "plain script without arguments is not in console mode" eval 'junk_there'
# shellcheck disable=SC2086
NO_COLOR=1 $SHELL_CMD "$LAUNCHER" -n "$CARD" </dev/null >"$OUT" 2>&1; RC=$?
check "console launcher with a path: normal preview" eval 'rc_is 0 && out_has "Preview only" && junk_there'
make_card
# shellcheck disable=SC2086
DOTCLEANER_CONSOLE_ROOT="$CARD" DOTCLEANER_NO_TTY=1 DOTCLEANER_LOG="$TMP/console.log" NO_COLOR=1 \
  $SHELL_CMD "$SCRIPT" --console </dev/null >"$OUT" 2>&1; RC=$?
check "--console option does the same"      eval 'rc_is 0 && junk_gone'

# --- Console mode: two SD cards, or one card split in several partitions ------------------
# DOTCLEANER_KNOWN_ROOTS replaces /roms, /roms2, /userdata...; DOTCLEANER_MOUNTS replaces
# /proc/mounts (device, mount point, file system), so no real card is touched.
SD1="$TMP/sd1"; SD2="$TMP/sd2"; MNT="$TMP/mounts"; MD="$TMP/media"
run_cards() {
  # shellcheck disable=SC2086
  DOTCLEANER_KNOWN_ROOTS="$1" DOTCLEANER_MOUNTS="$MNT" DOTCLEANER_NO_TTY=1 \
    DOTCLEANER_LOG="$TMP/console.log" NO_COLOR=1 $SHELL_CMD "$LAUNCHER" </dev/null >"$OUT" 2>&1; RC=$?
}
both_clean() { junk_gone "$SD1" && keep_list "$SD1" && junk_gone "$SD2" && keep_list "$SD2"; }

make_card "$SD1"; make_card "$SD2"; : >"$MNT"
run_cards "$SD1:$SD2"
check "two SD cards (ArkOS /roms + /roms2): both cleaned" eval 'rc_is 0 && both_clean && out_has "ROM cards: 2" && out_has "24 items deleted"'
check "two SD cards: log fits 40 columns" eval '[ "$(grep -v "^      /" "$TMP/console.log" | awk "length > 40" | wc -l)" -eq 0 ]'

# Knulli with two cards: /userdata is SD2, and both SHARE partitions are also in /media
rm -rf "$MD"; mkdir -p "$MD"; make_card "$SD1"; make_card "$SD2"
ln -s "$SD1" "$MD/SHARE"; ln -s "$SD2" "$MD/SHARE_1"
printf '/dev/mmcblk0p3 %s exfat rw 0 0\n/dev/mmcblk1p1 %s exfat rw 0 0\n' "$MD/SHARE" "$MD/SHARE_1" >"$MNT"
run_cards "$SD2"
check "two SD cards (Knulli): each card cleaned once" eval 'rc_is 0 && both_clean && out_has "ROM cards: 2" && out_has "24 items deleted" && ! out_has "SHARE_1"'

# one card split in two game partitions, plus a boot partition without a roms folder
P1="$TMP/part1"; P2="$TMP/part 2"; BOOT="$TMP/boot"
make_card "$P1"; make_card "$P2"; rm -rf "$BOOT"; mkdir -p "$BOOT"; touch "$BOOT/._kernel.img"
printf '/dev/mmcblk0p1 %s vfat rw 0 0\n/dev/mmcblk0p2 %s exfat rw 0 0\n/dev/mmcblk0p3 %s exfat rw 0 0\nproc /proc proc rw 0 0\n' \
  "$BOOT" "$P1" "$(printf '%s' "$P2" | sed 's/ /\\040/g')" >"$MNT"
run_cards ""
check "one card split in two partitions: both cleaned" eval 'rc_is 0 && junk_gone "$P1" && keep_list "$P1" && junk_gone "$P2" && keep_list "$P2" && out_has "ROM cards: 2"'
check "split card: partition without games left alone" eval 'exists "$BOOT/._kernel.img"'

# a union folder (mergerfs pool of several cards) is skipped: its cards are cleaned directly
POOL="$TMP/pool"; make_card "$POOL"; make_card "$SD2"
printf 'mergerfs %s fuse.mergerfs rw 0 0\n' "$POOL" >"$MNT"
run_cards "$POOL:$SD2"
check "union folder (mergerfs) skipped, real card cleaned" eval 'rc_is 0 && junk_there "$POOL" && junk_gone "$SD2" && out_has "^\[1/4\] ROM card$"'

# the same card reached by its games folder and by its root: the whole card is cleaned
make_card "$SD1"; printf '/dev/mmcblk1p1 %s exfat rw 0 0\n' "$SD1" >"$MNT"
run_cards "$SD1/roms"
check "same card twice: the whole card is cleaned once" eval 'rc_is 0 && junk_gone "$SD1" && keep_list "$SD1" && out_has "^\[1/4\] ROM card$" && out_has "12 items deleted"'

# --- More firmwares and devices -------------------------------------------------------------
# packages for Onion / spruceOS, TrimUI / CrossMix-OS, MinUI / NextUI, muOS: the same launcher
PK="$HERE/../console"; export PK   # used inside the eval tests below
check "packages: Onion, TrimUI, MinUI use the same launcher" eval 'cmp -s "$PK/Dotcleaner.sh" "$PK/Onion/App/Dotcleaner/launch.sh" && cmp -s "$PK/Dotcleaner.sh" "$PK/TrimUI/Apps/Dotcleaner/launch.sh" && cmp -s "$PK/Dotcleaner.sh" "$PK/MinUI/Dotcleaner.pak/launch.sh"'
check "packages: muOS launcher = same script + its HELP line" eval 'sed -n 2p "$PK/muOS/MUOS/application/Dotcleaner/mux_launch.sh" | grep -q "^# HELP: " && sed 2d "$PK/muOS/MUOS/application/Dotcleaner/mux_launch.sh" | cmp -s - "$PK/Dotcleaner.sh"'
check "packages: app folders have config.json and icon" eval 'for _a in Onion/App TrimUI/Apps; do grep -q "\"launch\": \"launch.sh\"" "$PK/$_a/Dotcleaner/config.json" && [ -s "$PK/$_a/Dotcleaner/icon.png" ] || exit 1; done'

# games folders other than "roms": EmuDeck (Emulation/roms), MinUI (Roms), muOS (ROMS)
DECK="$TMP/deck"; rm -rf "$DECK"; mkdir -p "$DECK"; make_card "$DECK/sdcard"
mkdir -p "$DECK/card/Emulation"; mv "$DECK/sdcard/roms" "$DECK/card/Emulation/roms"; cp -R "$DECK/sdcard/." "$DECK/card/"
mkdir -p "$DECK/minui"; make_card "$DECK/minui"; mv "$DECK/minui/roms" "$DECK/minui/Roms"
printf '/dev/mmcblk0p1 %s exfat rw 0 0\n/dev/sdb1 %s vfat rw 0 0\n' "$DECK/card" "$DECK/minui" >"$MNT"
run_cards ""
check "games folders Emulation/roms (EmuDeck) and Roms (MinUI) found" eval 'rc_is 0 && out_has "ROM cards: 2" && [ ! -e "$DECK/card/Emulation/roms/gba/._Pokemon Emerald.gba" ] && [ -e "$DECK/card/Emulation/roms/gba/Pokemon Emerald.gba" ] && [ ! -e "$DECK/minui/Roms/gba/.DS_Store" ] && [ -e "$DECK/minui/Roms/gba/.hidden_save.srm" ] && [ ! -e "$DECK/card/.Spotlight-V100" ]'

# find without -xdev (some very old BusyBox): still cleans, keeps everything else
make_card
DOTCLEANER_NO_XDEV=1; export DOTCLEANER_NO_XDEV; run -y "$CARD"; unset DOTCLEANER_NO_XDEV
check "old find without -xdev: junk deleted, rest kept" eval 'rc_is 0 && junk_gone && keep_list'

# --- Console mode: menu entry with the icon (gamelist.xml next to the launcher) -------------
PD="$TMP/ports"; GL="$PD/gamelist.xml"
mkdir -p "$PD/icons"; cp "$LAUNCHER" "$PD/Dotcleaner.sh"
run_menu() {
  make_card
  # shellcheck disable=SC2086
  DOTCLEANER_CONSOLE_ROOT="$CARD" DOTCLEANER_NO_TTY=1 DOTCLEANER_LOG="$TMP/console.log" NO_COLOR=1 \
    $SHELL_CMD "$PD/Dotcleaner.sh" </dev/null >"$OUT" 2>&1; RC=$?
}
games() { grep -c '<game[ >]' "$GL"; }
ours()  { grep -c '<path>./Dotcleaner.sh</path>' "$GL"; }
imgs()  { grep -c '<image>./icons/dotcleaner.png</image>' "$GL"; }
no_tmp(){ [ -z "$(find "$PD" -name '.gamelist.xml.dotcleaner.*')" ]; }

run_menu
check "menu: no icon -> no gamelist.xml created" eval 'rc_is 0 && missing "$GL"'
: >"$PD/icons/dotcleaner.png"
run_menu
check "menu: icon -> gamelist.xml created with the entry" eval 'rc_is 0 && junk_gone && [ "$(games)" -eq 1 ] && [ "$(imgs)" -eq 1 ] && tail -n 1 "$GL" | grep -q "^</gameList>$" && no_tmp'
check "menu: log still fits 40 columns" eval '[ "$(grep -v "^      /" "$TMP/console.log" | awk "length > 40" | wc -l)" -eq 0 ] && grep -q "^Menu: entry with icon added$" "$TMP/console.log"'
cp "$GL" "$TMP/gl.before"
run_menu
check "menu: second run changes nothing"     eval 'rc_is 0 && cmp -s "$GL" "$TMP/gl.before"'
printf '<?xml version="1.0"?>\n<gameList>\n\t<game>\n\t\t<path>./Doom.sh</path>\n\t\t<name>Doom</name>\n\t\t<image>./Imgs/doom.png</image>\n\t</game>\n</gameList>\n' >"$GL"
run_menu
check "menu: existing list kept, entry added" eval 'rc_is 0 && [ "$(games)" -eq 2 ] && [ "$(ours)" -eq 1 ] && grep -q "<path>./Doom.sh</path>" "$GL" && grep -q "./Imgs/doom.png" "$GL" && tail -n 1 "$GL" | grep -q "^</gameList>$" && no_tmp'
printf '<?xml version="1.0"?>\n<gameList>\n\t<game>\n\t\t<path>./Doom.sh</path>\n\t\t<name>Doom</name>\n\t</game>\n\t<game>\n\t\t<path>./Dotcleaner.sh</path>\n\t\t<name>Dotcleaner</name>\n\t\t<playcount>3</playcount>\n\t</game>\n</gameList>\n' >"$GL"
run_menu
check "menu: entry rewritten by the menu gets its icon back" eval 'rc_is 0 && [ "$(games)" -eq 2 ] && [ "$(ours)" -eq 1 ] && [ "$(imgs)" -eq 1 ] && grep -q "<playcount>3</playcount>" "$GL" && [ "$(grep -c "<image>" "$GL")" -eq 1 ]'
printf '<gameList />\n' >"$GL"; cp "$GL" "$TMP/gl.before"
run_menu
check "menu: unknown gamelist format left alone" eval 'rc_is 0 && junk_gone && cmp -s "$GL" "$TMP/gl.before" && no_tmp'

check "tests leave the repository's console folder untouched" eval '[ ! -e "$HERE/../console/gamelist.xml" ] && [ ! -e "$HERE/../console/dotcleaner.log" ]'

# --- Installer -----------------------------------------------------------------------------
INSTALLER="$HERE/../install.sh"
# shellcheck disable=SC2086
PREFIX="$TMP/prefix" DOTCLEANER_SRC="$SCRIPT" $SHELL_CMD "$INSTALLER" >"$OUT" 2>&1; RC=$?
check "installer: installs the command"     eval 'rc_is 0 && [ -x "$TMP/prefix/bin/dotcleaner" ] && out_has "Installed: dotcleaner"'
check "installer: installed command runs"   eval '"$TMP/prefix/bin/dotcleaner" --version | grep -q "^dotcleaner "'

# shellcheck disable=SC2086
PREFIX="$TMP/prefix" $SHELL_CMD "$INSTALLER" --uninstall >"$OUT" 2>&1; RC=$?
check "installer: --uninstall removes it"   eval 'rc_is 0 && missing "$TMP/prefix/bin/dotcleaner"'

printf 'not a script\n' >"$TMP/bad.sh"
# shellcheck disable=SC2086
PREFIX="$TMP/prefix" DOTCLEANER_SRC="$TMP/bad.sh" $SHELL_CMD "$INSTALLER" >"$OUT" 2>&1; RC=$?
check "installer: refuses a broken download" eval '[ "$RC" -ne 0 ] && missing "$TMP/prefix/bin/dotcleaner"'

# --- Summary -----------------------------------------------------------------------
printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
