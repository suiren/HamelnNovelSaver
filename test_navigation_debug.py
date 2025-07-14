#!/usr/bin/env python3
"""
ナビゲーションリンク処理のデバッグスクリプト
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper_final import HamelnFinalScraper

def test_navigation_processing():
    print("=== ナビゲーションリンク処理のデバッグ ===")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    # テスト用のマッピングを作成（実際のスクレイピング時のマッピングを模擬）
    test_mapping = {
        'https://syosetu.org/novel/378070/1.html': 'ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html',
        'https://syosetu.org/novel/378070/2.html': 'ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html',
        'https://syosetu.org/novel/378070/3.html': 'ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html'
    }
    
    print("現在のチャプターマッピング:")
    for url, filename in test_mapping.items():
        print(f"  {url} -> {filename}")
    
    # 実際に生成されたHTMLファイルから前の話リンクを確認
    html_file = '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様/ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html'
    
    if os.path.exists(html_file):
        print(f"\nHTMLファイルを分析中: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 前の話リンクを検索
        if 'https://syosetu.org/novel/378070/1.html' in content:
            print("❌ 前の話リンクがまだ外部URLです")
            print("   リンク: https://syosetu.org/novel/378070/1.html")
            print("   期待される変換: ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html")
        else:
            print("✅ 前の話リンクは修正されています")
            
        # 次の話リンクを確認
        if '第3話.html' in content:
            print("✅ 次の話リンクは正常に変換されています")
        else:
            print("❌ 次の話リンクに問題があります")
    else:
        print(f"❌ HTMLファイルが見つかりません: {html_file}")

if __name__ == "__main__":
    test_navigation_processing()