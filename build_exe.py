#!/usr/bin/env python3
"""
Windows実行可能ファイル(.exe)作成スクリプト
PyInstallerを使用してGUIアプリケーションをビルドします
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """実行可能ファイルをビルド"""
    print("ハーメルン小説保存ツール - Windows実行可能ファイル作成")
    print("=" * 60)
    
    # 現在のディレクトリ
    current_dir = Path.cwd()
    
    # 必要なファイルの存在確認
    required_files = ['hameln_gui.py', 'hameln_scraper.py']
    for file in required_files:
        if not (current_dir / file).exists():
            print(f"エラー: {file} が見つかりません")
            return False
    
    # ビルドコマンドを構築
    build_cmd = [
        'pyinstaller',
        '--onefile',                    # 単一ファイルとして出力
        '--windowed',                   # コンソールウィンドウを非表示
        '--name=HamelnNovelSaver',      # 実行ファイル名
        '--icon=icon.ico',              # アイコン（オプション）
        '--add-data=hameln_scraper.py;.',  # 追加ファイル
        '--clean',                      # キャッシュクリア
        'hameln_gui.py'
    ]
    
    # アイコンファイルがない場合は除外
    if not (current_dir / 'icon.ico').exists():
        build_cmd = [cmd for cmd in build_cmd if not cmd.startswith('--icon')]
    
    print("ビルドコマンド:")
    print(" ".join(build_cmd))
    print()
    
    try:
        # PyInstallerでビルド実行
        print("ビルド開始...")
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ ビルド完了!")
            
            # 出力ファイルの場所を確認
            exe_path = current_dir / 'dist' / 'HamelnNovelSaver.exe'
            if exe_path.exists():
                print(f"✓ 実行ファイル作成: {exe_path}")
                print(f"ファイルサイズ: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                
                # 使用方法を表示
                print("\n使用方法:")
                print("1. dist/HamelnNovelSaver.exe をダブルクリックで起動")
                print("2. 小説のURLを入力してダウンロード開始")
                print("3. 保存先フォルダを選択（デフォルト: saved_novels）")
                
                return True
            else:
                print("✗ 実行ファイルが見つかりません")
                return False
        else:
            print("✗ ビルドに失敗しました")
            print("エラー出力:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("✗ PyInstallerが見つかりません")
        print("以下のコマンドでインストールしてください:")
        print("pip install pyinstaller")
        return False
    except Exception as e:
        print(f"✗ ビルド中にエラーが発生しました: {e}")
        return False

def clean_build_files():
    """ビルド時の一時ファイルを削除"""
    print("\n一時ファイルの削除中...")
    
    dirs_to_remove = ['build', '__pycache__']
    files_to_remove = ['*.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ {dir_name} を削除")
    
    import glob
    for pattern in files_to_remove:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"✓ {file} を削除")

def main():
    """メイン処理"""
    print("実行可能ファイル作成を開始しますか？ (y/n): ", end="")
    
    if input().lower() in ['y', 'yes']:
        success = build_executable()
        
        if success:
            print("\n一時ファイルを削除しますか？ (y/n): ", end="")
            if input().lower() in ['y', 'yes']:
                clean_build_files()
        
        print("\n完了!")
    else:
        print("キャンセルされました")

if __name__ == "__main__":
    main()