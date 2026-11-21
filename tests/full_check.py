#!/usr/bin/env python3
"""
Full check of every version of Dotcleaner, in one command.

  1. static      ShellCheck, pure ASCII, same VERSION everywhere, console launchers up to
                 date, SAME cleaning rules in the shell, the app engine and the referee,
                 complete translations
  2. shells      tests/run_tests.sh with every shell found (bash, dash, BusyBox, ksh,
                 mksh, posh, yash, zsh)
  3. audits      file-by-file deletion audit (tests/audit.py) of the 3 engines:
                 shell (every shell, old BusyBox find too), app engine, console launcher
  4. cross       the 3 engines on copies of the same random cards: identical results
  5. edge        extreme cards: 120 nested folders, 10 000 junk files, Unicode NFC/NFD,
                 names starting with "-", read-only junk, empty card, card full of junk
  6. menu        the interactive menu driven like a user (options, scan, cancel, clean)
  7. app         tests/test_app.py (window, 5 languages, real clean) when PySide6 is there
  8. mutations   deliberate bugs in copies of each engine: the audit must catch every one

Usage: python3 tests/full_check.py [--cards 300] [--quick]
"""
import argparse
import os
import random
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "app"))
import audit                                   # noqa: E402  (referee, card builders)

RESULTS = []                                   # (section, check, ok, detail)


def record(section, check, ok, detail=""):
    RESULTS.append((section, check, ok, detail))
    print(f"  {'ok  ' if ok else 'FAIL'}  [{section}] {check}" + (f" — {detail}" if detail else ""), flush=True)


def run(cmd, env=None, cwd=ROOT, timeout=1800, stdin=subprocess.DEVNULL):
    e = dict(os.environ, NO_COLOR="1")
    if env:
        e.update(env)
    return subprocess.run(cmd, env=e, cwd=cwd, stdin=stdin, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=timeout)


def available_shells():
    shells = []
    for name, cmd in [("dash", "dash"), ("bash", "bash"), ("bash --posix", "bash --posix"),
                      ("ksh", "ksh"), ("mksh", "mksh"), ("posh", "posh"), ("yash", "yash"),
                      ("zsh", "zsh --emulate sh")]:
        if shutil.which(cmd.split()[0]):
            shells.append((name, cmd))
    bb = shutil.which("busybox")
    if bb:
        appdir = os.path.join(tempfile.gettempdir(), "dotcleaner-bb")
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
            subprocess.run([bb, "--install", "-s", appdir], stderr=subprocess.DEVNULL)
        shells.append(("busybox", f"{bb} sh", {"PATH": appdir}))
    return [s if len(s) == 3 else (s[0], s[1], {}) for s in shells]


# ------------------------------------------------------------------ 1. static
def static_checks():
    sec = "static"
    files = ["dotcleaner.sh", "install.sh", "dotcleaner.command", "console/Dotcleaner.sh",
             "tools/make_console.sh", "tests/run_tests.sh", "tests/macos_card.sh"]
    if shutil.which("shellcheck"):
        r = run(["shellcheck", "-s", "sh"] + files)
        record(sec, "ShellCheck on every shell script", r.returncode == 0, r.stdout.decode()[:300])
    for f in ["dotcleaner.sh", "install.sh", "dotcleaner.command", "console/Dotcleaner.sh"]:
        data = open(os.path.join(ROOT, f), "rb").read()
        record(sec, f"{f} is pure ASCII", all(b < 128 for b in data))
    sh = open(os.path.join(ROOT, "dotcleaner.sh"), encoding="ascii").read()
    core_src = open(os.path.join(ROOT, "app", "dotcleaner_core.py"), encoding="utf-8").read()
    v_sh = re.search(r'^VERSION="(.*)"$', sh, re.M).group(1)
    v_core = re.search(r'^VERSION = "(.*)"$', core_src, re.M).group(1)
    v_log = re.search(r"^## \[([^\]]+)\]", open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read(), re.M).group(1)
    record(sec, f"same VERSION in shell, app, CHANGELOG ({v_sh})", v_sh == v_core == v_log, f"{v_sh}/{v_core}/{v_log}")
    for launcher in ["console/Dotcleaner.sh", "console/Onion/App/Dotcleaner/launch.sh"]:
        expected = sh.replace("\nCONSOLE_LAUNCHER=0\n", "\nCONSOLE_LAUNCHER=1\n")
        got = open(os.path.join(ROOT, launcher), encoding="ascii").read()
        record(sec, f"{launcher} = dotcleaner.sh in console mode", got == expected)

    def sh_list(name):
        return set(re.search(rf"^{name}='([^']*)'", sh, re.M).group(1).split())
    import dotcleaner_core as core
    rules = {
        "files": (sh_list("JUNK_FILES"), {"._*"} | set(core.JUNK_FILES), {"._*"} | audit.JUNK_FILES),
        "system folders": (sh_list("SYSTEM_DIRS"), set(core.SYSTEM_DIRS), audit.SYSTEM_DIRS),
        "archive folders": (sh_list("ARCHIVE_DIRS"), set(core.ARCHIVE_DIRS), audit.JUNK_DIRS - audit.SYSTEM_DIRS),
        "Windows files": (sh_list("WINDOWS_FILES"), set(core.WINDOWS_FILES), audit.WINDOWS_FILES),
    }
    for what, (a, b, c) in rules.items():
        record(sec, f"same {what} in shell, app and referee", a == b == c, f"{sorted(a)}")
    try:
        from i18n import LANGUAGES, T
        ok = all(set(T[c]) == set(T["en"]) for c in LANGUAGES) and len(LANGUAGES) == 5
        record(sec, "app translations complete (5 languages)", ok)
    except Exception as e:                                       # pragma: no cover
        record(sec, "app translations complete", False, str(e))


