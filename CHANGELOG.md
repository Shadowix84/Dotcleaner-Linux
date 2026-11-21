# Changelog

All notable changes to dotcleaner.

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
