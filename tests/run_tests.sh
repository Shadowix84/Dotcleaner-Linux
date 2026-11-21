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

ok() { PASS=$((PASS + 1)); printf '  ok    %s\n' "$1"; }
ko() { FAIL=$((FAIL + 1)); printf '  FAIL  %s\n' "$1"; }

# check "description" test-command...
check() {
  _desc=$1; shift
  if "$@"; then ok "$_desc"; else ko "$_desc"; fi
}

# run dotcleaner with English messages and no colours; stdin is not a terminal
run() {
  # shellcheck disable=SC2086  # SHELL_CMD may be "busybox sh"
  DOTCLEANER_LANG=en NO_COLOR=1 $SHELL_CMD "$SCRIPT" "$@" </dev/null >"$OUT" 2>&1
  RC=$?
}

rc_is()    { [ "$RC" -eq "$1" ]; }
out_has()  { grep -q -- "$1" "$OUT"; }
out_has_e(){ grep -Eq -- "$1" "$OUT"; }
exists()   { [ -e "$1" ] || [ -L "$1" ]; }
missing()  { ! exists "$1"; }

all_exist() { for _f in "$@"; do exists "$_f" || return 1; done; }
all_missing() { for _f in "$@"; do missing "$_f" || return 1; done; }

# make_card [DIR] — a realistic SD card full of macOS junk
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

printf 'dotcleaner tests — shell: %s\n\n' "$SHELL_CMD"

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

# --- French messages -------------------------------------------------------------------
make_card
# shellcheck disable=SC2086
DOTCLEANER_LANG=fr NO_COLOR=1 $SHELL_CMD "$SCRIPT" -n "$CARD" </dev/null >"$OUT" 2>&1; RC=$?
check "French messages"                     eval 'rc_is 0 && out_has "Simulation" && out_has "éléments"'

# --- Summary -----------------------------------------------------------------------
printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
