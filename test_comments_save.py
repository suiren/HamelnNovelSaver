#!/usr/bin/env python3
"""
感想保存機能のテスト
"""

import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper

def test_comments_save():
    """感想保存機能のテスト"""
    
    # テスト対象ディレクトリ
    novel_dir = "/home/suiren/ClaudeTest/novels/片田舎の剣聖 錬鉄の英霊"
    base_url = "https://syosetu.org/novel/380014/"
    
    print("=== 感想保存機能テスト ===")
    print(f"対象ディレクトリ: {novel_dir}")
    print(f"ベースURL: {base_url}")
    
    # スクレイパーを初期化
    scraper = HamelnModularScraper()
    
    # 感想保存を実行
    print(f"\n感想保存開始...")
    result = scraper.save_comments_if_enabled(base_url, novel_dir)
    
    print(f"\n感想保存結果:")
    print(f"  成功: {result.get('success')}")
    
    if result.get('success'):
        print(f"  保存されたファイル数: {len(result.get('saved_files', []))}")
        print(f"  総ページ数: {result.get('total_pages', 0)}")
        print(f"  感想URL: {result.get('comments_url')}")
        
        # 保存されたファイルの詳細
        saved_files = result.get('saved_files', [])
        if saved_files:
            print(f"\n保存されたファイル:")
            for i, file_path in enumerate(saved_files, 1):
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"  {i}. {os.path.basename(file_path)} ({file_size:,} bytes)")
                else:
                    print(f"  {i}. {os.path.basename(file_path)} (ファイルが見つかりません)")
    else:
        reason = result.get('reason', 'unknown')
        error = result.get('error', '')
        print(f"  失敗理由: {reason}")
        if error:
            print(f"  エラー: {error}")
    
    # 感想フォルダの確認
    comments_dir = os.path.join(novel_dir, "感想")
    if os.path.exists(comments_dir):
        print(f"\n感想フォルダ内容:")
        files = os.listdir(comments_dir)
        for file in sorted(files):
            file_path = os.path.join(comments_dir, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  {file} ({file_size:,} bytes)")
    else:
        print(f"\n感想フォルダが見つかりません: {comments_dir}")
    
    return result

if __name__ == "__main__":
    test_comments_save()