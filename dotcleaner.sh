#!/bin/sh
#
# dotcleaner - removes the junk files macOS leaves on SD cards and USB drives
# (._* files, .DS_Store, .Spotlight-V100, .Trashes, .fseventsd, __MACOSX...).
# Made for emulation handhelds (R36S, Anbernic, Miyoo, Retroid, TrimUI...).
#
# Run it without arguments for the interactive menu, or see --help.
# Plain POSIX sh, pure ASCII: runs on macOS, Linux, WSL, ChromeOS, Steam Deck
# and on the consoles themselves (ArkOS, Knulli, Batocera, ROCKNIX, AmberELEC,
# muOS, Onion, MinUI...), with bash, dash, BusyBox ash, ksh, mksh, zsh, posh, yash.
#
# https://github.com/Shadowix84/Dotcleaner-Multi-Software
# MIT License - Copyright (c) 2026 Shadowix84

set -u

VERSION="2.3.2"
PROG=${0##*/}

# --- What gets removed (keep in sync with app/dotcleaner_core.py) ------------
# Files, at any depth
JUNK_FILES='._* .DS_Store .apdisk'
# macOS system folders, at any depth (removed with everything inside)
SYSTEM_DIRS='.Spotlight-V100 .Trashes .fseventsd .TemporaryItems .DocumentRevisions-V100 .AppleDouble .AppleDB .AppleDesktop'
# Leftovers of zip archives made on a Mac
ARCHIVE_DIRS='__MACOSX'
# Windows files, only with -w / --windows
WINDOWS_FILES='Thumbs.db ehthumbs.db desktop.ini'

# --- Settings ----------------------------------------------------------------
DRY_RUN=0
ASSUME_YES=0
CLEAN_WINDOWS=0
EJECT=0
VERBOSE=0
QUIET=0
KEEP_TRASH=0
SHOW_HELP=0
MENU=0
CONSOLE=0
# 1 in the console launcher (Dotcleaner.sh, made by tools/make_console.sh):
# started from the console menu with no arguments -> console mode
CONSOLE_LAUNCHER=0
SCRIPT_DIR=$(cd "$(dirname "$0")" 2>/dev/null && pwd)

# Set per drive by set_rules
JUNK_DIRS=''
PRUNE_DIRS=''

# --- Output helpers ----------------------------------------------------------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_BOLD=$(printf '\033[1m'); C_DIM=$(printf '\033[2m')
  C_RED=$(printf '\033[31m'); C_GRN=$(printf '\033[32m')
  C_YEL=$(printf '\033[33m'); C_CYN=$(printf '\033[36m'); C_OFF=$(printf '\033[0m')
else
  C_BOLD='' C_DIM='' C_RED='' C_GRN='' C_YEL='' C_CYN='' C_OFF=''
fi

say()  { if [ "$QUIET" -eq 0 ]; then printf '%s\n' "$*"; fi; }
warn() { printf '%s\n' "${C_YEL}$*${C_OFF}" >&2; }
err()  { printf '%s\n' "${C_RED}Error: $*${C_OFF}" >&2; }

usage() {
  cat <<EOF
dotcleaner $VERSION - removes the junk files macOS leaves on SD cards and
USB drives (made for emulation handhelds: R36S, Anbernic, Miyoo, Retroid...)

Usage: $PROG                    interactive menu
       $PROG [options] PATH...  clean these drives or folders

Options:
  -n, --dry-run     preview: show what would be deleted, delete nothing
  -y, --yes         do not ask for confirmation
  -w, --windows     also remove Windows files (Thumbs.db, desktop.ini)
  -k, --keep-trash  leave the drive's Trash (.Trashes) untouched
  -e, --eject       eject the drive when done (macOS)
  -v, --verbose     list every deleted item
  -q, --quiet       only print errors
      --console     console mode: find the ROM card of this console, clean it
                    without questions, show the result and write dotcleaner.log
  -h, --help        show this help
  -V, --version     show the version

Removed: ._* files, .DS_Store, .apdisk, __MACOSX and the macOS folders
.Spotlight-V100, .Trashes, .fseventsd, .TemporaryItems,
.DocumentRevisions-V100, .AppleDouble, .AppleDB, .AppleDesktop.
Never touched: your ROMs, saves, BIOS and every other file.
On Mac-formatted drives (APFS, HFS+) only the junk files are removed:
the system folders hold real data there and are kept (safe mode).

Examples:
  $PROG                          open the menu
  $PROG -n /Volumes/EASYROMS     preview what would be deleted
  $PROG -y -e /Volumes/SHARE     clean then eject, no questions
EOF
}

die_usage() {
  err "$1"
  printf '%s\n' "Try: $PROG --help" >&2
  exit 2
}

# n_items N -> "1 item" / "5 items"
n_items() { if [ "$1" -eq 1 ]; then printf '1 item'; else printf '%s items' "$1"; fi; }

# --- Rules -------------------------------------------------------------------

# set_rules FILES_ONLY -> sets JUNK_DIRS (deleted) and PRUNE_DIRS (untouched)
set_rules() {
  if [ "$1" -eq 1 ]; then
    JUNK_DIRS=$ARCHIVE_DIRS
    PRUNE_DIRS=$SYSTEM_DIRS
  elif [ "$KEEP_TRASH" -eq 1 ]; then
    JUNK_DIRS="$(printf ' %s ' "$SYSTEM_DIRS" | sed 's/ \.Trashes / /; s/^ *//; s/ *$//') $ARCHIVE_DIRS"
    PRUNE_DIRS='.Trashes'
  else
    JUNK_DIRS="$SYSTEM_DIRS $ARCHIVE_DIRS"
    PRUNE_DIRS=''
  fi
}

# junk_find ROOT MODE
#   MODE = print    -> print every junk item
#          delete   -> delete every junk item
#          progress -> delete every junk item, printing how many were deleted
#          size   -> disk usage (KB) of every junk item
# Never follows symlinks and never leaves the drive's filesystem (-xdev).
# Two passes (folders, then files) on purpose: BusyBox find, used by most
# console firmwares, silently ignores "-exec ... {} +" inside \( \).
junk_find() {
  _jf_root=$1 _jf_mode=$2
  _jf_files=$JUNK_FILES
  if [ "$CLEAN_WINDOWS" -eq 1 ]; then _jf_files="$_jf_files $WINDOWS_FILES"; fi

  set -f  # the '._*' pattern must reach find untouched
  # shellcheck disable=SC2086  # $_jf_or is meant to vanish when empty
  {
    set -- "$_jf_root" -xdev
    # Folders left completely untouched (-k, safe mode)
    if [ -n "$PRUNE_DIRS" ]; then
      set -- "$@" -type d \(
      _jf_or=''
      for _jf_n in $PRUNE_DIRS; do set -- "$@" $_jf_or -name "$_jf_n"; _jf_or='-o'; done
      set -- "$@" \) -prune -o
    fi

    # Pass 1: junk folders (pruned, so their content is not listed twice)
    set -- "$@" -type d \(
    _jf_or=''
    for _jf_n in $JUNK_DIRS; do set -- "$@" $_jf_or -name "$_jf_n"; _jf_or='-o'; done
    set -- "$@" \) -prune
    _jf_run "$@"

    # Pass 2: junk files, outside the junk folders
    set -- "$@" -o -type f \(
    _jf_or=''
    for _jf_n in $_jf_files; do set -- "$@" $_jf_or -name "$_jf_n"; _jf_or='-o'; done
    set -- "$@" \)
    _jf_run "$@"
  }
  set +f
}

# _jf_run FIND-ARGS... -> runs find with the action of $_jf_mode
# shellcheck disable=SC2016  # the sh -c scripts get "$f" / "$1" from find
_jf_run() {
  if exec_plus; then
    case $_jf_mode in
      print)  find "$@" -print ;;
      delete) find "$@" -exec rm -rf {} + ;;
      size)   find "$@" -exec du -sk {} + ;;
      # prints how many items it deleted, batch after batch, for the progress
      # bar (names are never parsed); 32 items per rm keeps it fast
      progress) find "$@" -exec sh -c 'while [ $# -ge 32 ]; do rm -rf "${1}" "${2}" "${3}" "${4}" "${5}" "${6}" "${7}" "${8}" "${9}" "${10}" "${11}" "${12}" "${13}" "${14}" "${15}" "${16}" "${17}" "${18}" "${19}" "${20}" "${21}" "${22}" "${23}" "${24}" "${25}" "${26}" "${27}" "${28}" "${29}" "${30}" "${31}" "${32}"; echo 32; shift 32; done; for f do rm -rf "$f" && echo 1; done' sh {} + ;;
    esac
  else
    case $_jf_mode in                  # old BusyBox: one command per item
      print)  find "$@" -print ;;
      delete) find "$@" -exec rm -rf {} \; ;;
      size)   find "$@" -exec du -sk {} \; ;;
      progress) find "$@" -exec sh -c 'rm -rf "$1" && echo 1' sh {} \; ;;
    esac
  fi
}

