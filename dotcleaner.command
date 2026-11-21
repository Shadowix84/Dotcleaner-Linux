#!/bin/sh
#
# macOS launcher: double-click this file in Finder to clean an SD card.
# It opens Terminal, lists the plugged-in cards, cleans the one you pick
# (after confirmation) and ejects it.
#
# Keep it in the same folder as dotcleaner.sh, or install the
# "dotcleaner" command first (see README).

cd "$(dirname "$0")" || exit 1

if [ -f ./dotcleaner.sh ]; then
  sh ./dotcleaner.sh --eject "$@"
elif command -v dotcleaner >/dev/null 2>&1; then
  dotcleaner --eject "$@"
else
  printf '%s\n' "dotcleaner.sh was not found next to this file."
fi

printf '\n%s' "Press Enter to close this window..."
read -r _ || true
