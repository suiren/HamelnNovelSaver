#!/usr/bin/env python3
"""
完全な小説保存機能のテスト
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_complete_functionality():
    """完全な小説保存機能のテスト"""
    
    print("=== 完全な小説保存機能テスト ===")
    
    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    print(f"テスト用ディレクトリ: {temp_dir}")
    
    try:
        # スクレイパーを初期化
        scraper = HamelnFinalScraper()
        
        print("✓ HamelnFinalScraper初期化成功")
        
        # テスト用の小説URL（実際のハーメルンURL）
        test_url = "https://syosetu.org/novel/380014/"
        
        print(f"テスト対象URL: {test_url}")
        print("小説取得テスト開始...")
        
        # 現在のディレクトリを一時ディレクトリに変更
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # 小説を取得
            result = scraper.scrape_novel(test_url)
            
            print(f"取得結果: {result}")
            
            if result.get('success'):
                print("✓ 小説取得成功")
                print(f"  - タイトル: {result.get('title', 'N/A')}")
                print(f"  - 作者: {result.get('author', 'N/A')}")
                print(f"  - 章数: {result.get('chapters', 'N/A')}")
                print(f"  - 出力ディレクトリ: {result.get('output_dir', 'N/A')}")
                
                # 保存されたファイルを確認
                output_dir = result.get('output_dir')
                if output_dir and os.path.exists(output_dir):
                    files = os.listdir(output_dir)
                    print(f"  - 保存されたファイル数: {len(files)}")
                    if files:
                        print("  - 保存ファイル:")
                        for file in files[:10]:  # 最大10個表示
                            print(f"    - {file}")
                        if len(files) > 10:
                            print(f"    ... 他{len(files)-10}個")
                    
                    # resourcesフォルダの確認
                    resources_dir = os.path.join(output_dir, 'resources')
                    if os.path.exists(resources_dir):
                        resource_files = os.listdir(resources_dir)
                        print(f"  - リソースファイル数: {len(resource_files)}")
                    else:
                        print("  - リソースディレクトリが見つかりません")
                else:
                    print("  - 出力ディレクトリが見つかりません")
                
                return True
            else:
                print(f"❌ 小説取得失敗: {result.get('error', 'Unknown error')}")
                return False
                
        finally:
            os.chdir(original_dir)
            
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 一時ディレクトリを削除
        shutil.rmtree(temp_dir, ignore_errors=True)
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    success = test_complete_functionality()
    if success:
        print("\n✅ 完全な小説保存機能テストが成功しました")
    else:
        print("\n❌ 完全な小説保存機能テストが失敗しました")
        sys.exit(1)