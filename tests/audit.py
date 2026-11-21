#!/usr/bin/env python3
"""
Deletion audit for dotcleaner.

Builds SD cards, snapshots EVERY path before and after running dotcleaner,
and compares what really disappeared with what an independent referee
(written here in Python, from the README rules, without using `find`)
says must disappear. Any difference -- one file too many or one too few --
fails the audit.

  1. a realistic card (ArkOS + Knulli layouts, saves, BIOS, media,
     PortMaster ports with hidden folders, configs...) with all the junk;
  2. random "fuzz" cards with tricky names (spaces, quotes, *, ?, \\, $,
     unicode, newlines, leading dashes, junk-like names that must stay),
     junk names used as files/folders/symlinks, dangling links, links
     pointing outside the card.

Each card is checked with the default options, -w and -k.
The dry-run list (-n) must also match exactly what is then deleted.

Usage: python3 tests/audit.py [--shell "sh"] [--cards 200] [--seed 1]
"""
import argparse
import os
import platform
import random
import shlex
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "dotcleaner.sh")

# ---- Referee: the rules, re-implemented independently -----------------------
JUNK_DIRS = {".Spotlight-V100", ".Trashes", ".fseventsd", ".TemporaryItems",
             ".DocumentRevisions-V100", ".AppleDouble", ".AppleDB",
             ".AppleDesktop", "__MACOSX"}
JUNK_FILES = {".DS_Store", ".apdisk"}
WINDOWS_FILES = {"Thumbs.db", "ehthumbs.db", "desktop.ini"}


def referee(root, windows=False, keep_trash=False):
    """Return (deleted, listed): every path that must disappear, and the
    top-level items the dry run must list (junk folders, not their content)."""
    deleted, listed = set(), set()
    junk_dirs = JUNK_DIRS - ({".Trashes"} if keep_trash else set())
    junk_files = JUNK_FILES | (WINDOWS_FILES if windows else set())

    def walk(path):
        for name in sorted(os.listdir(path)):
            p = os.path.join(path, name)
            st = os.lstat(p)
            is_link = os.path.islink(p)
            is_dir = not is_link and os.path.isdir(p)
            is_file = not is_link and os.path.isfile(p)
            if is_dir and name in junk_dirs:
                listed.add(p)
                deleted.add(p)
                deleted.update(all_paths(p))
            elif is_dir and keep_trash and name == ".Trashes":
                continue                      # -k: the Trash is left untouched
            elif is_dir:
                walk(p)
            elif is_file and (name.startswith("._") or name in junk_files):
                listed.add(p)
                deleted.add(p)
            # symlinks and anything else: never deleted, never followed
            del st
    walk(root)
    return deleted, listed


def all_paths(root):
    """Every path under root (not following symlinks), root excluded."""
    out = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for n in dirnames + filenames:
            out.add(os.path.join(dirpath, n))
    return out


# ---- Card builders ----------------------------------------------------------
def touch(path, size=0):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"x" * size)


