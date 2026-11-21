<div align="center">

# 🧹 Dotcleaner

**Remove the junk files macOS leaves on SD cards and USB drives — made for emulation handhelds.**<br>
`._*` · `.DS_Store` · `.Spotlight-V100` · `.Trashes` · `.fseventsd` · `__MACOSX` …

[![Download for macOS](https://img.shields.io/badge/Download-macOS-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-macOS.dmg)
[![Download for Windows](https://img.shields.io/badge/Download-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Windows.exe)
[![Shell version](https://img.shields.io/badge/Shell-macOS%20·%20Linux%20·%20consoles-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)](#%EF%B8%8F-the-shell-version-macos-linux-consoles)

[![Release](https://img.shields.io/github/v/release/Shadowix84/Dotcleaner-Multi-Software?label=release)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Shadowix84/Dotcleaner-Multi-Software/total?label=downloads)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases)
[![CI](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/ci.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/ci.yml)
[![Apps](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/apps.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/apps.yml)
[![Languages](https://img.shields.io/badge/languages-EN%20·%20FR%20·%20ES%20·%20中文%20·%20हिन्दी-8A2BE2)](#️-the-app-macos--windows)
[![Discord](https://img.shields.io/badge/Discord-join-5865F2?logo=discord&logoColor=white)](https://discord.gg/4FbhkuhRMm)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🌐 [Website](https://shadowix84.github.io/Dotcleaner-Multi-Software/) · 🇫🇷 [Version française](README.fr.md)

<img src="docs/app-en.png" alt="Dotcleaner app" width="560">

</div>

**Contents:** [Why?](#why) · [Two versions](#two-versions-same-menu) · [The app](#️-the-app-macos--windows) ·
[The shell](#️-the-shell-version-macos-linux-consoles) · [On the console](#-on-the-console-itself) ·
[Compatibility](#compatibility) · [What it removes](#what-it-removes) ·
[FAQ](#faq) · [Building and testing](#building-and-testing) · [Community](#community)

## Why?

When you copy ROMs to an SD card or USB drive from a Mac, macOS quietly adds hidden files:
a `._` twin for every file (`._Pokemon Emerald.gba`), a `.DS_Store` in every folder you open
in Finder, and `.Spotlight-V100`, `.Trashes` or `.fseventsd` folders at the root.

On the console they can show up as **ghost games that won't launch**, confuse scrapers and
waste space. **Dotcleaner** removes them — and **only them**.

## Two versions, same menu

| | 🖥️ **App** — `.dmg` / `.exe` | ⌨️ **Shell** — `dotcleaner.sh` |
| --- | --- | --- |
| Runs on | macOS (Intel & Apple Silicon), Windows, Linux (x86_64 & ARM) | macOS, Linux, WSL, the console itself |
| Drives | any SD card or USB drive | any SD card or USB drive, or a folder |
| Languages | English, Français, Español, 中文, हिन्दी | English |
| Menu | **1.** Choose a drive · **2.** Options · **3.** Scan · **4.** Clean · Help · Quit | same |

Both use exactly the same cleaning rules, checked by the same audit.

## 🖥️ The app (macOS & Windows)

1. Download the latest version:
   - **macOS** 13+ (Intel & Apple Silicon): [**Dotcleaner-macOS.dmg**](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-macOS.dmg) → open it, drag **Dotcleaner** to **Applications**.
   - **Windows** 10 / 11: [**Dotcleaner-Windows.exe**](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Windows.exe) → double-click it (nothing to install).
   - **Linux**: [x86_64](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Linux-x86_64) (Steam Deck, PC) or [ARM64](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Linux-arm64) (Raspberry Pi) → `chmod +x` it, then run it.
2. Plug in your SD card or USB drive and open Dotcleaner.
3. **1.** Choose the drive · **2.** tick the options · **3.** Scan to preview · **4.** Clean.

Pick your language in the top-right menu:

<img src="docs/app-languages.png" alt="Dotcleaner in English, French, Spanish, Chinese and Hindi" width="900">

> **First launch.** The app is free and not signed with a paid Apple / Microsoft certificate, so the
> system warns you once:
> - **macOS:** open **System Settings → Privacy & Security**, scroll down and click **Open Anyway**.
>   Then allow Dotcleaner to access *removable volumes* when asked.
> - **Windows:** on the blue *Windows protected your PC* screen, click **More info → Run anyway**.

## ⌨️ The shell version (macOS, Linux, consoles)

Install the `dotcleaner` command — open **Terminal** and paste:

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Multi-Software/main/install.sh | sh
```

Then run `dotcleaner` to open the menu:

<img src="docs/demo.svg" alt="dotcleaner menu in Terminal" width="640">

No Terminal? Download the release zip and double-click **`dotcleaner.command`** (macOS).
On the console itself, see [On the console itself](#-on-the-console-itself) below.

### Command-line options

For scripts, give one or more paths instead of using the menu:

```sh
dotcleaner -n /Volumes/EASYROMS      # preview: show what would be deleted
dotcleaner -y -e /Volumes/EASYROMS   # clean then eject, no questions
dotcleaner -w "/Volumes/NO NAME"     # also remove Windows files
```

| Option | Effect |
| --- | --- |
| `-n`, `--dry-run` | Preview: show what would be deleted, delete nothing |
| `-y`, `--yes` | Do not ask for confirmation |
| `-w`, `--windows` | Also remove `Thumbs.db`, `ehthumbs.db`, `desktop.ini` |
| `-k`, `--keep-trash` | Leave the drive's Trash (`.Trashes`) untouched |
| `-e`, `--eject` | Eject the drive when done (macOS) |
| `-v`, `--verbose` | List every deleted item |
| `-q`, `--quiet` | Only print errors |
| `-h`, `--help` / `-V`, `--version` | Help / version |

Exit codes: `0` OK · `1` error on at least one drive · `2` wrong usage · `130` interrupted.

## 🎮 On the console itself

Clean the card **without a computer**, from the console's own menu: no keyboard, no terminal.
Download [**Dotcleaner-console.zip**](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-console.zip) and copy the launcher to the card:

| Firmware (examples of consoles) | Copy | Then on the console |
| --- | --- | --- |
| **ArkOS**, dArkOS (R36S, RG351, RG353…) | `Dotcleaner.sh` → `EASYROMS/ports/` | **Ports → Dotcleaner** — the result shows on screen |
| **Knulli**, Batocera (Anbernic RG40XX, RG35XX…) | `Dotcleaner.sh` → `SHARE/roms/ports/` | Update the game lists, then **Ports → Dotcleaner** — a notification shows the result |
| **ROCKNIX**, AmberELEC, JELOS, EmuELEC | `Dotcleaner.sh` → `roms/ports/` | **Ports → Dotcleaner** |
| **Onion** (Miyoo Mini) | folder `Onion/App/Dotcleaner` → `App/` | **Apps → Dotcleaner** |
| muOS, MinUI, others | `dotcleaner.sh` anywhere | over SSH: `sh dotcleaner.sh --console` |

Create the `ports` folder if it does not exist. The launcher finds the ROM card by itself, cleans it
without asking, and writes **`dotcleaner.log`** next to itself — send this file with any bug report.

**What you see.** On ArkOS-like firmwares (and over SSH) a full-screen view follows each step — card
found, scan, cleaning with a progress bar, result — then goes back to the menu after 8 seconds.
On Knulli / Batocera a notification appears at each step; on Onion, a message box.

<p align="center">
  <img src="docs/console-cleaning.svg" alt="Console screen while cleaning, with a progress bar" width="440">
  <img src="docs/console-done.svg" alt="Console screen when done" width="440">
</p>

It even removes the `._Dotcleaner.sh` ghost that macOS creates when you copy the launcher.

## Compatibility

| System | App | Shell |
| --- | --- | --- |
| macOS 13 or newer, Intel and Apple Silicon | ✅ `.dmg` | ✅ |
| macOS 12 or older | — | ✅ |
| Windows 10 / 11 (x64, and ARM through emulation) | ✅ `.exe` | ✅ in WSL |
| Linux x86_64 with glibc 2.35+ (Steam Deck, Ubuntu 22.04+, Debian 12+, Fedora…) | ✅ `Dotcleaner-Linux-x86_64` | ✅ |
| Linux ARM64 with glibc 2.39+ (Raspberry Pi OS 13+, Ubuntu 24.04+…) | ✅ `Dotcleaner-Linux-arm64` | ✅ |
| ChromeOS (Linux), WSL | — | ✅ |
| Consoles: ArkOS, dArkOS, Knulli, Batocera, ROCKNIX, AmberELEC, JELOS, EmuELEC, Onion, muOS, MinUI, Allium, spruceOS, TrimUI, RetroPie | — | ✅ launcher or SSH |

The shell version is pure POSIX `sh` and pure ASCII. It is tested at every change with **bash, dash,
BusyBox ash (recent and old `find`), ksh, mksh, posh, yash and zsh**, on Ubuntu and macOS.
On Linux, the Linux app needs the usual desktop libraries; if it does not start, install `libxcb-cursor0`.

## What it removes

| Item | Where it comes from |
| --- | --- |
| `._*` | AppleDouble files: macOS metadata of every copied file |
| `.DS_Store` | Finder folder view settings |
| `.Spotlight-V100` | Spotlight index of the drive |
| `.Trashes` | The drive's Trash (files deleted in Finder without emptying the Trash) |
| `.fseventsd` | File system event log |
| `.TemporaryItems`, `.DocumentRevisions-V100` | Temporary files and document versions |
| `.apdisk`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop` | Disk and network share metadata |
| `__MACOSX` | Leftovers from zip archives made on a Mac |
| `Thumbs.db`, `ehthumbs.db`, `desktop.ini` | Windows — **only with the Windows option** |

**Never touched:** your ROMs, saves, BIOS, photos, documents and every other file, hidden or not.
Links are never followed and other drives are never entered. System and home folders are refused.

🛡️ **Safe mode on Mac-formatted drives (APFS, HFS+).** There, the macOS system folders hold real
data (document versions, the Trash…), so only the junk files (`._*`, `.DS_Store`, `.apdisk`,
`__MACOSX`) are removed. Consoles use FAT32/exFAT cards, which are cleaned completely.

### Where is my card?

| Firmware (examples) | Name on the computer | Path on the console |
| --- | --- | --- |
| ArkOS (R36S, RG351…) | `EASYROMS` | `/roms` |
| Knulli, Batocera (Anbernic RG40XX…) | `SHARE` | `/userdata/roms` |
| ROCKNIX | depends on the card | `/storage/roms` |
| Onion (Miyoo Mini) | depends on the card | `/mnt/SDCARD` |
| muOS | depends on the card | `/mnt/mmc` |

## FAQ

<details>
<summary><b>Can it delete my games or saves?</b></summary>

No. It only deletes the exact names listed above. A file like `Game._beta.gba` or a hidden save
like `.game.srm` is kept. Scan first to see the full list before anything is deleted.

This is checked at every change by an audit ([`tests/audit.py`](tests/audit.py)): realistic cards
(ArkOS, Knulli, PortMaster…) and hundreds of random cards full of tricky names are scanned path by
path before and after cleaning — with **both** the app and the shell — and compared with an
independent referee. One file deleted by mistake, or one junk file left behind, and the audit fails.
</details>

<details>
<summary><b>The <code>._</code> files came back. Why?</b></summary>

macOS creates them every time you copy files from the Mac to the drive. Clean after each copy
session, with **Eject when done** ticked: the drive is ejected right away.
</details>

<details>
<summary><b>What about the drive's Trash?</b></summary>

Files you delete in Finder on the drive go to its hidden `.Trashes` folder and still take space.
Dotcleaner warns you and erases them for good. Tick **Keep the drive's Trash** (`-k`) to keep them.
</details>

<details>
<summary><b>Nothing happens when I start it on my console.</b></summary>

Use the **launcher** (`Dotcleaner.sh` from `Dotcleaner-console.zip`), not `dotcleaner.sh`: launched from
a console menu there is no keyboard, and the plain script waits for one. Check that it is in the `ports`
folder (or `App/` on Onion), then open **`dotcleaner.log`** next to it: it says what was found and cleaned.
If it still fails, open a bug report with this file.
</details>

## Building and testing

Everything is built and tested by GitHub Actions on every change:

- [`ci.yml`](.github/workflows/ci.yml) — ShellCheck, shell tests and deletion audit on Ubuntu, macOS and
  BusyBox, real exFAT/FAT32 cards mounted on macOS.
- [`apps.yml`](.github/workflows/apps.yml) — app engine audit and app tests on macOS, Windows and Linux,
  then builds and launches the `.dmg` and the `.exe`.
- [`release.yml`](.github/workflows/release.yml) — **Actions → Release → Run workflow** publishes the
  release with the `.dmg`, the `.exe`, the zip and the script.

See [CONTRIBUTING.md](CONTRIBUTING.md) to run the tests yourself.

Every release lists the SHA-256 of its files in `SHA256SUMS.txt` — see [SECURITY.md](SECURITY.md).

## Community

- 💬 Chat with other users on [Discord](https://discord.gg/4FbhkuhRMm)
- 🐞 [Report a bug](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=bug_report.yml) ·
  💡 [Suggest an idea](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=feature_request.yml) ·
  🌍 [Improve a translation](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=translation.yml)
- 🤝 [Contributing](CONTRIBUTING.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Support](SUPPORT.md) · [Security](SECURITY.md)
- ⭐ If Dotcleaner saved your card, a star on GitHub helps other players find it!

## License

[MIT](LICENSE) — © 2026 Shadowix84