# ------------------------------------------------------------------ 2. shells
def shell_tests(shells):
    for name, cmd, env in shells:
        r = run(["sh", "tests/run_tests.sh", cmd], env=env)
        m = re.search(rb"(\d+) passed, (\d+) failed", r.stdout)
        ok = r.returncode == 0 and m and m.group(2) == b"0"
        record("shells", f"run_tests.sh with {name}", bool(ok), m.group(0).decode() if m else r.stdout.decode()[-200:])


# ------------------------------------------------------------------ 3. audits
def audits(shells, cards, seed):
    configs = []
    for name, cmd, env in shells:
        configs.append((f"shell engine, {name}", ["--engine", "sh", "--shell", cmd], env))
    for name, cmd, env in shells:
        if name in ("dash", "busybox"):
            configs.append((f"shell engine, {name}, old find (no -exec +)", ["--engine", "sh", "--shell", cmd],
                            dict(env, DOTCLEANER_NO_EXEC_PLUS="1")))
    for name, cmd, env in shells:
        if name in ("dash", "bash", "busybox", "posh"):
            configs.append((f"console launcher, {name}", ["--engine", "console", "--shell", cmd], env))
    configs.append(("app engine (Python)", ["--engine", "python"], {}))
    total_paths = 0
    for i, (label, args, env) in enumerate(configs):
        if "PATH" in env:
            env = dict(env, PATH=env["PATH"] + os.pathsep + os.environ["PATH"])
        r = run([sys.executable, "tests/audit.py", "--cards", str(cards), "--seed", str(seed + i)] + args, env=env)
        out = r.stdout.decode(errors="replace")
        m = re.search(r"paths checked: (\d+)", out)
        total_paths += int(m.group(1)) if m else 0
        record("audits", label, r.returncode == 0 and "AUDIT OK" in out,
               (m.group(0) if m else "") + ("" if r.returncode == 0 else " " + out[-400:]))
    return total_paths


# ------------------------------------------------------------------ helpers for 4-6
def engines(shells):
    dash = next((c for n, c, e in shells if n == "dash"), "sh")
    return [
        ("shell", lambda card, extra=(): [*shlex.split(dash), "dotcleaner.sh", "-y", *extra, card], {}),
        ("app engine", lambda card, extra=(): [sys.executable, "app/dotcleaner_core.py", "-y", *extra, card], {}),
        ("console", lambda card, extra=(): [*shlex.split(dash), "console/Dotcleaner.sh"],
         {"DOTCLEANER_NO_TTY": "1"}),
    ]


def run_engine(eng, card, log_dir, extra=()):
    name, mk, env = eng
    env = dict(env, DOTCLEANER_FS_TYPE="exfat", PYTHONIOENCODING="utf-8")
    if name == "console":
        env.update(DOTCLEANER_CONSOLE_ROOT=card, DOTCLEANER_LOG=os.path.join(log_dir, "console.log"))
    return run(mk(card, extra), env=env)


