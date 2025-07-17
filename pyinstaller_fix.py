#!/usr/bin/env python3
"""
PyInstaller実行ファイル用の修正パッチ
感想ページ取得とリソースファイル取得の問題を修正
"""

import os
import sys

def apply_pyinstaller_fixes():
    """PyInstaller実行環境での修正を適用"""
    
    # 1. 実行ファイルのパス検出
    if getattr(sys, 'frozen', False):
        # PyInstallerでビルドされた実行ファイルの場合
        application_path = sys._MEIPASS
        print(f"PyInstaller実行環境を検出: {application_path}")
        
        # 2. 一時ディレクトリの設定
        temp_dir = os.path.join(os.path.expanduser("~"), "hameln_temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 3. 環境変数の設定
        os.environ['HAMELN_TEMP_DIR'] = temp_dir
        os.environ['HAMELN_PYINSTALLER'] = '1'
        
        return True
    else:
        print("通常のPython実行環境")
        return False

def get_resource_path(relative_path):
    """リソースファイルのパスを取得（PyInstaller対応）"""
    if getattr(sys, 'frozen', False):
        # PyInstallerでビルドされた実行ファイルの場合
        base_path = sys._MEIPASS
    else:
        # 通常のPython実行の場合
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    apply_pyinstaller_fixes()