# exec_plus -> true when find supports "-exec ... {} +" (some old BusyBox do not)
EXEC_PLUS=''
exec_plus() {
  if [ -z "$EXEC_PLUS" ]; then
    if [ -z "${DOTCLEANER_NO_EXEC_PLUS:-}" ] && find / -prune -exec true {} + >/dev/null 2>&1; then
      EXEC_PLUS=1
    else
      EXEC_PLUS=0
    fi
  fi
  [ "$EXEC_PLUS" -eq 1 ]
}

# trash_count ROOT -> number of user files waiting in the drive's Trash
trash_count() {
  find "$1" -xdev -path '*/.Trashes/*' -type f ! -name '._*' ! -name .DS_Store 2>/dev/null |
    awk 'END { print NR }'
}

# Reads paths on stdin, prints: appledouble ds_store system windows total
classify() {
  W="$WINDOWS_FILES" awk -F/ '
    BEGIN { n = split(ENVIRON["W"], w, " "); for (i = 1; i <= n; i++) win[w[i]] = 1 }
    {
      f = $NF
      if (f ~ /^\._/)            a++
      else if (f == ".DS_Store") d++
      else if (f in win)         x++
      else                       s++
    }
    END { printf "%d %d %d %d %d\n", a, d, s, x, a + d + s + x }'
}

