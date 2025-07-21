#!/usr/bin/env python3
"""
Phase 3 セッション復旧・状況診断スクリプト
次セッションでの即座復旧を支援
"""

import os
import subprocess
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """ファイル存在確認"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} が見つかりません")
        return False


def run_command(command, description):
    """コマンド実行と結果確認"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}: 成功")
            return True, result.stdout
        else:
            print(f"❌ {description}: 失敗")
            print(f"   エラー: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description}: 例外発生 - {e}")
        return False, str(e)


def main():
    """メイン復旧診断"""
    print("🔍 Phase 3 セッション状況診断開始")
    print("=" * 50)
    
    # 1. 基本ファイル確認
    print("\n📁 1. 重要ファイル確認")
    critical_files = [
        ("PHASE_3_PROGRESS_TRACKER.md", "進捗トラッカー"),
        ("NEXT_SESSION_STARTUP_GUIDE.md", "復旧ガイド"),
        ("CURRENT_STATE_SNAPSHOT.md", "状態スナップショット"),
        ("SESSION_RECOVERY_TEMPLATE.md", "復旧テンプレート"),
        ("test_parsing_module.py", "解析モジュールテスト")
    ]
    
    file_status = []
    for filepath, desc in critical_files:
        status = check_file_exists(filepath, desc)
        file_status.append(status)
    
    # 2. モジュールファイル確認
    print("\n🐍 2. Python モジュール確認")
    module_files = [
        ("hameln_scraper/parsing/content_extractor.py", "コンテンツ抽出モジュール"),
        ("hameln_scraper/parsing/url_extractor.py", "URL抽出モジュール"),
        ("hameln_scraper/parsing/validator.py", "検証モジュール"),
        ("hameln_scraper/core/scraper.py", "メインスクレイパー"),
        ("hameln_scraper/network/client.py", "ネットワーククライアント")
    ]
    
    for filepath, desc in module_files:
        status = check_file_exists(filepath, desc)
        file_status.append(status)
    
    # 3. Git状況確認
    print("\n📋 3. Git状況確認")
    git_commands = [
        ("git branch --show-current", "現在のブランチ確認"),
        ("git status --porcelain", "ワーキングディレクトリ状態"),
        ("git log --oneline -3", "最新コミット確認")
    ]
    
    git_status = []
    for cmd, desc in git_commands:
        success, output = run_command(cmd, desc)
        git_status.append(success)
        if success and output:
            print(f"   出力: {output.strip()}")
    
    # 4. Python環境確認
    print("\n🔧 4. Python環境確認")
    python_checks = [
        ("python --version", "Python バージョン"),
        ("python -c 'import pytest; print(f\"pytest {pytest.__version__}\")'", "pytest確認"),
        ("python -c 'import bs4; print(f\"BeautifulSoup {bs4.__version__}\")'", "BeautifulSoup確認")
    ]
    
    for cmd, desc in python_checks:
        success, output = run_command(cmd, desc)
        if success and output:
            print(f"   {output.strip()}")
    
    # 5. テスト実行確認
    print("\n🧪 5. テスト実行確認")
    if os.path.exists("test_parsing_module.py"):
        success, output = run_command("python -m pytest test_parsing_module.py -q", "解析モジュールテスト")
        if success:
            print(f"   結果: {output.strip()}")
    
    # 6. 診断結果サマリー
    print("\n" + "=" * 50)
    print("📊 診断結果サマリー")
    
    total_files = len(file_status)
    ok_files = sum(file_status)
    
    print(f"📁 ファイル状況: {ok_files}/{total_files} ファイル存在")
    print(f"📋 Git状況: {'✅ 正常' if all(git_status) else '⚠️ 要確認'}")
    
    if ok_files == total_files and all(git_status):
        print("\n🎉 状況: 完全復旧可能")
        print("   次セッションで通常継続指示を使用してください")
    elif ok_files >= total_files * 0.8:
        print("\n⚠️ 状況: 部分的問題あり")
        print("   次セッションで完全復旧指示を使用してください")
    else:
        print("\n🆘 状況: 重大な問題")
        print("   次セッションで緊急復旧指示を使用してください")
    
    # 7. 次セッション用指示生成
    print("\n📝 次セッション用指示:")
    if ok_files == total_files:
        print("┌─ コピペ用 ─────────────────────────────────")
        print("│ NEXT_SESSION_STARTUP_GUIDE.mdに従ってPhase 3を継続してください。")
        print("└────────────────────────────────────────────")
    else:
        print("┌─ コピペ用 ─────────────────────────────────")
        print("│ 前セッションの継続です。NEXT_SESSION_STARTUP_GUIDE.md")
        print("│ の手順で復旧後、Phase 3を継続してください。")
        print("└────────────────────────────────────────────")


if __name__ == "__main__":
    main()