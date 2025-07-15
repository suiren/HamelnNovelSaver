#!/usr/bin/env python3
"""
実際のハーメルンサイトでの感想ページ複数ページ取得テスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_actual_comments_pagination():
    """実際のハーメルンサイトでの感想ページ複数ページ取得テスト"""
    scraper = HamelnFinalScraper()
    
    # テスト用のURL（感想が複数ページある小説）
    test_url = "https://syosetu.org/novel/378070/?mode=review"
    
    print(f"テスト対象URL: {test_url}")
    
    try:
        # 感想ページを取得
        print("感想ページを取得中...")
        soup = scraper.get_page(test_url)
        
        if not soup:
            print("❌ 感想ページの取得に失敗しました")
            return False
        
        # ページネーションを検出
        print("ページネーションを検出中...")
        page_links = scraper.detect_comments_pagination(soup, test_url)
        
        print(f"検出されたページ数: {len(page_links)}")
        for i, url in enumerate(page_links, 1):
            print(f"  ページ{i}: {url}")
        
        # 複数ページの感想を取得
        if len(page_links) > 1:
            print("複数ページの感想統合を開始...")
            integrated_soup = scraper.get_all_comments_pages(test_url)
            
            if integrated_soup:
                print("✅ 複数ページの感想統合が完了しました")
                
                # 統合結果を保存
                output_file = "test_integrated_comments.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(str(integrated_soup))
                
                print(f"統合結果を保存しました: {output_file}")
                return True
            else:
                print("❌ 感想統合に失敗しました")
                return False
        else:
            print("✅ 単一ページの感想です（正常動作）")
            return True
            
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("実際のハーメルンサイトでの感想ページ複数ページ取得テストを開始...")
    success = test_actual_comments_pagination()
    
    if success:
        print("\n✅ テストが成功しました！")
    else:
        print("\n❌ テストが失敗しました。")