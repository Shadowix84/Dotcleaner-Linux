#!/usr/bin/env python3
"""
dotcleaner core — the cleaning engine of the desktop app (macOS .dmg, Windows .exe).

It applies EXACTLY the same rules as dotcleaner.sh (keep both in sync; the
audit in tests/audit.py checks both engines against the same referee):

  * removed files, at any depth:   ._*  .DS_Store  .apdisk
                                    (+ Thumbs.db ehthumbs.db desktop.ini with "windows")
  * removed folders, at any depth: .Spotlight-V100 .Trashes .fseventsd .TemporaryItems
                                    .DocumentRevisions-V100 .AppleDouble .AppleDB
                                    .AppleDesktop __MACOSX
  * symlinks / junctions are never followed nor deleted, other filesystems never entered
  * "keep_trash": .Trashes is left completely untouched
  * safe mode, automatic on Mac-formatted drives (APFS, HFS+): only the junk files and
    __MACOSX are removed, the macOS system folders are left completely untouched

Also usable from the command line (used by the tests):
    python3 dotcleaner_core.py [-n] [-y] [-w] [-k] PATH
"""
import os
import platform
import shutil
import stat
import string
import subprocess
import sys
from dataclasses import dataclass, field

VERSION = "2.2.0"

JUNK_FILES = (".DS_Store", ".apdisk")          # plus every name starting with "._"
SYSTEM_DIRS = (".Spotlight-V100", ".Trashes", ".fseventsd", ".TemporaryItems",
               ".DocumentRevisions-V100", ".AppleDouble", ".AppleDB", ".AppleDesktop")
ARCHIVE_DIRS = ("__MACOSX",)
WINDOWS_FILES = ("Thumbs.db", "ehthumbs.db", "desktop.ini")
MAC_FILESYSTEMS = {"apfs", "hfs", "hfsplus", "hfs+"}
# ROM folders of console firmwares, when the app runs on the handheld itself
CONSOLE_ROOTS = ("/userdata", "/roms", "/roms2", "/storage/roms", "/mnt/mmc", "/mnt/SDCARD", "/mnt/sdcard")

SYSTEM = platform.system()          # "Darwin", "Windows", "Linux"


# ---------------------------------------------------------------- data ----
@dataclass
class Item:
    path: str
    is_dir: bool
    category: str        # appledouble | ds_store | system | windows
    size: int            # bytes on disk


@dataclass
class ScanResult:
    root: str
    items: list = field(default_factory=list)
    safe_mode: bool = False
    fs: str = ""
    trash_files: int = 0         # user files in a .Trashes that will be erased
    windows: bool = False
    keep_trash: bool = False

    @property
    def total_size(self):
        return sum(i.size for i in self.items)

    def count(self, category):
        return sum(1 for i in self.items if i.category == category)


@dataclass
class CleanResult:
    deleted: int
    freed: int
    left: list            # items still present after cleaning
    only_system_left: bool


@dataclass
class Drive:
    path: str
    name: str
    fs: str
    size: int            # total bytes, 0 if unknown
    safe_mode: bool


class TargetError(Exception):
    """Raised when a path must not (or cannot) be cleaned. .code is a message key."""

    def __init__(self, code, path):
        super().__init__(f"{code}: {path}")
        self.code = code
        self.path = path


# --------------------------------------------------------- filesystems ----
def _run(cmd):
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              text=True, timeout=10, **_no_window()).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def _no_window():
    """Hide the console window of child processes on Windows."""
    if SYSTEM == "Windows":
        return {"creationflags": 0x08000000}          # CREATE_NO_WINDOW
    return {}


def fs_type(path):
    """Filesystem type of the drive holding path: apfs, hfs, msdos, exfat, ntfs, vfat..."""
    forced = os.environ.get("DOTCLEANER_FS_TYPE")
    if forced is not None and forced != "":
        return forced.lower()
    try:
        if SYSTEM == "Darwin":
            dev = _run(["/usr/bin/stat", "-f", "%Sd", path]).strip()
            for line in _run(["/sbin/mount"]).splitlines():
                if line.startswith(f"/dev/{dev} on "):
                    return line.rsplit("(", 1)[1].split(",")[0].split(")")[0].strip().lower()
        elif SYSTEM == "Windows":
            return _win_volume_info(_win_drive_root(path))[1].lower()
        else:
            best, kind = "", ""
            real = os.path.realpath(path)
            with open("/proc/mounts", encoding="utf-8", errors="replace") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    mnt = parts[1].replace("\\040", " ")
                    if (real == mnt or real.startswith(mnt.rstrip("/") + "/")) and len(mnt) > len(best):
                        best, kind = mnt, parts[2]
            return kind.lower()
    except (OSError, IndexError):
        pass
    return ""