# ------------------------------------------------------------------ 4. cross-engine
def cross_engine(shells, n, seed):
    rng = random.Random(seed)
    engs = engines(shells)
    mismatch = 0
    base = tempfile.mkdtemp(prefix="dotcleaner-cross.")
    try:
        for i in range(n):
            work = os.path.join(base, f"c{i}")
            outside = audit.make_outside(work)
            src = os.path.join(work, "src")
            os.makedirs(src)
            audit.fuzz_card(src, outside, rng)
            results = {}
            for eng in engs:
                card = os.path.join(work, eng[0].replace(" ", "_"))
                shutil.copytree(src, card, symlinks=True)
                run_engine(eng, card, work)
                results[eng[0]] = {os.path.relpath(p, card) for p in audit.all_paths(card)}
            if len({frozenset(v) for v in results.values()}) != 1:
                mismatch += 1
            shutil.rmtree(work, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    record("cross", f"shell, app engine and console give identical results on {n} random cards",
           mismatch == 0, f"{mismatch} different")


# ------------------------------------------------------------------ 5. edge cases
def edge_cases(shells):
    def deep(card):
        p = card
        for i in range(120):
            p = os.path.join(p, f"d{i}")
        os.makedirs(p)
        for f in ("._deep.gba", ".DS_Store", "deep.gba"):
            audit.touch(os.path.join(p, f), 1)
        os.makedirs(os.path.join(p, "__MACOSX"))

    def many(card):
        os.makedirs(os.path.join(card, "roms", "arcade"))
        for i in range(10000):
            open(os.path.join(card, "roms", "arcade", f"._game{i}.zip"), "wb").close()
            if i % 10 == 0:
                open(os.path.join(card, "roms", "arcade", f"game{i}.zip"), "wb").close()

    def unicode_names(card):
        for name in ["Pokémon Émeraude.gba", "ポケモン.gba", "Pokémon Rubis.gba", "पोकेमॉन.gba"]:
            for form in ("NFC", "NFD"):
                n = unicodedata.normalize(form, name)
                audit.touch(os.path.join(card, "roms", n), 1)
                audit.touch(os.path.join(card, "roms", "._" + n), 1)

    def dashes(card):
        for n in ["-rf", "--help", "-", "._-rf", "._--help", "-.DS_Store", ".DS_Store-", "-n.gba"]:
            audit.touch(os.path.join(card, "roms", n), 1)
        os.makedirs(os.path.join(card, "-dir", "__MACOSX"))
        audit.touch(os.path.join(card, "-dir", "._x"), 1)

    def readonly(card):
        for n in ["._ro.gba", ".DS_Store", "ro.gba"]:
            p = os.path.join(card, "roms", n)
            audit.touch(p, 1)
            os.chmod(p, 0o444)
        d = os.path.join(card, ".Spotlight-V100", "Store")
        os.makedirs(d)
        audit.touch(os.path.join(d, "db"), 1)
        os.chmod(os.path.join(d, "db"), 0o444)

    def empty(card):
        os.makedirs(os.path.join(card, "roms"))

    def only_junk(card):
        for n in ["._a", "._b", ".DS_Store", ".apdisk"]:
            audit.touch(os.path.join(card, n), 1)
        os.makedirs(os.path.join(card, ".Trashes", "501"))
        os.makedirs(os.path.join(card, ".fseventsd"))

    def mixed_kinds(card):
        # junk names used for the "wrong" kind: must follow the rules exactly
        os.makedirs(os.path.join(card, ".DS_Store"))                # a folder named .DS_Store: kept
        audit.touch(os.path.join(card, ".DS_Store", "keep.txt"), 1)
        audit.touch(os.path.join(card, "__MACOSX"), 1)              # a file named __MACOSX: kept
        audit.touch(os.path.join(card, ".Trashes"), 1)              # a file named .Trashes: kept
        os.makedirs(os.path.join(card, "._folder"))                 # a folder named ._x: kept
        audit.touch(os.path.join(card, "._folder", "._inner"), 1)   # ... but junk inside: removed

    scenarios = [("120 nested folders", deep), ("10 000 junk files", many),
                 ("Unicode names, NFC and NFD", unicode_names), ("names starting with '-'", dashes),
                 ("read-only junk", readonly), ("empty card", empty), ("card with only junk", only_junk),
                 ("junk names on the wrong kind of item", mixed_kinds)]
    base = tempfile.mkdtemp(prefix="dotcleaner-edge.")
    try:
        for label, build in scenarios:
            for eng in engines(shells):
                work = os.path.join(base, f"{label[:8]}-{eng[0]}".replace(" ", "_"))
                card = os.path.join(work, "NO NAME")
                os.makedirs(card)
                try:
                    build(card)
                except OSError as e:                              # e.g. filesystem limits
                    record("edge", f"{label} ({eng[0]})", True, f"skipped: {e}")
                    continue
                must_go, _ = audit.referee(card)
                before = audit.all_paths(card)
                t0 = time.time()
                r = run_engine(eng, card, work)
                dt = time.time() - t0
                after = audit.all_paths(card)
                gone = before - after
                ok = gone == must_go and not (after - before) and r.returncode == 0
                detail = f"{len(must_go)} junk, {len(before) - len(must_go)} kept, {dt:.1f}s"
                if not ok:
                    detail += f" | wrongly deleted {sorted(gone - must_go)[:3]} left {sorted(must_go - gone)[:3]} rc={r.returncode}"
                record("edge", f"{label} ({eng[0]})", ok, detail)
                subprocess.run(["chmod", "-R", "u+w", work])
                shutil.rmtree(work, ignore_errors=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ------------------------------------------------------------------ 6. menu
def menu_test():
    if os.name == "nt":
        return
    import pty
    import select

    def drive(inputs, card):
        pid, fd = pty.fork()
        if pid == 0:
            os.environ.update(DOTCLEANER_FS_TYPE="exfat", NO_COLOR="1", TERM="xterm")
            os.chdir(ROOT)
            os.execvp("sh", ["sh", "dotcleaner.sh"])
        out = b""

        def drain(t):
            nonlocal out
            end = time.time() + t
            while time.time() < end:
                r, _, _ = select.select([fd], [], [], 0.05)
                if r:
                    try:
                        out += os.read(fd, 65536)
                    except OSError:
                        return
        for i in inputs:
            drain(0.4)
            os.write(fd, (i + "\n").encode())
        drain(0.8)
        os.waitpid(pid, 0)
        return out.decode(errors="replace")

    base = tempfile.mkdtemp(prefix="dotcleaner-menu.")
    try:
        work = os.path.join(base, "w")
        outside = audit.make_outside(work)
        card = os.path.join(work, "EASYROMS")
        os.makedirs(card)
        audit.realistic_card(card, outside)
        before = audit.all_paths(card)
        out = drive(["1", "o", card, "3", "y", "", "4", "n", "", "q"], card)
        record("menu", "menu: other folder, scan with list, clean cancelled -> nothing deleted",
               audit.all_paths(card) == before and "Preview only" in out and "Cancelled" in out)
        must_go, _ = audit.referee(card, windows=True)
        out = drive(["1", "o", card, "2", "1", "", "4", "y", "", "q"], card)
        gone = before - audit.all_paths(card)
        record("menu", "menu: Windows option on, clean confirmed -> exactly the junk deleted",
               gone == must_go and "Done:" in out, f"{len(gone)} deleted / {len(must_go)} expected")
        out = drive(["h", "", "q"], card)
        record("menu", "menu: help page and quit", "Help" in out and "1. Choose a drive" in out)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ------------------------------------------------------------------ 7. app
def app_tests():
    try:
        import PySide6  # noqa: F401
    except ImportError:
        record("app", "tests/test_app.py", True, "skipped: PySide6 not installed")
        return
    r = run([sys.executable, "tests/test_app.py"], env={"QT_QPA_PLATFORM": "offscreen"})
    m = re.search(rb"(\d+) passed, (\d+) failed", r.stdout)
    record("app", "window, 5 languages, scan/cancel/clean, safe mode (test_app.py)",
           r.returncode == 0, m.group(0).decode() if m else r.stdout.decode()[-300:])


# ------------------------------------------------------------------ 8. mutations
MUTATIONS = [
    ("shell", "dotcleaner.sh", "JUNK_FILES='._* .DS_Store .apdisk'", "JUNK_FILES='._* .DS_Store .apdisk *.srm'", "deletes saves (*.srm)"),
    ("shell", "dotcleaner.sh", "JUNK_FILES='._* .DS_Store .apdisk'", "JUNK_FILES='._* .DS_Store'", "forgets .apdisk"),
    ("shell", "dotcleaner.sh", 'set -- "$_jf_root" -xdev', 'set -- -L "$_jf_root" -xdev', "follows symlinks"),
    ("shell", "dotcleaner.sh", "set -- \"$@\" -o -type f \\(", "set -- \"$@\" -o \\(", "deletes links named like junk"),
    ("shell", "dotcleaner.sh", "JUNK_DIRS=$ARCHIVE_DIRS\n    PRUNE_DIRS=$SYSTEM_DIRS", "JUNK_DIRS=\"$SYSTEM_DIRS $ARCHIVE_DIRS\"\n    PRUNE_DIRS=''", "ignores safe mode"),
    ("console", "dotcleaner.sh", 'do rm -rf "${1}" "${2}"', 'do rm -rf "${1}" "${1%/*}"/*.zip "${2}"', "console batch deletes games next to junk"),
    ("console", "dotcleaner.sh", 'for f do rm -rf "$f" && echo 1; done', 'for f do rm -rf "$f" "${f%/*}"/*.zip && echo 1; done', "console deletes games next to the last junk"),
    ("shell", "dotcleaner.sh", '      delete) find "$@" -exec rm -rf {} + ;;', '      delete) find "$@" -exec sh -c \'rm -rf "$@" "${1%/*}"/*.zip\' sh {} + ;;', "batch delete also removes games"),
    ("python", "app/dotcleaner_core.py", 'if name.startswith("._") or name in junk_files:', 'if name.startswith(".") or name in junk_files:', "deletes every hidden file"),
    ("python", "app/dotcleaner_core.py", "                    if name in prune_dirs:\n                        continue", "                    if False:\n                        continue", "ignores safe mode / -k"),
    ("python", "app/dotcleaner_core.py", "junk_files = set(JUNK_FILES) | (set(WINDOWS_FILES) if windows else set())", "junk_files = set(JUNK_FILES) | set(WINDOWS_FILES)", "ignores the Windows option"),
]


def mutations(cards):
    for engine, f, old, new, label in MUTATIONS:
        tmp = tempfile.mkdtemp(prefix="dotcleaner-mut.")
        try:
            for d in ("tests", "app", "console", "tools"):
                shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp, d), ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy(os.path.join(ROOT, "dotcleaner.sh"), tmp)
            src = open(os.path.join(tmp, f), encoding="utf-8").read()
            if old not in src:
                record("mutations", f"{engine}: {label}", False, "mutation point not found")
                continue
            open(os.path.join(tmp, f), "w", encoding="utf-8").write(src.replace(old, new, 1))
            if engine == "console":
                subprocess.run(["sh", "tools/make_console.sh"], cwd=tmp, stdout=subprocess.DEVNULL)
            args = {"shell": ["--engine", "sh", "--shell", "dash" if shutil.which("dash") else "sh"],
                    "console": ["--engine", "console", "--shell", "dash" if shutil.which("dash") else "sh"],
                    "python": ["--engine", "python"]}[engine]
            r = run([sys.executable, "tests/audit.py", "--cards", str(cards)] + args, cwd=tmp)
            caught = r.returncode != 0
            kinds = sorted(set(re.findall(r"DELETED WRONG FILES|junk left behind|OUTSIDE the card|dry-run list differs",
                                          r.stdout.decode(errors="replace"))))
            record("mutations", f"{engine}: bug '{label}' caught", caught, ", ".join(kinds))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ main
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--cards", type=int, default=300, help="random cards per audit")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--quick", action="store_true", help="fewer cards, no mutations")
    a = ap.parse_args()
    cards = 40 if a.quick else a.cards
    shells = available_shells()
    t0 = time.time()
    print(f"Dotcleaner full check — shells: {', '.join(n for n, _, _ in shells)}\n")
    print("1. static");    static_checks()
    print("2. shells");    shell_tests(shells)
    print("3. audits");    paths = audits(shells, cards, a.seed)
    print("4. cross");     cross_engine(shells, 25 if a.quick else 120, a.seed)
    print("5. edge");      edge_cases(shells)
    print("6. menu");      menu_test()
    print("7. app");       app_tests()
    if not a.quick:
        print("8. mutations"); mutations(60)
    fails = [r for r in RESULTS if not r[2]]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} checks passed, "
          f"{paths} paths audited, {time.time() - t0:.0f}s")
    for s, c, _, d in fails:
        print(f"  FAIL [{s}] {c} — {d}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
