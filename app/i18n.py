"""
Translations of the dotcleaner app: English, French, Spanish, Chinese (Mandarin,
simplified) and Hindi. The structure mirrors the menu of dotcleaner.sh:
1. Choose a drive · 2. Options · 3. Scan · 4. Clean · Help · Quit.

To add a language: copy the "en" block, translate every value, add it to LANGUAGES.
tests/test_app.py checks that every language has every key and the same {placeholders}.
"""

# code -> name shown in the language menu (in its own language)
LANGUAGES = {
    "en": "English",
    "fr": "Français",
    "es": "Español",
    "zh": "中文（简体）",
    "hi": "हिन्दी",
}

# units and decimal separator used for sizes
UNITS = {
    "en": (("B", "KB", "MB", "GB", "TB"), "."),
    "fr": (("o", "Ko", "Mo", "Go", "To"), ","),
    "es": (("B", "KB", "MB", "GB", "TB"), ","),
    "zh": (("B", "KB", "MB", "GB", "TB"), "."),
    "hi": (("B", "KB", "MB", "GB", "TB"), "."),
}

T = {
    # ------------------------------------------------------------------ English
    "en": {
        "tagline": "Clean macOS junk from SD cards & USB drives",
        "language": "Language",
        "step_drive": "1. Choose a drive",
        "refresh": "Refresh",
        "other_folder": "Other folder…",
        "choose_folder_title": "Choose a drive or folder",
        "no_drive": "No SD card or USB drive found. Plug one in, then click Refresh.",
        "safe_mode": "Mac-formatted drive: safe mode. Only junk files are removed, system folders are kept.",
        "step_options": "2. Options",
        "opt_windows": "Also remove Windows files (Thumbs.db, desktop.ini)",
        "opt_trash": "Keep the drive's Trash",
        "opt_eject": "Eject when done",
        "step_scan": "3. Scan",
        "scan_btn": "Scan (preview, deletes nothing)",
        "scanning": "Scanning…",
        "step_clean": "4. Clean",
        "clean_btn": "Clean",
        "cleaning": "Cleaning…",
        "cat_appledouble": "._* files (AppleDouble)",
        "cat_ds_store": ".DS_Store files",
        "cat_system": "macOS system items (.Spotlight-V100, .Trashes, __MACOSX…)",
        "cat_windows": "Windows files",
        "items_one": "{n} item",
        "items_many": "{n} items",
        "total": "Total: {items}, {size}",
        "already_clean": "Already clean, nothing to delete.",
        "preview_only": "Preview only: nothing was deleted.",
        "show_list": "Show the list",
        "hide_list": "Hide the list",
        "trash_warning": "The drive's Trash holds {n} file(s) deleted in Finder: they will be erased for good. Tick “Keep the drive's Trash” to keep them.",
        "confirm_title": "Delete the junk?",
        "confirm_text": "Delete {items} ({size}) from {drive}?\nThis cannot be undone.",
        "delete": "Delete",
        "cancel": "Cancel",
        "done": "Done: {items} deleted ({size} freed).",
        "partial": "{items} deleted. {left} could not be deleted (read-only drive or in use).",
        "came_back": "macOS recreated {left} system folder(s) while the drive is plugged in. This is harmless: eject the drive now.",
        "ejected": "{drive} ejected: you can unplug it.",
        "eject_failed": "Could not eject {drive}. Close any file open on it, then eject it from Finder or File Explorer.",
        "err_not_found": "This drive or folder no longer exists. Click Refresh.",
        "err_not_folder": "This is not a folder.",
        "err_forbidden": "This is a system or home folder: choose an SD card or USB drive.",
        "err_junk_root": "This folder is itself junk: delete it directly.",
        "err_cannot_open": "This drive cannot be read. On macOS, allow the app to access removable volumes.",
        "choose_first": "Choose a drive first.",
        "help": "Help",
        "quit": "Quit",
        "help_title": "How Dotcleaner works",
        "help_text": (
            "When you copy files from a Mac to an SD card or USB drive, macOS adds hidden files: "
            "a “._” twin for every file, “.DS_Store” in every folder, and “.Spotlight-V100”, "
            "“.Trashes”, “.fseventsd” folders. On a console they can show up as ghost games.\n\n"
            "1. Choose a drive: pick your SD card or USB drive.\n"
            "2. Options: Windows files, keep the Trash, eject when done.\n"
            "3. Scan: shows what would be deleted, deletes nothing.\n"
            "4. Clean: deletes the junk after your confirmation.\n\n"
            "Your games, saves, BIOS, photos and documents are never touched. "
            "On Mac-formatted drives (APFS, HFS+) only junk files are removed."
        ),
        "about": "Version {version} · MIT License · Shadowix84",
    },
    # ------------------------------------------------------------------- French
    "fr": {
        "tagline": "Nettoie les fichiers parasites de macOS sur cartes SD et clés USB",
        "language": "Langue",
        "step_drive": "1. Choisir un lecteur",
        "refresh": "Actualiser",
        "other_folder": "Autre dossier…",
        "choose_folder_title": "Choisir un lecteur ou un dossier",
        "no_drive": "Aucune carte SD ni clé USB trouvée. Branchez-en une, puis cliquez sur Actualiser.",
        "safe_mode": "Disque au format Mac : mode sûr. Seuls les fichiers parasites sont supprimés, les dossiers système sont conservés.",
        "step_options": "2. Options",
        "opt_windows": "Supprimer aussi les fichiers Windows (Thumbs.db, desktop.ini)",
        "opt_trash": "Garder la corbeille du lecteur",
        "opt_eject": "Éjecter à la fin",
        "step_scan": "3. Analyser",
        "scan_btn": "Analyser (aperçu, ne supprime rien)",
        "scanning": "Analyse en cours…",
        "step_clean": "4. Nettoyer",
        "clean_btn": "Nettoyer",
        "cleaning": "Nettoyage en cours…",
        "cat_appledouble": "Fichiers ._* (AppleDouble)",
        "cat_ds_store": "Fichiers .DS_Store",
        "cat_system": "Éléments système macOS (.Spotlight-V100, .Trashes, __MACOSX…)",
        "cat_windows": "Fichiers Windows",
        "items_one": "{n} élément",
        "items_many": "{n} éléments",
        "total": "Total : {items}, {size}",
        "already_clean": "Déjà propre, rien à supprimer.",
        "preview_only": "Aperçu seulement : rien n'a été supprimé.",
        "show_list": "Afficher la liste",
        "hide_list": "Masquer la liste",
        "trash_warning": "La corbeille du lecteur contient {n} fichier(s) supprimé(s) dans le Finder : ils seront effacés définitivement. Cochez « Garder la corbeille du lecteur » pour les conserver.",
        "confirm_title": "Supprimer les fichiers parasites ?",
        "confirm_text": "Supprimer {items} ({size}) de {drive} ?\nCette action est irréversible.",
        "delete": "Supprimer",
        "cancel": "Annuler",
        "done": "Terminé : {items} supprimé(s) ({size} libérés).",
        "partial": "{items} supprimé(s). {left} n'ont pas pu l'être (lecteur en lecture seule ou en cours d'utilisation).",
        "came_back": "macOS a recréé {left} dossier(s) système tant que le lecteur est branché. C'est sans danger : éjectez le lecteur maintenant.",
        "ejected": "{drive} éjecté : vous pouvez le débrancher.",
        "eject_failed": "Impossible d'éjecter {drive}. Fermez les fichiers ouverts dessus, puis éjectez-le depuis le Finder ou l'Explorateur de fichiers.",
        "err_not_found": "Ce lecteur ou dossier n'existe plus. Cliquez sur Actualiser.",
        "err_not_folder": "Ce n'est pas un dossier.",
        "err_forbidden": "C'est un dossier système ou personnel : choisissez une carte SD ou une clé USB.",
        "err_junk_root": "Ce dossier est lui-même un parasite : supprimez-le directement.",
        "err_cannot_open": "Impossible de lire ce lecteur. Sur macOS, autorisez l'app à accéder aux volumes amovibles.",
        "choose_first": "Choisissez d'abord un lecteur.",
        "help": "Aide",
        "quit": "Quitter",
        "help_title": "Comment fonctionne Dotcleaner",
        "help_text": (
            "Quand on copie des fichiers d'un Mac vers une carte SD ou une clé USB, macOS ajoute des fichiers cachés : "
            "un jumeau « ._ » pour chaque fichier, un « .DS_Store » dans chaque dossier, et des dossiers "
            "« .Spotlight-V100 », « .Trashes », « .fseventsd ». Sur une console, ils peuvent apparaître comme des jeux fantômes.\n\n"
            "1. Choisir un lecteur : votre carte SD ou clé USB.\n"
            "2. Options : fichiers Windows, garder la corbeille, éjecter à la fin.\n"
            "3. Analyser : montre ce qui serait supprimé, ne supprime rien.\n"
            "4. Nettoyer : supprime les parasites après votre confirmation.\n\n"
            "Vos jeux, sauvegardes, BIOS, photos et documents ne sont jamais touchés. "
            "Sur les disques au format Mac (APFS, HFS+), seuls les fichiers parasites sont supprimés."
        ),
        "about": "Version {version} · Licence MIT · Shadowix84",
    },
    # ------------------------------------------------------------------ Spanish
    "es": {
        "tagline": "Limpia la basura de macOS de tarjetas SD y memorias USB",
        "language": "Idioma",
        "step_drive": "1. Elige una unidad",
        "refresh": "Actualizar",
        "other_folder": "Otra carpeta…",
        "choose_folder_title": "Elige una unidad o carpeta",
        "no_drive": "No se encontró ninguna tarjeta SD ni memoria USB. Conecta una y pulsa Actualizar.",
        "safe_mode": "Unidad con formato Mac: modo seguro. Solo se eliminan los archivos basura; las carpetas del sistema se conservan.",
        "step_options": "2. Opciones",
        "opt_windows": "Eliminar también los archivos de Windows (Thumbs.db, desktop.ini)",
        "opt_trash": "Conservar la papelera de la unidad",
        "opt_eject": "Expulsar al terminar",
        "step_scan": "3. Analizar",
        "scan_btn": "Analizar (vista previa, no elimina nada)",
        "scanning": "Analizando…",
        "step_clean": "4. Limpiar",
        "clean_btn": "Limpiar",
        "cleaning": "Limpiando…",
        "cat_appledouble": "Archivos ._* (AppleDouble)",
        "cat_ds_store": "Archivos .DS_Store",
        "cat_system": "Elementos del sistema macOS (.Spotlight-V100, .Trashes, __MACOSX…)",
        "cat_windows": "Archivos de Windows",
        "items_one": "{n} elemento",
        "items_many": "{n} elementos",
        "total": "Total: {items}, {size}",
        "already_clean": "Ya está limpia, no hay nada que eliminar.",
        "preview_only": "Solo vista previa: no se eliminó nada.",
        "show_list": "Mostrar la lista",
        "hide_list": "Ocultar la lista",
        "trash_warning": "La papelera de la unidad contiene {n} archivo(s) eliminados en el Finder: se borrarán definitivamente. Marca «Conservar la papelera de la unidad» para guardarlos.",
        "confirm_title": "¿Eliminar la basura?",
        "confirm_text": "¿Eliminar {items} ({size}) de {drive}?\nEsta acción no se puede deshacer.",
        "delete": "Eliminar",
        "cancel": "Cancelar",
        "done": "Listo: {items} eliminado(s) ({size} liberados).",
        "partial": "{items} eliminado(s). {left} no se pudieron eliminar (unidad de solo lectura o en uso).",
        "came_back": "macOS volvió a crear {left} carpeta(s) del sistema mientras la unidad está conectada. Es inofensivo: expulsa la unidad ahora.",
        "ejected": "{drive} expulsada: ya puedes desconectarla.",
        "eject_failed": "No se pudo expulsar {drive}. Cierra los archivos abiertos en ella y expúlsala desde el Finder o el Explorador de archivos.",
        "err_not_found": "Esta unidad o carpeta ya no existe. Pulsa Actualizar.",
        "err_not_folder": "No es una carpeta.",
        "err_forbidden": "Es una carpeta del sistema o personal: elige una tarjeta SD o una memoria USB.",
        "err_junk_root": "Esta carpeta es basura en sí misma: elimínala directamente.",
        "err_cannot_open": "No se puede leer esta unidad. En macOS, permite que la app acceda a los volúmenes extraíbles.",
        "choose_first": "Elige primero una unidad.",
        "help": "Ayuda",
        "quit": "Salir",
        "help_title": "Cómo funciona Dotcleaner",
        "help_text": (
            "Al copiar archivos de un Mac a una tarjeta SD o memoria USB, macOS añade archivos ocultos: "
            "un gemelo «._» por cada archivo, un «.DS_Store» en cada carpeta y las carpetas «.Spotlight-V100», "
            "«.Trashes» y «.fseventsd». En una consola pueden aparecer como juegos fantasma.\n\n"
            "1. Elige una unidad: tu tarjeta SD o memoria USB.\n"
            "2. Opciones: archivos de Windows, conservar la papelera, expulsar al terminar.\n"
            "3. Analizar: muestra lo que se eliminaría, no elimina nada.\n"
            "4. Limpiar: elimina la basura tras tu confirmación.\n\n"
            "Tus juegos, partidas guardadas, BIOS, fotos y documentos nunca se tocan. "
            "En unidades con formato Mac (APFS, HFS+) solo se eliminan los archivos basura."
        ),
        "about": "Versión {version} · Licencia MIT · Shadowix84",
    },
    # ---------------------------------------------------- Chinese (Mandarin, simplified)
    "zh": {
        "tagline": "清除 SD 卡和 U 盘上的 macOS 垃圾文件",
        "language": "语言",
        "step_drive": "1. 选择磁盘",
        "refresh": "刷新",
        "other_folder": "其他文件夹…",
        "choose_folder_title": "选择磁盘或文件夹",
        "no_drive": "未找到 SD 卡或 U 盘。请插入设备，然后点击“刷新”。",
        "safe_mode": "Mac 格式的磁盘：安全模式。只删除垃圾文件，保留系统文件夹。",
        "step_options": "2. 选项",
        "opt_windows": "同时删除 Windows 文件（Thumbs.db、desktop.ini）",
        "opt_trash": "保留磁盘的废纸篓",
        "opt_eject": "完成后推出磁盘",
        "step_scan": "3. 扫描",
        "scan_btn": "扫描（仅预览，不删除任何内容）",
        "scanning": "正在扫描…",
        "step_clean": "4. 清理",
        "clean_btn": "清理",
        "cleaning": "正在清理…",
        "cat_appledouble": "._* 文件（AppleDouble）",
        "cat_ds_store": ".DS_Store 文件",
        "cat_system": "macOS 系统项目（.Spotlight-V100、.Trashes、__MACOSX…）",
        "cat_windows": "Windows 文件",
        "items_one": "{n} 项",
        "items_many": "{n} 项",
        "total": "共计：{items}，{size}",
        "already_clean": "已经很干净，没有需要删除的内容。",
        "preview_only": "仅预览：没有删除任何内容。",
        "show_list": "显示列表",
        "hide_list": "隐藏列表",
        "trash_warning": "该磁盘的废纸篓中有 {n} 个在访达中删除的文件，它们将被永久删除。勾选“保留磁盘的废纸篓”即可保留。",
        "confirm_title": "删除垃圾文件？",
        "confirm_text": "从 {drive} 删除 {items}（{size}）？\n此操作无法撤销。",
        "delete": "删除",
        "cancel": "取消",
        "done": "完成：已删除 {items}（释放 {size}）。",
        "partial": "已删除 {items}。有 {left} 项无法删除（磁盘为只读或正在使用）。",
        "came_back": "磁盘插入期间，macOS 重新创建了 {left} 个系统文件夹。这无害：请现在推出磁盘。",
        "ejected": "{drive} 已推出，可以拔下了。",
        "eject_failed": "无法推出 {drive}。请关闭其中打开的文件，然后在访达或文件资源管理器中推出。",
        "err_not_found": "该磁盘或文件夹已不存在。请点击“刷新”。",
        "err_not_folder": "这不是文件夹。",
        "err_forbidden": "这是系统文件夹或个人文件夹：请选择 SD 卡或 U 盘。",
        "err_junk_root": "该文件夹本身就是垃圾：请直接删除它。",
        "err_cannot_open": "无法读取该磁盘。在 macOS 上，请允许本应用访问可移除宗卷。",
        "choose_first": "请先选择一个磁盘。",
        "help": "帮助",
        "quit": "退出",
        "help_title": "Dotcleaner 如何工作",
        "help_text": (
            "从 Mac 向 SD 卡或 U 盘复制文件时，macOS 会添加隐藏文件：每个文件都有一个“._”副本，"
            "每个文件夹里有一个“.DS_Store”，还有“.Spotlight-V100”“.Trashes”“.fseventsd”等文件夹。"
            "在游戏掌机上，它们可能显示为无法启动的幽灵游戏。\n\n"
            "1. 选择磁盘：选择你的 SD 卡或 U 盘。\n"
            "2. 选项：Windows 文件、保留废纸篓、完成后推出。\n"
            "3. 扫描：显示将被删除的内容，不删除任何东西。\n"
            "4. 清理：在你确认后删除垃圾文件。\n\n"
            "你的游戏、存档、BIOS、照片和文档绝不会被改动。"
            "在 Mac 格式的磁盘（APFS、HFS+）上，只删除垃圾文件。"
        ),
        "about": "版本 {version} · MIT 许可证 · Shadowix84",
    },
    # -------------------------------------------------------------------- Hindi
    "hi": {
        "tagline": "SD कार्ड और USB ड्राइव से macOS की बेकार फ़ाइलें साफ़ करें",
        "language": "भाषा",
        "step_drive": "1. ड्राइव चुनें",
        "refresh": "रीफ़्रेश करें",
        "other_folder": "दूसरा फ़ोल्डर…",
        "choose_folder_title": "ड्राइव या फ़ोल्डर चुनें",
        "no_drive": "कोई SD कार्ड या USB ड्राइव नहीं मिली। एक लगाएँ, फिर “रीफ़्रेश करें” पर क्लिक करें।",
        "safe_mode": "Mac फ़ॉर्मेट वाली ड्राइव: सुरक्षित मोड। केवल बेकार फ़ाइलें हटेंगी, सिस्टम फ़ोल्डर रखे जाएँगे।",
        "step_options": "2. विकल्प",
        "opt_windows": "Windows फ़ाइलें भी हटाएँ (Thumbs.db, desktop.ini)",
        "opt_trash": "ड्राइव का ट्रैश रखें",
        "opt_eject": "काम पूरा होने पर ड्राइव इजेक्ट करें",
        "step_scan": "3. स्कैन करें",
        "scan_btn": "स्कैन करें (केवल पूर्वावलोकन, कुछ नहीं हटेगा)",
        "scanning": "स्कैन हो रहा है…",
        "step_clean": "4. साफ़ करें",
        "clean_btn": "साफ़ करें",
        "cleaning": "साफ़ किया जा रहा है…",
        "cat_appledouble": "._* फ़ाइलें (AppleDouble)",
        "cat_ds_store": ".DS_Store फ़ाइलें",
        "cat_system": "macOS सिस्टम आइटम (.Spotlight-V100, .Trashes, __MACOSX…)",
        "cat_windows": "Windows फ़ाइलें",
        "items_one": "{n} आइटम",
        "items_many": "{n} आइटम",
        "total": "कुल: {items}, {size}",
        "already_clean": "ड्राइव पहले से साफ़ है, हटाने के लिए कुछ नहीं है।",
        "preview_only": "केवल पूर्वावलोकन: कुछ भी नहीं हटाया गया।",
        "show_list": "सूची दिखाएँ",
        "hide_list": "सूची छिपाएँ",
        "trash_warning": "ड्राइव के ट्रैश में Finder से हटाई गई {n} फ़ाइलें हैं: वे हमेशा के लिए मिट जाएँगी। उन्हें रखने के लिए “ड्राइव का ट्रैश रखें” चुनें।",
        "confirm_title": "बेकार फ़ाइलें हटाएँ?",
        "confirm_text": "{drive} से {items} ({size}) हटाएँ?\nइसे वापस नहीं किया जा सकता।",
        "delete": "हटाएँ",
        "cancel": "रद्द करें",
        "done": "हो गया: {items} हटाए गए ({size} खाली हुआ)।",
        "partial": "{items} हटाए गए। {left} आइटम नहीं हटाए जा सके (ड्राइव केवल-पढ़ने योग्य है या उपयोग में है)।",
        "came_back": "ड्राइव लगी रहने के दौरान macOS ने {left} सिस्टम फ़ोल्डर फिर से बना दिए। यह हानिरहित है: अब ड्राइव इजेक्ट करें।",
        "ejected": "{drive} इजेक्ट हो गई: अब आप इसे निकाल सकते हैं।",
        "eject_failed": "{drive} इजेक्ट नहीं हो सकी। उस पर खुली फ़ाइलें बंद करें, फिर Finder या File Explorer से इजेक्ट करें।",
        "err_not_found": "यह ड्राइव या फ़ोल्डर अब मौजूद नहीं है। “रीफ़्रेश करें” पर क्लिक करें।",
        "err_not_folder": "यह फ़ोल्डर नहीं है।",
        "err_forbidden": "यह सिस्टम या होम फ़ोल्डर है: कोई SD कार्ड या USB ड्राइव चुनें।",
        "err_junk_root": "यह फ़ोल्डर खुद बेकार है: इसे सीधे हटा दें।",
        "err_cannot_open": "यह ड्राइव पढ़ी नहीं जा सकती। macOS पर, ऐप को रिमूवेबल वॉल्यूम तक पहुँच की अनुमति दें।",
        "choose_first": "पहले एक ड्राइव चुनें।",
        "help": "सहायता",
        "quit": "बंद करें",
        "help_title": "Dotcleaner कैसे काम करता है",
        "help_text": (
            "जब आप Mac से SD कार्ड या USB ड्राइव पर फ़ाइलें कॉपी करते हैं, तो macOS छिपी हुई फ़ाइलें जोड़ देता है: "
            "हर फ़ाइल के लिए एक “._” जुड़वाँ फ़ाइल, हर फ़ोल्डर में “.DS_Store”, और “.Spotlight-V100”, "
            "“.Trashes”, “.fseventsd” फ़ोल्डर। कंसोल पर ये ऐसे नकली गेम की तरह दिख सकती हैं जो चलते नहीं।\n\n"
            "1. ड्राइव चुनें: अपना SD कार्ड या USB ड्राइव चुनें।\n"
            "2. विकल्प: Windows फ़ाइलें, ट्रैश रखें, काम पूरा होने पर इजेक्ट करें।\n"
            "3. स्कैन करें: दिखाता है कि क्या हटेगा, कुछ नहीं हटाता।\n"
            "4. साफ़ करें: आपकी पुष्टि के बाद बेकार फ़ाइलें हटाता है।\n\n"
            "आपके गेम, सेव, BIOS, फ़ोटो और दस्तावेज़ कभी नहीं छुए जाते। "
            "Mac फ़ॉर्मेट वाली ड्राइव (APFS, HFS+) पर केवल बेकार फ़ाइलें हटाई जाती हैं।"
        ),
        "about": "संस्करण {version} · MIT लाइसेंस · Shadowix84",
    },
}


def tr(lang, key, **kw):
    """Translated text; falls back to English."""
    text = T.get(lang, T["en"]).get(key) or T["en"][key]
    return text.format(**kw) if kw else text


def items(lang, n):
    return tr(lang, "items_one" if n == 1 else "items_many", n=n)
