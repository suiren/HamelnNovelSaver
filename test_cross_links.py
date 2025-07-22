#!/usr/bin/env python3
"""
クロスページリンク修正機能のテスト
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper
from bs4 import BeautifulSoup

def test_cross_links():
    """クロスページリンク修正のテスト"""
    
    # テスト対象ディレクトリ
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    base_url = "https://syosetu.org/novel/380014/"
    
    print("=== クロスページリンク修正テスト ===")
    print(f"対象ディレクトリ: {novel_dir}")
    print(f"ベースURL: {base_url}")
    
    # 修正前の状況確認
    print(f"\n修正前のリンク状況:")
    check_cross_links_status(novel_dir, "修正前")
    
    # スクレイパーを初期化
    scraper = HamelnModularScraper()
    
    # クロスページリンク修正を実行
    print(f"\nクロスページリンク修正開始...")
    result = scraper.fix_cross_page_links(novel_dir, base_url)
    
    print(f"\nクロスページリンク修正結果:")
    print(f"  成功: {result.get('success')}")
    
    if result.get('success'):
        print(f"  総修正リンク数: {result.get('total_links_fixed', 0)}")
        page_results = result.get('page_results', {})
        
        for page_type, page_result in page_results.items():
            if page_result.get('success'):
                links_fixed = page_result.get('links_fixed', 0)
                files_processed = page_result.get('files_processed', 1)
                print(f"  {page_type}: {links_fixed}個のリンク修正 ({files_processed}ファイル)")
            else:
                reason = page_result.get('reason', 'unknown')
                print(f"  {page_type}: 失敗 ({reason})")
        
        # リンクマッピング詳細
        mapping = result.get('cross_link_mapping', {})
        print(f"\n使用されたリンクマッピング:")
        for external_url, local_path in mapping.items():
            if local_path:
                print(f"  {external_url} → {local_path}")
    else:
        reason = result.get('reason', 'unknown')
        error = result.get('error', '')
        print(f"  失敗理由: {reason}")
        if error:
            print(f"  エラー: {error}")
    
    # 修正後の状況確認
    print(f"\n修正後のリンク状況:")
    check_cross_links_status(novel_dir, "修正後")
    
    return result

def check_cross_links_status(novel_dir, phase):
    """クロスリンクの状況を確認"""
    
    target_urls = [
        'https://syosetu.org/novel/380014/',
        'https://syosetu.org/?mode=ss_detail&nid=380014',
        'https://syosetu.org/?mode=review&nid=380014'
    ]
    
    files_to_check = [
        ('目次.html', '目次'),
        ('片田舎の剣聖 錬鉄の英霊 - 小説情報.html', '小説情報'),
        ('第001話.html', '第1話')
    ]
    
    # 感想ページも追加
    comments_dir = os.path.join(novel_dir, "感想")
    if os.path.exists(comments_dir):
        for filename in os.listdir(comments_dir):
            if filename.endswith('.html'):
                relative_path = os.path.join('感想', filename)
                files_to_check.append((relative_path, f'感想-{filename}'))
                break  # 最初の1つだけテスト
    
    for file_path, file_desc in files_to_check:
        full_path = os.path.join(novel_dir, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            external_count = 0
            local_count = 0
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(target_url in href for target_url in target_urls):
                    if href.startswith('http'):
                        external_count += 1
                    else:
                        local_count += 1
            
            if external_count > 0 or local_count > 0:
                print(f"  {file_desc}: 外部リンク{external_count}個, ローカルリンク{local_count}個")

if __name__ == "__main__":
    test_cross_links()