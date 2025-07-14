#!/usr/bin/env python3
"""
緊急ナビゲーションリンク修正スクリプト
目次リンクと次の話リンクを完全に修正する
"""
import os
import sys
from bs4 import BeautifulSoup

def fix_all_navigation_links():
    print("=== 緊急ナビゲーションリンク修正開始 ===")
    
    base_dir = "/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様"
    
    # 実際のファイル一覧
    files = [
        "ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html",
        "ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html", 
        "ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html",
        "ダウナー女神のアクア様 - 目次.html"
    ]
    
    # ファイル順序マッピング
    navigation_mapping = {
        "ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html": {
            "next": "ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html"
        },
        "ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html": {
            "prev": "ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html",
            "next": "ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html"
        },
        "ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html": {
            "prev": "ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html"
        }
    }
    
    index_file = "ダウナー女神のアクア様 - 目次.html"
    
    for filename in files:
        file_path = os.path.join(base_dir, filename)
        if not os.path.exists(file_path):
            print(f"❌ ファイルが存在しません: {filename}")
            continue
            
        print(f"\n🔧 修正中: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        modified = False
        
        # 1. 目次リンクを全て修正
        index_patterns = [
            lambda tag: tag.name == 'a' and tag.get('href') == 'https://syosetu.org/novel/378070/',
            lambda tag: tag.name == 'a' and tag.get('href') and '/novel/378070/' in tag.get('href') and tag.get('href').endswith('/'),
            lambda tag: tag.name == 'a' and '目次' in tag.get_text() and 'syosetu.org' in str(tag.get('href', ''))
        ]
        
        for pattern in index_patterns:
            links = soup.find_all(pattern)
            for link in links:
                if link.get('href') != index_file:
                    print(f"  📂 目次リンク修正: {link.get('href')} -> {index_file}")
                    link['href'] = index_file
                    modified = True
        
        # 2. 次の話・前の話リンクを修正
        if filename in navigation_mapping:
            nav_info = navigation_mapping[filename]
            
            # 次の話リンク
            if 'next' in nav_info:
                next_patterns = [
                    lambda tag: tag.name == 'a' and '次の話' in tag.get_text(),
                    lambda tag: tag.name == 'a' and tag.get('class') and 'next_page_link' in tag.get('class'),
                    lambda tag: tag.name == 'a' and tag.get('href') and (tag.get('href').startswith('第') and tag.get('href').endswith('話.html'))
                ]
                
                for pattern in next_patterns:
                    links = soup.find_all(pattern)
                    for link in links:
                        if link.get('href') != nav_info['next']:
                            print(f"  ▶️ 次の話リンク修正: {link.get('href')} -> {nav_info['next']}")
                            link['href'] = nav_info['next']
                            modified = True
            
            # 前の話リンク
            if 'prev' in nav_info:
                prev_patterns = [
                    lambda tag: tag.name == 'a' and '前の話' in tag.get_text()
                ]
                
                for pattern in prev_patterns:
                    links = soup.find_all(pattern)
                    for link in links:
                        if link.get('href') != nav_info['prev']:
                            print(f"  ◀️ 前の話リンク修正: {link.get('href')} -> {nav_info['prev']}")
                            link['href'] = nav_info['prev']
                            modified = True
        
        # 3. ファイルを保存
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"  ✅ 保存完了")
        else:
            print(f"  ℹ️ 修正不要")
    
    print("\n=== 緊急ナビゲーションリンク修正完了 ===")

if __name__ == "__main__":
    fix_all_navigation_links()