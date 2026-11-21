#!/usr/bin/env python3
"""Write build/version_info.txt: the Windows "Properties > Details" of dotcleaner.exe
(product name, version, copyright), read by PyInstaller --version-file."""
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
with open(os.path.join(ROOT, "app", "dotcleaner_core.py"), encoding="utf-8") as f:
    version = re.search(r'^VERSION = "(.*)"$', f.read(), re.M).group(1)
nums = tuple(int(x) for x in (version.split(".") + ["0", "0", "0"])[:4])

text = f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}, mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Shadowix84'),
      StringStruct('FileDescription', 'Dotcleaner - clean macOS junk from SD cards and USB drives'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', 'dotcleaner'),
      StringStruct('LegalCopyright', 'Copyright (c) 2026 Shadowix84 - MIT License'),
      StringStruct('OriginalFilename', 'Dotcleaner-Windows.exe'),
      StringStruct('ProductName', 'Dotcleaner'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
with open(os.path.join(ROOT, "build", "version_info.txt"), "w", encoding="utf-8") as f:
    f.write(text)
print("build/version_info.txt written for", version)
