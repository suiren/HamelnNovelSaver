#!/usr/bin/env python3
"""
全話取得機能のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_full_novel_download():
    """全話取得のテスト"""
    # テスト用の小説URL（章ページ）
    test_url = "https://syosetu.org/novel/378070/2.html"
    
    print(f"=== 全話取得テスト開始 ===")
    print(f"テストURL: {test_url}")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    try:
        # 全話取得を実行
        result = scraper.scrape_novel(test_url)
        
        if result:
            print(f"✓ 全話取得成功: {result}")
            return True
        else:
            print("✗ 全話取得失敗")
            return False
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scraper.close()

if __name__ == "__main__":
    test_full_novel_download()