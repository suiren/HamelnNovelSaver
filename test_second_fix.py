#!/usr/bin/env python3
"""
第2回目のナビゲーション修正プロセスをテスト
"""
import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from bs4 import BeautifulSoup
from hameln_scraper_final import HamelnFinalScraper

def test_second_navigation_fix():
    print("=== 第2回目のナビゲーション修正テスト ===")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    # 実際のマッピング（第2回目で使用されるべきもの）
    correct_mapping = {
        'https://syosetu.org/novel/378070/1.html': 'ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html',
        'https://syosetu.org/novel/378070/2.html': 'ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html',
        'https://syosetu.org/novel/378070/3.html': 'ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html'
    }
    
    print("第2回目修正で使用されるべきマッピング:")
    for url, filename in correct_mapping.items():
        print(f"  {url} -> {filename}")
    
    # 実際のHTMLファイルを読み込んで修正をテスト
    test_file = '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様/ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html'
    test_url = 'https://syosetu.org/novel/378070/2.html'
    
    if not os.path.exists(test_file):
        print(f"❌ テストファイルが見つかりません: {test_file}")
        return
    
    print(f"\nテストファイル: {test_file}")
    print(f"対応URL: {test_url}")
    
    # ファイルを読み込み
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正前の前の話リンクを確認
    if 'https://syosetu.org/novel/378070/1.html' in content:
        print("✅ 修正前：前の話リンクが外部URLとして確認")
    else:
        print("❌ 修正前：前の話リンクが見つからず")
    
    # BeautifulSoupでパース
    soup = BeautifulSoup(content, 'html.parser')
    
    # fix_local_navigation_linksを実行
    print("\nナビゲーション修正を実行中...")
    modified_soup = scraper.fix_local_navigation_links(
        soup, 
        correct_mapping, 
        test_url, 
        None
    )
    
    # 修正後の結果を確認
    modified_content = str(modified_soup)
    
    if 'https://syosetu.org/novel/378070/1.html' in modified_content:
        print("❌ 修正後：前の話リンクがまだ外部URLです")
        
        # どのリンクが修正されなかったかを詳細確認
        import re
        external_links = re.findall(r'href="(https://syosetu\.org/novel/\d+/\d+\.html)"', modified_content)
        print("修正されなかった外部リンク:")
        for link in external_links:
            print(f"  {link}")
            if link in correct_mapping:
                print(f"    → マッピング有り: {correct_mapping[link]}")
            else:
                print(f"    → マッピング無し")
    else:
        print("✅ 修正後：前の話リンクが正しく修正されました")
        
        # 修正されたリンクを確認
        if 'ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html' in modified_content:
            print("✅ 正しいローカルファイル名に変換されています")

if __name__ == "__main__":
    test_second_navigation_fix()