def is_mac_disk(path):
    return fs_type(path) in MAC_FILESYSTEMS


# -------------------------------------------------------------- safety ----
def _forbidden_paths():
    if SYSTEM == "Windows":
        out = set()
        sysdrive = os.environ.get("SystemDrive", "C:") + "\\"
        out.add(sysdrive)
        for var in ("WINDIR", "ProgramFiles", "ProgramFiles(x86)", "ProgramData",
                    "USERPROFILE", "APPDATA", "LOCALAPPDATA"):
            if os.environ.get(var):
                out.add(os.environ[var])
        out.add(os.path.join(sysdrive, "Users"))
        return {os.path.normcase(os.path.realpath(p)) for p in out}
    paths = ["/", "/Applications", "/Library", "/System", "/System/Volumes/Data", "/Users",
             "/Volumes", "/bin", "/boot", "/dev", "/etc", "/home", "/media", "/mnt", "/opt",
             "/private", "/private/etc", "/private/tmp", "/private/var", "/proc", "/root",
             "/run", "/run/media", "/sbin", "/sys", "/tmp", "/usr", "/var"]
    out = set(paths)
    if os.environ.get("HOME"):
        out.add(os.path.realpath(os.environ["HOME"]))
    return out


def check_target(path):
    """Return the real path to clean, or raise TargetError."""
    if not os.path.lexists(path):
        raise TargetError("not_found", path)
    if not os.path.isdir(path):
        raise TargetError("not_folder", path)
    real = os.path.realpath(path)
    key = os.path.normcase(real) if SYSTEM == "Windows" else real
    if key in _forbidden_paths():
        raise TargetError("forbidden", real)
    if os.path.basename(real.rstrip("\\/")) in SYSTEM_DIRS + ARCHIVE_DIRS:
        raise TargetError("junk_root", real)
    try:
        os.listdir(real)
    except OSError:
        raise TargetError("cannot_open", real)
    return real


# ---------------------------------------------------------------- scan ----
def _rules(windows, keep_trash, safe_mode):
    if safe_mode:
        junk_dirs, prune_dirs = set(ARCHIVE_DIRS), set(SYSTEM_DIRS)
    elif keep_trash:
        junk_dirs = (set(SYSTEM_DIRS) - {".Trashes"}) | set(ARCHIVE_DIRS)
        prune_dirs = {".Trashes"}
    else:
        junk_dirs, prune_dirs = set(SYSTEM_DIRS) | set(ARCHIVE_DIRS), set()
    junk_files = set(JUNK_FILES) | (set(WINDOWS_FILES) if windows else set())
    return junk_dirs, prune_dirs, junk_files


def _is_link(entry):
    try:
        if entry.is_symlink():
            return True
        if hasattr(entry, "is_junction") and entry.is_junction():    # Python 3.12+, Windows
            return True
    except OSError:
        return True
    return False


def _device(entry):
    """Device id of a directory entry. On Windows, DirEntry.stat() leaves st_dev at 0,
    so a full os.stat() is needed there."""
    if SYSTEM == "Windows":
        return os.stat(entry.path, follow_symlinks=False).st_dev
    return entry.stat(follow_symlinks=False).st_dev


def _disk_size(st):
    blocks = getattr(st, "st_blocks", None)
    if blocks is not None:
        return blocks * 512
    return st.st_size


def _tree_size(path):
    total = 0
    stack = [path]
    while stack:
        p = stack.pop()
        try:
            with os.scandir(p) as it:
                for e in it:
                    try:
                        st = e.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    total += _disk_size(st)
                    if not _is_link(e) and e.is_dir(follow_symlinks=False):
                        stack.append(e.path)
        except OSError:
            pass
    return total


def _count_trash_files(path):
    n = 0
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        for f in filenames:
            full = os.path.join(dirpath, f)
            if os.path.islink(full):
                continue
            if not f.startswith("._") and f != ".DS_Store":
                n += 1
    return n


def _category(name):
    if name.startswith("._"):
        return "appledouble"
    if name == ".DS_Store":
        return "ds_store"
    if name in WINDOWS_FILES:
        return "windows"
    return "system"


