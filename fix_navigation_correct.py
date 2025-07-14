#!/usr/bin/env python3
"""
ナビゲーションリンクの緊急修正
目次リンクと次の話リンクを正しく修正
"""
import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from bs4 import BeautifulSoup

def fix_navigation_links():
    print("=== ナビゲーションリンクの緊急修正 ===")
    
    # 正しいファイルマッピング
    files = {
        'ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html': {
            'next': 'ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html'
        },
        'ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html': {
            'prev': 'ダウナー女神のアクア様 - 序章　彼と彼女の出会い - ハーメルン.html',
            'next': 'ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html'
        },
        'ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html': {
            'prev': 'ダウナー女神のアクア様 - 第一話　女神、降り立つ。そしてやらかす。 - ハーメルン.html'
        }
    }
    
    base_dir = '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様'
    index_file = 'ダウナー女神のアクア様 - 目次.html'
    
    for filename, links in files.items():
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            print(f"\n修正中: {filename}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 目次リンクを修正
            index_links = soup.find_all('a', href='https://syosetu.org/novel/378070/')
            for link in index_links:
                link['href'] = index_file
                print(f"  ✅ 目次リンク修正: {index_file}")
            
            # 次の話リンクを修正
            if 'next' in links:
                # 間違ったリンクを検索
                wrong_next_links = soup.find_all('a', href=lambda x: x and x.startswith('第') and x.endswith('話.html'))
                for link in wrong_next_links:
                    if '次の話' in link.get_text():
                        link['href'] = links['next']
                        print(f"  ✅ 次の話リンク修正: {links['next']}")
            
            # ファイルに保存
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
        else:
            print(f"❌ ファイルが見つかりません: {filename}")
    
    print("\n=== 修正完了 ===")

if __name__ == "__main__":
    fix_navigation_links()