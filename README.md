<div align="center">

# 🧹 Dotcleaner

**Remove the hidden junk files macOS leaves on SD cards and USB drives — made for emulation handhelds.**<br>
No more ghost games. Your games, saves and BIOS are never touched.

[![Download for macOS](https://img.shields.io/badge/macOS-Download-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-macOS.dmg)
[![Download for Windows](https://img.shields.io/badge/Windows-Download-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Windows.exe)
[![Download for Linux](https://img.shields.io/badge/Linux-Download-E95420?style=for-the-badge&logo=linux&logoColor=white)](#️-the-app-macos-windows-linux)
[![Download for consoles](https://img.shields.io/badge/Consoles-Download-4EAA25?style=for-the-badge&logo=retroarch&logoColor=white)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-console.zip)

[![Release](https://img.shields.io/github/v/release/Shadowix84/Dotcleaner-Multi-Software?label=version)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Shadowix84/Dotcleaner-Multi-Software/total?label=downloads)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases)
[![Tests](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/ci.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Multi-Software/actions/workflows/ci.yml)
[![Discord (French)](https://img.shields.io/badge/Discord-French%20community-5865F2?logo=discord&logoColor=white)](https://discord.gg/4FbhkuhRMm)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🌐 [Website](https://shadowix84.github.io/Dotcleaner-Multi-Software/) · 🇫🇷 [Version française](README.fr.md)

<img src="docs/app-en.png" alt="The Dotcleaner app after scanning a card" width="520">

</div>

**Contents** — [Why?](#why) · [Which version?](#which-version-do-i-need) · [App](#️-the-app-macos-windows-linux) ·
[On the console](#-on-the-console-itself) · [Shell](#️-the-shell-version-terminal) ·
[What it removes](#what-it-removes) · [Compatibility](#compatibility) · [FAQ](#faq) ·
[Roadmap](#️-roadmap) · [Community](#community)

## Why?

When a Mac copies files to an SD card, it adds hidden files next to them: a `._` twin for every file,
a `.DS_Store` in every folder opened in Finder, and folders like `.Spotlight-V100` or `.Trashes`.
Your console lists the `._` twins as **games that won't launch**:

```text
Before                                  After Dotcleaner
roms/gba/                               roms/gba/
├── ._Pokemon Emerald.gba   ← ghost     └── Pokemon Emerald.gba
└── Pokemon Emerald.gba
```

Dotcleaner finds these files and removes them — **only them**.

## Which version do I need?

| You want to… | Use | Languages |
| --- | --- | --- |
| Clean the card **on your Mac or PC** (easiest) | 🖥️ [The app](#️-the-app-macos-windows-linux) | English, Français, Español, 中文, हिन्दी |
| Clean the card **on the console**, without a computer | 🎮 [The console launcher](#-on-the-console-itself) | English (simple screen) |
| Use the **terminal** or scripts | ⌨️ [The shell version](#️-the-shell-version-terminal) | English |

All three use the same cleaning rules and the same four steps:
**1.** Choose a drive · **2.** Options · **3.** Scan (preview, deletes nothing) · **4.** Clean.

## 🖥️ The app (macOS, Windows, Linux)

1. **Download** the version for your computer:

   | System | File | Then |
   | --- | --- | --- |
   | **macOS** 13+ (Intel & Apple Silicon) | [Dotcleaner-macOS.dmg](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-macOS.dmg) | Open it, drag **Dotcleaner** to **Applications** |
   | **Windows** 10 / 11 | [Dotcleaner-Windows.exe](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Windows.exe) | Double-click it (nothing to install) |
   | **Linux** PC, Steam Deck | [Dotcleaner-Linux-x86_64](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Linux-x86_64) | `chmod +x` it, then run it |
   | **Linux** Raspberry Pi (64-bit) | [Dotcleaner-Linux-arm64](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-Linux-arm64) | `chmod +x` it, then run it |

2. **Plug in** your SD card or USB drive and open Dotcleaner.
3. **Choose** the drive → **Scan** to see what would be deleted → **Clean**.
   With **Eject when done** ticked, you can unplug the card right away.

> [!NOTE]
> **First launch.** The app is free and not signed with a paid Apple / Microsoft certificate, so your
> computer warns you once:
> - **macOS:** **System Settings → Privacy & Security**, scroll down, click **Open Anyway**.
>   Then allow access to *removable volumes* when asked.
> - **Windows:** on the blue *Windows protected your PC* screen, click **More info → Run anyway**.

Choose your language in the top-right menu:

<img src="docs/app-languages.png" alt="Dotcleaner in English, French, Spanish, Chinese and Hindi" width="900">

## 🎮 On the console itself

Clean the card **without a computer**, from the console's menu — no keyboard needed.

1. Download [**Dotcleaner-console.zip**](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-console.zip) and unzip it. Inside: `Dotcleaner.sh`
   (the launcher), `Onion/` (the Onion app), `menu-logo/` (optional logo) and a `README.txt`.
2. Copy the launcher to the card (create the folder if it does not exist):

   | Firmware (consoles) | Copy | Card name on a computer |
   | --- | --- | --- |
   | **ArkOS**, dArkOS (R36S, RG351, RG353…) | `Dotcleaner.sh` → `ports/` | `EASYROMS` |
   | **Knulli** (RG40XXV, RG35XX…) | `Dotcleaner.sh` → `roms/tools/` | `SHARE` |
   | **Batocera** | `Dotcleaner.sh` → `roms/ports/` | `SHARE` |
   | **ROCKNIX**, AmberELEC, JELOS, EmuELEC | `Dotcleaner.sh` → `roms/ports/` | depends on the card |
   | **Onion** (Miyoo Mini) | the `Onion/App/Dotcleaner` folder → `App/` | depends on the card |
   | muOS, MinUI, spruceOS, others | `dotcleaner.sh` anywhere, then over SSH: `sh dotcleaner.sh --console` | depends on the card |

3. On the console, open **Ports → Dotcleaner** — **Tools → Dotcleaner** on Knulli, **Apps → Dotcleaner**
   on Onion. On Knulli / Batocera, update the game lists first so it appears.

The launcher finds the ROM card by itself and cleans it without asking.

**What you see depends on the firmware:**

- **ArkOS and similar** (dArkOS, ROCKNIX, AmberELEC, JELOS…): a **very simple text screen** shows each
  step, then the console goes back to the menu after 6 seconds.
- **Knulli: no screen** — that is normal. The cleaning takes a few seconds, then you are back in the
  menu. Check the result in `dotcleaner.log`.
- **Onion:** a message box at each step.

<p align="center">
  <img src="docs/console-cleaning.svg" alt="Console screen while cleaning, with a progress bar" width="400">
  <img src="docs/console-done.svg" alt="Console screen when done" width="400">
</p>

Everywhere, a **`dotcleaner.log`** file is written next to the launcher (on Knulli: `roms/tools/` on
the `SHARE` card): it lists what was found and deleted — send it with any bug report. If ghost games
are still listed afterwards, update the game lists.

<details>
<summary><b>Optional: Dotcleaner's logo in the console menu</b></summary>

<p align="center"><img src="docs/console-menu-logo.png" alt="The Dotcleaner logo in the ArkOS and Knulli menus" width="760"></p>

The `menu-logo/` folder of the zip holds the logo (transparent background) and a `gamelist.xml`,
the file the menu reads to show pictures. With the card in your computer:

1. Copy the `images` folder of `menu-logo/` next to `Dotcleaner.sh` (`ports/`, or `roms/tools/` on Knulli).
2. **No `gamelist.xml` there yet?** Copy `menu-logo/gamelist.xml` too.
   **There is one already** (PortMaster creates one)? **Do not replace it**: open it and paste the
   `<game>…</game>` block of `menu-logo/gamelist.xml` just before the last line `</gameList>`.

Do it with the card in your computer, not on the running console: the menu rewrites this file.
Onion does not need it: the Onion app has its own icon.
</details>

> [!TIP]
> **Two SD cards?** The launcher cleans the ROM card it finds first. A version that cleans both cards
> is coming — see the [roadmap](#️-roadmap) and the [FAQ](#faq) for what to do until then.

## ⌨️ The shell version (terminal)

For macOS, Linux, WSL and SSH on a console. Install the `dotcleaner` command — open **Terminal** and paste:

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Multi-Software/main/install.sh | sh
```

Then type `dotcleaner` to open the menu:

<img src="docs/demo.svg" alt="The dotcleaner menu in Terminal" width="620">

No Terminal? Download [**Dotcleaner-shell.zip**](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest/download/Dotcleaner-shell.zip), unzip it
and double-click **`dotcleaner.command`** (macOS).

<details>
<summary><b>Command-line options</b> (for scripts)</summary>

Give one or more paths instead of using the menu:

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
| `--console` | Console mode: find the ROM card and clean it with the simple screen |
| `-h`, `--help` / `-V`, `--version` | Help / version |

Exit codes: `0` OK · `1` error on at least one drive · `2` wrong usage · `130` interrupted.
</details>

## What it removes

| Item | What it is |
| --- | --- |
| `._*` | macOS metadata saved next to every copied file — the **ghost games** |
| `.DS_Store` | Finder folder view settings |
| `.Spotlight-V100` | Spotlight search index of the drive |
| `.Trashes` | The drive's Trash (files deleted in Finder) |
| `.fseventsd` | File system event log |
| `.TemporaryItems`, `.DocumentRevisions-V100` | Temporary files and document versions |
| `.apdisk`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop` | Disk and network share metadata |
| `__MACOSX` | Leftovers from zip files made on a Mac |
| `Thumbs.db`, `ehthumbs.db`, `desktop.ini` | Windows files — **only if you tick the Windows option** |

**Never touched:** ROMs, saves, BIOS, photos, documents and every other file, hidden or not.

- 🔗 Links are never followed and other drives are never entered; system and home folders are refused.
- 🛡️ **Safe mode on Mac-formatted drives** (APFS, HFS+): there, the macOS folders hold real data, so
  only `._*`, `.DS_Store`, `.apdisk` and `__MACOSX` are removed. Console cards (FAT32, exFAT) are cleaned completely.
- 🔬 Every change is checked by an automatic audit: thousands of test cards are compared file by file
  before and after cleaning, with every version. One wrong deletion and the release is blocked.

## Compatibility

| System | App | Shell / launcher |
| --- | --- | --- |
| macOS 13+ (Intel & Apple Silicon) | ✅ | ✅ |
| macOS 12 or older | — | ✅ |
| Windows 10 / 11 | ✅ | ✅ in WSL |
| Linux x86_64 — Steam Deck, Ubuntu 22.04+, Debian 12+, Fedora… | ✅ | ✅ |
| Linux ARM64 — Raspberry Pi OS 13+, Ubuntu 24.04+… | ✅ | ✅ |
| **Consoles** — ArkOS, dArkOS, Knulli, Batocera, ROCKNIX, AmberELEC, JELOS, EmuELEC, Onion, muOS, MinUI, Allium, spruceOS, TrimUI, RetroPie | — | ✅ |

If the Linux app does not start, install `libxcb-cursor0`. The shell version is plain POSIX `sh`: it
runs with bash, dash, BusyBox, ksh, mksh, posh, yash and zsh.

## FAQ

<details>
<summary><b>Can it delete my games or saves?</b></summary>

No. It only deletes the exact names listed in [What it removes](#what-it-removes). A file like
`Game._beta.gba` or a hidden save like `.game.srm` is kept. Use **Scan** first: it shows the full list
and deletes nothing.
</details>

<details>
<summary><b>The <code>._</code> files came back. Why?</b></summary>

macOS creates them again every time it copies files to the card. Clean after each copy — on the
console it only takes a few seconds.
</details>

<details>
<summary><b>What about the drive's Trash?</b></summary>

Files deleted in Finder on the drive go to its hidden `.Trashes` folder and still take space.
Dotcleaner warns you before erasing them. Tick **Keep the drive's Trash** (`-k`) to keep them.
</details>

<details>
<summary><b>Nothing happens when I start it on my console.</b></summary>

1. Use the **launcher** `Dotcleaner.sh` (capital D, from `Dotcleaner-console.zip`), not `dotcleaner.sh`:
   the plain script waits for a keyboard.
2. Check that it is in the right folder (`ports`, `tools` on Knulli, `App/` on Onion), and on Knulli /
   Batocera update the game lists.
3. **On Knulli nothing appears on screen**: that is normal, the cleaning only takes a few seconds.
4. Open **`dotcleaner.log`** next to it: it says what was found and cleaned. Still stuck? Open a
   [bug report](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=bug_report.yml) with this file.
</details>

<details>
<summary><b>My console has two SD cards.</b></summary>

For now the launcher cleans the ROM card it finds first (for example `/roms` on ArkOS). To clean the
other card: put it in your computer and use the app, or connect over SSH and run `dotcleaner.sh`
without options — the menu lists both cards (`/roms2` on ArkOS). A launcher that cleans both cards
in one go is [planned](#️-roadmap).
</details>

## 🗺️ Roadmap

- [ ] **Console version for two SD cards** — for handhelds with a system card and a games card
      (R36S, RG40XXV, RG35XX…): find both cards and clean them in one go from the Ports menu.
- Ideas? [Suggest one](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=feature_request.yml).

What changed in each version: [CHANGELOG](CHANGELOG.md).

## Community

- 💬 **[Discord](https://discord.gg/4FbhkuhRMm) — French-speaking community 🇫🇷.**
  Prefer English? Open an issue on GitHub: questions are welcome in any language.
- 🐞 [Report a bug](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=bug_report.yml) ·
  💡 [Suggest an idea](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=feature_request.yml) ·
  🌍 [Improve a translation](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new?template=translation.yml)
- 🛠️ Want to help with the code or run the tests? See [CONTRIBUTING.md](CONTRIBUTING.md).
- 🔒 A file deleted that should not have been? See [SECURITY.md](SECURITY.md).
- ⭐ If Dotcleaner saved your card, a star helps other players find it!

## License

[MIT](LICENSE) — © 2026 Shadowix84
