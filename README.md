# dotcleaner

**Removes the junk files macOS leaves on the SD cards of emulation handhelds.**

[![CI](https://github.com/Shadowix84/Dotcleaner-Linux/actions/workflows/ci.yml/badge.svg)](https://github.com/Shadowix84/Dotcleaner-Linux/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🇫🇷 [Version française](README.fr.md)

When you copy ROMs to an SD card from a Mac, macOS quietly adds hidden files: a `._` twin for
every file (`._Pokemon Emerald.gba`), a `.DS_Store` in every folder opened in Finder, and
`.Spotlight-V100`, `.Trashes` or `.fseventsd` folders at the root.

On the console these files can show up as **ghost games that won't launch**, confuse scrapers
and waste space.

**dotcleaner** removes them in one command — and **only them**.

Works with any handheld whose card you plug into a Mac: R36S (ArkOS), Anbernic (Knulli, muOS,
ROCKNIX…), Miyoo (Onion), Retroid, TrimUI… and directly on the console over SSH.

## What it removes

| Item | Where it comes from |
| --- | --- |
| `._*` | AppleDouble files: the macOS metadata of every copied file |
| `.DS_Store` | Finder folder view settings |
| `.Spotlight-V100` | Spotlight index of the card |
| `.Trashes` | The card's Trash (files deleted in Finder without emptying the Trash) |
| `.fseventsd` | File system event log |
| `.TemporaryItems`, `.DocumentRevisions-V100` | Temporary files and document versions |
| `.apdisk`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop` | Disk and network share metadata |
| `__MACOSX` | Leftovers from zip archives made on a Mac |
| `Thumbs.db`, `ehthumbs.db`, `desktop.ini` | Windows — **only with `-w`** |

**Never touched:** your ROMs, saves, BIOS, and every other file, hidden or not (`.keep`, config files…).
Symlinks are not followed and the script never leaves the card.

> ⚠️ `.Trashes` holds the files you deleted in Finder without emptying the Trash:
> dotcleaner deletes them for good (which frees space on the card).

## Install

Open **Terminal** (`Cmd + Space`, type "Terminal", Enter), then paste:

```sh
curl -fsSL https://raw.githubusercontent.com/Shadowix84/Dotcleaner-Linux/main/dotcleaner.sh -o dotcleaner.sh
chmod +x dotcleaner.sh
```

*Optional* — to type just `dotcleaner` from any folder:

```sh
sudo mkdir -p /usr/local/bin
sudo install -m 755 dotcleaner.sh /usr/local/bin/dotcleaner
```

Or download everything with the green **Code** button → **Download ZIP** on the GitHub page.

## Usage

1. Plug the SD card into your Mac.
2. Run `./dotcleaner.sh` (or `dotcleaner` if you installed it).
3. Pick the card from the list, check the summary, confirm with `y`.

```text
$ ./dotcleaner.sh
dotcleaner 1.0.0
Which card do you want to clean?
  1) /Volumes/EASYROMS
Number (Enter to cancel): 1

/Volumes/EASYROMS
    1342  ._* files (AppleDouble)
      37  .DS_Store
       3  macOS system items (.Spotlight-V100, .Trashes...)
  ------
  Total: 1382 items, 41.6 MB
  Delete 1382 items? [y/N] y
  Done: 1382 items deleted (41.6 MB freed).
```

*(sample output; numbers depend on your card)*

### Examples

```sh
./dotcleaner.sh -n /Volumes/EASYROMS      # dry run: show what would be deleted
./dotcleaner.sh /Volumes/SHARE            # clean a given card
./dotcleaner.sh -y -e /Volumes/EASYROMS   # clean then eject, no questions
./dotcleaner.sh -w "/Volumes/NO NAME"     # also remove Windows files
./dotcleaner.sh /Volumes/BOOT /Volumes/EASYROMS   # several partitions at once
```

The card's name is the one shown in Finder's sidebar (for example `EASYROMS` on an R36S running
ArkOS, `SHARE` on Knulli or Batocera). Quote the path if it contains spaces.

### Options

| Option | Effect |
| --- | --- |
| `-n`, `--dry-run` | Preview: show what would be deleted, delete nothing |
| `-y`, `--yes` | Do not ask for confirmation |
| `-w`, `--windows` | Also remove `Thumbs.db`, `ehthumbs.db`, `desktop.ini` |
| `-e`, `--eject` | Eject the card when done (macOS) |
| `-v`, `--verbose` | List every deleted item |
| `-q`, `--quiet` | Only print errors |
| `-h`, `--help` | Help |
| `-V`, `--version` | Version |

Messages are in French when your system is in French, in English otherwise
(force with `DOTCLEANER_LANG=en` or `DOTCLEANER_LANG=fr`).

Exit codes: `0` = OK, `1` = error on at least one card, `2` = wrong usage.

### On the console itself

If SSH is enabled on your firmware, copy `dotcleaner.sh` to the console and run `sh dotcleaner.sh`:
without a path it offers the usual ROM folders (`/roms`, `/userdata/roms`, `/storage/roms`,
`/mnt/SDCARD`, `/mnt/mmc`…). The script is pure POSIX `sh` and works with BusyBox.

## macOS tips

- **First run:** macOS asks whether Terminal may access files on a removable volume → click *Allow*.
- **Use `-e`** to eject right after cleaning: while the card stays mounted, macOS may recreate
  `.fseventsd` or `.Spotlight-V100` at the root. Those folders are harmless for the console; the
  `._` files next to your ROMs only come back when you copy new files from the Mac.
- **Fewer `.DS_Store` on USB drives and cards:**
  `defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true`, then log out.
  Apple does not document this setting for USB and its effect may vary between macOS versions.
- macOS ships a `dot_clean` command, but it only deals with `._` files.

## Tests

```sh
sh tests/run_tests.sh               # with the default sh
sh tests/run_tests.sh bash          # with another shell
```

The tests build a fake SD card and check what gets deleted and, above all, what is kept.
On every push, GitHub Actions runs ShellCheck and the tests on Ubuntu, macOS and BusyBox (like on a console).

## Uninstall

Delete `dotcleaner.sh` (and `/usr/local/bin/dotcleaner` if you installed it:
`sudo rm /usr/local/bin/dotcleaner`). Nothing else is installed.

## License

[MIT](LICENSE) — © 2026 Shadowix84
