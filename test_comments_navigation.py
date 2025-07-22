#!/usr/bin/env python3
"""
感想ページナビゲーション修正機能のテスト
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper
from bs4 import BeautifulSoup

def test_comments_navigation():
    """感想ページナビゲーション修正のテスト"""
    
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    comments_dir = os.path.join(novel_dir, "感想")
    
    print("=== 感想ページナビゲーション修正テスト ===")
    print(f"対象ディレクトリ: {comments_dir}")
    
    # 修正前の状況確認
    print(f"\n修正前の状況:")
    check_pagination_links(comments_dir, "修正前")
    check_chapter_links(comments_dir, "修正前")
    
    # スクレイパーを初期化
    scraper = HamelnModularScraper()
    
    # 保存済み章情報を構築
    saved_chapters = []
    if os.path.exists(novel_dir):
        for filename in os.listdir(novel_dir):
            if filename.startswith('第') and filename.endswith('.html'):
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
    
    print(f"\n保存済み章: {len(saved_chapters)}個")
    
    # ページネーションリンク修正
    print(f"\nページネーションリンク修正実行...")
    pagination_result = scraper.fix_comments_pagination_links(novel_dir)
    if pagination_result.get('success'):
        pagination_fixed = pagination_result.get('total_links_fixed', 0)
        print(f"ページネーション修正完了: {pagination_fixed}個のリンク")
    else:
        print(f"ページネーション修正失敗: {pagination_result.get('error', 'unknown error')}")
    
    # 章リンク修正
    print(f"\n章リンク修正実行...")
    chapter_result = scraper.fix_comments_chapter_links(novel_dir, "380014", saved_chapters)
    if chapter_result.get('success'):
        chapter_fixed = chapter_result.get('total_links_fixed', 0)
        print(f"章リンク修正完了: {chapter_fixed}個のリンク")
    else:
        print(f"章リンク修正失敗: {chapter_result.get('error', 'unknown error')}")
    
    # 修正後の状況確認
    print(f"\n修正後の状況:")
    check_pagination_links(comments_dir, "修正後")
    check_chapter_links(comments_dir, "修正後")
    
    return {
        'pagination_result': pagination_result,
        'chapter_result': chapter_result
    }

def check_pagination_links(comments_dir, phase):
    """ページネーションリンクの状況確認"""
    
    pagination_pattern = 'mode=review'
    local_pagination_pattern = '感想 - ページ'
    
    files = ['感想 - ページ1.html', '感想 - ページ2.html']
    
    for filename in files:
        file_path = os.path.join(comments_dir, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            external_pagination = 0
            local_pagination = 0
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if pagination_pattern in href and 'page=' in href:
                    external_pagination += 1
                elif local_pagination_pattern in href:
                    local_pagination += 1
            
            print(f"  {filename}: 外部ページネーション{external_pagination}個, ローカルページネーション{local_pagination}個")
        else:
            print(f"  {filename}: ファイルが見つかりません")

def check_chapter_links(comments_dir, phase):
    """章リンクの状況確認"""
    
    chapter_external_pattern = 'syosetu.org/novel/380014/'
    chapter_local_pattern = '../第'
    
    files = ['感想 - ページ1.html', '感想 - ページ2.html']
    
    for filename in files:
        file_path = os.path.join(comments_dir, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            external_chapters = 0
            local_chapters = 0
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if chapter_external_pattern in href:
                    external_chapters += 1
                elif chapter_local_pattern in href:
                    local_chapters += 1
            
            print(f"  {filename}: 外部章リンク{external_chapters}個, ローカル章リンク{local_chapters}個")
        else:
            print(f"  {filename}: ファイルが見つかりません")

if __name__ == "__main__":
    test_comments_navigation()