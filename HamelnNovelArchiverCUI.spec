# -*- mode: python ; coding: utf-8 -*-
# CUI版用のPyInstallerスペックファイル

a = Analysis(
    ['hameln_scraper_final.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test', 
        'tests', 
        'unittest',
        'pdb',
        'doctest',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter'
    ],
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
    name='NovelArchiveToolCUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Windows環境での警告回避
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CUI版はコンソールウィンドウを表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)