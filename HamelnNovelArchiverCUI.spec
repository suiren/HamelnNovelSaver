# -*- mode: python ; coding: utf-8 -*-
# CUI版用のPyInstallerスペックファイル - v2.0モジュール構造対応版

# リファクタリング版hameln_scraperモジュールを含むための設定
hameln_scraper_datas = []
hameln_scraper_hiddenimports = [
    'hameln_scraper',
    'hameln_scraper.core',
    'hameln_scraper.core.scraper',
    'hameln_scraper.core.config', 
    'hameln_scraper.network',
    'hameln_scraper.network.client',
    'hameln_scraper.network.user_agent',
    'hameln_scraper.network.compression',
    'hameln_scraper.parsing',
    'hameln_scraper.parsing.validator',
    'hameln_scraper.parsing.content_extractor',
    'hameln_scraper.parsing.url_extractor',
    'hameln_scraper.resources',
    'hameln_scraper.resources.processor',
    'hameln_scraper.resources.downloader',
    'hameln_scraper.resources.file_manager',
    'hameln_scraper.resources.saver',
    'hameln_scraper.resources.resource_downloader',
    'hameln_scraper.novel',
    'hameln_scraper.novel.processor',
    'hameln_scraper.comments',
    'hameln_scraper.comments.handler',
    'hameln_scraper.output',
    'hameln_scraper.output.file_manager'
]

a = Analysis(
    ['hameln_scraper_final.py'],
    pathex=[],
    binaries=[],
    datas=hameln_scraper_datas,
    hiddenimports=hameln_scraper_hiddenimports + [
        # 外部依存関係
        'cloudscraper',
        'undetected_chromedriver',
        'selenium',
        'bs4',
        'lxml',
        'brotli',
        'PIL',
        'PIL.Image',
        'requests',
        'urllib3'
    ],
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
    name='HamelnNovelArchiverCUI',
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