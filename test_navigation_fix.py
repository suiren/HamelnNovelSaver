#!/usr/bin/env python3
"""
ナビゲーションリンク修正のテスト
"""
import os
from bs4 import BeautifulSoup

def test_navigation_fix():
    print("=== ナビゲーションリンク修正テスト ===")
    
    file_path = "/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様/ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html"
    
    if not os.path.exists(file_path):
        print(f"❌ ファイルが存在しません: {file_path}")
        return
    
    print(f"📂 テスト対象: {os.path.basename(file_path)}")
    
    # ファイル読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 空リンクの検出と修正前の状態確認
    print("\n🔍 修正前の状態:")
    empty_links = soup.find_all('a', href='#')
    for i, link in enumerate(empty_links):
        print(f"  空リンク {i+1}: href='{link.get('href')}' text='{link.get_text().strip()}'")
    
    # 修正適用
    print("\n🔧 修正適用中:")
    modified = False
    for link in empty_links:
        link_text = link.get_text().strip()
        if link_text == '×' or '次の話' in link_text:
            print(f"  📝 修正対象: '{link_text}'")
            link['href'] = 'javascript:void(0);'
            link.string = '最終話'
            link['class'] = link.get('class', []) + ['disabled']
            link['style'] = 'color: #999; cursor: not-allowed; text-decoration: none;'
            print(f"  ✅ 修正完了: href='javascript:void(0);' text='最終話'")
            modified = True
    
    if modified:
        # ファイル保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"\n💾 ファイル保存完了")
    else:
        print(f"\n ℹ️ 修正対象なし")
    
    # 修正後の確認
    print("\n✅ 修正後の状態:")
    empty_links_after = soup.find_all('a', href='javascript:void(0);')
    for i, link in enumerate(empty_links_after):
        print(f"  無効化リンク {i+1}: href='{link.get('href')}' text='{link.get_text().strip()}'")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_navigation_fix()