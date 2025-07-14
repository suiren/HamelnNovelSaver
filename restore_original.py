#!/usr/bin/env python3
"""
勝手な修正を元に戻すスクリプト
"""
import os
from bs4 import BeautifulSoup

def restore_original():
    print("=== 勝手な修正を元に戻します ===")
    
    file_path = "/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様/ダウナー女神のアクア様 - 第二話　今日を何とか頑張るぞい！ - ハーメルン.html"
    
    if not os.path.exists(file_path):
        print(f"❌ ファイルが存在しません: {file_path}")
        return
    
    print(f"📂 復元対象: {os.path.basename(file_path)}")
    
    # ファイル読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 勝手に変更した「最終話」を元の「×」に戻す
    print("\n🔄 勝手な修正を元に戻し中:")
    modified = False
    
    # javascript:void(0); のリンクを探して元に戻す
    modified_links = soup.find_all('a', href='javascript:void(0);')
    for link in modified_links:
        if link.get_text().strip() == '最終話':
            print(f"  📝 復元対象: '{link.get_text().strip()}'")
            link['href'] = '#'
            link.string = '×'
            # 追加したクラスとスタイルを削除
            if 'class' in link.attrs:
                link.attrs.pop('class')
            if 'style' in link.attrs:
                link.attrs.pop('style')
            print(f"  ✅ 復元完了: href='#' text='×'")
            modified = True
    
    if modified:
        # ファイル保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"\n💾 ファイル復元完了")
    else:
        print(f"\n ℹ️ 復元対象なし")
    
    # 復元後の確認
    print("\n✅ 復元後の状態:")
    empty_links_after = soup.find_all('a', href='#')
    for i, link in enumerate(empty_links_after):
        if link.get_text().strip() == '×':
            print(f"  空リンク {i+1}: href='{link.get('href')}' text='{link.get_text().strip()}'")
    
    print("\n=== 復元完了 ===")

if __name__ == "__main__":
    restore_original()