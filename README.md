<div align="center">

# 🧹 dotcleaner

**Remove the junk files macOS leaves on your emulation handheld's SD card.**<br>
`._*` · `.DS_Store` · `.Spotlight-V100` · `.Trashes` · `.fseventsd` · `__MACOSX` …

[![CI](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/actions/workflows/ci.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Shadowix84/Dotcleaner-Linux-Handheld?label=release)](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/releases/latest)
[![POSIX sh](https://img.shields.io/badge/shell-POSIX%20sh-89e051)](dotcleaner.sh)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🇫🇷 [Version française](README.fr.md)

<img src="docs/demo.svg" alt="dotcleaner cleaning an SD card in Terminal" width="640">

</div>

## Why?

When you copy ROMs to an SD card from a Mac, macOS quietly adds hidden files:
a `._` twin for every file (`._Pokemon Emerald.gba`), a `.DS_Store` in every folder you open
in Finder, and `.Spotlight-V100`, `.Trashes` or `.fseventsd` folders at the root.

On the console they can show up as **ghost games that won't launch**, confuse scrapers and
waste space. **dotcleaner** removes them in one command — and **only them**.

## Features

- 🎯 **Precise** — removes a fixed list of macOS junk, never your ROMs, saves or BIOS
- 👀 **Safe** — shows a summary and asks before deleting; `-n` previews without touching anything
- 🗑️ **Trash-aware** — warns before erasing files left in the card's Trash (`-k` keeps them)
- 💾 **Pick & eject** — lists the plugged-in cards, cleans, then ejects (`-e`)
- 🖱️ **Double-click launcher** for macOS — no Terminal commands needed
- 🐧 **Runs anywhere** — macOS, Linux and on the console itself (pure POSIX `sh`, BusyBox-compatible)
- 🛡️ **Refuses Mac disks** — a backup drive picked by mistake is never touched (APFS/HFS+)
- ✅ **Audited** — at every change, thousands of cards are checked file by file on macOS, Ubuntu and BusyBox, plus real exFAT/FAT32 cards

## Quick start

### Option 1 — install the command (recommended)

Open **Terminal** (`Cmd + Space`, type "Terminal", Enter) and paste:

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Linux-Handheld/main/install.sh | sh
```

Then plug in your SD card and run:

```sh
dotcleaner
```

Pick the card from the list, check the summary, confirm with `y`. Done.

### Option 2 — double-click (no Terminal commands)

1. Download the latest `dotcleaner-x.y.z.zip` from the [Releases page](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/releases/latest) and unzip it.
2. Plug in your SD card.
3. Double-click **`dotcleaner.command`**: Terminal opens, you pick the card, confirm, and it is ejected at the end.

> If macOS says it cannot verify the developer: open **System Settings → Privacy & Security**,
> scroll down and click **Open Anyway** (on older macOS: right-click the file → **Open**).
> Keep `dotcleaner.command` next to `dotcleaner.sh`.

### Option 3 — on the console itself

If SSH is enabled on your firmware, copy `dotcleaner.sh` to the console and run `sh dotcleaner.sh`.
Without a path it offers the usual ROM folders (see the table below).

## Usage

```text
dotcleaner [options] [PATH...]
```

```sh
dotcleaner                          # pick the card from a list
dotcleaner -n /Volumes/EASYROMS     # preview: show what would be deleted
dotcleaner -y -e /Volumes/EASYROMS  # clean then eject, no questions
dotcleaner -w "/Volumes/NO NAME"    # also remove Windows files
dotcleaner /Volumes/BOOT /Volumes/EASYROMS   # several partitions at once
```

| Option | Effect |
| --- | --- |
| `-n`, `--dry-run` | Preview: show what would be deleted, delete nothing |
| `-y`, `--yes` | Do not ask for confirmation |
| `-w`, `--windows` | Also remove `Thumbs.db`, `ehthumbs.db`, `desktop.ini` |
| `-k`, `--keep-trash` | Leave the card's Trash (`.Trashes`) untouched |
| `--force` | Also accept a Mac disk (APFS/HFS+), refused by default |
| `-e`, `--eject` | Eject the card when done (macOS) |
| `-v`, `--verbose` | List every deleted item |
| `-q`, `--quiet` | Only print errors |
| `--lang fr` | French messages (default: English) — or set `DOTCLEANER_LANG=fr` |
| `-h`, `--help` / `-V`, `--version` | Help / version |

Exit codes: `0` OK · `1` error on at least one card · `2` wrong usage · `130` interrupted (Ctrl-C).

### Where is my card?

The name is the one shown in Finder's sidebar. Typical names:

| Firmware (examples) | Name on the Mac | Path on the console |
| --- | --- | --- |
| ArkOS (R36S, RG351…) | `EASYROMS` | `/roms` |
| Knulli, Batocera (Anbernic RG40XX…) | `SHARE` | `/userdata/roms` |
| ROCKNIX | depends on the card | `/storage/roms` |
| Onion (Miyoo Mini) | depends on the card | `/mnt/SDCARD` |
| muOS | depends on the card | `/mnt/mmc` |

Quote the path if it contains spaces: `"/Volumes/NO NAME"`.

## What it removes

| Item | Where it comes from |
| --- | --- |
| `._*` | AppleDouble files: macOS metadata of every copied file |
| `.DS_Store` | Finder folder view settings |
| `.Spotlight-V100` | Spotlight index of the card |
| `.Trashes` | The card's Trash (files deleted in Finder without emptying the Trash) |
| `.fseventsd` | File system event log |
| `.TemporaryItems`, `.DocumentRevisions-V100` | Temporary files and document versions |
| `.apdisk`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop` | Disk and network share metadata |
| `__MACOSX` | Leftovers from zip archives made on a Mac |
| `Thumbs.db`, `ehthumbs.db`, `desktop.ini` | Windows — **only with `-w`** |

**Never touched:** your ROMs, saves, BIOS, and every other file, hidden or not (`.keep`, config files…).
Symlinks are not followed and the script never leaves the card. It refuses to run on system
folders, on your home folder and on Mac disks (APFS/HFS+), where these folders hold real data.

## FAQ

<details>
<summary><b>Can it delete my games or saves?</b></summary>

No. It only deletes the exact names listed above. A file like `Game._beta.gba` or a hidden save
like `.game.srm` is kept. Run with `-n` first to see the full list before anything is deleted.

This is checked at every change by an audit ([`tests/audit.py`](tests/audit.py)): realistic cards
(ArkOS, Knulli, PortMaster…) and hundreds of random cards full of tricky names are scanned path by
path before and after cleaning, and compared with an independent referee. One file deleted by
mistake, or one junk file left behind, and the audit fails.
</details>

<details>
<summary><b>The <code>._</code> files came back. Why?</b></summary>

macOS creates them every time you copy files from the Mac to the card. Run dotcleaner after each
copy session — with `-e` it ejects the card right away, so macOS has no time to add new junk.
</details>

<details>
<summary><b>What about the card's Trash?</b></summary>

Files you delete in Finder on the card go to its hidden `.Trashes` folder and still take space.
dotcleaner warns you and erases them for good. Use `-k` to keep them.
</details>

<details>
<summary><b>I use Windows or Linux, not a Mac.</b></summary>

On Linux it works the same way (cards under `/media/...` are offered automatically). With `-w` it
also removes Windows' `Thumbs.db` and `desktop.ini`. On Windows, run it on the console over SSH or in WSL.
</details>

<details>
<summary><b>Isn't there a built-in macOS tool?</b></summary>

macOS has `dot_clean`, but it only deals with `._` files — not `.DS_Store`, Spotlight or Trash folders.
</details>

## macOS tips

- **First run:** macOS asks whether Terminal may access files on a removable volume → click *Allow*.
- **Fewer `.DS_Store` on USB drives and cards:**
  `defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true`, then log out.
  Apple does not document this setting for USB and its effect may vary between macOS versions.

## Uninstall

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Linux-Handheld/main/install.sh | sh -s -- --uninstall
```

## Contributing

Bug reports and ideas are welcome in the [issues](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/issues).
See [CONTRIBUTING.md](CONTRIBUTING.md) to run the tests before sending a change.

## License

[MIT](LICENSE) — © 2026 Shadowix84