def scan(root, windows=False, keep_trash=False, safe_mode=None, cancel=None, progress=None):
    """Find the junk under root. root must come from check_target().
    safe_mode=None -> automatic (on for Mac-formatted drives)."""
    fs = fs_type(root)
    if safe_mode is None:
        safe_mode = fs in MAC_FILESYSTEMS
    junk_dirs, prune_dirs, junk_files = _rules(windows, keep_trash, safe_mode)
    result = ScanResult(root=root, safe_mode=safe_mode, fs=fs, windows=windows, keep_trash=keep_trash)
    try:
        root_dev = os.stat(root).st_dev
    except OSError:
        return result

    stack = [root]
    seen = 0
    while stack:
        if cancel is not None and cancel():
            break
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        for e in entries:
            seen += 1
            if progress is not None and seen % 500 == 0:
                progress(seen)
            if _is_link(e):
                continue                                  # never followed, never deleted
            name = e.name
            try:
                if e.is_dir(follow_symlinks=False):
                    if name in prune_dirs:
                        continue                          # left completely untouched
                    if name in junk_dirs:
                        result.items.append(Item(e.path, True, _category(name), _tree_size(e.path)))
                        if name == ".Trashes":
                            result.trash_files += _count_trash_files(e.path)
                        continue
                    if _device(e) == root_dev:
                        stack.append(e.path)              # stay on the same drive
                elif e.is_file(follow_symlinks=False):
                    if name.startswith("._") or name in junk_files:
                        st = e.stat(follow_symlinks=False)
                        result.items.append(Item(e.path, False, _category(name), _disk_size(st)))
            except OSError:
                continue
    result.items.sort(key=lambda i: i.path)
    return result


# --------------------------------------------------------------- clean ----
def _make_writable_and_retry(func, path, *_):
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD | (stat.S_IEXEC if os.path.isdir(path) else 0))
        func(path)
    except OSError:
        pass


def _delete(item):
    p = item.path
    if os.path.islink(p):
        return                                            # changed since the scan: leave it
    if item.is_dir:
        if os.path.isdir(p):
            if sys.version_info >= (3, 12):
                shutil.rmtree(p, onexc=_make_writable_and_retry)
            else:
                shutil.rmtree(p, onerror=_make_writable_and_retry)
    elif os.path.isfile(p):
        try:
            os.remove(p)
        except PermissionError:
            _make_writable_and_retry(os.remove, p)


def clean(scan_result, progress=None):
    """Delete the items of a scan, then rescan to report what is left."""
    for n, item in enumerate(scan_result.items, 1):
        try:
            _delete(item)
        except OSError:
            pass
        if progress is not None:
            progress(n, len(scan_result.items))
    after = scan(scan_result.root, windows=scan_result.windows,
                 keep_trash=scan_result.keep_trash, safe_mode=scan_result.safe_mode)
    before_paths = {i.path for i in scan_result.items}
    left = [i for i in after.items if i.path in before_paths]
    deleted = len(scan_result.items) - len(left)
    freed = scan_result.total_size - sum(i.size for i in left)
    only_system = bool(left) and all(i.category == "system" for i in left)
    return CleanResult(deleted=deleted, freed=freed, left=left, only_system_left=only_system)


# -------------------------------------------------------------- drives ----
def _win_drive_root(path):
    drive = os.path.splitdrive(os.path.realpath(path))[0]
    return drive + "\\"


def _win_volume_info(root):
    import ctypes
    label = ctypes.create_unicode_buffer(261)
    fsname = ctypes.create_unicode_buffer(261)
    ok = ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(root), label, 261, None, None, None, fsname, 261)
    if not ok:
        return "", ""
    return label.value, fsname.value


def _size(path):
    try:
        return shutil.disk_usage(path).total
    except OSError:
        return 0


