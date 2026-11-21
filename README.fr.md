<div align="center">

# 🧹 dotcleaner

**Supprime les fichiers parasites que macOS laisse sur la carte SD de votre console d'émulation.**<br>
`._*` · `.DS_Store` · `.Spotlight-V100` · `.Trashes` · `.fseventsd` · `__MACOSX` …

[![CI](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/actions/workflows/ci.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Shadowix84/Dotcleaner-Linux-Handheld?label=version)](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/releases/latest)
[![POSIX sh](https://img.shields.io/badge/shell-POSIX%20sh-89e051)](dotcleaner.sh)
[![Licence : MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

🇬🇧 [English version](README.md)

<img src="docs/demo.svg" alt="dotcleaner nettoie une carte SD dans le Terminal" width="640">

</div>

## Pourquoi ?

Quand on copie des ROM sur une carte SD depuis un Mac, macOS ajoute en douce des fichiers cachés :
un jumeau `._` pour chaque fichier (`._Pokemon Emeraude.gba`), un `.DS_Store` dans chaque dossier
ouvert dans le Finder, et des dossiers `.Spotlight-V100`, `.Trashes` ou `.fseventsd` à la racine.

Sur la console, ils peuvent apparaître comme des **jeux fantômes qui ne se lancent pas**, perturber
le scraping et prendre de la place. **dotcleaner** les supprime en une commande — et **uniquement eux**.

## Points forts

- 🎯 **Précis** — supprime une liste fixe de fichiers macOS, jamais vos ROM, sauvegardes ou BIOS
- 👀 **Sûr** — affiche un résumé et demande confirmation ; `-n` montre tout sans rien toucher
- 🗑️ **Attentif à la corbeille** — prévient avant d'effacer les fichiers restés dans la corbeille de la carte (`-k` pour les garder)
- 💾 **Choix et éjection** — liste les cartes branchées, nettoie, puis éjecte (`-e`)
- 🖱️ **Lanceur double-clic** pour macOS — aucune commande à taper
- 🐧 **Partout** — macOS, Linux et sur la console elle-même (`sh` POSIX pur, compatible BusyBox)
- 🛡️ **Refuse les disques Mac** — un disque de sauvegarde choisi par erreur n'est jamais touché (APFS/HFS+)
- ✅ **Audité** — à chaque modification, des milliers de cartes sont vérifiées fichier par fichier sur macOS, Ubuntu et BusyBox, plus de vraies cartes exFAT/FAT32

Les messages sont en anglais ; ajoutez `--lang fr` pour les avoir en français.

## Démarrage rapide

### Option 1 — installer la commande (recommandé)

Ouvrez le **Terminal** (`Cmd + Espace`, tapez « Terminal », Entrée) et collez :

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Linux-Handheld/main/install.sh | sh
```

Branchez ensuite la carte SD et lancez :

```sh
dotcleaner --lang fr
```

Choisissez la carte dans la liste, vérifiez le résumé, confirmez avec `o`. C'est fini.

### Option 2 — double-clic (aucune commande)

1. Téléchargez le dernier `dotcleaner-x.y.z.zip` sur la [page Releases](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/releases/latest) et décompressez-le.
2. Branchez la carte SD.
3. Double-cliquez sur **`dotcleaner.command`** : le Terminal s'ouvre, vous choisissez la carte, confirmez, et elle est éjectée à la fin.

> Si macOS indique qu'il ne peut pas vérifier le développeur : ouvrez **Réglages Système → Confidentialité et sécurité**,
> descendez et cliquez sur **Ouvrir quand même** (sur un macOS plus ancien : clic droit sur le fichier → **Ouvrir**).
> Gardez `dotcleaner.command` à côté de `dotcleaner.sh`.

### Option 3 — sur la console

Si le SSH est activé sur votre firmware, copiez `dotcleaner.sh` sur la console et lancez `sh dotcleaner.sh`.
Sans chemin, il propose les dossiers de ROM habituels (voir le tableau plus bas).

## Utilisation

```text
dotcleaner [options] [CHEMIN...]
```

```sh
dotcleaner                          # choisir la carte dans une liste
dotcleaner -n /Volumes/EASYROMS     # simulation : montre ce qui serait supprimé
dotcleaner -y -e /Volumes/EASYROMS  # nettoyer puis éjecter, sans question
dotcleaner -w "/Volumes/NO NAME"    # supprimer aussi les fichiers Windows
dotcleaner /Volumes/BOOT /Volumes/EASYROMS   # plusieurs partitions d'un coup
```

| Option | Effet |
| --- | --- |
| `-n`, `--dry-run` | Simulation : affiche ce qui serait supprimé, ne supprime rien |
| `-y`, `--yes` | Ne pas demander de confirmation |
| `-w`, `--windows` | Supprimer aussi `Thumbs.db`, `ehthumbs.db`, `desktop.ini` |
| `-k`, `--keep-trash` | Ne pas toucher à la corbeille de la carte (`.Trashes`) |
| `--force` | Accepter aussi un disque Mac (APFS/HFS+), refusé par défaut |
| `-e`, `--eject` | Éjecter la carte à la fin (macOS) |
| `-v`, `--verbose` | Afficher chaque élément supprimé |
| `-q`, `--quiet` | N'afficher que les erreurs |
| `--lang fr` | Messages en français (par défaut : anglais) — ou `DOTCLEANER_LANG=fr` |
| `-h`, `--help` / `-V`, `--version` | Aide / version |

Codes de sortie : `0` OK · `1` erreur sur au moins une carte · `2` mauvaise utilisation · `130` interrompu (Ctrl-C).

### Où est ma carte ?

Le nom est celui affiché dans la barre latérale du Finder. Noms habituels :

| Firmware (exemples) | Nom sur le Mac | Chemin sur la console |
| --- | --- | --- |
| ArkOS (R36S, RG351…) | `EASYROMS` | `/roms` |
| Knulli, Batocera (Anbernic RG40XX…) | `SHARE` | `/userdata/roms` |
| ROCKNIX | dépend de la carte | `/storage/roms` |
| Onion (Miyoo Mini) | dépend de la carte | `/mnt/SDCARD` |
| muOS | dépend de la carte | `/mnt/mmc` |

Mettez le chemin entre guillemets s'il contient des espaces : `"/Volumes/NO NAME"`.

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

**Jamais touché :** vos ROM, sauvegardes, BIOS, et tout autre fichier, caché ou non (`.keep`, fichiers de config…).
Les liens symboliques ne sont pas suivis et le script ne sort jamais de la carte. Il refuse de
s'exécuter sur les dossiers système, sur votre dossier personnel et sur les disques Mac (APFS/HFS+),
où ces dossiers contiennent de vraies données.

## FAQ

<details>
<summary><b>Peut-il supprimer mes jeux ou mes sauvegardes ?</b></summary>

Non. Il ne supprime que les noms exacts listés ci-dessus. Un fichier comme `Jeu._beta.gba` ou une
sauvegarde cachée comme `.jeu.srm` est conservé. Lancez d'abord avec `-n` pour voir la liste complète.

C'est vérifié à chaque modification par un audit ([`tests/audit.py`](tests/audit.py)) : des cartes
réalistes (ArkOS, Knulli, PortMaster…) et des centaines de cartes aléatoires remplies de noms piégés
sont scannées chemin par chemin avant et après nettoyage, puis comparées à un arbitre indépendant.
Un seul fichier supprimé à tort, ou un seul parasite oublié, et l'audit échoue.
</details>

<details>
<summary><b>Les fichiers <code>._</code> sont revenus. Pourquoi ?</b></summary>

macOS les crée à chaque copie de fichiers du Mac vers la carte. Lancez dotcleaner après chaque
séance de copie — avec `-e`, la carte est éjectée tout de suite, sans laisser à macOS le temps d'en rajouter.
</details>

<details>
<summary><b>Et la corbeille de la carte ?</b></summary>

Les fichiers supprimés dans le Finder sur la carte vont dans son dossier caché `.Trashes` et prennent
toujours de la place. dotcleaner vous prévient et les efface définitivement. `-k` pour les garder.
</details>

<details>
<summary><b>J'utilise Windows ou Linux, pas un Mac.</b></summary>

Sous Linux, tout fonctionne pareil (les cartes dans `/media/...` sont proposées automatiquement). Avec `-w`,
il supprime aussi `Thumbs.db` et `desktop.ini` de Windows. Sous Windows, lancez-le sur la console en SSH ou dans WSL.
</details>

<details>
<summary><b>macOS n'a pas déjà un outil pour ça ?</b></summary>

macOS a `dot_clean`, mais il ne traite que les fichiers `._` — pas `.DS_Store`, ni Spotlight, ni la corbeille.
</details>

## Astuces macOS

- **Première utilisation :** macOS demande si le Terminal peut accéder aux fichiers d'un volume amovible → cliquez sur *Autoriser*.
- **Moins de `.DS_Store` sur les clés et cartes :**
  `defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true`, puis fermez la session.
  Ce réglage n'est pas documenté par Apple pour l'USB et son effet peut varier selon la version de macOS.

## Désinstallation

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Linux-Handheld/main/install.sh | sh -s -- --uninstall
```

## Contribuer

Signalements de bugs et idées sont les bienvenus dans les [issues](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/issues).
Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour lancer les tests avant de proposer une modification.

## Licence

[MIT](LICENSE) — © 2026 Shadowix84
