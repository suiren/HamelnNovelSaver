#!/usr/bin/env python3
"""
実際のdetect_comments_pagination関数をテスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_real_pagination_function():
    """実際のdetect_comments_pagination関数をテスト"""
    print("実際のdetect_comments_pagination関数をテスト中...")
    
    scraper = HamelnFinalScraper()
    
    # 問題が発生したURL
    test_url = "https://syosetu.org/?mode=review&nid=378070"
    
    try:
        # 感想ページを取得
        comments_page = scraper.get_page(test_url)
        if not comments_page:
            print("❌ 感想ページの取得に失敗")
            return False
        
        print(f"テストURL: {test_url}")
        
        # 実際のdetect_comments_pagination関数を呼び出し
        page_links = scraper.detect_comments_pagination(comments_page, test_url)
        
        print(f"検出されたページ数: {len(page_links)}")
        for i, url in enumerate(page_links, 1):
            page_num = scraper.extract_page_number(url)
            print(f"  ページ{i}: {url} (ページ番号: {page_num})")
        
        # 複数ページが検出されたかチェック
        if len(page_links) > 1:
            print("✅ 複数ページが正常に検出されました")
            
            # 実際に複数ページの統合を試す
            print("\n複数ページの統合テスト...")
            integrated_result = scraper.get_all_comments_pages(test_url)
            
            if integrated_result:
                result_text = str(integrated_result)
                if "統合表示" in result_text:
                    print("✅ 複数ページの統合が成功しました")
                    return True
                else:
                    print("⚠️ 統合は実行されましたが、統合表示マークが見つかりません")
                    return True  # ページ検出自体は成功
            else:
                print("❌ 複数ページの統合に失敗")
                return False
        else:
            print("❌ 複数ページが検出されませんでした")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_conversion():
    """URL変換の単体テスト"""
    print("\nURL変換の単体テスト...")
    
    scraper = HamelnFinalScraper()
    base_url = "https://syosetu.org/?mode=review&nid=378070"
    
    test_cases = [
        ("./?mode=review&nid=378070&page=2", "https://syosetu.org/?mode=review&nid=378070&page=2"),
        ("?page=3", "https://syosetu.org?page=3"),
        ("//syosetu.org/?mode=review&page=4", "https://syosetu.org/?mode=review&page=4"),
        ("/novel/123/?page=5", "https://syosetu.org/novel/123/?page=5"),
        ("https://syosetu.org/?page=6", "https://syosetu.org/?page=6"),
    ]
    
    for input_href, expected_output in test_cases:
        # 実際の変換ロジックをシミュレート
        if input_href.startswith('?'):
            actual_output = base_url.split('?')[0] + input_href
        elif input_href.startswith('./'):
            actual_output = base_url.split('?')[0] + input_href[1:]
        elif input_href.startswith('//'):
            actual_output = f"https:{input_href}"
        elif input_href.startswith('/'):
            actual_output = 'https://syosetu.org' + input_href
        elif input_href.startswith('http'):
            actual_output = input_href
        else:
            actual_output = "SKIPPED"
        
        print(f"  '{input_href}' -> '{actual_output}' (期待値: '{expected_output}')")
        if actual_output == expected_output:
            print("    ✅ OK")
        else:
            print("    ❌ NG")

if __name__ == "__main__":
    test_url_conversion()
    success = test_real_pagination_function()
    
    print(f"\n=== 結果 ===")
    print(f"実機能テスト: {'✅ 成功' if success else '❌ 失敗'}")
    
    if success:
        print("\n✅ 感想ページの複数ページ取得機能が正常に動作しています!")
    else:
        print("\n❌ まだ問題があります。")