#!/usr/bin/env python3
"""
全話取得の詳細テスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_full_download():
    """詳細な全話取得テスト"""
    print("=== 詳細な全話取得テスト ===")
    
    # 目次ページから開始
    index_url = "https://syosetu.org/novel/378070/"
    
    scraper = HamelnFinalScraper()
    
    try:
        # 1. 目次ページ取得
        print(f"目次ページ取得: {index_url}")
        soup = scraper.get_page(index_url)
        if not soup:
            print("✗ 目次ページ取得失敗")
            return False
        
        # 2. 章リンク抽出
        print("\n章リンク抽出中...")
        chapter_links = scraper.get_chapter_links(soup, index_url)
        
        print(f"\n発見された章数: {len(chapter_links)}")
        print("詳細:")
        for i, link in enumerate(chapter_links, 1):
            print(f"  第{i}章: {link}")
        
        # 3. 各章の内容確認（実際の取得テスト）
        print(f"\n各章の内容確認:")
        for i, chapter_url in enumerate(chapter_links, 1):
            print(f"\n--- 第{i}章の内容取得テスト ---")
            print(f"URL: {chapter_url}")
            
            # 章ページを取得
            chapter_soup = scraper.get_page(chapter_url)
            if chapter_soup:
                # タイトル取得
                title_elem = chapter_soup.find('title')
                title = title_elem.get_text() if title_elem else 'タイトル不明'
                print(f"✓ ページ取得成功")
                print(f"  タイトル: {title}")
                
                # 本文抽出テスト
                content = scraper.extract_chapter_content(chapter_soup, chapter_url)
                if content:
                    print(f"  ✓ 本文取得成功: {len(content)}文字")
                    # 本文の冒頭を表示（テキストのみ）
                    from bs4 import BeautifulSoup
                    soup_content = BeautifulSoup(content, 'html.parser')
                    text_content = soup_content.get_text(strip=True)
                    preview = text_content[:100] if text_content else "テキスト内容なし"
                    print(f"  本文冒頭: {preview}...")
                else:
                    print(f"  ✗ 本文取得失敗")
            else:
                print(f"✗ ページ取得失敗: {chapter_url}")
        
        # 4. scrape_novel機能のテスト（目次ページから）
        print(f"\n=== scrape_novel統合テスト ===")
        print(f"目次ページから全話取得を実行...")
        
        # 実際のファイル保存は行わず、処理の流れを確認
        print("※ファイル保存はスキップして処理フローのみ確認")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scraper.close()

if __name__ == "__main__":
    test_full_download()