#!/usr/bin/env python3
"""
目次ページ保存機能のテスト
"""
import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper_final import HamelnFinalScraper

def test_index_save():
    print("=== 目次ページ保存機能のテスト ===")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    # テスト用URL
    test_url = "https://syosetu.org/novel/378070/"
    
    print(f"テストURL: {test_url}")
    print("小説をスクレイピング中...")
    
    # スクレイピング実行
    result = scraper.scrape_novel(test_url)
    
    if result:
        print(f"✅ スクレイピング完了: {result}")
        
        # 保存されたファイルを確認
        novel_dir = '/home/suiren/ClaudeTest/saved_novels/ダウナー女神のアクア様'
        if os.path.exists(novel_dir):
            files = os.listdir(novel_dir)
            html_files = [f for f in files if f.endswith('.html')]
            
            print(f"\n保存されたHTMLファイル ({len(html_files)}個):")
            for file in sorted(html_files):
                if '目次' in file:
                    print(f"  📖 {file} ← 目次ページ")
                else:
                    print(f"  📄 {file}")
                    
            # 目次ページが保存されているか確認
            index_files = [f for f in html_files if '目次' in f]
            if index_files:
                print(f"\n✅ 目次ページが正常に保存されました: {index_files[0]}")
            else:
                print(f"\n❌ 目次ページが保存されていません")
        else:
            print(f"❌ 保存ディレクトリが見つかりません: {novel_dir}")
    else:
        print("❌ スクレイピングに失敗しました")

if __name__ == "__main__":
    test_index_save()