@echo off
echo ハーメルン小説保存ツール - 統合ビルドスクリプト
echo.

:menu
echo ===========================================
echo    ビルドオプション選択
echo ===========================================
echo 1. GUI版のみビルド (HamelnNovelArchiverGUI)
echo 2. CUI版のみビルド (HamelnNovelArchiverCUI)
echo 3. 両方をビルド (GUI + CUI)
echo 4. 従来版（後方互換性）
echo 5. 終了
echo ===========================================
set /p choice=選択してください (1-5): 

if "%choice%"=="1" goto build_gui
if "%choice%"=="2" goto build_cui
if "%choice%"=="3" goto build_both
if "%choice%"=="4" goto build_legacy
if "%choice%"=="5" goto exit
echo 無効な選択です。
goto menu

:build_gui
echo.
echo GUI版をビルドしています...
call :install_deps
call :check_modules
pyinstaller --clean HamelnNovelArchiverGUI.spec
call :check_result "dist\HamelnNovelArchiverGUI.exe" "GUI版"
goto menu

:build_cui
echo.
echo CUI版をビルドしています...
call :install_deps
call :check_modules
pyinstaller --clean HamelnNovelArchiverCUI.spec
call :check_result "dist\HamelnNovelArchiverCUI.exe" "CUI版"
goto menu

:build_both
echo.
echo GUI版とCUI版の両方をビルドしています...
call :install_deps
call :check_modules
echo GUI版をビルド中...
pyinstaller --clean HamelnNovelArchiverGUI.spec
echo CUI版をビルド中...
pyinstaller --clean HamelnNovelArchiverCUI.spec
call :check_result "dist\HamelnNovelArchiverGUI.exe" "GUI版"
call :check_result "dist\HamelnNovelArchiverCUI.exe" "CUI版"
goto menu

:build_legacy
echo.
echo 従来版をビルドしています...
call :install_deps
call :check_modules
pyinstaller --clean HamelnNovelSaver.spec
call :check_result "dist\HamelnNovelArchiver.exe" "従来版"
goto menu

:install_deps
echo 必要なモジュールをインストール中...
pip install pyinstaller brotli cloudscraper undetected-chromedriver selenium beautifulsoup4 lxml requests Pillow
exit /b

:check_modules
if not exist "hameln_scraper\" (
    echo エラー: hameln_scraperモジュールが見つかりません
    echo リファクタリング版ブランチ（refactor/code-restructuring）にいることを確認してください
    pause
    exit /b 1
)
exit /b

:check_result
if exist "%~1" (
    echo ✅ %~2 ビルド完了！
    echo 実行ファイル: %~1
    echo.
    if "%~2"=="GUI版" (
        echo ✨ GUI版の特徴:
        echo - グラフィカルユーザーインターフェース
        echo - 使いやすい操作画面
        echo - リアルタイム進捗表示
        echo - ファイル選択ダイアログ
    )
    if "%~2"=="CUI版" (
        echo ✨ CUI版の特徴:
        echo - コマンドライン操作
        echo - 軽量で高速
        echo - バッチ処理に最適
        echo - サーバー環境対応
    )
) else (
    echo ❌ %~2 ビルド失敗
    echo %~1 が作成されませんでした
)
echo.
exit /b

:exit
echo ビルドスクリプトを終了します。
pause