# human_size KB -> "12.3 MB"
human_size() {
  awk -v k="$1" 'BEGIN {
    if (k < 1024)            printf "%d KB\n", k
    else if (k < 1048576)    printf "%.1f MB\n", k / 1024
    else if (k < 1073741824) printf "%.1f GB\n", k / 1048576
    else                     printf "%.1f TB\n", k / 1073741824
  }'
}

# list_items ROOT -> junk items, relative to ROOT, sorted
list_items() {
  junk_find "$1" print 2>/dev/null | sort | P="$1/" awk '{
    p = ENVIRON["P"]
    if (index($0, p) == 1) $0 = substr($0, length(p) + 1)
    print "    " $0
  }'
}

# Folders that must never be cleaned as a whole
is_forbidden() {
  case $1 in
    /|/Applications|/Library|/System|/System/Volumes/Data|/Users|/Volumes|\
    /bin|/boot|/dev|/etc|/home|/media|/mnt|/opt|/private|/private/etc|\
    /private/tmp|/private/var|/proc|/root|/run|/run/media|/sbin|/sys|/tmp|\
    /usr|/var)
      return 0 ;;
  esac
  if [ -n "${HOME:-}" ] && _home=$(cd "$HOME" 2>/dev/null && pwd -P); then
    if [ "$1" = "$_home" ]; then return 0; fi
  fi
  return 1
}

# --- Drives ------------------------------------------------------------------

# fs_type PATH -> filesystem type (apfs, hfs, msdos, exfat, ext2/ext3...), or nothing
# (DOTCLEANER_FS_TYPE overrides the detection: used by the tests)
fs_type() {
  if [ -n "${DOTCLEANER_FS_TYPE:-}" ]; then
    printf '%s\n' "$DOTCLEANER_FS_TYPE"
  elif [ "$(uname -s 2>/dev/null)" = Darwin ]; then
    _ft_dev=$(stat -f %Sd "$1" 2>/dev/null) || return 0
    mount | awk -v d="/dev/$_ft_dev" '$1 == d { sub(/.*\(/, ""); sub(/[,)].*/, ""); print; exit }'
  else
    stat -f -c %T "$1" 2>/dev/null || true
  fi
}

# Mac-formatted drives (APFS, HFS+): safe mode
is_mac_disk() {
  case $(fs_type "$1") in
    apfs|hfs|hfsplus|hfs+) return 0 ;;
  esac
  return 1
}

# drive_size PATH -> "29.7 GB" (total size of the drive)
drive_size() {
  _ds_kb=$(df -Pk "$1" 2>/dev/null | awk 'NR == 2 { print $2 }')
  if [ -n "$_ds_kb" ]; then human_size "$_ds_kb"; fi
}

# drive_info PATH -> "exfat, 29.7 GB" (+ ", safe mode" on Mac disks)
drive_info() {
  _di=$(fs_type "$1")
  _ds=$(drive_size "$1")
  if [ -n "$_ds" ]; then _di="${_di:+$_di, }$_ds"; fi
  if is_mac_disk "$1"; then _di="$_di, safe mode"; fi
  printf '%s' "$_di"
}

# is_mountpoint DIR -> true when DIR is the top of a mounted drive
is_mountpoint() {
  _mp=$(df -P "$1" 2>/dev/null | awk 'NR == 2 { for (i = 6; i <= NF; i++) printf "%s%s", $i, (i < NF ? " " : "") }')
  [ -n "$_mp" ] && [ "$_mp" = "$1" ]
}

# console_root -> the ROM card of the console we are running on, if any
console_root() {
  if [ -n "${DOTCLEANER_CONSOLE_ROOT+x}" ]; then        # tests
    if [ -n "$DOTCLEANER_CONSOLE_ROOT" ]; then printf '%s\n' "$DOTCLEANER_CONSOLE_ROOT"; fi
    return 0
  fi
  if [ -d /userdata/roms ]; then printf '%s\n' /userdata; return 0; fi        # Knulli, Batocera
  for _cr in /roms /storage/roms /mnt/mmc /mnt/SDCARD /mnt/sdcard; do
    # ArkOS, dArkOS | ROCKNIX, AmberELEC, JELOS, EmuELEC, Lakka | muOS |
    # Onion, MinUI, Allium, spruceOS, TrimUI, Miyoo stock
    if [ -d "$_cr" ] && [ ! -L "$_cr" ]; then printf '%s\n' "$_cr"; return 0; fi
  done
  if [ -n "${HOME:-}" ] && [ -d "$HOME/RetroPie/roms" ]; then printf '%s\n' "$HOME/RetroPie/roms"; fi
}

