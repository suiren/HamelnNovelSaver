#!/usr/bin/env python3
"""
章別感想リンク修正のテスト
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper
from bs4 import BeautifulSoup

def test_volume_link_fix():
    """章別感想リンク修正のテスト"""
    
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    base_url = "https://syosetu.org/novel/380014/"
    
    print("=== 章別感想リンク修正テスト ===")
    
    # 修正前の状況確認
    print(f"\n修正前の状況:")
    check_volume_links(novel_dir, "修正前")
    
    # スクレイパーを初期化
    scraper = HamelnModularScraper()
    
    # クロスページリンク修正を実行
    print(f"\nクロスページリンク修正実行...")
    result = scraper.fix_cross_page_links(novel_dir, base_url)
    
    if result.get('success'):
        total_fixed = result.get('total_links_fixed', 0)
        print(f"修正完了: {total_fixed}個のリンクを修正")
    else:
        print(f"修正失敗: {result.get('error', 'unknown error')}")
    
    # 修正後の状況確認
    print(f"\n修正後の状況:")
    check_volume_links(novel_dir, "修正後")
    
    return result

def check_volume_links(novel_dir, phase):
    """章別感想リンクの状況確認"""
    
    volume_pattern = 'mode=review&nid=380014&volume='
    
    # 章ファイルをチェック
    chapter_files = ['第001話.html', '第002話.html', '第003話.html']
    
    total_volume_links = 0
    
    for chapter_file in chapter_files:
        file_path = os.path.join(novel_dir, chapter_file)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            volume_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if volume_pattern in href:
                    volume_links.append(href)
            
            if volume_links:
                print(f"  {chapter_file}: {len(volume_links)}個の章別感想リンク")
                for link in volume_links[:2]:  # 最初の2つを表示
                    print(f"    {link}")
                total_volume_links += len(volume_links)
            else:
                print(f"  {chapter_file}: 章別感想リンクなし")
    
    print(f"  合計: {total_volume_links}個の章別感想リンク")

if __name__ == "__main__":
    test_volume_link_fix()