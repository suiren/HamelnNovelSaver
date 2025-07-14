# Hameln Novel Saver - PowerShell Build Script
# Windows用実行可能ファイル作成スクリプト

Write-Host "Hameln Novel Saver - Windows Executable Builder" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Pythonのインストール確認
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# 必要なライブラリのインストール
Write-Host ""
Write-Host "Installing required libraries..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Libraries installed successfully" -ForegroundColor Green
    } else {
        throw "pip install failed"
    }
}
catch {
    Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# PyInstallerでビルド実行
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
try {
    pyinstaller --onefile --windowed --name=HamelnNovelSaver --add-data="hameln_scraper.py;." --clean hameln_gui.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build process completed" -ForegroundColor Green
    } else {
        throw "PyInstaller build failed"
    }
}
catch {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# 結果確認
Write-Host ""
if (Test-Path "dist\HamelnNovelSaver.exe") {
    Write-Host "SUCCESS: Build completed!" -ForegroundColor Green
    Write-Host "Executable: dist\HamelnNovelSaver.exe" -ForegroundColor Green
    
    # ファイルサイズを表示
    $fileSize = (Get-Item "dist\HamelnNovelSaver.exe").Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 1)
    Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "1. Double-click dist\HamelnNovelSaver.exe to start" -ForegroundColor White
    Write-Host "2. Enter novel URL and start download" -ForegroundColor White
    Write-Host "3. Select save folder (default: saved_novels)" -ForegroundColor White
} else {
    Write-Host "ERROR: Build failed - executable not found" -ForegroundColor Red
    Write-Host "Please check the error log above" -ForegroundColor Red
}

# 一時ファイルの削除
Write-Host ""
Write-Host "Cleaning temporary files..." -ForegroundColor Yellow
$foldersToRemove = @("build", "__pycache__")
$filesToRemove = @("*.spec")

foreach ($folder in $foldersToRemove) {
    if (Test-Path $folder) {
        Remove-Item $folder -Recurse -Force
        Write-Host "Removed: $folder" -ForegroundColor Gray
    }
}

foreach ($filePattern in $filesToRemove) {
    $files = Get-ChildItem $filePattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Remove-Item $file -Force
        Write-Host "Removed: $($file.Name)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Build process completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"