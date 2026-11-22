#!/bin/sh
#
# Builds the console launchers from dotcleaner.sh (run it after every change
# to dotcleaner.sh; CI checks that console/ is up to date):
#
#   console/Dotcleaner.sh                    -> "ports" folder: ArkOS, dArkOS, Batocera,
#                                               ROCKNIX, AmberELEC, JELOS... / "tools": Knulli
#   console/Onion/App/Dotcleaner/launch.sh   -> Onion (Miyoo Mini): copy App/Dotcleaner
#   console/README.txt                       -> where to copy it, in English and French
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
cat >console/README.txt <<'TXT'
DOTCLEANER - console launcher
=============================

Removes the macOS junk files (._*, .DS_Store...) from the ROM card,
right on the console. Your games, saves and BIOS are never touched.

1. Copy the launcher to the card:

   Firmware                           Copy                    To
   ---------------------------------  ----------------------  -------------
   ArkOS, dArkOS (R36S...)            Dotcleaner.sh           ports/
   Knulli (RG40XXV, RG35XX...)        Dotcleaner.sh           roms/tools/
   Batocera                           Dotcleaner.sh           roms/ports/
   ROCKNIX, AmberELEC, JELOS, EmuELEC Dotcleaner.sh           roms/ports/
   Onion (Miyoo Mini)                 the Onion/App/Dotcleaner folder   App/

   Create the folder if it does not exist.

2. On the console: Ports > Dotcleaner (Tools on Knulli, Apps on Onion).
   On Knulli / Batocera, update the game lists first so it shows up.

3. ArkOS-like firmwares show the steps on screen. Knulli shows nothing:
   it cleans in a few seconds and you are back in the menu.
   The result is always in dotcleaner.log, next to the launcher.
   If ghost games are still listed, update the game lists.

Help: https://github.com/Shadowix84/Dotcleaner-Multi-Software#faq


DOTCLEANER - lanceur console (francais)
=======================================

Supprime les fichiers parasites de macOS (._*, .DS_Store...) de la carte
des ROM, directement sur la console. Jeux, sauvegardes et BIOS ne sont
jamais touches.

1. Copiez le lanceur sur la carte :
   - ArkOS, dArkOS (R36S...) : Dotcleaner.sh dans ports/
   - Knulli (RG40XXV, RG35XX...) : Dotcleaner.sh dans roms/tools/
   - Batocera, ROCKNIX, AmberELEC, JELOS, EmuELEC : Dotcleaner.sh dans roms/ports/
   - Onion (Miyoo Mini) : le dossier Onion/App/Dotcleaner dans App/
   Creez le dossier s'il n'existe pas.

2. Sur la console : Ports > Dotcleaner (Tools sur Knulli, Apps sur Onion).
   Sur Knulli / Batocera, mettez d'abord a jour les listes de jeux.

3. Les firmwares type ArkOS affichent les etapes a l'ecran. Knulli
   n'affiche rien : le nettoyage prend quelques secondes, puis retour au
   menu. Le resultat est toujours dans dotcleaner.log, a cote du lanceur.
   Si des jeux fantomes restent dans la liste, mettez a jour les listes
   de jeux.

Discord (en francais) : https://discord.gg/4FbhkuhRMm
TXT
chmod 644 console/README.txt
chmod 755 console/Dotcleaner.sh console/Onion/App/Dotcleaner/launch.sh
echo "console launchers updated"
