# Changelog

All notable changes to dotcleaner.

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