# SD cards and USB drives plugged in, one path per line
candidate_dirs() {
  if [ -d /Volumes ]; then
    for _cd in /Volumes/*; do
      if [ ! -d "$_cd" ] || [ -L "$_cd" ]; then continue; fi   # skip "Macintosh HD" (symlink to /)
      case ${_cd##*/} in com.apple.*|.*) continue ;; esac
      printf '%s\n' "$_cd"
    done
    return 0
  fi
  {
    # The console itself (when run on the handheld)
    console_root
    if [ -d /roms2 ]; then printf '%s\n' /roms2; fi            # ArkOS: second card
    # Linux desktops, Raspberry Pi, Steam Deck (/run/media/deck/NAME or /run/media/mmcblk0p1)
    for _cd in /media/*/* /run/media/*/*; do
      if [ -d "$_cd" ]; then printf '%s\n' "$_cd"; fi
    done
    for _cd in /media/* /run/media/*; do
      if [ -d "$_cd" ] && is_mountpoint "$_cd"; then printf '%s\n' "$_cd"; fi
    done
    # ChromeOS Linux, Windows WSL (USB drives as /mnt/d, /mnt/e...)
    for _cd in /mnt/chromeos/removable/* /mnt/[d-z]; do
      if [ -d "$_cd" ] && is_mountpoint "$_cd"; then printf '%s\n' "$_cd"; fi
    done
  } | awk '!seen[$0]++'
}

eject_volume() {
  if [ "$(uname -s 2>/dev/null)" != Darwin ]; then
    warn "  Eject only works on macOS: unmount the drive from your file manager."
    return 0
  fi
  case $1 in
    /Volumes/?*) _rest=${1#/Volumes/}; _vol=/Volumes/${_rest%%/*} ;;
    *) warn "  $1 is not on an external drive, nothing to eject."; return 0 ;;
  esac
  if diskutil eject "$_vol" >/dev/null 2>&1; then
    say "  ${C_GRN}$_vol ejected: you can unplug it.${C_OFF}"
  else
    warn "  Could not eject $_vol (a file may still be open)."
    return 1
  fi
}

# --- Cleaning ------------------------------------------------------------------

# clean_target PATH -> 0 if OK, 1 on error (honours DRY_RUN, ASSUME_YES...)
# resolve_target PATH -> sets _root (real path) and the rules, or prints why not
resolve_target() {
  _in=$1
  case $_in in -*) _in="./$_in" ;; esac

  if [ ! -e "$_in" ]; then err "not found: $1"; return 1; fi
  if [ ! -d "$_in" ]; then err "not a folder: $1"; return 1; fi
  if ! _root=$(cd "$_in" 2>/dev/null && pwd -P); then err "cannot open: $1"; return 1; fi
  if is_forbidden "$_root"; then
    err "refusing to clean $_root (system or home folder). Point to your SD card or USB drive, e.g. /Volumes/EASYROMS."
    return 1
  fi
  for _jd in $SYSTEM_DIRS $ARCHIVE_DIRS; do
    if [ "${_root##*/}" = "$_jd" ]; then
      err "$_root is itself a junk folder: delete it directly."
      return 1
    fi
  done

  # Safe mode on Mac-formatted drives: junk files only, system folders kept
  _files_only=0
  if is_mac_disk "$_root"; then _files_only=1; fi
  set_rules "$_files_only"
}

