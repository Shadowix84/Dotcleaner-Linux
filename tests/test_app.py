#!/usr/bin/env python3
"""
Tests of the desktop app (app/dotcleaner_gui.py + app/i18n.py), run headless.

  * every language has every text, with the same {placeholders} as English
  * the window drives a real clean like a user: choose the drive, Scan, Clean,
    confirm -> junk gone, games kept; Cancel -> nothing deleted
  * safe mode on a Mac-formatted drive, system/home folders refused

Usage: python3 tests/test_app.py        (needs: pip install PySide6-Essentials)
"""
import os
import re
import shutil
import sys
import tempfile
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["DOTCLEANER_FS_TYPE"] = "exfat"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "app"))

from PySide6.QtCore import QSettings                      # noqa: E402
from PySide6.QtWidgets import QApplication                # noqa: E402

import dotcleaner_core as core                            # noqa: E402
import dotcleaner_gui as gui                              # noqa: E402
from i18n import LANGUAGES, T                             # noqa: E402

PASS = FAIL = 0


def check(desc, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok    {desc}")
    else:
        FAIL += 1
        print(f"  FAIL  {desc}")


def wait_idle(app, w, timeout=30):
    end = time.time() + timeout
    time.sleep(0.05)
    while time.time() < end:
        app.processEvents()
        if not w.busy:
            app.processEvents()
            return True
        time.sleep(0.02)
    return False


def make_card(base):
    card = os.path.join(base, "EASYROMS")
    keep = ["roms/gba/Pokemon Emerald.gba", "roms/gba/Pokemon Emerald.srm", "bios/gba_bios.bin",
            "roms/gba/Game._beta.gba", "roms/.keep", "roms/psx/Thumbs.db"]
    junk = ["roms/gba/._Pokemon Emerald.gba", "roms/gba/.DS_Store", ".Spotlight-V100/Store-V2/db",
            ".Trashes/501/old.gba", ".fseventsd/0001", "__MACOSX/._x", "._.Trashes", ".apdisk"]
    for f in keep + junk:
        p = os.path.join(card, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(b"x")
    return card, keep, junk


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")   # Windows console
    except (AttributeError, ValueError):
        pass
    print("dotcleaner app tests\n")
    app = QApplication.instance() or QApplication(sys.argv)
    tmp = tempfile.mkdtemp(prefix="dotcleaner-apptest.")
    try:
        # --- translations -------------------------------------------------------
        en = T["en"]
        check("5 languages: en, fr, es, zh, hi", list(LANGUAGES) == ["en", "fr", "es", "zh", "hi"])
        for code in LANGUAGES:
            missing = set(en) - set(T[code])
            check(f"{code}: every text translated", not missing)
            bad = [k for k in en if k in T[code] and
                   set(re.findall(r"{(\w+)}", en[k])) != set(re.findall(r"{(\w+)}", T[code][k]))]
            check(f"{code}: same placeholders as English", not bad)
            same = [k for k in en if code != "en" and T[code].get(k) == en[k]
                    and k not in ("step_options", "total", "about")]
            check(f"{code}: texts really translated", len(same) <= 2)

        settings = QSettings(os.path.join(tmp, "settings.ini"), QSettings.IniFormat)
        w = gui.MainWindow(settings)
        w.opt_eject.setChecked(False)
        for code in LANGUAGES:
            w.set_language(code)
            check(f"window switches to {LANGUAGES[code]}", w.scan_btn.text() == T[code]["scan_btn"]
                  and w.t_drive.text() == gui.step_title(T[code]["step_drive"]))
        w.set_language("en")
        check("language is remembered", settings.value("language") == "en")

        # --- scan (preview) -----------------------------------------------------
        card, keep, junk = make_card(tmp)
        w.add_folder(card)
        check("folder selected", w.selected_path() == os.path.realpath(card))
        w.start_scan()
        wait_idle(app, w)
        res = w.last_scan
        check("scan finds the 8 junk items", res is not None and len(res.items) == 8)
        check("scan deletes nothing", all(os.path.lexists(os.path.join(card, j)) for j in junk))
        check("trash warning shown", "Trash holds 1 file" in w.warning.text())
        check("status: preview only", "Preview only" in w.status.text())

        # --- clean, cancelled ---------------------------------------------------
        w._confirm = lambda res: False
        w.start_clean()
        wait_idle(app, w)
        check("cancel: nothing deleted", all(os.path.lexists(os.path.join(card, j)) for j in junk))

        # --- clean, confirmed ---------------------------------------------------
        w._confirm = lambda res: True
        w.start_clean()
        wait_idle(app, w)
        wait_idle(app, w)
        check("clean: junk deleted", not any(os.path.lexists(os.path.join(card, j)) for j in junk))
        check("clean: games, saves, BIOS kept", all(os.path.exists(os.path.join(card, k)) for k in keep))
        check("clean: Windows file kept (option off)", os.path.exists(os.path.join(card, "roms/psx/Thumbs.db")))
        check("status: done", "Done: 8 items deleted" in w.status.text())

        w.opt_windows.setChecked(True)
        w.start_clean()
        wait_idle(app, w)
        check("Windows option: Thumbs.db deleted", not os.path.exists(os.path.join(card, "roms/psx/Thumbs.db")))

        w.start_scan()
        wait_idle(app, w)
        check("second scan: already clean", "Already clean" in w.total.text())

        # --- French messages after a clean --------------------------------------
        w.set_language("fr")
        check("status follows the language", "Déjà propre" in w.status.text() or "Aperçu" in w.status.text()
              or "Déjà propre" in w.total.text())

        # --- safe mode ------------------------------------------------------------
        card2, keep2, junk2 = make_card(os.path.join(tmp, "mac"))
        os.environ["DOTCLEANER_FS_TYPE"] = "apfs"
        w.set_language("en")
        w.add_folder(card2)
        check("safe mode shown for a Mac disk", "safe mode" in w.drive_info.text())
        w.start_clean()
        wait_idle(app, w)
        check("safe mode: ._ and .DS_Store deleted",
              not os.path.exists(os.path.join(card2, "roms/gba/._Pokemon Emerald.gba"))
              and not os.path.exists(os.path.join(card2, "roms/gba/.DS_Store")))
        check("safe mode: system folders kept",
              os.path.exists(os.path.join(card2, ".Spotlight-V100/Store-V2/db"))
              and os.path.exists(os.path.join(card2, ".Trashes/501/old.gba")))
        os.environ["DOTCLEANER_FS_TYPE"] = "exfat"

        # --- refused targets ------------------------------------------------------
        home = os.path.expanduser("~")
        try:
            core.check_target(home)
            refused = False
        except core.TargetError as e:
            refused = e.code == "forbidden"
        check("home folder refused", refused)
        w.add_folder(home)
        w.start_scan()
        wait_idle(app, w)
        check("window shows the refusal", "system or home folder" in w.status.text())
        try:
            core.check_target(os.path.join(tmp, "nope"))
            nf = False
        except core.TargetError as e:
            nf = e.code == "not_found"
        check("missing folder refused", nf)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
