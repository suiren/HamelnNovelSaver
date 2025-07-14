@echo off
chcp 65001 > nul
echo Hameln Novel Saver - Windows Executable Builder
echo ============================================================

:: Change to the script directory
cd /d "%~dp0"

:: Check if required files exist
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in current directory
    echo Current directory: %CD%
    echo Please ensure all files are in the same folder
    pause
    exit /b 1
)

if not exist "hameln_gui.py" (
    echo ERROR: hameln_gui.py not found in current directory
    echo Current directory: %CD%
    echo Please ensure all files are in the same folder
    pause
    exit /b 1
)

if not exist "hameln_scraper.py" (
    echo ERROR: hameln_scraper.py not found in current directory
    echo Current directory: %CD%
    echo Please ensure all files are in the same folder
    pause
    exit /b 1
)

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Install required libraries
echo Installing required libraries...
echo Current directory: %CD%
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

:: Build with PyInstaller
echo.
echo Building executable...
pyinstaller --onefile --windowed --name=HamelnNovelSaver --add-data="hameln_scraper.py;." --clean hameln_gui.py

:: Check build result
if exist "dist\HamelnNovelSaver.exe" (
    echo.
    echo SUCCESS: Build completed!
    echo Executable: dist\HamelnNovelSaver.exe
    echo.
    echo Usage:
    echo 1. Double-click dist\HamelnNovelSaver.exe to start
    echo 2. Enter novel URL and start download
    echo 3. Select save folder (default: saved_novels)
) else (
    echo.
    echo ERROR: Build failed
    echo Please check the error log above
)

echo.
echo Cleaning temporary files...
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.spec" del "*.spec"

pause