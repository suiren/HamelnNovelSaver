#!/usr/bin/env python3
"""
目次ページリンク修正機能のテスト
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper
from bs4 import BeautifulSoup

def test_index_link_fix():
    """目次ページリンク修正のテスト"""
    
    # テスト対象ディレクトリ
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    index_file = os.path.join(novel_dir, "目次.html")
    
    print("=== 目次ページリンク修正テスト ===")
    print(f"対象ディレクトリ: {novel_dir}")
    print(f"目次ファイル: {index_file}")
    
    # 修正前の状況確認
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        external_links = []
        local_links = []
        
        for link in links:
            href = link['href']
            if href.startswith('https://syosetu.org/novel/'):
                external_links.append(href)
            elif href.endswith('.html'):
                local_links.append(href)
        
        print(f"\n修正前のリンク状況:")
        print(f"  外部章リンク: {len(external_links)}個")
        print(f"  ローカルリンク: {len(local_links)}個")
        
        if external_links:
            print(f"  外部リンク例: {external_links[:3]}")
    
    # スクレイパーを初期化
    scraper = HamelnModularScraper()
    
    # 保存済み章の情報を推測構築（実際のファイルから）
    saved_chapters = []
    if os.path.exists(novel_dir):
        for filename in os.listdir(novel_dir):
            if filename.startswith('第') and filename.endswith('.html'):
                # ファイル名から章番号を推測
                chapter_num = filename.replace('第', '').replace('話.html', '')
                try:
                    chapter_number = int(chapter_num)
                    chapter_url = f"https://syosetu.org/novel/380014/{chapter_number}.html"
                    
                    saved_chapters.append({
                        'success': True,
                        'chapter_url': chapter_url,
                        'filename': filename
                    })
                except ValueError:
                    continue
    
    print(f"\n検出された保存済み章: {len(saved_chapters)}個")
    
    # 目次ページリンク修正を実行
    result = scraper.fix_index_page_chapter_links(novel_dir, saved_chapters)
    
    print(f"\n修正実行結果:")
    print(f"  成功: {result.get('success')}")
    print(f"  修正されたリンク数: {result.get('links_fixed', 0)}")
    
    if result.get('error'):
        print(f"  エラー: {result['error']}")
    
    # 修正後の状況確認
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        external_links_after = []
        local_links_after = []
        
        for link in links:
            href = link['href']
            if href.startswith('https://syosetu.org/novel/'):
                external_links_after.append(href)
            elif href.endswith('.html'):
                local_links_after.append(href)
        
        print(f"\n修正後のリンク状況:")
        print(f"  外部章リンク: {len(external_links_after)}個")
        print(f"  ローカルリンク: {len(local_links_after)}個")
        
        if local_links_after:
            print(f"  ローカルリンク例: {local_links_after[:3]}")
    
    return result

if __name__ == "__main__":
    test_index_link_fix()