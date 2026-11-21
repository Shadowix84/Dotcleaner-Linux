<div align="center">

# 🧹 Dotcleaner

**Supprime les fichiers parasites que macOS laisse sur les cartes SD et clés USB — pensé pour les consoles d'émulation.**<br>
`._*` · `.DS_Store` · `.Spotlight-V100` · `.Trashes` · `.fseventsd` · `__MACOSX` …

[![Télécharger pour macOS](https://img.shields.io/badge/Télécharger-macOS-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-macOS.dmg)
[![Télécharger pour Windows](https://img.shields.io/badge/Télécharger-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Windows.exe)
[![Version shell](https://img.shields.io/badge/Shell-macOS%20·%20Linux%20·%20consoles-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)](#️-la-version-shell-macos-linux-consoles)

[![Version](https://img.shields.io/github/v/release/Shadowix84/Dotcleaner-Multi-Software?label=version)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest)
[![Téléchargements](https://img.shields.io/github/downloads/Shadowix84/Dotcleaner-Multi-Software/total?label=t%C3%A9l%C3%A9chargements)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases)
[![CI](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/ci.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/ci.yml)
[![Apps](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/apps.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/apps.yml)
[![Langues](https://img.shields.io/badge/langues-EN%20·%20FR%20·%20ES%20·%20中文%20·%20हिन्दी-8A2BE2)](#️-lapplication-macos-et-windows)
[![Discord](https://img.shields.io/badge/Discord-rejoindre-5865F2?logo=discord&logoColor=white)](https://discord.gg/4FbhkuhRMm)
[![Licence : MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

🌐 [Site web](https://shadowix84.github.io/Dotcleaner-Multi-Software/) · 🇬🇧 [English version](README.md)

<img src="docs/app-fr.png" alt="Application Dotcleaner" width="560">

</div>

**Sommaire :** [Pourquoi ?](#pourquoi-) · [Deux versions](#deux-versions-le-même-menu) · [L'application](#️-lapplication-macos-et-windows) ·
[Le shell](#️-la-version-shell-macos-linux-consoles) · [Ce qui est supprimé](#ce-qui-est-supprimé) ·
[FAQ](#faq) · [Fabrication et tests](#fabrication-et-tests) · [Communauté](#communauté)

## Pourquoi ?

Quand on copie des ROM sur une carte SD ou une clé USB depuis un Mac, macOS ajoute en douce des fichiers cachés :
un jumeau `._` pour chaque fichier (`._Pokemon Emeraude.gba`), un `.DS_Store` dans chaque dossier
ouvert dans le Finder, et des dossiers `.Spotlight-V100`, `.Trashes` ou `.fseventsd` à la racine.

Sur la console, ils peuvent apparaître comme des **jeux fantômes qui ne se lancent pas**, perturber
le scraping et prendre de la place. **Dotcleaner** les supprime — et **uniquement eux**.

## Deux versions, le même menu

| | 🖥️ **Application** — `.dmg` / `.exe` | ⌨️ **Shell** — `dotcleaner.sh` |
| --- | --- | --- |
| Fonctionne sur | macOS, Windows | macOS, Linux, la console elle-même (BusyBox) |
| Lecteurs | toute carte SD ou clé USB | toute carte SD ou clé USB, ou un dossier |
| Langues | English, Français, Español, 中文, हिन्दी | anglais |
| Menu | **1.** Choisir un lecteur · **2.** Options · **3.** Analyser · **4.** Nettoyer · Aide · Quitter | identique (en anglais) |

Les deux appliquent exactement les mêmes règles de nettoyage, vérifiées par le même audit.

## 🖥️ L'application (macOS et Windows)

1. Téléchargez la dernière version :
   - **macOS** (Apple Silicon) : [**Dotcleaner-macOS.dmg**](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-macOS.dmg) → ouvrez-le, glissez **Dotcleaner** dans **Applications**.
   - **Windows** 10 / 11 : [**Dotcleaner-Windows.exe**](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Windows.exe) → double-cliquez dessus (rien à installer).
2. Branchez la carte SD ou la clé USB et ouvrez Dotcleaner.
3. **1.** Choisissez le lecteur · **2.** cochez les options · **3.** Analysez pour voir · **4.** Nettoyez.

Choisissez la langue dans le menu en haut à droite :

<img src="docs/app-languages.png" alt="Dotcleaner en anglais, français, espagnol, chinois et hindi" width="900">

> **Premier lancement.** L'application est gratuite et n'est pas signée avec un certificat payant
> d'Apple ou de Microsoft : le système prévient donc une fois.
> - **macOS :** ouvrez **Réglages Système → Confidentialité et sécurité**, descendez et cliquez sur
>   **Ouvrir quand même**. Autorisez ensuite Dotcleaner à accéder aux *volumes amovibles*.
> - **Windows :** sur l'écran bleu *Windows a protégé votre ordinateur*, cliquez sur
>   **Informations complémentaires → Exécuter quand même**.

## ⌨️ La version shell (macOS, Linux, consoles)

Installez la commande `dotcleaner` — ouvrez le **Terminal** et collez :

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Multi-Software/main/install.sh | sh
```

Puis lancez `dotcleaner` pour ouvrir le menu (en anglais) :

<img src="docs/demo.svg" alt="Menu de dotcleaner dans le Terminal" width="640">

Pas de Terminal ? Téléchargez le zip de la version et double-cliquez sur **`dotcleaner.command`** (macOS).
Sur la console (SSH activé), copiez `dotcleaner.sh` et lancez `sh dotcleaner.sh`.

### Options en ligne de commande

Pour les scripts, indiquez un ou plusieurs chemins au lieu d'utiliser le menu :

```sh
dotcleaner -n /Volumes/EASYROMS      # aperçu : montre ce qui serait supprimé
dotcleaner -y -e /Volumes/EASYROMS   # nettoyer puis éjecter, sans question
dotcleaner -w "/Volumes/NO NAME"     # supprimer aussi les fichiers Windows
```

| Option | Effet |
| --- | --- |
| `-n`, `--dry-run` | Aperçu : affiche ce qui serait supprimé, ne supprime rien |
| `-y`, `--yes` | Ne pas demander de confirmation |
| `-w`, `--windows` | Supprimer aussi `Thumbs.db`, `ehthumbs.db`, `desktop.ini` |
| `-k`, `--keep-trash` | Ne pas toucher à la corbeille du lecteur (`.Trashes`) |
| `-e`, `--eject` | Éjecter le lecteur à la fin (macOS) |
| `-v`, `--verbose` | Afficher chaque élément supprimé |
| `-q`, `--quiet` | N'afficher que les erreurs |
| `-h`, `--help` / `-V`, `--version` | Aide / version |

Codes de sortie : `0` OK · `1` erreur sur au moins un lecteur · `2` mauvaise utilisation · `130` interrompu.

## Ce qui est supprimé

| Élément | D'où ça vient |
| --- | --- |
| `._*` | Fichiers AppleDouble : les métadonnées macOS de chaque fichier copié |
| `.DS_Store` | Réglages d'affichage des dossiers du Finder |
| `.Spotlight-V100` | Index Spotlight du lecteur |
| `.Trashes` | Corbeille du lecteur (fichiers supprimés dans le Finder sans vider la corbeille) |
| `.fseventsd` | Journal des modifications du système de fichiers |
| `.TemporaryItems`, `.DocumentRevisions-V100` | Fichiers temporaires et versions de documents |
| `.apdisk`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop` | Métadonnées de disque et de partages réseau |
| `__MACOSX` | Restes d'archives zip créées sur Mac |
| `Thumbs.db`, `ehthumbs.db`, `desktop.ini` | Windows — **seulement avec l'option Windows** |

**Jamais touché :** vos ROM, sauvegardes, BIOS, photos, documents et tout autre fichier, caché ou non.
Les liens ne sont jamais suivis et les autres lecteurs jamais parcourus. Les dossiers système et personnels sont refusés.

🛡️ **Mode sûr sur les disques au format Mac (APFS, HFS+).** Là, les dossiers système de macOS
contiennent de vraies données (versions de documents, corbeille…) : seuls les fichiers parasites
(`._*`, `.DS_Store`, `.apdisk`, `__MACOSX`) sont supprimés. Les consoles utilisent des cartes
FAT32/exFAT, qui sont nettoyées entièrement.

### Où est ma carte ?

| Firmware (exemples) | Nom sur l'ordinateur | Chemin sur la console |
| --- | --- | --- |
| ArkOS (R36S, RG351…) | `EASYROMS` | `/roms` |
| Knulli, Batocera (Anbernic RG40XX…) | `SHARE` | `/userdata/roms` |
| ROCKNIX | dépend de la carte | `/storage/roms` |
| Onion (Miyoo Mini) | dépend de la carte | `/mnt/SDCARD` |
| muOS | dépend de la carte | `/mnt/mmc` |

## FAQ

<details>
<summary><b>Peut-il supprimer mes jeux ou mes sauvegardes ?</b></summary>

Non. Il ne supprime que les noms exacts listés ci-dessus. Un fichier comme `Jeu._beta.gba` ou une
sauvegarde cachée comme `.jeu.srm` est conservé. Analysez d'abord pour voir la liste complète.

C'est vérifié à chaque modification par un audit ([`tests/audit.py`](tests/audit.py)) : des cartes
réalistes (ArkOS, Knulli, PortMaster…) et des centaines de cartes aléatoires remplies de noms piégés
sont scannées chemin par chemin avant et après nettoyage — avec l'application **et** le shell — puis
comparées à un arbitre indépendant. Un seul fichier supprimé à tort, ou un seul parasite oublié, et l'audit échoue.
</details>

<details>
<summary><b>Les fichiers <code>._</code> sont revenus. Pourquoi ?</b></summary>

macOS les crée à chaque copie de fichiers du Mac vers le lecteur. Nettoyez après chaque séance de
copie, avec **Éjecter à la fin** coché : le lecteur est éjecté tout de suite.
</details>

<details>
<summary><b>Et la corbeille du lecteur ?</b></summary>

Les fichiers supprimés dans le Finder sur le lecteur vont dans son dossier caché `.Trashes` et prennent
toujours de la place. Dotcleaner vous prévient et les efface définitivement. Cochez **Garder la
corbeille du lecteur** (`-k`) pour les conserver.
</details>

<details>
<summary><b>Existe-t-il une application pour Mac Intel ou Linux ?</b></summary>

Le `.dmg` est fait pour les Mac Apple Silicon. Sur Mac Intel et sous Linux, utilisez la version shell —
ou lancez l'application depuis les sources : `pip install PySide6-Essentials && python3 app/dotcleaner_gui.py`.
</details>

## Fabrication et tests

Tout est fabriqué et testé par GitHub Actions à chaque modification :

- [`ci.yml`](.github/workflows/ci.yml) — ShellCheck, tests et audit du shell sur Ubuntu, macOS et
  BusyBox, vraies cartes exFAT/FAT32 montées sur macOS.
- [`apps.yml`](.github/workflows/apps.yml) — audit du moteur et tests de l'application sur macOS,
  Windows et Linux, puis fabrication et lancement du `.dmg` et du `.exe`.
- [`release.yml`](.github/workflows/release.yml) — **Actions → Release → Run workflow** publie la
  version avec le `.dmg`, le `.exe`, le zip et le script.

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour lancer les tests vous-même.

Chaque version liste l'empreinte SHA-256 de ses fichiers dans `SHA256SUMS.txt` — voir [SECURITY.md](SECURITY.md).

## Communauté

- 💬 Discutez avec les autres joueurs sur [Discord](https://discord.gg/4FbhkuhRMm)
- 🐞 [Signaler un bug](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=bug_report.yml) ·
  💡 [Proposer une idée](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=feature_request.yml) ·
  🌍 [Améliorer une traduction](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=translation.yml)
- 🤝 [Contribuer](CONTRIBUTING.md) · [Code de conduite](CODE_OF_CONDUCT.md) · [Aide](SUPPORT.md) · [Sécurité](SECURITY.md)
- ⭐ Si Dotcleaner a sauvé votre carte, une étoile sur GitHub aide d'autres joueurs à le trouver !

## Licence

[MIT](LICENSE) — © 2026 Shadowix84
