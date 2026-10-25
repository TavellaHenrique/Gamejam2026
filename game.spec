# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_root = Path(SPECPATH).resolve()
pygame_datas, pygame_binaries, pygame_hiddenimports = collect_all("pygame")

a = Analysis(
    [str(project_root / "game" / "main.py")],
    pathex=[str(project_root)],
    binaries=pygame_binaries,
    datas=[
        (str(project_root / "game" / "assets"), "assets"),
        (str(project_root / "game" / "data" / "dialogues.json"), "data"),
        *pygame_datas,
    ],
    hiddenimports=pygame_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Fatec Presas Abertas",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