def realistic_card(root, outside):
    keep = [
        # ArkOS / R36S
        "roms/gba/Pokemon - Emerald Version (USA, Europe).gba",
        "roms/gba/Pokemon - Emerald Version (USA, Europe).srm",
        "roms/gba/Pokemon - Emerald Version (USA, Europe).state1",
        "roms/gba/Pokémon Odyssey COMPLETE FR4.1.6 EXPANDED BAG.gba",
        "roms/gba/Game._beta.gba", "roms/gba/DS_Store.gba", "roms/gba/_._weird.gba",
        "roms/gba/gamelist.xml", "roms/gba/images/Pokemon - Emerald Version (USA, Europe)-image.png",
        "roms/snes/Super Mario World (USA).sfc", "roms/snes/Zelda [!] (E) {beta} #1.smc",
        "roms/psx/Final Fantasy VII (Disc 1).chd", "roms/psx/Final Fantasy VII.m3u",
        "roms/psx/Thumbs.db.bak", "roms/psx/desktop.ini.txt",
        "roms/nds/.hidden_save.sav", "roms/nds/.keep", "roms/n64/.DS_Store.bak",
        "roms/n64/.DS_Storex", "roms/n64/.ds_store", "roms/n64/._",
        "roms/arcade/mslug.zip", "roms/arcade/__MACOSX.zip",
        "roms/ports/PortMaster/PortMaster.sh", "roms/ports/stardew/.config/StardewValley/startup_preferences",
        "roms/ports/stardew/.local/share/StardewValley/Saves/Farm_1/Farm_1",
        "roms/ports/celeste/.git/HEAD",
        "roms/themes/es-theme-art-book-next/.gitattributes",
        "bios/gba_bios.bin", "bios/scph5501.bin", "bios/.version",
        "BGM/01 - Title.mp3", ".Trashes-notreally/x", "Trashes/x", "fseventsd/x",
        # Knulli / Batocera (SHARE)
        "system/batocera.conf", "system/.ssh/known_hosts", "system/.cache/emulationstation/x",
        "system/configs/retroarch/retroarchcustom.cfg",
        "saves/gba/Pokemon - Emerald Version (USA, Europe).srm",
        "screenshots/screenshot-2026.11.21.png",
    ]
    junk = [
        "roms/gba/._Pokemon - Emerald Version (USA, Europe).gba",
        "roms/gba/._Pokemon - Emerald Version (USA, Europe).srm",
        "roms/gba/._Pokémon Odyssey COMPLETE FR4.1.6 EXPANDED BAG.gba",
        "roms/gba/.DS_Store", "roms/gba/images/.DS_Store", "roms/gba/images/._x-image.png",
        "roms/snes/._Zelda [!] (E) {beta} #1.smc", "roms/psx/Thumbs.db", "roms/psx/desktop.ini",
        "roms/psx/ehthumbs.db", "roms/ports/stardew/.config/._x", "roms/ports/celeste/.git/.DS_Store",
        "bios/._gba_bios.bin", "._.Trashes", ".DS_Store", ".apdisk", "._.DS_Store",
        ".Spotlight-V100/Store-V2/8F3/store.db", ".Spotlight-V100/VolumeConfiguration.plist",
        ".fseventsd/fseventsd-uuid", ".fseventsd/0000000000a1b2c3",
        ".Trashes/501/old rom.gba", ".Trashes/501/._old rom.gba", ".Trashes/501/sub/deep.sav",
        ".TemporaryItems/folders.501/TemporaryItems/x", ".DocumentRevisions-V100/db-V1/db.sqlite",
        "roms/arcade/__MACOSX/roms/arcade/._mslug.zip", "__MACOSX/._readme.txt",
        "system/.AppleDouble/x", "system/.AppleDB/x", ".AppleDesktop/x",
        "roms/.Spotlight-V100/x",
    ]
    for p in keep + junk:
        touch(os.path.join(root, p), 1)
    os.makedirs(os.path.join(root, "roms/._folder_not_a_file"), exist_ok=True)
    os.makedirs(os.path.join(root, "roms/empty"), exist_ok=True)
    # links: never followed, never deleted (even with junk names)
    touch(os.path.join(outside, "._outside.gba"), 1)
    touch(os.path.join(outside, ".DS_Store"), 1)
    os.makedirs(os.path.join(outside, "__MACOSX"), exist_ok=True)
    os.symlink(outside, os.path.join(root, "roms/link-to-outside"))
    os.symlink(os.path.join(outside, "__MACOSX"), os.path.join(root, "__MACOSX-link"))
    os.symlink(os.path.join(outside, "__MACOSX"), os.path.join(root, "roms/.Trashes"))
    os.symlink(os.path.join(root, "roms/gba/gamelist.xml"), os.path.join(root, "roms/gba/._link"))
    os.symlink("/nonexistent/target", os.path.join(root, "roms/.DS_Store"))


PIECES = ["._", ".", "_", "-", " ", "  ", "DS_Store", ".DS_Store", "Thumbs.db", "desktop.ini",
          "ehthumbs.db", ".apdisk", "__MACOSX", ".Trashes", ".Spotlight-V100", ".fseventsd",
          ".AppleDouble", ".TemporaryItems", "rom", "Pokémon", "日本語", ".gba", ".srm", ".sav",
          "[!]", "(USA)", "*", "?", "\\", "'", '"', "$HOME", "`x`", ";", "&", "#", "~", "%",
          "\n", "\t", "é", ".DS_STORE", "._.", "BIOS", "--", "-rf", "{}", "+"]
EXACT = [".DS_Store", ".apdisk", "Thumbs.db", "desktop.ini", "ehthumbs.db", "__MACOSX",
         ".Trashes", ".Spotlight-V100", ".fseventsd", ".TemporaryItems",
         ".DocumentRevisions-V100", ".AppleDouble", ".AppleDB", ".AppleDesktop"]


def rand_name(rng):
    if rng.random() < 0.3:
        return rng.choice(EXACT)
    name = "".join(rng.choice(PIECES) for _ in range(rng.randint(1, 3)))
    if rng.random() < 0.3:
        name = "._" + name
    if name in (".", "..") or "/" in name or len(name.encode()) > 200:
        name = "x" + name.replace("/", "")
    return name


def fuzz_card(root, outside, rng):
    dirs = [root]
    for _ in range(rng.randint(10, 60)):
        parent = rng.choice(dirs)
        p = os.path.join(parent, rand_name(rng))
        if os.path.lexists(p):
            continue
        kind = rng.random()
        try:
            if kind < 0.30:
                os.mkdir(p)
                dirs.append(p)
            elif kind < 0.85:
                touch(p, rng.randint(0, 3))
            elif kind < 0.92:
                os.symlink(outside, p)               # link to a folder outside the card
            elif kind < 0.96:
                target = rng.choice(dirs)
                os.symlink(target, p)                # link inside the card
            else:
                os.symlink("/does/not/exist", p)     # dangling link
        except OSError:
            pass


