#!/usr/bin/env python3
"""
Dotcleaner — desktop app (macOS .dmg, Windows .exe, Linux).

Same steps as the shell version:  1. Choose a drive · 2. Options · 3. Scan · 4. Clean · Help · Quit
plus a language menu: English, Français, Español, 中文, हिन्दी.

Run from source:  pip install PySide6-Essentials && python3 app/dotcleaner_gui.py
Self-test:        python3 app/dotcleaner_gui.py --selftest
Screenshots:      python3 app/dotcleaner_gui.py --screenshots DIR
Dark theme:       DOTCLEANER_THEME=dark (otherwise it follows the system)
"""
import os
import re
import sys
import tempfile
import threading

from PySide6.QtCore import QObject, QSettings, QLocale, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog, QFrame,
                               QHBoxLayout, QLabel, QListWidget, QMessageBox, QProgressBar,
                               QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dotcleaner_core as core                                          # noqa: E402
from i18n import LANGUAGES, T, UNITS, items as items_text, tr          # noqa: E402

REPO_URL = "https://github.com/Shadowix84/Dotcleaner-Multi-Software"
CATEGORIES = ("appledouble", "ds_store", "system", "windows")

LIGHT = dict(bg="#f2f5fb", card="#ffffff", line="#e1e7f1", text="#15203a", muted="#66748f",
             accent="#2f6fde", accent2="#1f55b8", soft="#e9f0ff", ok="#1b7f3a", okbg="#e5f5ea",
             warn="#8a5200", warnbg="#fff3d6", err="#b3261e", errbg="#fdeceb", tile="#f6f8fd")
DARK = dict(bg="#0d1320", card="#151e30", line="#26334d", text="#e8eefc", muted="#97a6c4",
            accent="#5a92f5", accent2="#3f74d6", soft="#1c2a46", ok="#62d483", okbg="#12301f",
            warn="#ffc75e", warnbg="#3a2e12", err="#ff8a80", errbg="#3d1a1a", tile="#1a2438")


def step_title(text):
    """'1. Choose a drive' -> 'Choose a drive' (the number is shown in a round badge)."""
    return re.sub(r"^\s*\d+\.\s*", "", text)


def stylesheet(c):
    return f"""
    QWidget#content {{ background: {c['bg']}; }}
    QScrollArea {{ background: {c['bg']}; border: 0; }}
    QLabel {{ color: {c['text']}; background: transparent; }}
    QFrame#hero {{ border-radius: 16px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3f86f5, stop:1 #1b47a8); }}
    QFrame#hero QLabel {{ color: white; }}
    QLabel#tagline {{ color: #dbe7ff; }}
    QLabel#version {{ color: white; background: rgba(255,255,255,0.20); border-radius: 9px; padding: 1px 9px; }}
    QFrame#hero QComboBox {{ background: rgba(255,255,255,0.18); color: white;
        border: 1px solid rgba(255,255,255,0.40); border-radius: 8px; padding: 5px 10px; min-width: 120px; }}
    QFrame#hero QComboBox QAbstractItemView {{ background: {c['card']}; color: {c['text']}; }}
    QFrame#card {{ background: {c['card']}; border: 1px solid {c['line']}; border-radius: 14px; }}
    QLabel#badge {{ background: {c['accent']}; color: white; border-radius: 13px; font-weight: bold; }}
    QLabel#stepTitle {{ font-weight: bold; }}
    QLabel#muted {{ color: {c['muted']}; }}
    QComboBox {{ background: {c['card']}; color: {c['text']}; border: 1px solid {c['line']};
        border-radius: 8px; padding: 6px 10px; }}
    QComboBox QAbstractItemView {{ background: {c['card']}; color: {c['text']};
        selection-background-color: {c['soft']}; selection-color: {c['text']}; }}
    QCheckBox {{ color: {c['text']}; spacing: 8px; padding: 3px 0; }}
    QPushButton {{ background: {c['card']}; color: {c['text']}; border: 1px solid {c['line']};
        border-radius: 9px; padding: 7px 14px; }}
    QPushButton:hover {{ background: {c['soft']}; }}
    QPushButton:disabled {{ color: {c['muted']}; }}
    QPushButton#scan {{ border: 1.5px solid {c['accent']}; color: {c['accent']}; font-weight: bold; padding: 9px; }}
    QPushButton#clean {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {c['accent']}, stop:1 {c['accent2']});
        color: white; border: 0; font-weight: bold; padding: 12px; border-radius: 10px; }}
    QPushButton#clean:hover {{ background: {c['accent2']}; }}
    QPushButton#clean:disabled {{ background: {c['line']}; color: {c['muted']}; }}
    QPushButton#link {{ border: 0; background: transparent; color: {c['accent']}; text-align: left; padding: 2px 0; }}
    QFrame#tile {{ background: {c['tile']}; border: 1px solid {c['line']}; border-radius: 10px; }}
    QLabel#tileNum {{ font-weight: bold; color: {c['accent']}; }}
    QLabel#tileText {{ color: {c['muted']}; }}
    QLabel#total {{ font-weight: bold; }}
    QLabel#total[kind="ok"] {{ color: {c['ok']}; }}
    QLabel#warning {{ background: {c['warnbg']}; color: {c['warn']}; border-radius: 9px; padding: 8px 10px; }}
    QLabel#status {{ border-radius: 9px; padding: 9px 12px; }}
    QLabel#status[kind="ok"] {{ background: {c['okbg']}; color: {c['ok']}; font-weight: bold; }}
    QLabel#status[kind="err"] {{ background: {c['errbg']}; color: {c['err']}; }}
    QLabel#status[kind="info"] {{ background: {c['soft']}; color: {c['text']}; }}
    QLabel#driveInfo[kind="safe"] {{ color: {c['accent']}; }}
    QLabel#driveInfo[kind="warn"] {{ color: {c['warn']}; }}
    QLabel#driveInfo[kind="path"] {{ color: {c['muted']}; }}
    QProgressBar {{ background: {c['line']}; border: 0; border-radius: 5px; }}
    QProgressBar::chunk {{ background: {c['accent']}; border-radius: 5px; }}
    QListWidget {{ background: {c['tile']}; color: {c['text']}; border: 1px solid {c['line']}; border-radius: 8px; }}
    """


