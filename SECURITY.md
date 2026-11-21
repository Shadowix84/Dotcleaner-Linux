# Security policy

Dotcleaner deletes files, so safety comes first: it only deletes a fixed list of macOS junk names,
never follows links, never leaves the drive, refuses system and home folders, and uses a safe mode on
Mac-formatted drives. Every change is checked by a file-by-file deletion audit (`tests/audit.py`).

## Reporting a problem

- **A file was deleted that should not have been**, or any other security issue: please report it
  privately with **Security → Report a vulnerability** on this repository (GitHub private advisory).
  If that is not possible, open an issue without sensitive details and say you need a private contact.
- Include the version (`dotcleaner --version`, or the version shown in the app), your system, the drive
  type (exFAT, FAT32, APFS…) and, if you can, the output of a scan.

You will get an answer as soon as possible, and a fixed version will be published with a note in the CHANGELOG.

## Supported versions

Only the [latest release](https://github.com/Shadowix84/Dotcleaner-Multi-Software/releases/latest) gets fixes.

## Checking your download

The apps are built from this repository by GitHub Actions — the build logs are public. They are not
signed with a paid Apple or Microsoft certificate, which is why the system warns you on first launch.

Every release contains `SHA256SUMS.txt`. To check a file:

```sh
# macOS / Linux, in the download folder
shasum -a 256 -c SHA256SUMS.txt --ignore-missing
```

```powershell
# Windows PowerShell: compare with the line in SHA256SUMS.txt
Get-FileHash .\Dotcleaner-Windows.exe -Algorithm SHA256
```
