# -*- mode: python ; coding: utf-8 -*-
"""
ハーメルン小説保存ツール - 統合ビルド設定
リファクタリング版hameln_scraperモジュールを含む
"""

# リファクタリング版モジュールを含むための設定
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
    'hameln_scraper.output'
]

a = Analysis(
    ['hameln_gui.py'],
    pathex=[],
    binaries=[],
    datas=hameln_scraper_datas,
    hiddenimports=hameln_scraper_hiddenimports + [
        # 元々必要な隠れインポート
        'cloudscraper',
        'undetected_chromedriver',
        'selenium',
        'bs4',
        'lxml',
        'brotli',
        'PIL',
        'PIL.Image'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# 重複除去
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HamelnNovelArchiver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリケーションなのでコンソールを非表示
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # アイコンファイルがあれば指定
)