def list_drives():
    """SD cards and USB drives plugged in (and the usual console ROM folders on Linux)."""
    drives = []
    if SYSTEM == "Darwin":
        try:
            names = sorted(os.listdir("/Volumes"))
        except OSError:
            names = []
        for n in names:
            p = os.path.join("/Volumes", n)
            if n.startswith(".") or n.startswith("com.apple") or os.path.islink(p) or not os.path.isdir(p):
                continue
            fs = fs_type(p)
            drives.append(Drive(p, n, fs, _size(p), fs in MAC_FILESYSTEMS))
    elif SYSTEM == "Windows":
        import ctypes
        k32 = ctypes.windll.kernel32
        mask = k32.GetLogicalDrives()
        system_drive = os.environ.get("SystemDrive", "C:").upper()
        for i, letter in enumerate(string.ascii_uppercase):
            if not mask & (1 << i):
                continue
            root = f"{letter}:\\"
            kind = k32.GetDriveTypeW(ctypes.c_wchar_p(root))
            # 2 = removable (SD, USB sticks), 3 = fixed (USB hard drives / SSDs)
            if kind not in (2, 3) or f"{letter}:" == system_drive:
                continue
            label, fs = _win_volume_info(root)
            if not fs:
                continue                                  # empty card reader slot
            name = f"{label} ({letter}:)" if label else f"{letter}:"
            drives.append(Drive(root, name, fs.lower(), _size(root), fs.lower() in MAC_FILESYSTEMS))
    else:
        # Every mounted drive under /media, /run/media, /mnt (Linux desktops, Raspberry Pi,
        # Steam Deck, ChromeOS, WSL), then the ROM folder of the console itself
        seen = set()
        mounts = []
        try:
            with open("/proc/mounts", encoding="utf-8", errors="replace") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 3:
                        mounts.append((parts[1].replace("\\040", " "), parts[2].lower()))
        except OSError:
            pass
        skip_fs = {"tmpfs", "proc", "sysfs", "devtmpfs", "overlay", "squashfs", "autofs", "cgroup2"}
        for mnt, fs in mounts:
            if not mnt.startswith(("/media/", "/run/media/", "/mnt/")) or fs in skip_fs:
                continue
            if mnt.startswith(("/mnt/wsl", "/mnt/wslg", "/mnt/c")) and mnt.count("/") <= 2:
                continue                                  # WSL system mounts
            if mnt not in seen and os.path.isdir(mnt):
                seen.add(mnt)
                drives.append(Drive(mnt, os.path.basename(mnt), fs, _size(mnt), fs in MAC_FILESYSTEMS))
        for p in CONSOLE_ROOTS:
            if os.path.isdir(p) and not os.path.islink(p) and p not in seen:
                fs = fs_type(p)
                drives.append(Drive(p, os.path.basename(p), fs, _size(p), fs in MAC_FILESYSTEMS))
    return drives


def eject(path):
    """Eject the drive holding path. Returns True when it is gone."""
    if SYSTEM == "Darwin":
        if not path.startswith("/Volumes/"):
            return False
        vol = "/Volumes/" + path[len("/Volumes/"):].split("/")[0]
        _run(["/usr/sbin/diskutil", "eject", vol])
        return not os.path.exists(vol)
    if SYSTEM == "Windows":
        drive = _win_drive_root(path)[:2]
        ps = ("$d = (New-Object -ComObject Shell.Application).Namespace(17).ParseName('%s'); "
              "if ($d) { $d.InvokeVerb('Eject') }; Start-Sleep -Seconds 2" % drive)
        _run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps])
        return not os.path.exists(drive + "\\")
    for cmd in (["gio", "mount", "-e", path], ["umount", path]):
        if shutil.which(cmd[0]):
            _run(cmd)
            if not os.path.ismount(path) and not os.path.exists(path):
                return True
    return not os.path.exists(path)


def human_size(n, units=("B", "KB", "MB", "GB", "TB"), decimal="."):
    value = float(n)
    for u in units:
        if value < 1024 or u == units[-1]:
            if u == units[0]:
                return f"{int(value)} {u}"
            return f"{value:.1f}".replace(".", decimal) + f" {u}"
        value /= 1024
    return f"{n} {units[0]}"


# ----------------------------------------------------------------- CLI ----
def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog="dotcleaner_core", description="dotcleaner engine (same rules as dotcleaner.sh)")
    ap.add_argument("path")
    ap.add_argument("-n", "--dry-run", action="store_true")
    ap.add_argument("-y", "--yes", action="store_true")
    ap.add_argument("-w", "--windows", action="store_true")
    ap.add_argument("-k", "--keep-trash", action="store_true")
    ap.add_argument("-V", "--version", action="version", version=f"dotcleaner {VERSION}")
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):              # file names in any language
        try:
            stream.reconfigure(encoding="utf-8", errors="surrogateescape")
        except (AttributeError, ValueError):
            pass
    try:
        root = check_target(a.path)
    except TargetError as e:
        print(f"Error: {e.code}: {e.path}", file=sys.stderr)
        return 1
    res = scan(root, windows=a.windows, keep_trash=a.keep_trash)
    if res.safe_mode:
        print("Mac-formatted drive: safe mode")
    print(f"Total: {len(res.items)} items, {human_size(res.total_size)}")
    if a.dry_run:
        print("  Would be deleted:")
        for i in res.items:
            print("    " + os.path.relpath(i.path, root))
        print("  Preview only: nothing was deleted.")
        return 0
    if not a.yes:
        print("Error: add -y to delete.", file=sys.stderr)
        return 1
    out = clean(res)
    print(f"Done: {out.deleted} items deleted, {len(out.left)} left.")
    return 0 if not out.left or out.only_system_left else 1


if __name__ == "__main__":
    sys.exit(main())
