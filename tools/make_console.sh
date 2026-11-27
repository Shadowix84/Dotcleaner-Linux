#!/bin/sh
#
# Builds the console launchers from dotcleaner.sh (run it after every change
# to dotcleaner.sh; CI checks that console/ is up to date):
#
#   console/Dotcleaner.sh                    -> "ports" folder: ArkOS, dArkOS, Batocera,
#                                               ROCKNIX, AmberELEC, JELOS... / "tools": Knulli
#   console/Onion/App/Dotcleaner/launch.sh   -> Onion, spruceOS (Miyoo Mini, A30...): App/
#   console/TrimUI/Apps/Dotcleaner/          -> TrimUI stock OS, CrossMix-OS: Apps/
#   console/MinUI/Dotcleaner.pak/launch.sh   -> MinUI, NextUI: Tools/<device>/
#   console/muOS/MUOS/application/Dotcleaner/mux_launch.sh -> muOS: MUOS/application/
#   console/README.txt                       -> where to copy it, in English and French
#   console/icons/dotcleaner.png             -> the icon in the Ports / Tools menu, copied next
#                                               to the launcher (drawn by tools/make_logos.py)
#
# The launcher is dotcleaner.sh itself, switched to console mode when it is
# started with no arguments: it finds the ROM card(s), cleans them, shows the result
# and writes dotcleaner.log next to itself.

set -eu
cd "$(dirname "$0")/.."

mkdir -p console/Onion/App/Dotcleaner
sed 's/^CONSOLE_LAUNCHER=0$/CONSOLE_LAUNCHER=1/' dotcleaner.sh >console/Dotcleaner.sh
grep -q '^CONSOLE_LAUNCHER=1$' console/Dotcleaner.sh
cp console/Dotcleaner.sh console/Onion/App/Dotcleaner/launch.sh

# TrimUI stock OS / CrossMix-OS: same app format as Onion, in Apps/
mkdir -p console/TrimUI/Apps/Dotcleaner
cp console/Dotcleaner.sh console/TrimUI/Apps/Dotcleaner/launch.sh
cp console/Onion/App/Dotcleaner/icon.png console/TrimUI/Apps/Dotcleaner/icon.png

# MinUI / NextUI: a .pak folder with launch.sh, in Tools/<device folder>/
mkdir -p console/MinUI/Dotcleaner.pak
cp console/Dotcleaner.sh console/MinUI/Dotcleaner.pak/launch.sh

# muOS: an application folder with mux_launch.sh (the "# HELP:" line is shown by muOS)
mkdir -p console/muOS/MUOS/application/Dotcleaner
{
  sed -n '1p' console/Dotcleaner.sh
  echo '# HELP: Removes the macOS junk files (._*, .DS_Store...) from the SD cards. Games, saves and BIOS are never touched.'
  sed '1d' console/Dotcleaner.sh
} >console/muOS/MUOS/application/Dotcleaner/mux_launch.sh
for _app in console/Onion/App/Dotcleaner console/TrimUI/Apps/Dotcleaner; do
  cat >"$_app/config.json" <<'JSON'
{
  "label": "Dotcleaner",
  "icon": "icon.png",
  "launch": "launch.sh",
  "description": "Remove macOS junk files (._*, .DS_Store...) from the SD card"
}
JSON
done
cat >console/README.txt <<'TXT'
DOTCLEANER - console launcher
=============================

Removes the macOS junk files (._*, .DS_Store...) from the ROM card,
right on the console. Your games, saves and BIOS are never touched.

WHAT IS IN THIS ZIP
  Dotcleaner.sh       the launcher (ArkOS, Knulli, Batocera, ROCKNIX...)
  icons/              its icon for the menu
  Onion/              the same launcher as an app: Onion, spruceOS
  TrimUI/             ... as an app: TrimUI stock OS, CrossMix-OS
  MinUI/              ... as a tool: MinUI, NextUI
  muOS/               ... as an application: muOS
  README.txt          this file

1. COPY (card in your computer) - create the folder if needed

   Firmware                            Copy                    Into
   ----------------------------------  ----------------------  ------------
   ArkOS, dArkOS (R36S...)             Dotcleaner.sh + icons/  ports/
   Knulli (RG40XXV, RG35XX...)         Dotcleaner.sh + icons/  roms/tools/
   Batocera                            Dotcleaner.sh + icons/  roms/ports/
   ROCKNIX, AmberELEC, JELOS...        Dotcleaner.sh + icons/  roms/ports/
   Onion, spruceOS (Miyoo Mini, A30)   folder Onion/App/Dotcleaner  App/

   Other firmwares: copy the whole folder
   - TrimUI stock OS, CrossMix-OS: TrimUI/Apps/Dotcleaner into Apps/
   - MinUI, NextUI: MinUI/Dotcleaner.pak into Tools/<device>/, where
     <device> is the folder already in Tools: tg5040 (TrimUI Smart Pro,
     Brick), miyoomini, my282 (Miyoo A30), rg35xxplus...
   - muOS: muOS/MUOS/application/Dotcleaner into MUOS/application/

