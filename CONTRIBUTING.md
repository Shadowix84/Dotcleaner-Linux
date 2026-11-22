# Contributing to Dotcleaner

Thanks for helping! Bug reports, ideas, translations and pull requests are welcome, in English or in French.

## Reporting a bug

Open an [issue](https://github.com/Shadowix84/Dotcleaner-Multi-Software/issues/new/choose) and include:

- your console and firmware (e.g. R36S + ArkOS, RG40XXV + Knulli),
- what you used: the app (macOS, Windows, Linux), the console launcher, or the shell,
- on the console: the content of `dotcleaner.log`; with the shell: the output of `dotcleaner -n -v YOUR_DRIVE`.

## How the project is organised

| Path | What it is |
| --- | --- |
| `dotcleaner.sh` | The shell version and the cleaning engine for consoles — plain POSIX `sh` |
| `console/` | Console launchers and `README.txt`, **generated** from `dotcleaner.sh` by `tools/make_console.sh` |
| `console/menu-logo/` | Optional logo for the console menus (`gamelist.xml` + images from `tools/make_logos.py`) |
| `app/dotcleaner_core.py` | The engine of the desktop app (same rules as the shell) |
| `app/dotcleaner_gui.py` | The desktop app (PySide6), packaged as `.dmg`, `.exe` and Linux binaries |
| `app/i18n.py` | App texts in 5 languages |
| `site/index.html` | The website (GitHub Pages), with its own texts in 5 languages |
| `tests/` | Shell tests, deletion audit, app tests, full check |
| `docs/` | Images used by the READMEs and the website |

## Changing the code

The two engines have **exactly the same rules**:

- `dotcleaner.sh` must stay **plain POSIX `sh` and pure ASCII**, so it runs on macOS, Linux and the
  BusyBox of console firmwares: no bash-only syntax (`[[ ]]`, arrays, `local`, `$'...'`), no GNU-only
  options. Its interface is in English only. The console screen must stay simple: plain lines, at most
  40 columns, no colours or cursor moves.
- After any change to `dotcleaner.sh`, run `sh tools/make_console.sh` to rebuild `console/`
  (CI checks it is up to date).
- To add a file or folder to clean, change **both** engines (`JUNK_FILES` / `SYSTEM_DIRS` at the top of
  each), the referee at the top of `tests/audit.py`, the fake card in `tests/run_tests.sh`, and the
  tables in both READMEs.

### Translations

- **App:** all texts are in `app/i18n.py` (English, French, Spanish, Chinese simplified, Hindi). Every
  language must have every key with the same `{placeholders}` — `tests/test_app.py` checks it.
  To add a language, copy the `"en"` block, translate it and add it to `LANGUAGES`.
- **Website:** the `T` object at the bottom of `site/index.html`, same languages.

## Running the checks

```sh
python3 tests/full_check.py                 # everything below in one command (about 10 min)

shellcheck -s sh dotcleaner.sh install.sh dotcleaner.command tests/run_tests.sh tests/macos_card.sh
sh tests/run_tests.sh                       # shell version (default sh)
sh tests/run_tests.sh bash                  # another shell (also: mksh, posh, yash, ksh, "zsh --emulate sh")
python3 tests/audit.py                      # deletion audit of the shell engine
python3 tests/audit.py --engine python      # deletion audit of the app engine (also on Windows)
pip install PySide6-Essentials && python3 tests/test_app.py   # app: translations + real clean
sh tests/macos_card.sh                      # macOS only: real exFAT/FAT32 cards, eject, safe mode
```

Run the app from source: `python3 app/dotcleaner_gui.py` (add `DOTCLEANER_THEME=dark` to try the dark theme).

**The deletion audit** ([`tests/audit.py`](tests/audit.py)) is the safety net: realistic cards (ArkOS,
Knulli, PortMaster…) and hundreds of random cards full of tricky names are listed path by path before
and after cleaning, with every engine, and compared with an independent referee. One file deleted by
mistake, or one junk file left behind, and it fails.

## What GitHub Actions does

| Workflow | When | What |
| --- | --- | --- |
| [`ci.yml`](.github/workflows/ci.yml) | every push | ShellCheck, shell tests with 8 shells and BusyBox, deletion audit, real exFAT/FAT32 cards on macOS |
| [`apps.yml`](.github/workflows/apps.yml) | every push | App audit and tests on macOS, Windows and Linux, then builds and launches every app — download them from the run's **Artifacts** to try a change |
| [`full-check.yml`](.github/workflows/full-check.yml) | every Monday | `tests/full_check.py`: every version at once, extreme cards, and deliberate bugs the audit must catch |
| [`pages.yml`](.github/workflows/pages.yml) | changes to `site/` or `docs/` | Publishes the website |
| [`release.yml`](.github/workflows/release.yml) | by hand | Publishes a release (see below) |
| [`tidy-releases.yml`](.github/workflows/tidy-releases.yml) | after each release, or by hand | Titles every release from the CHANGELOG and marks the older ones "old version" |

## Releasing (maintainer)

1. Bump `VERSION` in `dotcleaner.sh` **and** `app/dotcleaner_core.py`, run `sh tools/make_console.sh`,
   and add a section at the top of `CHANGELOG.md`: `## [x.y.z] — YYYY-MM-DD — Short title`.
   The short title becomes the release title (`Dotcleaner x.y.z — Short title`).
2. Push to `main` and wait for CI to be green.
3. Optional: **Actions → Apps → Run workflow** with *update screenshots* ticked, to refresh the app
   pictures in the READMEs and on the website.
4. **Actions → Release → Run workflow.** It runs the tests, creates the `vx.y.z` tag and the release
   with every file (`.dmg`, `.exe`, Linux apps, `Dotcleaner-console.zip`, `Dotcleaner-shell.zip`,
   `dotcleaner.sh`, `SHA256SUMS.txt`). The notes start with a "Which file do I need?" table, then the
   CHANGELOG section.
