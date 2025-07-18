# -*- mode: python ; coding: utf-8 -*-
# GUI版用のPyInstallerスペックファイル

a = Analysis(
    ['hameln_gui.py'],
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
        'pandas'
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
    name='NovelArchiveTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Windows環境での警告回避
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI版はコンソールウィンドウを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 必要に応じてアイコンファイルを指定
)