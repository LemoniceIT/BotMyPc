# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for BotMyPC.
Generates a standalone windowed Windows executable with custom tray icon,
assets, and all required hidden imports.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect CustomTkinter assets and data files
customtkinter_datas = collect_data_files('customtkinter')

added_datas = [
    ('assets', 'assets'),
    ('locales', 'locales'),
] + customtkinter_datas

hidden_imports = [
    'customtkinter',
    'pystray',
    'PIL',
    'PIL._tkinter_finder',
    'keyring',
    'keyring.backends',
    'keyring.backends.Windows',
    'cryptography',
    'psutil',
    'win32crypt',
    'winreg',
    'ctypes',
    'i18n',
    'icons',
    'commands.system',
    'commands.applications',
    'commands.processes',
] + collect_submodules('telegram')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'unittest', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BotMyPC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed GUI without cmd console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'ico\BotMyPc.ico',
)
