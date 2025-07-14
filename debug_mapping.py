#!/usr/bin/env python3
"""
実際のマッピングの状況を調査
"""
import os
import re

def check_actual_mapping():
    """実際に生成されたファイルから予想されるマッピングを確認"""
    
    novel_dir = '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様'
    
    if not os.path.exists(novel_dir):
        print(f"❌ ディレクトリが見つかりません: {novel_dir}")
        return
    
    # 実際のファイルを確認
    files = os.listdir(novel_dir)
    html_files = [f for f in files if f.endswith('.html')]
    
    print("=== 実際に生成されたHTMLファイル ===")
    for file in sorted(html_files):
        print(f"  {file}")
    
    # 期待されるマッピング
    expected_mapping = {
        'https://syosetu.org/novel/378070/1.html': '序章　彼と彼女の出会い',
        'https://syosetu.org/novel/378070/2.html': '第一話　女神、降り立つ。そしてやらかす。',
        'https://syosetu.org/novel/378070/3.html': '第二話　今日を何とか頑張るぞい！'
    }
    
    print("\n=== 期待されるマッピング vs 実際のファイル ===")
    for url, expected_title in expected_mapping.items():
        # 実際のファイル名を探す
        matching_files = [f for f in html_files if expected_title in f]
        if matching_files:
            print(f"✅ {url}")
            print(f"   期待タイトル: {expected_title}")
            print(f"   実際ファイル: {matching_files[0]}")
        else:
            print(f"❌ {url}")
            print(f"   期待タイトル: {expected_title}")
            print(f"   マッチするファイルなし")
    
    # 仮マッピングと実際マッピングの違い
    print("\n=== 仮マッピング vs 実際マッピング ===")
    temp_mapping = {
        'https://syosetu.org/novel/378070/1.html': '第1話.html',
        'https://syosetu.org/novel/378070/2.html': '第2話.html', 
        'https://syosetu.org/novel/378070/3.html': '第3話.html'
    }
    
    for url in expected_mapping.keys():
        temp_name = temp_mapping[url]
        expected_title = expected_mapping[url]
        matching_files = [f for f in html_files if expected_title in f]
        actual_name = matching_files[0] if matching_files else "見つからず"
        
        print(f"URL: {url}")
        print(f"  仮マッピング: {temp_name}")
        print(f"  実際ファイル: {actual_name}")
        print(f"  一致: {temp_name == actual_name}")
        print()

if __name__ == "__main__":
    check_actual_mapping()