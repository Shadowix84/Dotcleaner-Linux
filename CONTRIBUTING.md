# Contributing to dotcleaner

Thanks for helping! Bug reports, ideas and pull requests are welcome.

## Reporting a bug

Open an [issue](https://github.com/Shadowix84/Dotcleaner-Linux-Handheld/issues/new/choose) and include:

- your console and firmware (e.g. R36S + ArkOS, RG40XXV + Knulli),
- the computer you ran it on (macOS version, Linux distro, or the console itself),
- the command you ran and its full output (`dotcleaner -n -v ...` is a good start).

## Changing the code

dotcleaner is a single file, `dotcleaner.sh`, written in **plain POSIX `sh`** so it runs on
macOS, Linux and BusyBox (the system of most console firmwares). Please keep it that way:
no bash-only syntax (`[[ ]]`, arrays, `local`, `$'...'`), no GNU-only options.

To add a file or folder to clean, edit `JUNK_FILES` or `JUNK_DIRS` at the top of the script,
then add it to the fake card in `tests/run_tests.sh` and to the table in both READMEs.

Messages are written with `t "English" "Français"` so both languages stay in sync.

## Running the checks

```sh
shellcheck -s sh dotcleaner.sh install.sh dotcleaner.command tests/run_tests.sh tests/macos_card.sh
sh tests/run_tests.sh            # default sh
sh tests/run_tests.sh bash       # another shell
python3 tests/audit.py           # deletion audit: nothing wrongly deleted, nothing left behind
sh tests/macos_card.sh           # macOS only: real exFAT/FAT32 cards, eject, APFS refusal
```

If you change what gets deleted, update the referee at the top of `tests/audit.py` too.

GitHub Actions runs the same checks on Ubuntu, macOS and BusyBox for every push and pull request.

## Releasing (maintainer)

1. Bump `VERSION` in `dotcleaner.sh` and add a `## [x.y.z]` section at the top of `CHANGELOG.md`.
2. Push to `main` and wait for CI to be green.
3. **Actions → Release → Run workflow.** It runs the tests, creates the `vx.y.z` tag and the
   GitHub release with the zip, using the CHANGELOG section as release notes.
