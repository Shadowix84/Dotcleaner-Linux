# Contributing to dotcleaner

Thanks for helping! Bug reports, ideas and pull requests are welcome.

## Reporting a bug

Open an [issue](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new/choose) and include:

- your console and firmware (e.g. R36S + ArkOS, RG40XXV + Knulli),
- the computer you ran it on (macOS version, Linux distro, or the console itself),
- the command you ran and its full output (`dotcleaner -n -v ...` is a good start).

## Changing the code

There are two engines with **exactly the same rules**:

- `dotcleaner.sh` — the shell version, written in **plain POSIX `sh`** so it runs on macOS, Linux and
  BusyBox (most console firmwares). No bash-only syntax (`[[ ]]`, arrays, `local`, `$'...'`), no
  GNU-only options. Its interface is in English only.
- `app/dotcleaner_core.py` — the engine of the desktop app (`app/dotcleaner_gui.py`, PySide6),
  packaged as a `.dmg` and an `.exe`.

After any change to `dotcleaner.sh`, run `sh tools/make_console.sh` to rebuild the console launchers
in `console/` (CI checks they are up to date). Keep the shell scripts **pure ASCII**.

To add a file or folder to clean, change **both** engines (`JUNK_FILES` / `SYSTEM_DIRS` at the top of each),
the referee at the top of `tests/audit.py`, the fake card in `tests/run_tests.sh`, and the tables in both READMEs.

### Translations (app only)

All app texts are in `app/i18n.py`: English, French, Spanish, Chinese (Mandarin, simplified) and Hindi.
Every language must have every key with the same `{placeholders}` — `tests/test_app.py` checks it.
To add a language, copy the `"en"` block, translate it and add it to `LANGUAGES`.

## Running the checks

```sh
shellcheck -s sh dotcleaner.sh install.sh dotcleaner.command tests/run_tests.sh tests/macos_card.sh
sh tests/run_tests.sh                       # shell version (default sh)
sh tests/run_tests.sh bash                  # another shell (also: mksh, posh, yash, ksh, "zsh --emulate sh")
python3 tests/audit.py                      # deletion audit of the shell engine
python3 tests/audit.py --engine python      # deletion audit of the app engine (also on Windows)
pip install PySide6-Essentials && python3 tests/test_app.py   # app: translations + real clean
sh tests/macos_card.sh                      # macOS only: real exFAT/FAT32 cards, eject, safe mode
```

Run the app from source: `python3 app/dotcleaner_gui.py`.

GitHub Actions runs all of this on Ubuntu, macOS, Windows and BusyBox for every push, and builds the
`.dmg` and `.exe` (`apps.yml`): download them from the run's **Artifacts** to try a change.

## Releasing (maintainer)

1. Bump `VERSION` in `dotcleaner.sh` **and** `app/dotcleaner_core.py`, and add a `## [x.y.z]` section at the top of `CHANGELOG.md`.
2. Push to `main` and wait for CI to be green.
3. **Actions → Release → Run workflow.** It runs the tests, creates the `vx.y.z` tag and the
   GitHub release with the `.dmg`, the `.exe`, the zip and the script, using the CHANGELOG section as release notes.
