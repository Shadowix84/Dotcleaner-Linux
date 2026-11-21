#!/usr/bin/env python3
"""
Dotcleaner — desktop app (macOS .dmg, Windows .exe).

Same menu as the shell version:  1. Choose a drive · 2. Options · 3. Scan · 4. Clean · Help · Quit
plus a language menu: English, Français, Español, 中文, हिन्दी.

Run from source:  pip install PySide6-Essentials && python3 app/dotcleaner_gui.py
Self-test:        python3 app/dotcleaner_gui.py --selftest
Screenshots:      python3 app/dotcleaner_gui.py --screenshots DIR
"""
import os
import sys
import tempfile
import threading

from PySide6.QtCore import QObject, QSettings, QLocale, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog, QFrame,
                               QGridLayout, QHBoxLayout, QLabel, QListWidget, QMessageBox, QProgressBar,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dotcleaner_core as core                                          # noqa: E402
from i18n import LANGUAGES, T, UNITS, items as items_text, tr          # noqa: E402

REPO_URL = "https://github.com/Shadowix84/Dotcleaner-Multi-Software"
CATEGORIES = ("appledouble", "ds_store", "system", "windows")


def resource(*parts):
    base = getattr(sys, "_MEIPASS", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    return os.path.join(base, *parts)


def default_language():
    code = QLocale.system().name()[:2].lower()
    return code if code in LANGUAGES else "en"


class Bridge(QObject):
    """Carries results from worker threads back to the window."""
    done = Signal(str, object)


class MainWindow(QWidget):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings or QSettings("Shadowix84", "dotcleaner")
        self.lang = self.settings.value("language", default_language())
        if self.lang not in LANGUAGES:
            self.lang = "en"
        self.busy = False
        self.last_scan = None
        self.extra_paths = []                     # folders added with "Other folder…"
        self.bridge = Bridge()
        self.bridge.done.connect(self._on_done)
        self._build()
        self.refresh_drives()
        self.retranslate()

    # ------------------------------------------------------------ layout --
    def _section(self, layout):
        title = QLabel()
        f = title.font()
        f.setPointSizeF(f.pointSizeF() * 1.15)
        f.setBold(True)
        title.setFont(f)
        layout.addSpacing(6)
        layout.addWidget(title)
        return title

    def _build(self):
        self.setWindowIcon(QIcon(resource("assets", "icon.png")))
        self.setMinimumWidth(640)
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 16)
        root.setSpacing(6)

        # Header: icon, name, tagline, language menu
        head = QHBoxLayout()
        logo = QLabel()
        pm = QPixmap(resource("assets", "icon.png"))
        if not pm.isNull():
            logo.setPixmap(pm.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        head.addWidget(logo)
        titles = QVBoxLayout()
        titles.setSpacing(0)
        name = QLabel(f"Dotcleaner <span style='color:gray;font-weight:normal'>{core.VERSION}</span>")
        f = name.font()
        f.setPointSizeF(f.pointSizeF() * 1.6)
        f.setBold(True)
        name.setFont(f)
        self.tagline = QLabel()
        self.tagline.setStyleSheet("color: gray;")
        titles.addWidget(name)
        titles.addWidget(self.tagline)
        head.addLayout(titles, 1)
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        for code, label in LANGUAGES.items():
            self.lang_combo.addItem(label, code)
        self.lang_combo.setCurrentIndex(list(LANGUAGES).index(self.lang))
        self.lang_combo.currentIndexChanged.connect(self._on_language)
        head.addWidget(self.lang_label)
        head.addWidget(self.lang_combo)
        root.addLayout(head)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        root.addWidget(line)

        # 1. Choose a drive
        self.t_drive = self._section(root)
        row = QHBoxLayout()
        self.drive_combo = QComboBox()
        self.drive_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.drive_combo.currentIndexChanged.connect(self._on_drive_changed)
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.refresh_drives)
        self.other_btn = QPushButton()
        self.other_btn.clicked.connect(self._choose_folder)
        row.addWidget(self.drive_combo, 1)
        row.addWidget(self.refresh_btn)
        row.addWidget(self.other_btn)
        root.addLayout(row)
        self.drive_info = QLabel()
        self.drive_info.setWordWrap(True)
        root.addWidget(self.drive_info)

        # 2. Options
        self.t_options = self._section(root)
        self.opt_windows = QCheckBox()
        self.opt_trash = QCheckBox()
        self.opt_eject = QCheckBox()
        self.opt_windows.setChecked(self.settings.value("windows", False, type=bool))
        self.opt_trash.setChecked(self.settings.value("keep_trash", False, type=bool))
        self.opt_eject.setChecked(self.settings.value("eject", True, type=bool))
        for cb in (self.opt_windows, self.opt_trash, self.opt_eject):
            cb.toggled.connect(self._on_options)
            root.addWidget(cb)

        # 3. Scan
        self.t_scan = self._section(root)
        self.scan_btn = QPushButton()
        self.scan_btn.clicked.connect(self.start_scan)
        root.addWidget(self.scan_btn)
        # one row per category: count + description (plain labels, no rich text)
        self.results = QWidget()
        grid = QGridLayout(self.results)
        grid.setContentsMargins(4, 2, 0, 2)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(2)
        self.rows = {}
        for r, cat in enumerate(CATEGORIES):
            num, text = QLabel(), QLabel()
            f = num.font()
            f.setBold(True)
            num.setFont(f)
            num.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid.addWidget(num, r, 0)
            grid.addWidget(text, r, 1)
            self.rows[cat] = (num, text)
        grid.setColumnStretch(1, 1)
        root.addWidget(self.results)
        self.total = QLabel()
        bold = self.total.font()
        bold.setBold(True)
        self.total.setFont(bold)
        root.addWidget(self.total)
        self.warning = QLabel()
        self.warning.setWordWrap(True)
        self.warning.setStyleSheet("color: #b26a00;")
        root.addWidget(self.warning)
        self.list_btn = QPushButton()
        self.list_btn.setFlat(True)
        self.list_btn.setStyleSheet("text-align: left; color: #2f6fde;")
        self.list_btn.clicked.connect(self._toggle_list)
        root.addWidget(self.list_btn)
        self.item_list = QListWidget()
        self.item_list.setMinimumHeight(140)
        root.addWidget(self.item_list)

        # 4. Clean
        self.t_clean = self._section(root)
        self.clean_btn = QPushButton()
        self.clean_btn.setMinimumHeight(38)
        self.clean_btn.setStyleSheet(
            "QPushButton { background: #2f6fde; color: white; border-radius: 6px; font-weight: bold; padding: 6px 18px; }"
            "QPushButton:disabled { background: #9db6e8; }"
            "QPushButton:hover { background: #255cc0; }")
        self.clean_btn.clicked.connect(self.start_clean)
        root.addWidget(self.clean_btn)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(6)
        root.addWidget(self.progress)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.RichText)
        root.addWidget(self.status)

        root.addStretch(1)
        foot = QHBoxLayout()
        self.help_btn = QPushButton()
        self.help_btn.clicked.connect(self.show_help)
        self.about = QLabel()
        self.about.setStyleSheet("color: gray;")
        self.quit_btn = QPushButton()
        self.quit_btn.clicked.connect(self.close)
        foot.addWidget(self.help_btn)
        foot.addStretch(1)
        foot.addWidget(self.about)
        foot.addStretch(1)
        foot.addWidget(self.quit_btn)
        root.addLayout(foot)
        self._clear_results()
        self._set_busy(False)

    # -------------------------------------------------------- translation --
    def t(self, key, **kw):
        return tr(self.lang, key, **kw)

    def size_text(self, n):
        units, dec = UNITS[self.lang]
        return core.human_size(n, units, dec)

    def retranslate(self):
        self.setWindowTitle("Dotcleaner")
        self.tagline.setText(self.t("tagline"))
        self.lang_label.setText(self.t("language"))
        self.t_drive.setText(self.t("step_drive"))
        self.refresh_btn.setText(self.t("refresh"))
        self.other_btn.setText(self.t("other_folder"))
        self.t_options.setText(self.t("step_options"))
        self.opt_windows.setText(self.t("opt_windows"))
        self.opt_trash.setText(self.t("opt_trash"))
        self.opt_eject.setText(self.t("opt_eject"))
        self.t_scan.setText(self.t("step_scan"))
        self.scan_btn.setText(self.t("scan_btn"))
        self.t_clean.setText(self.t("step_clean"))
        self.clean_btn.setText(self.t("clean_btn"))
        self.help_btn.setText(self.t("help"))
        self.quit_btn.setText(self.t("quit"))
        self.about.setText(self.t("about", version=core.VERSION))
        self._update_drive_info()
        self._render_scan()
        self._update_list_button()
        self._render_status()

    def _on_language(self, index):
        self.lang = self.lang_combo.itemData(index)
        self.settings.setValue("language", self.lang)
        self.retranslate()

    def set_language(self, code):
        self.lang_combo.setCurrentIndex(list(LANGUAGES).index(code))

    # -------------------------------------------------------------- drives --
    def refresh_drives(self):
        current = self.selected_path()
        self.drive_combo.blockSignals(True)
        self.drive_combo.clear()
        for d in core.list_drives():
            details = ", ".join(x for x in (d.fs, self.size_text(d.size) if d.size else "") if x)
            self.drive_combo.addItem(f"{d.name}   —   {details}" if details else d.name, d.path)
        for p in self.extra_paths:
            if os.path.isdir(p) and self.drive_combo.findData(p) < 0:
                self.drive_combo.addItem(p, p)
        idx = self.drive_combo.findData(current) if current else -1
        self.drive_combo.setCurrentIndex(idx if idx >= 0 else (0 if self.drive_combo.count() else -1))
        self.drive_combo.blockSignals(False)
        self._on_drive_changed()

    def add_folder(self, path):
        path = os.path.realpath(path)
        if path not in self.extra_paths:
            self.extra_paths.append(path)
        self.refresh_drives()
        self.drive_combo.setCurrentIndex(self.drive_combo.findData(path))

    def _choose_folder(self):
        start = "/Volumes" if core.SYSTEM == "Darwin" else ""
        path = QFileDialog.getExistingDirectory(self, self.t("choose_folder_title"), start)
        if path:
            self.add_folder(path)

    def selected_path(self):
        return self.drive_combo.currentData() if self.drive_combo.count() else None

    def _on_drive_changed(self, *_):
        self._clear_results()
        self._update_drive_info()

    def _update_drive_info(self):
        path = self.selected_path()
        if not path:
            self.drive_info.setText(self.t("no_drive"))
            self.drive_info.setStyleSheet("color: #b26a00;")
        elif core.is_mac_disk(path):
            self.drive_info.setText("🛡  " + self.t("safe_mode"))
            self.drive_info.setStyleSheet("color: #2f6fde;")
        else:
            self.drive_info.setText(path)
            self.drive_info.setStyleSheet("color: gray;")

    def _on_options(self, *_):
        self.settings.setValue("windows", self.opt_windows.isChecked())
        self.settings.setValue("keep_trash", self.opt_trash.isChecked())
        self.settings.setValue("eject", self.opt_eject.isChecked())
        self._clear_results()

    # ------------------------------------------------------------- results --
    def _clear_results(self):
        self.last_scan = None
        self._statuses = []
        self.results.hide()
        self.total.hide()
        self.warning.setText("")
        self.warning.hide()
        self.status.setText("")
        self.item_list.clear()
        self.item_list.hide()
        self.list_btn.hide()

    def _render_scan(self):
        res = self.last_scan
        if res is None:
            return
        if not res.items:
            self.results.hide()
            self.total.setText("✓ " + self.t("already_clean"))
            self.total.setStyleSheet("color: #1e8e3e;")
            self.total.show()
            self.warning.hide()
            self.list_btn.hide()
            self.item_list.hide()
            return
        for cat in CATEGORIES:
            n = res.count(cat)
            num, text = self.rows[cat]
            num.setText(str(n))
            text.setText(self.t("cat_" + cat))
            num.setVisible(n > 0)
            text.setVisible(n > 0)
        self.results.show()
        total = self.t("total", items=items_text(self.lang, len(res.items)), size=self.size_text(res.total_size))
        self.total.setText(total)
        self.total.setStyleSheet("")
        self.total.show()
        if res.trash_files:
            self.warning.setText("⚠  " + self.t("trash_warning", n=res.trash_files))
            self.warning.show()
        else:
            self.warning.hide()
        self.list_btn.show()

    def _fill_list(self):
        res = self.last_scan
        self.item_list.clear()
        if res:
            for i in res.items:
                rel = os.path.relpath(i.path, res.root)
                self.item_list.addItem(rel + (os.sep if i.is_dir else ""))

    def _toggle_list(self):
        if self.item_list.isVisible():
            self.item_list.hide()
        else:
            self._fill_list()
            self.item_list.show()
        self._update_list_button()

    def _update_list_button(self):
        self.list_btn.setText(("▾ " + self.t("hide_list")) if self.item_list.isVisible()
                              else ("▸ " + self.t("show_list")))

    def _show_status(self, key, kw=None, error=False, append=False):
        entry = (key, dict(kw or {}), error)
        self._statuses = self._statuses + [entry] if append else [entry]
        self._render_status()

    def _render_status(self):
        lines = []
        for key, kw, error in self._statuses:
            kw = dict(kw)
            for k in ("items", "left"):
                if isinstance(kw.get(k), int):
                    kw[k] = items_text(self.lang, kw[k])
            if isinstance(kw.get("size"), int):
                kw["size"] = self.size_text(kw["size"])
            text = self.t(key, **kw).replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
            color = "#c5221f" if error else ("#1e8e3e" if key in ("done", "ejected") else "")
            lines.append(f"<span style='color:{color}'>{text}</span>" if color else text)
        self.status.setText("<br>".join(lines))

    # ------------------------------------------------------------- actions --
    def _set_busy(self, busy, key=None):
        self.busy = busy
        for w in (self.scan_btn, self.clean_btn, self.drive_combo, self.refresh_btn, self.other_btn,
                  self.opt_windows, self.opt_trash, self.opt_eject, self.lang_combo):
            w.setEnabled(not busy)
        self.progress.setVisible(busy)
        if busy and key:
            self._show_status(key)
        elif not busy and self._statuses and self._statuses[-1][0] in ("scanning", "cleaning"):
            self._statuses = self._statuses[:-1]
            self._render_status()

    def _target(self):
        path = self.selected_path()
        if not path:
            self._show_status("choose_first", error=True)
            return None
        try:
            return core.check_target(path)
        except core.TargetError as e:
            self._show_status("err_" + e.code, error=True)
            return None

    def _run(self, tag, fn):
        def work():
            try:
                self.bridge.done.emit(tag, fn())
            except Exception as e:                       # shown, never crashes the app
                self.bridge.done.emit("error", e)
        threading.Thread(target=work, daemon=True).start()

    def _scan_fn(self, root):
        windows, keep = self.opt_windows.isChecked(), self.opt_trash.isChecked()
        return lambda: core.scan(root, windows=windows, keep_trash=keep)

    def start_scan(self):
        root = self._target()
        if root:
            self._clear_results()
            self._set_busy(True, "scanning")
            self._run("scan", self._scan_fn(root))

    def start_clean(self):
        root = self._target()
        if root:
            self._clear_results()
            self._set_busy(True, "scanning")
            self._run("scan_then_clean", self._scan_fn(root))

    def _drive_name(self, path):
        return os.path.basename(path.rstrip("\\/")) or path

    def _on_done(self, tag, result):
        self._set_busy(False)
        if tag == "error":
            self._statuses = []
            self.status.setText(f"<span style='color:#c5221f'>{result}</span>")
            return
        if tag in ("scan", "scan_then_clean"):
            self.last_scan = result
            self._render_scan()
            if tag == "scan":
                self._show_status("preview_only" if result.items else "already_clean")
                return
            if not result.items:
                self._show_status("already_clean")
                self._maybe_eject(result.root)
                return
            if not self._confirm(result):
                self._show_status("preview_only")
                return
            self._set_busy(True, "cleaning")
            self._run("clean", lambda: core.clean(result))
        elif tag == "clean":
            res = result
            if not res.left:
                self._show_status("done", {"items": res.deleted, "size": res.freed})
            elif res.only_system_left:
                self._show_status("came_back", {"left": len(res.left)})
            else:
                self._show_status("partial", {"items": res.deleted, "left": len(res.left)}, error=True)
            self.last_scan = None
            self.results.hide()
            self.total.hide()
            self.warning.hide()
            self.list_btn.hide()
            self.item_list.hide()
            if not res.left or res.only_system_left:
                self._maybe_eject(self.selected_path())
        elif tag == "eject":
            path, ok = result
            kept = self._statuses
            self.refresh_drives()                          # clears the results and messages
            self._statuses = kept
            self._show_status("ejected" if ok else "eject_failed", {"drive": self._drive_name(path)},
                              error=not ok, append=True)

    def _maybe_eject(self, path):
        if path and self.opt_eject.isChecked():
            self._set_busy(True)
            self._run("eject", lambda: (path, core.eject(path)))

    def _confirm(self, res):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle(self.t("confirm_title"))
        box.setText(self.t("confirm_title"))
        text = self.t("confirm_text", items=items_text(self.lang, len(res.items)),
                      size=self.size_text(res.total_size), drive=self._drive_name(res.root))
        if res.trash_files:
            text += "\n\n" + self.t("trash_warning", n=res.trash_files)
        box.setInformativeText(text)
        delete = box.addButton(self.t("delete"), QMessageBox.DestructiveRole)
        cancel = box.addButton(self.t("cancel"), QMessageBox.RejectRole)
        box.setDefaultButton(cancel)
        box.exec()
        return box.clickedButton() is delete

    def show_help(self):
        box = QMessageBox(self)
        box.setWindowTitle(self.t("help_title"))
        box.setIconPixmap(QPixmap(resource("assets", "icon.png")).scaled(64, 64, Qt.KeepAspectRatio,
                                                                          Qt.SmoothTransformation))
        box.setText(f"<b>{self.t('help_title')}</b>")
        box.setInformativeText(self.t("help_text") + f"\n\n{REPO_URL}")
        box.exec()


