# Changelog

All notable changes to Dotcleaner. Downloads: [latest release](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest).

## [2.3.2] — 2026-11-22 — Logo in the console menus

### On the console
- **Dotcleaner's logo in the menu**: the console zip has a new optional `menu-logo/` folder (logo with a
  transparent background + `gamelist.xml`). Tested with the menus of ArkOS / RetroPie (theme carbon) and
  Knulli / Batocera (theme art-book-next). `README.txt` explains how to add it without replacing an
  existing `gamelist.xml`.
- The Onion app icon has a transparent background too.

### Downloads
- Clearer release page: "which file do I need?" table, advanced files grouped at the bottom.
- The terminal zip is now called `Dotcleaner-shell.zip` (it was `dotcleaner-x.y.z.zip`, easy to confuse
  with the console zip).

## [2.3.1] — 2026-11-22 — Knulli support from the Tools menu

### On the console
- **Knulli: put the launcher in `roms/tools/`** and start it from **Tools → Dotcleaner** (tested on an
  RG40XXV). Knulli shows no screen while a script runs: the launcher now finishes as soon as the card
  is clean instead of waiting 6 seconds in front of nothing. The result is in `dotcleaner.log`.
- `Dotcleaner-console.zip` now contains a `README.txt` (English and French) saying where to copy the
  launcher on each firmware.

### Documentation
- Clearer READMEs: which version to use, before/after example, console setup in 3 steps, what each
  firmware shows, FAQ for two SD cards, roadmap (console version for two SD cards), Discord marked as
  a French-speaking community.

## [2.3.0] — 2026-11-21 — New look for the app and the website

### On the console
- **Very simple screen that works on every firmware** (ArkOS, dArkOS, Knulli, Batocera, ROCKNIX,
  AmberELEC, JELOS, Onion, SSH…): plain ASCII lines, at most 40 columns, no colours and no cursor
  moves — `[1/4] ROM card`, `[2/4] Scan`, `[3/4] Clean` with a progress bar, `[4/4] Done!`.

### Desktop app
- **New look**: header with the version and the language menu, numbered step cards, result tiles per
  kind of junk, a real progress bar while cleaning, coloured result banner, and a light and dark theme
  that follows the system (same look on macOS, Windows and Linux).

### Website
- Redesigned: download button for your system (macOS, Windows or Linux), a before/after view of the
  ghost games, a section for cleaning on the console with the supported firmwares, safety cards, FAQ,
  the latest version shown automatically, and a better layout on phones.

## [2.2.1] — 2026-11-21 — Full check of every version

### Full check of every version
- New `tests/full_check.py`, also run every Monday by GitHub Actions (`full-check.yml`): static checks,
  8 shells + BusyBox, the 3 engines (shell, app, console) audited file by file and compared with each
  other, extreme cards, the interactive menu, the desktop app, and 11 deliberate bugs that must be caught.
- The audit now also uses big cards (hundreds of junk files), so batch deletion is covered.

### Fixed
- Console launcher: cleaning with the progress bar is about **20 times faster** on big cards
  (10 000 junk files: 1 s instead of 24 s): items are deleted 32 at a time.

## [2.2.0] — 2026-11-21 — See the progress on the console

### On the console
- **The console launcher now shows what is happening**: a full-screen view on ArkOS-like firmwares and
  over SSH, with the 4 steps (find the card, scan, clean, done), a **progress bar** while cleaning, the
  number of items per kind, and the result; it goes back to the menu after 8 seconds.
- Knulli / Batocera: a notification at each step (scanning, cleaning, done); Onion: a message box.
- The log (`dotcleaner.log`) lists the card, what was found and what was deleted.

### Tests
- The deletion audit now also checks the console launcher, file by file (including old BusyBox).

## [2.1.0] — 2026-11-21 — Clean right on the console

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

## [2.0.1] — 2026-11-21 — Stable download links

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

## [2.0.0] — 2026-11-21 — Desktop app for macOS and Windows

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

## [1.2.0] — 2026-11-21 — Safer on Mac disks

### Safety
- **Mac disks (APFS, HFS+) are refused** and hidden from the card list: consoles cannot read
  them, and there `.DocumentRevisions-V100`, `.fseventsd`… hold real data. `--force` overrides.
- `-k` now leaves the card's Trash **completely** untouched (before, `._*` files inside it were removed).

### Tests
- New deletion audit (`tests/audit.py`): every path of realistic and randomly generated cards is
  compared, before and after, with an independent referee — on macOS, Ubuntu and BusyBox.
- New end-to-end test on real exFAT and FAT32 cards mounted on macOS, including eject.

## [1.1.0] — 2026-11-21 — English by default

### Added
- `--lang fr|en` option (and `DOTCLEANER_LANG`): messages are now in **English by default**.
- Warning before erasing files left in the card's Trash, and `-k` / `--keep-trash` to keep them.
- `dotcleaner.command`: double-click launcher for macOS (pick, clean, eject).
- `install.sh`: one-line installer and uninstaller for the `dotcleaner` command.
- Clean exit on Ctrl-C (exit code 130).

### Changed
- `--help` follows `--lang`, wherever it is placed on the command line.
- `-q` also silences the Trash warning.

## [1.0.0] — 2026-11-21 — First version

First release.

- Removes `._*`, `.DS_Store`, `.apdisk`, `.Spotlight-V100`, `.Trashes`, `.fseventsd`,
  `.TemporaryItems`, `.DocumentRevisions-V100`, `.AppleDouble`, `.AppleDB`, `.AppleDesktop`, `__MACOSX`.
- `-w` also removes Windows files (`Thumbs.db`, `ehthumbs.db`, `desktop.ini`).
- Card picker when no path is given; dry run (`-n`), no-confirm (`-y`), eject (`-e`), verbose, quiet.
- French and English messages (system language).
- Runs on macOS, Linux and BusyBox (consoles); never follows symlinks, never leaves the card.
