DOTCLEANER - console launcher
=============================

Removes the macOS junk files (._*, .DS_Store...) from the ROM card,
right on the console. Your games, saves and BIOS are never touched.

WHAT IS IN THIS ZIP
  Dotcleaner.sh       the launcher (ArkOS, Knulli, Batocera, ROCKNIX...)
  Onion/              the same launcher as an Onion app (Miyoo Mini)
  menu-logo/          optional: the Dotcleaner logo in the console menu
  README.txt          this file

1. COPY THE LAUNCHER (card in your computer)

   Firmware                            Copy             Into
   ----------------------------------  ---------------  ------------
   ArkOS, dArkOS (R36S...)             Dotcleaner.sh    ports/
   Knulli (RG40XXV, RG35XX...)         Dotcleaner.sh    roms/tools/
   Batocera                            Dotcleaner.sh    roms/ports/
   ROCKNIX, AmberELEC, JELOS, EmuELEC  Dotcleaner.sh    roms/ports/
   Onion (Miyoo Mini)                  Onion/App/Dotcleaner (folder)  App/

   Create the folder if it does not exist.

2. OPTIONAL: SHOW THE LOGO IN THE MENU (not for Onion: it has its icon)
   Copy the "images" folder of menu-logo/ next to Dotcleaner.sh. Then:
   - no gamelist.xml there yet: copy menu-logo/gamelist.xml too;
   - a gamelist.xml is already there (PortMaster...): do NOT replace it.
     Open it and paste the <game>...</game> block of menu-logo/gamelist.xml
     just before the last line </gameList>.
   Do this with the card in your computer: the console rewrites this file.

3. ON THE CONSOLE
   Ports > Dotcleaner (Tools on Knulli, Apps on Onion).
   On Knulli / Batocera, update the game lists first so it shows up.
   - ArkOS and similar: the steps show on screen.
   - Knulli: nothing shows on screen, that is normal. It takes a few
     seconds, then you are back in the menu.
   The result is always in dotcleaner.log, next to the launcher.
   If ghost games are still listed, update the game lists.

Help: https://github.com/Shadowix84/Dotcleaner-Multi-Software#faq


DOTCLEANER - lanceur console (francais)
=======================================

Supprime les fichiers parasites de macOS (._*, .DS_Store...) de la carte
des ROM, directement sur la console. Jeux, sauvegardes et BIOS ne sont
jamais touches.

CONTENU DU ZIP
  Dotcleaner.sh       le lanceur (ArkOS, Knulli, Batocera, ROCKNIX...)
  Onion/              le meme lanceur en application Onion (Miyoo Mini)
  menu-logo/          facultatif : le logo Dotcleaner dans le menu
  README.txt          ce fichier

1. COPIER LE LANCEUR (carte dans l'ordinateur)
   - ArkOS, dArkOS (R36S...) : Dotcleaner.sh dans ports/
   - Knulli (RG40XXV, RG35XX...) : Dotcleaner.sh dans roms/tools/
   - Batocera, ROCKNIX, AmberELEC, JELOS... : Dotcleaner.sh dans roms/ports/
   - Onion (Miyoo Mini) : le dossier Onion/App/Dotcleaner dans App/
   Creez le dossier s'il n'existe pas.

2. FACULTATIF : LE LOGO DANS LE MENU (pas pour Onion : il a son icone)
   Copiez le dossier "images" de menu-logo/ a cote de Dotcleaner.sh. Puis :
   - pas encore de gamelist.xml dans ce dossier : copiez aussi
     menu-logo/gamelist.xml ;
   - un gamelist.xml existe deja (PortMaster...) : NE le remplacez PAS.
     Ouvrez-le et collez le bloc <game>...</game> de menu-logo/gamelist.xml
     juste avant la derniere ligne </gameList>.
   A faire avec la carte dans l'ordinateur : la console reecrit ce fichier.

3. SUR LA CONSOLE
   Ports > Dotcleaner (Tools sur Knulli, Apps sur Onion).
   Sur Knulli / Batocera, mettez d'abord a jour les listes de jeux.
   - ArkOS et similaires : les etapes s'affichent a l'ecran.
   - Knulli : rien ne s'affiche, c'est normal. Ca prend quelques
     secondes, puis retour au menu.
   Le resultat est toujours dans dotcleaner.log, a cote du lanceur.
   Si des jeux fantomes restent dans la liste, mettez a jour les listes.

Discord (en francais) : https://discord.gg/4FbhkuhRMm