clean_target() {
  resolve_target "$1" || return 1

  say ""
  say "${C_BOLD}$_root${C_OFF}"
  if [ "$_files_only" -eq 1 ]; then
    say "  ${C_CYN}Mac-formatted drive: safe mode, only junk files are removed (system folders are kept).${C_OFF}"
  fi

  # shellcheck disable=SC2046
  set -- $(junk_find "$_root" print 2>/dev/null | classify)
  _total=$5

  if [ "$_total" -eq 0 ]; then
    say "  ${C_GRN}Already clean, nothing to delete.${C_OFF}"
    if [ "$EJECT" -eq 1 ] && [ "$DRY_RUN" -eq 0 ]; then eject_volume "$_root"; return $?; fi
    return 0
  fi

  _kb=$(junk_find "$_root" size 2>/dev/null | awk '{ s += $1 } END { print s + 0 }')
  _size=$(human_size "$_kb")

  if [ "$1" -gt 0 ]; then say "$(printf '  %6d  %s' "$1" '._* files (AppleDouble)')"; fi
  if [ "$2" -gt 0 ]; then say "$(printf '  %6d  %s' "$2" '.DS_Store')"; fi
  if [ "$3" -gt 0 ]; then say "$(printf '  %6d  %s' "$3" 'macOS system items (.Spotlight-V100, .Trashes, __MACOSX...)')"; fi
  if [ "$4" -gt 0 ]; then say "$(printf '  %6d  %s' "$4" 'Windows files')"; fi
  say "  ${C_DIM}------${C_OFF}"
  say "${C_BOLD}  Total: $(n_items "$_total"), $_size${C_OFF}"

  if [ "$QUIET" -eq 0 ]; then
    if [ "$MENU" -eq 1 ] && [ "$DRY_RUN" -eq 1 ]; then
      printf '%s' "  Show the full list? [y/N] "
      read -r _show || _show=''
      case $_show in [yY]*) list_items "$_root" ;; esac
    elif [ "$DRY_RUN" -eq 1 ]; then
      say "  ${C_DIM}Would be deleted:${C_OFF}"; list_items "$_root"
    elif [ "$VERBOSE" -eq 1 ]; then
      say "  ${C_DIM}To be deleted:${C_OFF}"; list_items "$_root"
    fi
  fi

  case " $JUNK_DIRS " in
    *" .Trashes "*)
      _trash=$(trash_count "$_root")
      if [ "$_trash" -gt 0 ] && [ "$QUIET" -eq 0 ]; then
        warn "  Warning: the drive's Trash holds $_trash file(s) deleted in Finder; they will be erased for good (keep them with -k / the Keep Trash option)."
      fi ;;
  esac

  if [ "$DRY_RUN" -eq 1 ]; then
    say "  ${C_YEL}Preview only: nothing was deleted.${C_OFF}"
    return 0
  fi

  if [ "$ASSUME_YES" -eq 0 ]; then
    if [ ! -t 0 ]; then
      err "no terminal to ask for confirmation: add -y to delete."
      return 1
    fi
    printf '%s' "  Delete $(n_items "$_total")? This cannot be undone. [y/N] "
    read -r _answer || _answer=''
    case $_answer in
      [yY]*) ;;
      *) say "  Cancelled, nothing was deleted."; return 0 ;;
    esac
  fi

  junk_find "$_root" delete 2>/dev/null

  # Check what is left
  # shellcheck disable=SC2046
  set -- $(junk_find "$_root" print 2>/dev/null | classify)
  _left=$5
  _rc=0

  if [ "$_left" -eq 0 ]; then
    say "  ${C_GRN}Done: $(n_items "$_total") deleted ($_size freed).${C_OFF}"
  else
    say "  ${C_GRN}$(n_items $((_total - _left))) deleted.${C_OFF}"
    if [ "$1" -eq 0 ] && [ "$2" -eq 0 ] && [ "$4" -eq 0 ]; then
      # Only system folders left: macOS recreated or locked them while mounted
      warn "  $_left macOS system folder(s) came back or are in use: macOS recreates them while the drive is plugged in. Harmless for your console; eject right after cleaning."
    else
      warn "  Could not delete $(n_items "$_left"):"
      list_items "$_root" >&2
      warn "  Check that the drive is not read-only, then try again (or with sudo)."
      _rc=1
    fi
  fi

  if [ "$EJECT" -eq 1 ] && [ "$_rc" -eq 0 ]; then
    eject_volume "$_root" || _rc=1
  fi
  return "$_rc"
}

# --- Console mode ----------------------------------------------------------------
# Started from the console's own menu (Ports, Tools, Apps): no keyboard and often
# no visible terminal (Knulli and Batocera show nothing: only the log and, when the
# frontend supports it, a notification). Finds the ROM card, cleans it without questions, shows the
# result on screen when the firmware allows it, and writes dotcleaner.log.

notify_frontend() {
  # Batocera / Knulli (and EmulationStation forks with the same web API)
  if command -v curl >/dev/null 2>&1; then
    curl -s -m 2 -d "$1" http://127.0.0.1:1234/notify >/dev/null 2>&1
  elif command -v wget >/dev/null 2>&1; then
    wget -q -T 2 -O /dev/null --post-data="$1" http://127.0.0.1:1234/notify >/dev/null 2>&1
  fi
  # Onion (Miyoo Mini): message box, closes by itself
  if [ -x /mnt/SDCARD/.tmp_update/bin/infoPanel ]; then
    /mnt/SDCARD/.tmp_update/bin/infoPanel --title "Dotcleaner" --message "$1" --auto >/dev/null 2>&1
  fi
  return 0
}

# Console screen: plain text, one line after the other, 40 columns at most,
# ASCII only, no colours and no cursor moves. The same lines go to the screen
# and to dotcleaner.log, so it works everywhere: the text screen of ArkOS-like
# firmwares, Knulli, Batocera, ROCKNIX, muOS, Onion, SSH, a serial console.
SCREEN=''
LIVE=0

# cout TEXT -> the screen (or the output) and the log
cout() {
  printf '%s\n' "$*" >>"$_log" 2>/dev/null
  if [ -n "$SCREEN" ]; then printf '%s\n' "$*" >"$SCREEN" 2>/dev/null; else printf '%s\n' "$*"; fi
}

# clive TEXT -> rewrite the current line (progress), only on a live screen
clive() {
  if [ "$LIVE" -eq 1 ]; then
    if [ -n "$SCREEN" ]; then printf '\r%s' "$*" >"$SCREEN" 2>/dev/null; else printf '\r%s' "$*"; fi
  fi
}

