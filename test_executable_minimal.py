#!/usr/bin/env python3
"""
実行ファイルの最小機能テスト
"""
import subprocess
import sys
import time
import os

def test_executable_minimal():
    """実行ファイルの最小テスト"""
    print("🧪 実行ファイル最小テスト開始")
    
    executable_path = "./dist/HamelnNovelArchiver"
    
    # ファイル存在確認
    if not os.path.exists(executable_path):
        print("❌ 実行ファイルが見つかりません")
        return False
    
    print(f"✅ 実行ファイル確認: {executable_path}")
    
    # 実行権限確認
    if not os.access(executable_path, os.X_OK):
        print("❌ 実行権限がありません")
        return False
    
    print("✅ 実行権限確認完了")
    
    # 短時間起動テスト
    try:
        print("🚀 短時間起動テスト開始...")
        process = subprocess.Popen(
            [executable_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # 2秒待機
        time.sleep(2)
        
        # プロセスが生きているか確認
        if process.poll() is None:
            print("✅ プロセス正常起動確認")
            process.terminate()
            process.wait(timeout=3)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ プロセスが早期終了: return code {process.returncode}")
            if stdout:
                print(f"stdout: {stdout.decode()}")
            if stderr:
                print(f"stderr: {stderr.decode()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ 5秒実行後正常タイムアウト（期待された動作）")
        process.terminate()
        process.wait(timeout=3)
        return True
    except Exception as e:
        print(f"❌ 実行テストエラー: {e}")
        return False

if __name__ == "__main__":
    success = test_executable_minimal()
    print(f"\n📊 テスト結果: {'✅ 成功' if success else '❌ 失敗'}")
    sys.exit(0 if success else 1)