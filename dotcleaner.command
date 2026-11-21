#!/bin/sh
#
# macOS launcher: double-click this file in Finder to clean an SD card.
# It opens Terminal on the dotcleaner menu: choose the drive, scan, clean.
#
# Keep it in the same folder as dotcleaner.sh, or install the
# "dotcleaner" command first (see README).

cd "$(dirname "$0")" || exit 1

if [ -f ./dotcleaner.sh ]; then
  sh ./dotcleaner.sh "$@"
elif command -v dotcleaner >/dev/null 2>&1; then
  dotcleaner "$@"
else
  printf '%s\n' "dotcleaner.sh was not found next to this file."
fi

printf '\n%s' "Press Enter to close this window..."
read -r _ || true