2. ON THE CONSOLE
   Ports > Dotcleaner (Tools on Knulli and MinUI, Apps on Onion,
   spruceOS and TrimUI, Applications on muOS).
   On Knulli / Batocera, update the game lists first so it shows up.
   - ArkOS and similar: the steps show on screen.
   - Knulli: nothing shows on screen, that is normal. It takes a few
     seconds, then you are back in the menu.
   The result is always in dotcleaner.log, next to the launcher.
   If ghost games are still listed, update the game lists.
   TWO SD CARDS, or one card split in several partitions: nothing to
   do, every card / partition with a games folder (roms, Roms, ROMS...)
   is cleaned.

3. THE ICON IN THE MENU
   The launcher adds itself to the menu with its icon (gamelist.xml next
   to it). Knulli / Batocera: done the first time you start it.
   ArkOS and others: if the icon is still missing after a restart, put
   the card in your computer, open gamelist.xml next to Dotcleaner.sh and
   add these 2 lines inside the Dotcleaner <game> block:
       <image>./icons/dotcleaner.png</image>
       <thumbnail>./icons/dotcleaner.png</thumbnail>

Help: https://github.com/Shadowix84/Dotcleaner-Multi-Software#faq


DOTCLEANER - lanceur console (francais)
=======================================

Supprime les fichiers parasites de macOS (._*, .DS_Store...) de la carte
des ROM, directement sur la console. Jeux, sauvegardes et BIOS ne sont
jamais touches.

CONTENU DU ZIP
  Dotcleaner.sh       le lanceur (ArkOS, Knulli, Batocera, ROCKNIX...)
  icons/              son icone pour le menu
  Onion/              le meme lanceur en appli : Onion, spruceOS
  TrimUI/             ... en appli : TrimUI d'origine, CrossMix-OS
  MinUI/              ... en outil : MinUI, NextUI
  muOS/               ... en application : muOS
  README.txt          ce fichier

1. COPIER (carte dans l'ordinateur) - creez le dossier s'il n'existe pas
   - ArkOS, dArkOS (R36S...) : Dotcleaner.sh + icons/ dans ports/
   - Knulli (RG40XXV, RG35XX...) : Dotcleaner.sh + icons/ dans roms/tools/
   - Batocera, ROCKNIX, AmberELEC... : Dotcleaner.sh + icons/ dans roms/ports/
   - Onion, spruceOS : le dossier Onion/App/Dotcleaner dans App/
   - TrimUI d'origine, CrossMix-OS : le dossier TrimUI/Apps/Dotcleaner
     dans Apps/
   - MinUI, NextUI : le dossier MinUI/Dotcleaner.pak dans Tools/<appareil>/
     (le dossier deja present dans Tools : tg5040 pour TrimUI Smart Pro
     et Brick, miyoomini, my282 pour Miyoo A30, rg35xxplus...)
   - muOS : le dossier muOS/MUOS/application/Dotcleaner dans
     MUOS/application/

2. SUR LA CONSOLE
   Ports > Dotcleaner (Tools sur Knulli et MinUI, Apps sur Onion,
   spruceOS et TrimUI, Applications sur muOS).
   Sur Knulli / Batocera, mettez d'abord a jour les listes de jeux.
   - ArkOS et similaires : les etapes s'affichent a l'ecran.
   - Knulli : rien ne s'affiche, c'est normal. Ca prend quelques
     secondes, puis retour au menu.
   Le resultat est toujours dans dotcleaner.log, a cote du lanceur.
   Si des jeux fantomes restent dans la liste, mettez a jour les listes.
   DEUX CARTES SD, ou une carte divisee en plusieurs partitions : rien
   a faire, chaque carte / partition avec un dossier de jeux (roms, Roms,
   ROMS...) est nettoyee.

3. L'ICONE DANS LE MENU
   Le lanceur s'ajoute tout seul au menu avec son icone (gamelist.xml a
   cote de lui). Knulli / Batocera : c'est fait au premier lancement.
   ArkOS et autres : si l'icone manque encore apres un redemarrage,
   mettez la carte dans l'ordinateur, ouvrez gamelist.xml a cote de
   Dotcleaner.sh et ajoutez ces 2 lignes dans le bloc <game> de Dotcleaner :
       <image>./icons/dotcleaner.png</image>
       <thumbnail>./icons/dotcleaner.png</thumbnail>

Aide : https://github.com/Shadowix84/Dotcleaner-Multi-Software#faq
TXT
chmod 644 console/README.txt
chmod 755 console/Dotcleaner.sh console/Onion/App/Dotcleaner/launch.sh console/TrimUI/Apps/Dotcleaner/launch.sh \
  console/MinUI/Dotcleaner.pak/launch.sh console/muOS/MUOS/application/Dotcleaner/mux_launch.sh
echo "console launchers updated"