# cbar DONE TOTAL -> [####################] 100%
cbar() {
  awk -v d="$1" -v t="$2" 'BEGIN {
    p = (t > 0) ? int(d * 100 / t) : 100; f = int(p / 5); s = "["
    for (i = 0; i < 20; i++) s = s ((i < f) ? "#" : "-")
    printf "%s] %3d%%", s, p
  }'
}

console_mode() {
  ASSUME_YES=1 DRY_RUN=0 EJECT=0 MENU=0 QUIET=0
  C_BOLD='' C_DIM='' C_RED='' C_GRN='' C_YEL='' C_CYN='' C_OFF=''
  _log=${DOTCLEANER_LOG:-${SCRIPT_DIR:-.}/dotcleaner.log}
  : >"$_log" 2>/dev/null

  # Screen: the terminal (SSH), else the text screen of the console if any.
  # Knulli / Batocera keep their menu on screen while a script runs: the text
  # screen behind it is never seen, so do not use it (and do not wait at the end).
  if [ -t 1 ]; then
    LIVE=1
  elif [ -d "${DOTCLEANER_USERDATA:-/userdata}/system" ]; then
    :
  elif [ -z "${DOTCLEANER_NO_TTY:-}" ]; then
    for _t in /dev/tty1 /dev/tty0; do
      if [ -e "$_t" ] && [ ! -w "$_t" ] && command -v sudo >/dev/null 2>&1; then
        sudo -n chmod 666 "$_t" 2>/dev/null
      fi
      if [ -w "$_t" ]; then SCREEN=$_t LIVE=1; break; fi
    done
  fi
  if [ -n "$SCREEN" ]; then
    printf '\033c' >"$SCREEN" 2>/dev/null                      # clear the text screen
    if command -v setfont >/dev/null 2>&1 && [ -f /usr/share/consolefonts/Lat7-Terminus16.psf.gz ]; then
      setfont /usr/share/consolefonts/Lat7-Terminus16.psf.gz 2>/dev/null ||
        sudo -n setfont /usr/share/consolefonts/Lat7-Terminus16.psf.gz 2>/dev/null
    fi
  fi

  cout "=================================="
  cout " DOTCLEANER $VERSION"
  cout " macOS junk cleaner"
  cout "=================================="
  cout ""
  _rc=1

  # 1. Find the ROM card
  cout "[1/4] ROM card"
  _found=$(console_root)
  if [ -z "$_found" ]; then
    cout "      No ROM card found."
    cout "      Run it from a computer, or:"
    cout "      sh dotcleaner.sh /path/to/roms"
    notify_frontend "Dotcleaner: no ROM card found"
  elif ! _why=$(resolve_target "$_found" 2>&1); then
    cout "      $_found cannot be cleaned."
    printf '%s\n' "$_why" >>"$_log" 2>/dev/null
    notify_frontend "Dotcleaner: $_found cannot be cleaned"
  else
    resolve_target "$_found"
    _info=$(drive_info "$_root")
    cout "      $_root${_info:+ ($_info)}"
    if [ "$_files_only" -eq 1 ]; then cout "      Mac disk: safe mode"; fi

    # 2. Scan
    cout "[2/4] Scan"
    clive "      please wait..."
    notify_frontend "Dotcleaner: scanning $_root..."
    # shellcheck disable=SC2046
    set -- $(junk_find "$_root" print 2>/dev/null | classify)
    _total=$5
    _kb=$(junk_find "$_root" size 2>/dev/null | awk '{ s += $1 } END { print s + 0 }')
    _size=$(human_size "$_kb")
    clive "                    "; clive ""
    cout "      $(n_items "$_total") of junk, $_size"
    if [ "$_total" -gt 0 ]; then cout "      ($1 ._*, $2 .DS_Store, $(($3 + $4)) other)"; fi

    # 3. Clean
    cout "[3/4] Clean"
    if [ "$_total" -eq 0 ]; then
      cout "      nothing to delete"
      cout "[4/4] Done!"
      cout "      Already clean."
      notify_frontend "Dotcleaner: already clean, nothing to delete"
      _rc=0
    else
      notify_frontend "Dotcleaner: cleaning $(n_items "$_total")..."
      clive "      $(cbar 0 "$_total")"
      junk_find "$_root" progress 2>/dev/null | {
        _d=0 _last=-1
        while IFS= read -r _x; do
          case $_x in ''|*[!0-9]*) continue ;; esac
          _d=$((_d + _x))
          _p=$((_d * 100 / _total))
          if [ "$_p" -ne "$_last" ]; then _last=$_p; clive "      $(cbar "$_d" "$_total")"; fi
        done
      }
      # shellcheck disable=SC2046
      set -- $(junk_find "$_root" print 2>/dev/null | classify)
      _left=$5
      _done=$((_total - _left))
      if [ "$LIVE" -eq 1 ]; then                    # finish the progress line
        clive "      $(cbar "$_done" "$_total")"
        if [ -n "$SCREEN" ]; then printf '\n' >"$SCREEN" 2>/dev/null; else printf '\n'; fi
        printf '%s\n' "      $(cbar "$_done" "$_total")" >>"$_log" 2>/dev/null
      else
        cout "      $(cbar "$_done" "$_total")"
      fi
      cout "      $(n_items "$_done") deleted"
      if [ "$_left" -eq 0 ] || { [ "$1" -eq 0 ] && [ "$2" -eq 0 ] && [ "$4" -eq 0 ]; }; then
        cout "[4/4] Done!"
        cout "      $_size freed"
        if [ "$_left" -gt 0 ]; then cout "      ($_left system folder(s) in use)"; fi
        cout "      Games and saves untouched."
        notify_frontend "Dotcleaner: done, $(n_items "$_done") deleted ($_size freed)"
        _rc=0
      else
        cout "[4/4] Not finished"
        cout "      $_left item(s) could not be deleted"
        cout "      (read-only card?) See the log."
        list_items "$_root" >>"$_log" 2>/dev/null
        notify_frontend "Dotcleaner: $_left item(s) could not be deleted, see dotcleaner.log"
      fi
    fi
  fi

  cout ""
  cout "Log: dotcleaner.log"
  if [ -n "$SCREEN" ]; then
    _s=6
    while [ "$_s" -gt 0 ]; do
      clive "Back to the menu in $_s s "; sleep 1; _s=$((_s - 1))
    done
    printf '\033c' >"$SCREEN" 2>/dev/null
  fi
  exit "$_rc"
}

