@echo off
chcp 65001 > nul
echo Hameln Novel Archiver - Unified Build Script
echo.

rem Change to actual directory path to avoid UNC path issues
if "%~d0" NEQ "" (
    %~d0
    cd "%~dp0"
)

:menu
echo ===========================================
echo    Build Options
echo ===========================================
echo 1. Build GUI version only (HamelnNovelArchiverGUI)
echo 2. Build CUI version only (HamelnNovelArchiverCUI)
echo 3. Build both versions (GUI + CUI)
echo 4. Build legacy version (Backward compatibility)
echo 5. Exit
echo ===========================================
set /p choice=Please select (1-5): 

if "%choice%"=="1" goto build_gui
if "%choice%"=="2" goto build_cui
if "%choice%"=="3" goto build_both
if "%choice%"=="4" goto build_legacy
if "%choice%"=="5" goto exit
echo Invalid selection.
goto menu

:build_gui
echo.
echo Building GUI version...
call :install_deps
call :check_modules
pyinstaller --clean HamelnNovelArchiverGUI.spec
call :check_result "dist\HamelnNovelArchiverGUI.exe" "GUI version"
goto menu

:build_cui
echo.
echo Building CUI version...
call :install_deps
call :check_modules
pyinstaller --clean HamelnNovelArchiverCUI.spec
call :check_result "dist\HamelnNovelArchiverCUI.exe" "CUI version"
goto menu

:build_both
echo.
echo Building both GUI and CUI versions...
call :install_deps
call :check_modules
echo Building GUI version...
pyinstaller --clean HamelnNovelArchiverGUI.spec
echo Building CUI version...
pyinstaller --clean HamelnNovelArchiverCUI.spec
call :check_result "dist\HamelnNovelArchiverGUI.exe" "GUI version"
call :check_result "dist\HamelnNovelArchiverCUI.exe" "CUI version"
goto menu

:build_legacy
echo.
echo Building legacy version...
call :install_deps
call :check_modules
pyinstaller --clean HamelnNovelSaver.spec
call :check_result "dist\HamelnNovelArchiver.exe" "Legacy version"
goto menu

:install_deps
echo Installing required modules...
pip install pyinstaller brotli cloudscraper undetected-chromedriver selenium beautifulsoup4 lxml requests Pillow
exit /b

:check_modules
if not exist "hameln_scraper\" (
    echo Error: hameln_scraper module not found
    echo Please ensure you are in the refactoring branch (refactor/code-restructuring)
    pause
    exit /b 1
)
exit /b

:check_result
if exist "%~1" (
    echo ^✓ %~2 build completed!
    echo Executable: %~1
    echo.
    if "%~2"=="GUI version" (
        echo ^✨ GUI version features:
        echo - Graphical user interface
        echo - User-friendly operation
        echo - Real-time progress display
        echo - File selection dialogs
    )
    if "%~2"=="CUI version" (
        echo ^✨ CUI version features:
        echo - Command line operation
        echo - Lightweight and fast
        echo - Batch processing support
        echo - Server environment compatible
    )
) else (
    echo ^✗ %~2 build failed
    echo %~1 was not created
)
echo.
exit /b

:exit
echo Exiting build script.
pause