def resource(*parts):
    base = getattr(sys, "_MEIPASS", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    return os.path.join(base, *parts)


def default_language():
    code = QLocale.system().name()[:2].lower()
    return code if code in LANGUAGES else "en"


def want_dark(app):
    theme = os.environ.get("DOTCLEANER_THEME", "")
    if theme in ("dark", "light"):
        return theme == "dark"
    hints = app.styleHints()
    if hasattr(hints, "colorScheme"):
        return hints.colorScheme() == Qt.ColorScheme.Dark
    return app.palette().color(QPalette.Window).lightness() < 128


def set_kind(widget, kind):
    """Change a dynamic style property and re-apply the style sheet."""
    widget.setProperty("kind", kind)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def scaled_font(widget, factor, bold=False):
    f = widget.font()
    f.setPointSizeF(f.pointSizeF() * factor)
    f.setBold(bold)
    widget.setFont(f)


class Bridge(QObject):
    """Carries results and progress from worker threads back to the window."""
    done = Signal(str, object)
    progress = Signal(int, int)


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
        self._statuses = []
        self.bridge = Bridge()
        self.bridge.done.connect(self._on_done)
        self.bridge.progress.connect(self._on_progress)
        app = QApplication.instance()
        self.colors = DARK if (app is not None and want_dark(app)) else LIGHT
        self.setStyleSheet(stylesheet(self.colors))
        self._build()
        self.refresh_drives()
        self.retranslate()

    # ------------------------------------------------------------ layout --
    def _card(self, parent_layout, number):
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)
        head = QHBoxLayout()
        head.setSpacing(10)
        badge = QLabel(str(number))
        badge.setObjectName("badge")
        badge.setFixedSize(26, 26)
        badge.setAlignment(Qt.AlignCenter)
        title = QLabel()
        title.setObjectName("stepTitle")
        scaled_font(title, 1.12, bold=True)
        head.addWidget(badge)
        head.addWidget(title, 1)
        lay.addLayout(head)
        parent_layout.addWidget(card)
        return title, lay

    def _muted(self, wrap=True):
        lbl = QLabel()
        lbl.setObjectName("muted")
        lbl.setWordWrap(wrap)
        return lbl

    def _build(self):
        self.setWindowIcon(QIcon(resource("assets", "icon.png")))
        self.setMinimumWidth(640)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setObjectName("content")
        root = QVBoxLayout(content)
        root.setContentsMargins(18, 18, 18, 14)
        root.setSpacing(12)
        self._scroll.setWidget(content)
        outer.addWidget(self._scroll)

        # Hero: icon, name, version, tagline, language menu
        hero = QFrame()
        hero.setObjectName("hero")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(18, 16, 18, 16)
        hl.setSpacing(14)
        logo = QLabel()
        pm = QPixmap(resource("assets", "icon.png"))
        if not pm.isNull():
            logo.setPixmap(pm.scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        hl.addWidget(logo, 0, Qt.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(3)
        row = QHBoxLayout()
        row.setSpacing(8)
        name = QLabel("Dotcleaner")
        scaled_font(name, 1.8, bold=True)
        version = QLabel(core.VERSION)
        version.setObjectName("version")
        row.addWidget(name)
        row.addWidget(version, 0, Qt.AlignVCenter)
        row.addStretch(1)
        self.tagline = QLabel()
        self.tagline.setObjectName("tagline")
        self.tagline.setWordWrap(True)
        titles.addLayout(row)
        titles.addWidget(self.tagline)
        hl.addLayout(titles, 1)
        langbox = QVBoxLayout()
        langbox.setSpacing(3)
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        for code, label in LANGUAGES.items():
            self.lang_combo.addItem(label, code)
        self.lang_combo.setCurrentIndex(list(LANGUAGES).index(self.lang))
        self.lang_combo.currentIndexChanged.connect(self._on_language)
        langbox.addWidget(self.lang_label)
        langbox.addWidget(self.lang_combo)
        langbox.addStretch(1)
        hl.addLayout(langbox)
        root.addWidget(hero)

        # 1. Choose a drive
        self.t_drive, lay = self._card(root, 1)
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
        lay.addLayout(row)
        self.drive_info = QLabel()
        self.drive_info.setObjectName("driveInfo")
        self.drive_info.setWordWrap(True)
        lay.addWidget(self.drive_info)

        # 2. Options
        self.t_options, lay = self._card(root, 2)
        self.opt_windows = QCheckBox()
        self.opt_trash = QCheckBox()
        self.opt_eject = QCheckBox()
        self.opt_windows.setChecked(self.settings.value("windows", False, type=bool))
        self.opt_trash.setChecked(self.settings.value("keep_trash", False, type=bool))
        self.opt_eject.setChecked(self.settings.value("eject", True, type=bool))
        for cb in (self.opt_windows, self.opt_trash, self.opt_eject):
            cb.toggled.connect(self._on_options)
            lay.addWidget(cb)

        # 3. Scan
        self.t_scan, lay = self._card(root, 3)
        self.scan_btn = QPushButton()
        self.scan_btn.setObjectName("scan")
        self.scan_btn.setCursor(Qt.PointingHandCursor)
        self.scan_btn.clicked.connect(self.start_scan)
        lay.addWidget(self.scan_btn)
        self.ready = self._muted()
        lay.addWidget(self.ready)
        self.found_title = self._muted(False)
        lay.addWidget(self.found_title)
        self.results = QWidget()
        tiles = QHBoxLayout(self.results)
        tiles.setContentsMargins(0, 0, 0, 0)
        tiles.setSpacing(8)
        self.rows = {}
        for cat in CATEGORIES:
            tile = QFrame()
            tile.setObjectName("tile")
            tl = QVBoxLayout(tile)
            tl.setContentsMargins(12, 8, 12, 9)
            tl.setSpacing(1)
            num, text = QLabel(), QLabel()
            num.setObjectName("tileNum")
            scaled_font(num, 1.7, bold=True)
            text.setObjectName("tileText")
            text.setWordWrap(True)
            scaled_font(text, 0.88)
            tl.addWidget(num)
            tl.addWidget(text)
            tl.addStretch(1)
            tiles.addWidget(tile, 1)
            self.rows[cat] = (num, text, tile)
        lay.addWidget(self.results)
        self.total = QLabel()
        self.total.setObjectName("total")
        self.total.setWordWrap(True)
        lay.addWidget(self.total)
        self.warning = QLabel()
        self.warning.setObjectName("warning")
        self.warning.setWordWrap(True)
        lay.addWidget(self.warning)
        self.list_btn = QPushButton()
        self.list_btn.setObjectName("link")
        self.list_btn.setCursor(Qt.PointingHandCursor)
        self.list_btn.clicked.connect(self._toggle_list)
        lay.addWidget(self.list_btn)
        self.item_list = QListWidget()
        self.item_list.setMinimumHeight(150)
        lay.addWidget(self.item_list)

        # 4. Clean
        self.t_clean, lay = self._card(root, 4)
        self.clean_btn = QPushButton()
        self.clean_btn.setObjectName("clean")
        scaled_font(self.clean_btn, 1.1, bold=True)
        self.clean_btn.setCursor(Qt.PointingHandCursor)
        self.clean_btn.clicked.connect(self.start_clean)
        lay.addWidget(self.clean_btn)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(10)
        lay.addWidget(self.progress)
        self.status = QLabel()
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.RichText)
        lay.addWidget(self.status)
        self.untouched = self._muted()
        lay.addWidget(self.untouched)

        # Footer: Help · version · Quit
        foot = QHBoxLayout()
        self.help_btn = QPushButton()
        self.help_btn.clicked.connect(self.show_help)
        self.about = self._muted(False)
        self.about.setAlignment(Qt.AlignCenter)
        self.quit_btn = QPushButton()
        self.quit_btn.clicked.connect(self.close)
        foot.addWidget(self.help_btn)
        foot.addWidget(self.about, 1)
        foot.addWidget(self.quit_btn)
        root.addLayout(foot)
        root.addStretch(1)
        self._clear_results()
        self._set_busy(False)
        self.resize(720, 860)

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
        self.t_drive.setText(step_title(self.t("step_drive")))
        self.refresh_btn.setText("⟳  " + self.t("refresh"))
        self.other_btn.setText(self.t("other_folder"))
        self.t_options.setText(step_title(self.t("step_options")))
        self.opt_windows.setText(self.t("opt_windows"))
        self.opt_trash.setText(self.t("opt_trash"))
        self.opt_eject.setText(self.t("opt_eject"))
        self.t_scan.setText(step_title(self.t("step_scan")))
        self.scan_btn.setText(self.t("scan_btn"))
        self.ready.setText(self.t("ready"))
        self.found_title.setText(self.t("found_title").upper())
        self.t_clean.setText(step_title(self.t("step_clean")))
        self.clean_btn.setText(self.t("clean_btn"))
        self.untouched.setText("🛡  " + self.t("untouched"))
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
            label = f"{d.name}   —   {details}" if details else d.name
            self.drive_combo.addItem(("🛡  " if d.safe_mode else "💾  ") + label, d.path)
        for p in self.extra_paths:
            if os.path.isdir(p) and self.drive_combo.findData(p) < 0:
                self.drive_combo.addItem("📁  " + p, p)
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
            self.drive_info.setText("⚠  " + self.t("no_drive"))
            set_kind(self.drive_info, "warn")
        elif core.is_mac_disk(path):
            self.drive_info.setText("🛡  " + self.t("safe_mode"))
            set_kind(self.drive_info, "safe")
        else:
            self.drive_info.setText(path)
            set_kind(self.drive_info, "path")

    def _on_options(self, *_):
        self.settings.setValue("windows", self.opt_windows.isChecked())
        self.settings.setValue("keep_trash", self.opt_trash.isChecked())
        self.settings.setValue("eject", self.opt_eject.isChecked())
        self._clear_results()

    # ------------------------------------------------------------- results --
    def _hide_scan(self):
        for w in (self.found_title, self.results, self.total, self.warning, self.list_btn, self.item_list):
            w.hide()

    def _clear_results(self):
        self.last_scan = None
        self._statuses = []
        self._hide_scan()
        self.warning.setText("")
        self.item_list.clear()
        self.status.setText("")
        self.status.hide()
        self.ready.show()

    def _render_scan(self):
        res = self.last_scan
        if res is None:
            return
        self.ready.hide()
        if not res.items:
            self._hide_scan()
            self.total.setText("✓  " + self.t("already_clean"))
            set_kind(self.total, "ok")
            self.total.show()
            return
        for cat in CATEGORIES:
            n = res.count(cat)
            num, text, tile = self.rows[cat]
            num.setText(str(n))
            text.setText(self.t("cat_" + cat))
            tile.setVisible(n > 0)
        self.found_title.show()
        self.results.show()
        self.total.setText(self.t("total", items=items_text(self.lang, len(res.items)),
                                  size=self.size_text(res.total_size)))
        set_kind(self.total, "")
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
        self.list_btn.setText(("▾  " + self.t("hide_list")) if self.item_list.isVisible()
                              else ("▸  " + self.t("show_list")))

    def _show_status(self, key, kw=None, error=False, append=False):
        entry = (key, dict(kw or {}), error)
        self._statuses = self._statuses + [entry] if append else [entry]
        self._render_status()

    def _render_status(self):
        lines, kind = [], "info"
        for key, kw, error in self._statuses:
            kw = dict(kw)
            for k in ("items", "left"):
                if isinstance(kw.get(k), int):
                    kw[k] = items_text(self.lang, kw[k])
            if isinstance(kw.get("size"), int):
                kw["size"] = self.size_text(kw["size"])
            text = self.t(key, **kw).replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
            if error:
                kind = "err"
            elif key in ("done", "ejected", "already_clean"):
                text = "✓  " + text
                if kind != "err":
                    kind = "ok"
            lines.append(text)
        self.status.setText("<br>".join(lines))
        self.status.setVisible(bool(lines))
        set_kind(self.status, kind)

    def _show_error(self, message):
        self._statuses = []
        self.status.setText(str(message).replace("&", "&amp;").replace("<", "&lt;"))
        self.status.show()
        set_kind(self.status, "err")

    # ------------------------------------------------------------- actions --
    def _set_busy(self, busy, key=None):
        self.busy = busy
        for w in (self.scan_btn, self.clean_btn, self.drive_combo, self.refresh_btn, self.other_btn,
                  self.opt_windows, self.opt_trash, self.opt_eject, self.lang_combo):
            w.setEnabled(not busy)
        if busy:
            self.progress.setRange(0, 0)          # moving bar until real progress arrives
        self.progress.setVisible(busy)
        if busy and key:
            self._show_status(key)
        elif not busy and self._statuses and self._statuses[-1][0] in ("scanning", "cleaning"):
            self._statuses = self._statuses[:-1]
            self._render_status()

    def _on_progress(self, n, total):
        if self.busy:
            self.progress.setRange(0, max(total, 1))
            self.progress.setValue(n)

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
            self._show_error(result)
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
            emit = self.bridge.progress.emit
            self._run("clean", lambda: core.clean(result, progress=emit))
        elif tag == "clean":
            res = result
            if not res.left:
                self._show_status("done", {"items": res.deleted, "size": res.freed})
            elif res.only_system_left:
                self._show_status("came_back", {"left": len(res.left)})
            else:
                self._show_status("partial", {"items": res.deleted, "left": len(res.left)}, error=True)
            self.last_scan = None
            self._hide_scan()
            if not res.left or res.only_system_left:
                self._maybe_eject(self.selected_path())
        elif tag == "eject":
            path, ok = result
            kept = self._statuses
            self.refresh_drives()                          # clears the results and messages
            self._statuses = kept
            self.ready.hide()
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


# ------------------------------------------------------------ app setup --
def make_app(argv):
    """QApplication with the same clean look on macOS, Windows and Linux (light or dark)."""
    app = QApplication.instance() or QApplication(argv)
    dark = want_dark(app)
    app.setStyle("Fusion")
    c = DARK if dark else LIGHT
    pal = QPalette()
    for role, key in ((QPalette.Window, "bg"), (QPalette.Base, "card"), (QPalette.AlternateBase, "tile"),
                      (QPalette.Text, "text"), (QPalette.WindowText, "text"), (QPalette.Button, "card"),
                      (QPalette.ButtonText, "text"), (QPalette.Highlight, "accent"),
                      (QPalette.ToolTipBase, "card"), (QPalette.ToolTipText, "text"),
                      (QPalette.PlaceholderText, "muted")):
        pal.setColor(role, QColor(c[key]))
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)
    return app


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
    app = make_app(sys.argv)
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
    """One PNG per language after a scan of a demo card, plus the 'done' screen (README)."""
    os.environ.setdefault("DOTCLEANER_FS_TYPE", "exfat")
    app = make_app(sys.argv)
    tmp = tempfile.mkdtemp(prefix="dotcleaner-shots.")
    settings = QSettings(os.path.join(tmp, "settings.ini"), QSettings.IniFormat)
    w = MainWindow(settings)
    card = _make_demo_card(tmp)
    w.add_folder(card)
    idx = w.drive_combo.findData(os.path.realpath(card))
    w.drive_combo.setItemText(idx, "💾  EASYROMS   —   exfat, 29.7 GB")
    os.makedirs(out_dir, exist_ok=True)
    w.show()

    def shot(name):
        w.drive_info.setText("/Volumes/EASYROMS")
        set_kind(w.drive_info, "path")
        for _ in range(3):
            app.processEvents()
        content = w._scroll.widget()
        w.resize(720, content.sizeHint().height() + 2)
        for _ in range(3):
            app.processEvents()
        w.grab().save(os.path.join(out_dir, name))

    scan = core.scan(core.check_target(card), windows=False)
    for code in LANGUAGES:
        w.set_language(code)
        w.last_scan = scan
        w._render_scan()
        w._show_status("preview_only")
        shot(f"app-{code}.png")
    w.set_language("en")
    w._clear_results()
    w.ready.hide()
    w._show_status("done", {"items": len(scan.items), "size": scan.total_size})
    w._show_status("ejected", {"drive": "EASYROMS"}, append=True)
    shot("app-done.png")
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
    app = make_app(sys.argv)
    app.setApplicationName("Dotcleaner")
    app.setOrganizationName("Shadowix84")
    app.setWindowIcon(QIcon(resource("assets", "icon.png")))
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
