# Changelog

All notable changes to dotcleaner.

## [2.2.0] — 2026-11-21

### On the console
- **The console launcher now shows what is happening**: a full-screen view on ArkOS-like firmwares and
  over SSH, with the 4 steps (find the card, scan, clean, done), a **progress bar** while cleaning, the
  number of items per kind, and the result; it goes back to the menu after 8 seconds.
- Knulli / Batocera: a notification at each step (scanning, cleaning, done); Onion: a message box.
- The log (`dotcleaner.log`) lists the card, what was found and what was deleted.

### Tests
- The deletion audit now also checks the console launcher, file by file (including old BusyBox).

## [2.1.0] — 2026-11-21

### On the console
- **Console launcher** `Dotcleaner.sh` for the Ports menu (ArkOS, dArkOS, Knulli, Batocera, ROCKNIX,
  AmberELEC, JELOS, EmuELEC) and an **Onion app** (Miyoo Mini), in `Dotcleaner-console.zip`:
  finds the ROM card by itself, cleans it without a keyboard, shows the result (text screen on ArkOS,
  notification on Knulli/Batocera, message box on Onion) and writes `dotcleaner.log`.
- `--console` option for the same from SSH or any script.
- Fixed: started from a console menu, the plain script waited for a keyboard and did nothing.

### Compatibility
- Shell: pure ASCII (console text screens, strict shells), works with posh and yash (fixed empty
  `"$@"` and multibyte errors), fallback for old BusyBox `find` without `-exec {} +`, finds drives on
  Steam Deck, Raspberry Pi, ChromeOS and WSL. Tested with bash, dash, BusyBox, ksh, mksh, posh, yash, zsh.
- App: the `.dmg` now runs on **Intel and Apple Silicon** Macs (macOS 13+), tested on both.
- New **Linux app** for x86_64 (Steam Deck, PC) and ARM64 (Raspberry Pi); Linux drives found from the mount table.

## [2.0.1] — 2026-11-21

### Downloads
- Stable file names: **Dotcleaner-macOS.dmg** and **Dotcleaner-Windows.exe** — the "latest" download links never change.
- `SHA256SUMS.txt` in every release to check the downloads.
- The macOS app shows its real version, copyright and category; the Windows `.exe` shows its version,
  product name and copyright in *Properties → Details*.
- Release notes with a download table and first-launch help.

### Project
- Project website (GitHub Pages) in 5 languages, with a download button that detects Mac or Windows.
- New README (direct download buttons, contents), security policy, code of conduct, support page,
  issue forms for bugs, ideas and translations.

## [2.0.0] — 2026-11-21

### New: desktop app for macOS (.dmg) and Windows (.exe)
- Simple window with the same steps as the shell menu: 1. Choose a drive · 2. Options · 3. Scan · 4. Clean.
- Works with **any SD card or USB drive** (removable and external drives are listed automatically).
- 5 languages in the language menu: English, Français, Español, 中文（简体）, हिन्दी.
- Built and tested automatically by GitHub Actions (`apps.yml`) and attached to each release.

### Shell
- **Interactive menu** when run without arguments: 1. Choose a drive · 2. Options · 3. Scan · 4. Clean · Help · Quit.
- **English only**: `--lang` and the French messages are removed.
- Mac-formatted drives (APFS, HFS+) are no longer refused: **safe mode** removes only the junk files
  (`._*`, `.DS_Store`, `.apdisk`, `__MACOSX`) and leaves the macOS system folders untouched. `--force` is removed.
- All plugged-in drives are listed (including Mac-formatted ones, marked "safe mode").

### Tests
- The deletion audit now checks both engines (shell and app) and safe mode, on macOS, Windows, Linux and BusyBox.
- New app tests: every language complete, a real scan → confirm → clean driven through the window.

## [1.2.0] — 2026-11-21

### Safety
- **Mac disks (APFS, HFS+) are refused** and hidden from the card list: consoles cannot read
  them, and there `.DocumentRevisions-V100`, `.fseventsd`… hold real data. `--force` overrides.
- `-k` now leaves the card's Trash **completely** untouched (before, `._*` files inside it were removed).

### Tests
- New deletion audit (`tests/audit.py`): every path of realistic and randomly generated cards is
  compared, before and after, with an independent referee — on macOS, Ubuntu and BusyBox.
- New end-to-end test on real exFAT and FAT32 cards mounted on macOS, including eject.

## [1.1.0] — 2026-11-21

### Added
- `--lang fr|en` option (and `DOTCLEANER_LANG`): messages are now in **English by default**.
- Warning before erasing files left in the card's Trash, and `-k` / `--keep-trash` to keep them.
- `dotcleaner.command`: double-click launcher for macOS (pick, clean, eject).
- `install.sh`: one-line installer and uninstaller for the `dotcleaner` command.
- Clean exit on Ctrl-C (exit code 130).

### Changed
- `--help` follows `--lang`, wherever it is placed on the command line.
- `-q` also silences the Trash warning.

## [1.0.0] — 2026-11-21

First release.

- Removes `._*`, `.DS_Store`, `.apdisk`, `.Spotlight-V100`, `.Trashes`, `.fseventsd`,
  `.TemporaryItems`, `.DocumentRevisions-V100`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop`, `__MACOSX`.
- `-w` also removes Windows files (`Thumbs.db`, `ehthumbs.db`, `desktop.ini`).
- Card picker when no path is given; dry run (`-n`), no-confirm (`-y`), eject (`-e`), verbose, quiet.
- French and English messages (system language).
- Runs on macOS, Linux and BusyBox (consoles); never follows symlinks, never leaves the card.
