#!/usr/bin/env python3
"""
実行ファイルでの感想ページ1ページ問題のデバッグテスト
TDD手順：テストを先に作成して問題を再現
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper
from bs4 import BeautifulSoup

def test_comments_pagination_detection():
    """感想ページの複数ページ検出機能のテスト"""
    print("感想ページの複数ページ検出機能をテスト中...")
    
    scraper = HamelnFinalScraper()
    
    # 複数ページの感想がある小説のテスト
    # より多くの感想がある小説URLを使用
    test_novels = [
        "https://syosetu.org/novel/263207/",  # 人気小説（感想が多い可能性）
        "https://syosetu.org/novel/378070/",  # 既存テスト小説
    ]
    
    for novel_url in test_novels:
        print(f"\n--- テスト対象: {novel_url} ---")
        
        try:
            # メインページを取得
            main_page = scraper.get_page(novel_url)
            if not main_page:
                print("❌ メインページの取得に失敗")
                continue
                
            # 感想ページURLを抽出
            comments_url = scraper.extract_comments_url(main_page)
            if not comments_url:
                print("❌ 感想ページURLの取得に失敗")
                continue
                
            print(f"✅ 感想ページURL: {comments_url}")
            
            # 感想ページを取得
            comments_page = scraper.get_page(comments_url)
            if not comments_page:
                print("❌ 感想ページの取得に失敗")
                continue
                
            # ページネーションの検出
            page_links = scraper.detect_comments_pagination(comments_page, comments_url)
            print(f"検出されたページ数: {len(page_links)}")
            
            if len(page_links) > 1:
                print("✅ 複数ページの感想が検出されました")
                for i, url in enumerate(page_links, 1):
                    print(f"  ページ{i}: {url}")
                    
                # 実際に複数ページを取得してテスト
                print("複数ページの統合取得をテスト...")
                integrated_result = scraper.get_all_comments_pages(comments_url)
                
                if integrated_result:
                    result_text = str(integrated_result)
                    if "統合表示" in result_text:
                        print("✅ 複数ページの統合が正常に実行されました")
                        return True
                    else:
                        print("⚠️ 統合処理は実行されましたが、統合表示マークが見つかりません")
                else:
                    print("❌ 複数ページの統合取得に失敗")
            else:
                print("ℹ️ 単一ページの感想です")
                
        except Exception as e:
            print(f"❌ エラーが発生: {e}")
            import traceback
            traceback.print_exc()
    
    return False

def test_comments_page_structure():
    """感想ページの構造を調査"""
    print("\n感想ページの構造を調査中...")
    
    scraper = HamelnFinalScraper()
    
    # テスト用URL
    test_url = "https://syosetu.org/novel/263207/?mode=review"
    
    try:
        # 感想ページを取得
        comments_page = scraper.get_page(test_url)
        if not comments_page:
            print("❌ 感想ページの取得に失敗")
            return False
            
        # ページネーション要素を詳細に調査
        print("ページネーション要素の詳細調査:")
        
        # 各セレクターでの検索結果を出力
        selectors = [
            'div.pagination a',
            'div.pager a', 
            'div.page-nav a',
            'a[href*="mode=review"][href*="page="]',
            'a[href*="&page="]',
            'a[href*="page="]',  # より広範囲なセレクター
        ]
        
        for selector in selectors:
            elements = comments_page.select(selector)
            print(f"  {selector}: {len(elements)}個の要素")
            for i, elem in enumerate(elements[:5]):  # 最初の5個のみ表示
                href = elem.get('href', 'No href')
                text = elem.get_text().strip()
                print(f"    [{i+1}] href='{href}', text='{text}'")
        
        # ページ全体のリンクを調査
        all_links = comments_page.find_all('a', href=True)
        page_links = [link for link in all_links if 'page=' in link.get('href', '')]
        
        print(f"\n全体のページリンク数: {len(page_links)}")
        for i, link in enumerate(page_links[:10]):  # 最初の10個のみ表示
            href = link.get('href')
            text = link.get_text().strip()
            print(f"  [{i+1}] href='{href}', text='{text}'")
            
        return len(page_links) > 0
        
    except Exception as e:
        print(f"❌ エラーが発生: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("実行ファイルでの感想ページ問題のデバッグテストを開始...")
    
    # テスト1: 複数ページ検出機能
    result1 = test_comments_pagination_detection()
    
    # テスト2: 感想ページ構造調査
    result2 = test_comments_page_structure()
    
    print(f"\n=== テスト結果 ===")
    print(f"複数ページ検出テスト: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"ページ構造調査テスト: {'✅ PASS' if result2 else '❌ FAIL'}")
    
    if not result1 and not result2:
        print("\n❌ 両方のテストが失敗しました。感想ページの実装に問題があります。")
    elif result2 and not result1:
        print("\n⚠️ ページ構造は正常ですが、複数ページ検出に問題があります。")
    else:
        print("\n✅ テストが成功しました。")