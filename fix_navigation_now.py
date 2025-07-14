#!/usr/bin/env python3
"""
第2回目のナビゲーション修正を実際に適用
"""
import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from bs4 import BeautifulSoup
from hameln_scraper_final import HamelnFinalScraper

def apply_navigation_fix():
    print("=== ナビゲーションリンク修正の適用 ===")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    # 正しいマッピング
    chapter_mapping = {
        'https://syosetu.org/novel/378070/1.html': 'ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html',
        'https://syosetu.org/novel/378070/2.html': 'ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html',
        'https://syosetu.org/novel/378070/3.html': 'ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html'
    }
    
    # 修正対象のファイル情報
    saved_chapters = [
        {
            'url': 'https://syosetu.org/novel/378070/1.html',
            'file_path': '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様/ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html'
        },
        {
            'url': 'https://syosetu.org/novel/378070/2.html',
            'file_path': '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様/ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html'
        },
        {
            'url': 'https://syosetu.org/novel/378070/3.html',
            'file_path': '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様/ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html'
        }
    ]
    
    print("章間のナビゲーションリンクを修正中...")
    for chapter_info in saved_chapters:
        if os.path.exists(chapter_info['file_path']):
            print(f"\n処理中: {os.path.basename(chapter_info['file_path'])}")
            
            # 修正前の状況確認
            with open(chapter_info['file_path'], 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            external_links_before = []
            for url in chapter_mapping.keys():
                if url in original_content:
                    external_links_before.append(url)
            
            if external_links_before:
                print(f"  修正前の外部リンク: {external_links_before}")
            else:
                print(f"  修正前：外部リンクなし")
            
            # HTMLをパースして修正
            soup = BeautifulSoup(original_content, 'html.parser')
            soup = scraper.fix_local_navigation_links(
                soup, 
                chapter_mapping, 
                chapter_info['url'], 
                None  # index_filename
            )
            
            # 修正結果をファイルに保存
            modified_content = str(soup)
            with open(chapter_info['file_path'], 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # 修正後の状況確認
            external_links_after = []
            for url in chapter_mapping.keys():
                if url in modified_content:
                    external_links_after.append(url)
            
            if external_links_after:
                print(f"  修正後の外部リンク: {external_links_after}")
                print(f"  ❌ 修正が不完全です")
            else:
                print(f"  ✅ すべての外部リンクが修正されました")
        else:
            print(f"❌ ファイルが見つかりません: {chapter_info['file_path']}")
    
    print("\n=== 修正完了 ===")

if __name__ == "__main__":
    apply_navigation_fix()