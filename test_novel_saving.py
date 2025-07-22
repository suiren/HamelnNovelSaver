#!/usr/bin/env python3
"""
小説保存機能のテストスクリプト
修正後の動作確認用
"""

import sys
import json
from hameln_scraper.core.scraper import HamelnModularScraper

def test_novel_saving():
    """小説保存機能をテスト"""
    print("🔍 修正後の小説保存テスト開始")
    print("=" * 60)
    
    # テスト用URL
    test_url = "https://syosetu.org/novel/380014/"
    
    try:
        # スクレイパー初期化
        scraper = HamelnModularScraper()
        print(f"✅ スクレイパー初期化完了")
        
        # 小説保存実行
        print(f"\n📖 小説保存開始: {test_url}")
        result = scraper.scrape_novel(test_url)
        
        # 結果出力
        print("\n📊 保存結果:")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 重要な項目の確認
        if result.get('success'):
            print(f"\n✅ 保存成功:")
            print(f"  - 出力ディレクトリ: {result.get('output_dir')}")
            print(f"  - 保存章数: {result.get('saved_chapters')}")
            print(f"  - 総章数: {result.get('total_chapters')}")
            
            # 各章の詳細確認
            chapters = result.get('details', {}).get('chapters', [])
            print(f"\n📝 章の詳細:")
            for i, chapter in enumerate(chapters[:3]):  # 最初の3章のみ表示
                print(f"  {i+1}. {chapter.get('filename')}")
                print(f"     URL: {chapter.get('chapter_url')}")
                print(f"     file_path: {chapter.get('file_path')}")
                print(f"     content_length: {chapter.get('content_length')}")
        else:
            print(f"❌ 保存失敗: {result.get('error')}")
        
        # リソース解放
        scraper.close()
        
        return result
        
    except Exception as e:
        print(f"🚨 テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_novel_saving()
    
    # 終了コード設定
    if result and result.get('success'):
        print(f"\n🎉 テスト完了 - 保存成功")
        sys.exit(0)
    else:
        print(f"\n💥 テスト失敗")
        sys.exit(1)