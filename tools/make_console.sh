#!/bin/sh
#
# Builds the console launchers from dotcleaner.sh (run it after every change
# to dotcleaner.sh; CI checks that console/ is up to date):
#
#   console/Dotcleaner.sh                    -> "ports" folder: ArkOS, dArkOS, Knulli,
#                                               Batocera, ROCKNIX, AmberELEC, JELOS...
#   console/Onion/App/Dotcleaner/launch.sh   -> Onion (Miyoo Mini): copy App/Dotcleaner
#
# The launcher is dotcleaner.sh itself, switched to console mode when it is
# started with no arguments: it finds the ROM card, cleans it, shows the result
# and writes dotcleaner.log next to itself.

set -eu
cd "$(dirname "$0")/.."

mkdir -p console/Onion/App/Dotcleaner
sed 's/^CONSOLE_LAUNCHER=0$/CONSOLE_LAUNCHER=1/' dotcleaner.sh >console/Dotcleaner.sh
grep -q '^CONSOLE_LAUNCHER=1$' console/Dotcleaner.sh
cp console/Dotcleaner.sh console/Onion/App/Dotcleaner/launch.sh
cat >console/Onion/App/Dotcleaner/config.json <<'JSON'
{
  "label": "Dotcleaner",
  "icon": "icon.png",
  "launch": "launch.sh",
  "description": "Remove macOS junk files (._*, .DS_Store...) from the SD card"
}
JSON
chmod 755 console/Dotcleaner.sh console/Onion/App/Dotcleaner/launch.sh
echo "console launchers updated"
