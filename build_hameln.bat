@echo off
echo ハーメルン小説保存ツール - 統合ビルド（リファクタリング版対応）
echo.

echo 必要なモジュールをインストール中...
pip install pyinstaller brotli cloudscraper undetected-chromedriver selenium beautifulsoup4 lxml requests Pillow

echo.
echo リファクタリング版モジュール確認中...
if not exist "hameln_scraper\" (
    echo エラー: hameln_scraperモジュールが見つかりません
    echo リファクタリング版ブランチ（refactor/code-restructuring）にいることを確認してください
    pause
    exit /b 1
)

echo.
echo ビルド開始（リファクタリング版含む）...
pyinstaller --clean HamelnNovelSaver.spec

echo.
if exist "dist\HamelnNovelArchiver.exe" (
    echo ✅ ビルド完了！
    echo 実行ファイル: dist\HamelnNovelArchiver.exe
    echo.
    echo ✨ 新機能:
    echo - モジュール分割による保守性向上
    echo - テスト駆動開発による品質保証
    echo - 段階的フォールバック機能
) else (
    echo ❌ ビルド失敗
    echo dist\HamelnNovelArchiver.exe が作成されませんでした
)
echo.
pause