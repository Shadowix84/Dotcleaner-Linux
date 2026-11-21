# dotcleaner

**Supprime les fichiers parasites que macOS laisse sur les cartes SD des consoles d'émulation.**

[![CI](https://github.com/Shadowix84/Dotcleaner-Linux/actions/workflows/ci.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Linux/actions/workflows/ci.yml)
[![Licence : MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

🇬🇧 [English version](README.md)

Quand on copie des ROM sur une carte SD depuis un Mac, macOS ajoute en douce des fichiers cachés :
un jumeau `._` pour chaque fichier (`._Pokemon Emeraude.gba`), un `.DS_Store` dans chaque dossier
ouvert dans le Finder, et des dossiers `.Spotlight-V100`, `.Trashes` ou `.fseventsd` à la racine.

Sur la console, ces fichiers peuvent apparaître comme des **jeux fantômes qui ne se lancent pas**,
perturber le scraping et prendre de la place.

**dotcleaner** les supprime en une commande — et **uniquement eux**.

Fonctionne avec toute console dont la carte se branche sur un Mac : R36S (ArkOS), Anbernic (Knulli,
muOS, ROCKNIX…), Miyoo (Onion), Retroid, TrimUI… et directement sur la console via SSH.

## Ce qui est supprimé

| Élément | D'où ça vient |
| --- | --- |
| `._*` | Fichiers AppleDouble : les métadonnées macOS de chaque fichier copié |
| `.DS_Store` | Réglages d'affichage des dossiers du Finder |
| `.Spotlight-V100` | Index Spotlight de la carte |
| `.Trashes` | Corbeille de la carte (fichiers supprimés dans le Finder sans vider la corbeille) |
| `.fseventsd` | Journal des modifications du système de fichiers |
| `.TemporaryItems`, `.DocumentRevisions-V100` | Fichiers temporaires et versions de documents |
| `.apdisk`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop` | Métadonnées de disque et de partages réseau |
| `__MACOSX` | Restes d'archives zip créées sur Mac |
| `Thumbs.db`, `ehthumbs.db`, `desktop.ini` | Windows — **seulement avec `-w`** |

**Jamais touché :** vos ROM, sauvegardes, BIOS, et tout autre fichier, même caché (`.keep`, fichiers de config…).
Les liens symboliques ne sont pas suivis et le script ne sort jamais de la carte.

> ⚠️ `.Trashes` contient les fichiers supprimés dans le Finder sans avoir vidé la corbeille :
> dotcleaner les efface définitivement (ce qui libère de la place sur la carte).

## Installation

Ouvrez le **Terminal** (`Cmd + Espace`, tapez « Terminal », Entrée), puis collez :

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Linux/main/dotcleaner.sh -o dotcleaner.sh
chmod +x dotcleaner.sh
```

*Optionnel* — pour pouvoir taper simplement `dotcleaner` depuis n'importe quel dossier :

```sh
sudo mkdir -p /usr/local/bin
sudo install -m 755 dotcleaner.sh /usr/local/bin/dotcleaner
```

Ou téléchargez tout avec le bouton vert **Code** → **Download ZIP** sur la page GitHub.

## Utilisation

1. Branchez la carte SD sur le Mac.
2. Lancez `./dotcleaner.sh` (ou `dotcleaner` si vous l'avez installé).
3. Choisissez la carte dans la liste, vérifiez le résumé, confirmez avec `o`.

```text
$ ./dotcleaner.sh
dotcleaner 1.0.0
Quelle carte voulez-vous nettoyer ?
  1) /Volumes/EASYROMS
Numéro (Entrée pour annuler) : 1

/Volumes/EASYROMS
    1342  fichiers ._* (AppleDouble)
      37  .DS_Store
       3  éléments système macOS (.Spotlight-V100, .Trashes…)
  ------
  Total : 1382 éléments, 41,6 Mo
  Supprimer 1382 éléments ? [o/N] o
  Terminé : 1382 éléments supprimés (41,6 Mo libérés).
```

*(exemple de sortie ; les chiffres dépendent de votre carte)*

### Exemples

```sh
./dotcleaner.sh -n /Volumes/EASYROMS      # simulation : montre ce qui serait supprimé
./dotcleaner.sh /Volumes/SHARE            # nettoyer une carte précise
./dotcleaner.sh -y -e /Volumes/EASYROMS   # nettoyer puis éjecter, sans question
./dotcleaner.sh -w "/Volumes/NO NAME"     # supprimer aussi les fichiers Windows
./dotcleaner.sh /Volumes/BOOT /Volumes/EASYROMS   # plusieurs partitions d'un coup
```

Le nom de la carte est celui affiché dans la barre latérale du Finder (par exemple `EASYROMS` sur
une R36S sous ArkOS, `SHARE` sur Knulli ou Batocera). Mettez le chemin entre guillemets s'il contient
des espaces.

### Options

| Option | Effet |
| --- | --- |
| `-n`, `--dry-run` | Simulation : affiche ce qui serait supprimé, ne supprime rien |
| `-y`, `--yes` | Ne pas demander de confirmation |
| `-w`, `--windows` | Supprimer aussi `Thumbs.db`, `ehthumbs.db`, `desktop.ini` |
| `-e`, `--eject` | Éjecter la carte à la fin (macOS) |
| `-v`, `--verbose` | Afficher chaque élément supprimé |
| `-q`, `--quiet` | N'afficher que les erreurs |
| `-h`, `--help` | Aide |
| `-V`, `--version` | Version |

Les messages s'affichent en français si votre système est en français, sinon en anglais
(forcer avec `DOTCLEANER_LANG=fr` ou `DOTCLEANER_LANG=en`).

Codes de sortie : `0` = OK, `1` = erreur sur au moins une carte, `2` = mauvaise utilisation.

### Directement sur la console

Si le SSH est activé sur votre firmware, copiez `dotcleaner.sh` sur la console puis lancez
`sh dotcleaner.sh` : sans chemin, il propose les dossiers de ROM habituels
(`/roms`, `/userdata/roms`, `/storage/roms`, `/mnt/SDCARD`, `/mnt/mmc`…).
Le script est en `sh` POSIX pur et fonctionne avec BusyBox.

## Astuces macOS

- **Première utilisation :** macOS demande si le Terminal peut accéder aux fichiers d'un volume amovible → cliquez sur *Autoriser*.
- **Utilisez `-e`** pour éjecter juste après le nettoyage : tant que la carte reste branchée, macOS peut recréer
  `.fseventsd` ou `.Spotlight-V100` à la racine. Ces dossiers sont sans danger pour la console ; les fichiers
  `._` à côté des ROM, eux, ne reviennent que si vous copiez de nouveaux fichiers depuis le Mac.
- **Moins de `.DS_Store` sur les clés et cartes :**
  `defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true`, puis fermez la session.
  Ce réglage n'est pas documenté par Apple pour l'USB et son effet peut varier selon la version de macOS.
- macOS fournit la commande `dot_clean`, mais elle ne traite que les fichiers `._`.

## Tests

```sh
sh tests/run_tests.sh               # avec le sh par défaut
sh tests/run_tests.sh bash          # avec un autre shell
```

Les tests créent une fausse carte SD et vérifient ce qui est supprimé et, surtout, ce qui est conservé.
À chaque push, GitHub Actions lance ShellCheck et les tests sur Ubuntu, macOS et BusyBox (comme sur une console).

## Désinstallation

Supprimez `dotcleaner.sh` (et `/usr/local/bin/dotcleaner` si vous l'aviez installé :
`sudo rm /usr/local/bin/dotcleaner`). Le script n'installe rien d'autre.

## Licence

[MIT](LICENSE) — © 2026 Shadowix84
