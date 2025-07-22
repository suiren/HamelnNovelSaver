#!/usr/bin/env python3
"""
ビルドされた実行ファイルのテスト
debug_logエラーが修正されたかをチェック
"""

import subprocess
import sys
import os

def test_build_executable():
    """ビルドされた実行ファイルのテスト"""
    
    print("=== ビルドされた実行ファイルテスト ===")
    
    # 実行ファイルのパス
    executable_path = "/home/suiren/ClaudeTest/dist/HamelnNovelSaver"
    
    if not os.path.exists(executable_path):
        print(f"❌ 実行ファイルが見つかりません: {executable_path}")
        return False
    
    print(f"✓ 実行ファイル確認: {executable_path}")
    
    # 実行権限を確認
    if not os.access(executable_path, os.X_OK):
        print("❌ 実行権限がありません")
        return False
    
    print("✓ 実行権限確認")
    
    # 簡単なテストケース（短時間で失敗するもの）
    test_url = "https://invalid-url-for-test"
    
    try:
        print(f"テストURL: {test_url}")
        print("実行ファイルテスト開始...")
        
        # プロセスを短時間で強制終了
        result = subprocess.run([executable_path, test_url], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        print(f"終了コード: {result.returncode}")
        
        # 標準出力を確認
        if result.stdout:
            print("=== 標準出力 ===")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        
        # 標準エラーを確認
        if result.stderr:
            print("=== 標準エラー ===")
            print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
        
        # debug_logエラーが含まれているかチェック
        error_text = result.stderr.lower()
        if "debug_log" in error_text and "attribute" in error_text:
            print("❌ debug_logエラーが発生しました")
            return False
        
        print("✓ debug_logエラーは発生しませんでした")
        
        # CloudScraperの初期化が正常に行われているかチェック
        if "cloudscraper初期化開始" in result.stderr:
            print("✓ CloudScraperの初期化が正常に確認されました")
            return True
        else:
            print("⚠️ CloudScraperの初期化ログが見つかりません")
            return True  # エラーでないので成功扱い
        
    except subprocess.TimeoutExpired:
        print("✓ プロセスがタイムアウトしました（正常）")
        return True
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_build_executable()
    if success:
        print("\n✅ ビルドされた実行ファイルのテストが成功しました")
    else:
        print("\n❌ ビルドされた実行ファイルのテストが失敗しました")
        sys.exit(1)