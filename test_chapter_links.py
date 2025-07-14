#!/usr/bin/env python3
"""
章リンク抽出のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_chapter_links():
    """章リンク抽出のテスト"""
    # 目次ページのURL
    index_url = "https://syosetu.org/novel/378070/"
    
    print(f"=== 章リンク抽出テスト開始 ===")
    print(f"目次URL: {index_url}")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    try:
        # 目次ページを取得
        soup = scraper.get_page(index_url)
        if not soup:
            print("✗ 目次ページの取得に失敗")
            return False
        
        print("✓ 目次ページの取得成功")
        
        # 章リンクを抽出
        chapter_links = scraper.get_chapter_links(soup, index_url)
        
        print(f"抽出された章数: {len(chapter_links)}")
        
        # 抽出された章リンクを表示
        for i, link in enumerate(chapter_links[:5]):  # 最初の5つだけ表示
            print(f"章{i+1}: {link}")
        
        if len(chapter_links) > 5:
            print(f"... 他{len(chapter_links)-5}章")
        
        # 検証: 全てのリンクが同じ作品ID（378070）を含んでいるか
        all_valid = True
        for link in chapter_links:
            if '378070' not in link:
                print(f"✗ 不正なリンク発見: {link}")
                all_valid = False
        
        if all_valid and chapter_links:
            print("✓ 全ての章リンクが正しい作品IDを含んでいます")
            return True
        elif not chapter_links:
            print("✗ 章リンクが取得できませんでした")
            return False
        else:
            print("✗ 間違った作品の章リンクが混入しています")
            return False
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scraper.close()

if __name__ == "__main__":
    test_chapter_links()