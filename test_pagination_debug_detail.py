#!/usr/bin/env python3
"""
ページネーション検出の詳細デバッグ
問題：14個のリンクが見つかっているが1ページしか認識されない
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def debug_pagination_detection():
    """ページネーション検出処理の詳細デバッグ"""
    print("ページネーション検出処理の詳細デバッグを開始...")
    
    scraper = HamelnFinalScraper()
    
    # 問題が発生したURL
    test_url = "https://syosetu.org/?mode=review&nid=378070"
    
    try:
        # 感想ページを取得
        comments_page = scraper.get_page(test_url)
        if not comments_page:
            print("❌ 感想ページの取得に失敗")
            return False
        
        print(f"ベースURL: {test_url}")
        print(f"ベースページ番号: {scraper.extract_page_number(test_url)}")
        
        # 手動でページネーション検出をデバッグ
        page_links = []
        base_page_num = scraper.extract_page_number(test_url)
        
        pagination_selectors = [
            'div.pagination a',
            'div.pager a', 
            'div.page-nav a',
            'a[href*="mode=review"][href*="page="]',
            'a[href*="&page="]'
        ]
        
        for selector in pagination_selectors:
            pagination_links = comments_page.select(selector)
            if pagination_links:
                print(f"\n=== セレクター: {selector} ===")
                print(f"発見されたリンク数: {len(pagination_links)}")
                
                for i, link in enumerate(pagination_links):
                    href = link.get('href')
                    text = link.get_text().strip()
                    print(f"  [{i+1}] href='{href}', text='{text}'")
                    
                    if href and 'page=' in href:
                        # 相対URLを絶対URLに変換
                        if href.startswith('?'):
                            full_url = test_url.split('?')[0] + href
                        elif href.startswith('//'):
                            full_url = f"https:{href}"
                        elif href.startswith('/'):
                            full_url = f"https://syosetu.org{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        print(f"      -> 変換後URL: {full_url}")
                        
                        # ページ番号を抽出
                        page_num = scraper.extract_page_number(full_url)
                        print(f"      -> ページ番号: {page_num}")
                        
                        # 重複チェック（現在の実装をシミュレート）
                        is_duplicate = any(scraper.extract_page_number(existing_url) == page_num for existing_url in page_links)
                        print(f"      -> 重複チェック: {'重複' if is_duplicate else '新規'}")
                        
                        if not is_duplicate:
                            page_links.append(full_url)
                            print(f"      -> リストに追加: {len(page_links)}番目")
                        else:
                            print(f"      -> 重複のためスキップ")
                
                break  # 最初に見つかったセレクターのみ処理
        
        # ベースURLがリストに含まれているかチェック
        base_in_list = any(scraper.extract_page_number(url) == base_page_num for url in page_links)
        print(f"\nベースURL（ページ{base_page_num}）がリストに含まれているか: {base_in_list}")
        
        if not base_in_list:
            page_links.append(test_url)
            print(f"ベースURLを追加: {test_url}")
        
        # ページ番号順にソート
        page_links.sort(key=lambda url: scraper.extract_page_number(url))
        
        print(f"\n=== 最終結果 ===")
        print(f"検出されたページ数: {len(page_links)}")
        for i, url in enumerate(page_links, 1):
            page_num = scraper.extract_page_number(url)
            print(f"  ページ{i}: {url} (ページ番号: {page_num})")
        
        return len(page_links) > 1
        
    except Exception as e:
        print(f"❌ エラーが発生: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_extract_page_number():
    """ページ番号抽出のテスト"""
    print("\nページ番号抽出機能のテスト...")
    
    scraper = HamelnFinalScraper()
    
    test_urls = [
        "https://syosetu.org/?mode=review&nid=378070",
        "https://syosetu.org/?mode=review&nid=378070&page=1",
        "https://syosetu.org/?mode=review&nid=378070&page=2",
        "?page=3",
        "//syosetu.org/?mode=review&nid=378070&page=4",
        "/novel/123/?mode=review&page=5",
        "invalid-url",
    ]
    
    for url in test_urls:
        page_num = scraper.extract_page_number(url)
        print(f"  '{url}' -> ページ番号: {page_num}")

if __name__ == "__main__":
    test_extract_page_number()
    success = debug_pagination_detection()
    
    print(f"\n=== 結果 ===")
    print(f"デバッグテスト: {'✅ 複数ページ検出' if success else '❌ 単一ページのみ'}")
    
    if not success:
        print("\n❌ ページネーション検出に問題があります。")
        print("修正が必要な箇所：")
        print("1. 重複チェックロジック")
        print("2. URL変換処理")
        print("3. ページ番号抽出処理")