# --- Interactive menu ----------------------------------------------------------

DRIVE=''

pause() {
  printf '\n%s' "${C_DIM}Press Enter to go back to the menu...${C_OFF}"
  read -r _ || true
}

check_box() { if [ "$1" -eq 1 ]; then printf '[x]'; else printf '[ ]'; fi; }

header() {
  if [ -t 1 ]; then printf '\033[H\033[2J'; fi
  printf '%s\n' "${C_BOLD}dotcleaner $VERSION${C_OFF} ${C_DIM}- clean macOS junk from SD cards & USB drives${C_OFF}"
  printf '%s\n\n' "${C_DIM}==========================================================${C_OFF}"
}

menu_choose_drive() {
  while :; do
    header
    printf '%s\n\n' "${C_BOLD}1. Choose a drive${C_OFF}"
    _list=$(candidate_dirs)
    _count=0
    if [ -n "$_list" ]; then
      _count=$(printf '%s\n' "$_list" | awk 'END { print NR }')
      _i=0
      while IFS= read -r _d; do
        _i=$((_i + 1))
        printf '  %s) %-22s %s\n' "$_i" "${_d##*/}" "${C_DIM}$(drive_info "$_d")${C_OFF}"
      done <<EOF
$_list
EOF
    else
      printf '  %s\n' "${C_YEL}No SD card or USB drive found: plug one in, then press r.${C_OFF}"
    fi
    printf '\n  o) Other folder (type its path)\n  r) Refresh\n  Enter) Back\n\n'
    printf '%s' "Your choice: "
    read -r _c || return 0
    case $_c in
      '') return 0 ;;
      r|R) continue ;;
      o|O)
        printf '%s' "Path of the drive or folder: "
        read -r _p || return 0
        if [ -n "$_p" ]; then DRIVE=$_p; return 0; fi ;;
      *[!0-9]*) ;;
      *)
        if [ "$_c" -ge 1 ] && [ "$_c" -le "$_count" ]; then
          DRIVE=$(printf '%s\n' "$_list" | sed -n "${_c}p")
          return 0
        fi ;;
    esac
  done
}

menu_options() {
  while :; do
    header
    printf '%s\n\n' "${C_BOLD}2. Options${C_OFF} ${C_DIM}(type a number to switch it on or off)${C_OFF}"
    printf '  1) %s Also remove Windows files (Thumbs.db, desktop.ini)\n' "$(check_box "$CLEAN_WINDOWS")"
    printf '  2) %s Keep the drive'"'"'s Trash\n' "$(check_box "$KEEP_TRASH")"
    printf '  3) %s Eject when done\n' "$(check_box "$EJECT")"
    printf '\n  Enter) Back\n\n%s' "Your choice: "
    read -r _c || return 0
    case $_c in
      1) CLEAN_WINDOWS=$((1 - CLEAN_WINDOWS)) ;;
      2) KEEP_TRASH=$((1 - KEEP_TRASH)) ;;
      3) EJECT=$((1 - EJECT)) ;;
      '') return 0 ;;
    esac
  done
}