def make_outside(base):
    out = os.path.join(base, "outside")
    os.makedirs(out, exist_ok=True)
    for n in ["._secret.gba", ".DS_Store", "Thumbs.db"]:
        touch(os.path.join(out, n), 1)
    os.makedirs(os.path.join(out, ".Spotlight-V100"), exist_ok=True)
    return out


# ---- Running dotcleaner -------------------------------------------------------
def run(shell, args):
    env = dict(os.environ, DOTCLEANER_LANG="en", NO_COLOR="1")
    cmd = shlex.split(shell) + [SCRIPT] + args
    if platform.system() == "Darwin":
        cmd.append("--force")   # temp folders are on the Mac's own APFS disk
    return subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def dry_run_list(shell, root, opts):
    r = run(shell, ["-n"] + opts + [root])
    lines = r.stdout.decode("utf-8", "surrogateescape").split("\n")
    out, on = set(), False
    for ln in lines:
        if ln.strip().startswith("Would be deleted:"):
            on = True
            continue
        if on and ln.startswith("    "):
            out.add(os.path.join(root, ln[4:]))
        elif on:
            on = False
    return r.returncode, out


def check_card(shell, root, outside, opts, label, failures, stats):
    windows, keep = "-w" in opts, "-k" in opts
    before = all_paths(root)
    outside_before = all_paths(outside)
    must_go, must_list = referee(root, windows, keep)

    # 1) the dry run lists exactly the referee's items, and deletes nothing
    rc, listed = dry_run_list(shell, root, opts)
    has_newline = any("\n" in p for p in must_list)
    if rc != 0:
        failures.append(f"{label}: dry run exit code {rc}")
    if not has_newline and listed != must_list:
        failures.append(f"{label}: dry-run list differs\n  missing: {sorted(must_list - listed)[:5]}\n"
                        f"  extra: {sorted(listed - must_list)[:5]}")
    if all_paths(root) != before:
        failures.append(f"{label}: the dry run changed the card!")

    # 2) the real run deletes exactly the referee's set
    r = run(shell, ["-y"] + opts + [root])
    after = all_paths(root)
    gone = before - after
    if r.returncode != 0:
        failures.append(f"{label}: exit code {r.returncode}: {r.stderr.decode(errors='replace')[:200]}")
    if after - before:
        failures.append(f"{label}: new paths appeared: {sorted(after - before)[:5]}")
    wrongly_deleted = gone - must_go
    not_deleted = must_go - gone
    if wrongly_deleted:
        failures.append(f"{label}: DELETED WRONG FILES: {sorted(wrongly_deleted)[:10]}")
    if not_deleted:
        failures.append(f"{label}: junk left behind: {sorted(not_deleted)[:10]}")
    if all_paths(outside) != outside_before:
        failures.append(f"{label}: files OUTSIDE the card were touched!")
    stats["paths"] += len(before)
    stats["kept"] += len(before) - len(must_go)
    stats["deleted"] += len(must_go)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shell", default="sh")
    ap.add_argument("--cards", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    rng = random.Random(a.seed)
    failures = []
    stats = {"cards": 0, "paths": 0, "kept": 0, "deleted": 0}
    variants = [[], ["-w"], ["-k"], ["-w", "-k"]]

    base = os.path.realpath(tempfile.mkdtemp(prefix="dotcleaner-audit."))
    try:
        for opts in variants:
            work = os.path.join(base, "real" + "".join(opts))
            outside = make_outside(work)
            card = os.path.join(work, "NO NAME")
            os.makedirs(card)
            realistic_card(card, outside)
            check_card(a.shell, card, outside, opts, f"realistic card {opts}", failures, stats)
            stats["cards"] += 1
        for i in range(a.cards):
            opts = variants[i % len(variants)]
            work = os.path.join(base, f"fuzz{i}")
            outside = make_outside(work)
            card = os.path.join(work, "card")
            os.makedirs(card)
            fuzz_card(card, outside, rng)
            check_card(a.shell, card, outside, opts, f"fuzz card #{i} {opts}", failures, stats)
            stats["cards"] += 1
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print(f"shell: {a.shell} | cards: {stats['cards']} | paths checked: {stats['paths']} "
          f"| must keep: {stats['kept']} | must delete: {stats['deleted']}")
    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures[:30]:
            print(" -", f)
        sys.exit(1)
    print("AUDIT OK: nothing wrongly deleted, nothing left behind, dry run = real run.")


if __name__ == "__main__":
    main()