# ------------------------------------------------------------ self-tests --
def _make_demo_card(base):
    card = os.path.join(base, "EASYROMS")
    files = ["roms/gba/Pokemon Emerald.gba", "roms/gba/._Pokemon Emerald.gba", "roms/gba/.DS_Store",
             "roms/snes/Zelda.sfc", "roms/snes/._Zelda.sfc", "roms/psx/Thumbs.db",
             ".Spotlight-V100/Store-V2/db", ".Trashes/501/old.gba", ".fseventsd/0001", "._.Trashes"]
    for f in files:
        p = os.path.join(card, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(b"x" * 4096)
    return card


def selftest():
    """Builds the window in every language and cleans a temporary card. Exit code 0 = OK."""
    os.environ.setdefault("DOTCLEANER_FS_TYPE", "exfat")
    app = QApplication.instance() or QApplication(sys.argv)
    tmp = tempfile.mkdtemp(prefix="dotcleaner-selftest.")
    settings = QSettings(os.path.join(tmp, "settings.ini"), QSettings.IniFormat)
    w = MainWindow(settings)
    keys = set(T["en"])
    for code in LANGUAGES:
        assert set(T[code]) == keys, f"missing translations in {code}: {keys - set(T[code])}"
        w.set_language(code)
        assert w.clean_btn.text() == T[code]["clean_btn"]
    card = _make_demo_card(tmp)
    res = core.scan(core.check_target(card), windows=False)
    assert len(res.items) == 7, f"expected 7 junk items, got {len(res.items)}"
    out = core.clean(res)
    assert out.deleted == 7 and not out.left
    assert os.path.exists(os.path.join(card, "roms/gba/Pokemon Emerald.gba"))
    assert os.path.exists(os.path.join(card, "roms/psx/Thumbs.db"))
    assert not os.path.exists(os.path.join(card, ".Spotlight-V100"))
    del w
    app.quit()
    print("SELFTEST OK")
    return 0


def screenshots(out_dir):
    """One PNG per language, after a scan of a demo card (for the README)."""
    os.environ.setdefault("DOTCLEANER_FS_TYPE", "exfat")
    app = QApplication.instance() or QApplication(sys.argv)
    tmp = tempfile.mkdtemp(prefix="dotcleaner-shots.")
    settings = QSettings(os.path.join(tmp, "settings.ini"), QSettings.IniFormat)
    w = MainWindow(settings)
    card = _make_demo_card(tmp)
    w.add_folder(card)
    idx = w.drive_combo.findData(os.path.realpath(card))
    w.drive_combo.setItemText(idx, "EASYROMS   —   exfat, 29.7 GB")
    w.drive_info.setText(card)
    w.last_scan = core.scan(core.check_target(card), windows=False)
    os.makedirs(out_dir, exist_ok=True)
    w.show()
    for code in LANGUAGES:
        w.set_language(code)
        w._render_scan()
        w._show_status("preview_only")
        w.drive_info.setText("/Volumes/EASYROMS")
        w.drive_info.setStyleSheet("color: gray;")
        for _ in range(3):
            app.processEvents()
            w.adjustSize()
        w.grab().save(os.path.join(out_dir, f"app-{code}.png"))
    print("screenshots saved in", out_dir)
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--screenshots" in sys.argv:
        return screenshots(sys.argv[sys.argv.index("--screenshots") + 1])
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Shadowix84.dotcleaner")
        except Exception:
            pass
    app = QApplication(sys.argv)
    app.setApplicationName("Dotcleaner")
    app.setOrganizationName("Shadowix84")
    app.setWindowIcon(QIcon(resource("assets", "icon.png")))
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
