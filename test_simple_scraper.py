#!/usr/bin/env python3
"""
シンプルなスクレイパーテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper.core.scraper import HamelnScraper
from hameln_scraper.core.config import ScraperConfig

def test_simple_scraper():
    """シンプルなスクレイパーテスト"""
    
    print("=== シンプルなスクレイパーテスト ===")
    
    try:
        # 設定を作成
        config = ScraperConfig()
        
        # スクレイパーを初期化
        scraper = HamelnScraper(config)
        
        print("✓ HamelnScraper初期化成功")
        
        # テスト用の小説URL
        test_url = "https://syosetu.org/novel/380014/"
        
        print(f"テスト対象URL: {test_url}")
        print("基本的な小説取得テスト開始...")
        
        # 小説を取得
        result = scraper.scrape_novel(test_url)
        
        print(f"取得結果: {result}")
        
        if result.get('success'):
            print("✓ 小説取得成功")
            print(f"  - タイトル: {result.get('title', 'N/A')}")
            print(f"  - 作者: {result.get('author', 'N/A')}")
            print(f"  - URL: {result.get('url', 'N/A')}")
            
            html_content = result.get('html_content', '')
            if html_content:
                print(f"  - HTMLコンテンツ: {len(html_content)}文字")
                print(f"  - プレビュー: {html_content[:200]}...")
            else:
                print("  - HTMLコンテンツが空です")
                
            return True
        else:
            print(f"❌ 小説取得失敗: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    success = test_simple_scraper()
    if success:
        print("\n✅ シンプルなスクレイパーテストが成功しました")
    else:
        print("\n❌ シンプルなスクレイパーテストが失敗しました")
        sys.exit(1)