menu_help() {
  header
  cat <<EOF
${C_BOLD}Help${C_OFF}

When you copy files from a Mac to an SD card or USB drive, macOS adds
hidden files: a "._" twin for every file, ".DS_Store" in every folder,
and ".Spotlight-V100", ".Trashes", ".fseventsd" folders at the root.
On a console they can show up as ghost games that won't launch.

  1. Choose a drive   pick your SD card or USB drive
  2. Options          Windows files, keep the Trash, eject when done
  3. Scan             shows what would be deleted, deletes nothing
  4. Clean            deletes the junk after your confirmation

Your ROMs, saves, BIOS and every other file are never touched.
On Mac-formatted drives (APFS, HFS+) only junk files are removed.

More: https://github.com/Shadowix84/Dotcleaner-Multi-Software
EOF
  pause
}

need_drive() {
  if [ -z "$DRIVE" ]; then
    printf '\n%s\n' "${C_YEL}Choose a drive first (1).${C_OFF}"
    pause
    return 1
  fi
}

interactive_menu() {
  MENU=1
  # Eject when done: on by default where it works (macOS)
  if [ "$(uname -s 2>/dev/null)" = Darwin ]; then EJECT=1; fi
  # One drive plugged in: select it directly
  _only=$(candidate_dirs)
  if [ -n "$_only" ] && [ "$(printf '%s\n' "$_only" | awk 'END { print NR }')" -eq 1 ]; then DRIVE=$_only; fi

  while :; do
    header
    if [ -n "$DRIVE" ] && [ ! -d "$DRIVE" ]; then DRIVE=''; fi   # unplugged or ejected
    if [ -n "$DRIVE" ]; then
      printf '  Drive    %s %s\n' "${C_BOLD}${DRIVE##*/}${C_OFF}" "${C_DIM}($DRIVE, $(drive_info "$DRIVE"))${C_OFF}"
    else
      printf '  Drive    %s\n' "${C_YEL}none selected${C_OFF}"
    fi
    printf '  Options  %s Windows files   %s Keep Trash   %s Eject when done\n\n' \
      "$(check_box "$CLEAN_WINDOWS")" "$(check_box "$KEEP_TRASH")" "$(check_box "$EJECT")"
    printf '  1) Choose a drive\n'
    printf '  2) Options\n'
    printf '  3) Scan %s\n' "${C_DIM}(preview, deletes nothing)${C_OFF}"
    printf '  4) Clean\n'
    printf '  h) Help    q) Quit\n\n'
    printf '%s' "Your choice: "
    read -r _c || { printf '\n'; exit 0; }
    case $_c in
      1) menu_choose_drive ;;
      2) menu_options ;;
      3) if need_drive; then DRY_RUN=1; ASSUME_YES=0; clean_target "$DRIVE"; DRY_RUN=0; pause; fi ;;
      4) if need_drive; then DRY_RUN=0; ASSUME_YES=0; clean_target "$DRIVE"; pause; fi ;;
      h|H|'?') menu_help ;;
      q|Q) exit 0 ;;
    esac
  done
}

# --- Main --------------------------------------------------------------------
main() {
  # Parse options anywhere on the command line; paths are kept in order.
  _n=$#
  while [ "$_n" -gt 0 ]; do
    _arg=$1; shift; _n=$((_n - 1))
    case $_arg in
      -n|--dry-run)    DRY_RUN=1 ;;
      -y|--yes)        ASSUME_YES=1 ;;
      -w|--windows)    CLEAN_WINDOWS=1 ;;
      -e|--eject)      EJECT=1 ;;
      -v|--verbose)    VERBOSE=1 ;;
      -q|--quiet)      QUIET=1 ;;
      -k|--keep-trash) KEEP_TRASH=1 ;;
      --console)       CONSOLE=1 ;;
      -h|--help)       SHOW_HELP=1 ;;
      -V|--version)    printf 'dotcleaner %s\n' "$VERSION"; exit 0 ;;
      --)
        while [ "$_n" -gt 0 ]; do set -- ${1+"$@"} "$1"; shift; _n=$((_n - 1)); done ;;
      --*) die_usage "unknown option: $_arg" ;;
      -?*)
        if [ ${#_arg} -gt 2 ]; then
          # combined short options: -ny -> -n -y
          _rest=${_arg#-?}; _first=${_arg%"$_rest"}
          set -- "$_first" "-$_rest" ${1+"$@"}; _n=$((_n + 2))
        else
          die_usage "unknown option: $_arg"
        fi ;;
      *) set -- ${1+"$@"} "$_arg" ;;
    esac
  done

  if [ "$SHOW_HELP" -eq 1 ]; then usage; exit 0; fi

  trap 'printf "\n%s\n" "Interrupted." >&2; exit 130' INT TERM

  if [ "$CONSOLE" -eq 1 ] || { [ $# -eq 0 ] && [ "$CONSOLE_LAUNCHER" -eq 1 ]; }; then
    console_mode
  fi

  if [ $# -eq 0 ]; then
    if [ ! -t 0 ]; then die_usage "no path given."; fi
    interactive_menu
  fi

  say "${C_BOLD}dotcleaner $VERSION${C_OFF}"
  _status=0
  for _target in "$@"; do
    clean_target "$_target" || _status=1
  done
  exit "$_status"
}

main ${1+"$@"}
