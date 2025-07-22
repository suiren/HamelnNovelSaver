#!/usr/bin/env python3
"""
ローカルナビゲーション機能のテスト
Phase 2の実装確認
"""
import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper

def test_local_navigation():
    print("=== ローカルナビゲーション機能テスト ===")
    
    # テスト用URL（実際のハーメルン小説）
    test_url = "https://syosetu.org/novel/380014/"
    
    # スクレイパー初期化
    scraper = HamelnModularScraper()
    
    try:
        print(f"テスト対象URL: {test_url}")
        
        # Phase 1: 小説スクレイピング実行（ローカルナビゲーション機能含む）
        print("\n1. 小説スクレイピング（ローカルナビゲーション機能有効）...")
        result = scraper.scrape_novel(test_url)
        
        if not result.get('success'):
            print(f"❌ 小説スクレイピング失敗: {result.get('error')}")
            return
        
        print(f"✓ 小説スクレイピング成功: {result['title']}")
        print(f"  章数: {result['saved_chapters']}/{result['total_chapters']}")
        print(f"  目次ページ保存: {'✓' if result.get('index_page_saved') else '❌'}")
        
        # Phase 2: ローカルナビゲーションリンク確認
        print("\n2. ローカルナビゲーションリンク確認...")
        output_dir = result['output_dir']
        
        # 最初の章ファイルを確認
        first_chapter_file = os.path.join(output_dir, "第001話.html")
        if not os.path.exists(first_chapter_file):
            print(f"❌ 第001話.htmlが見つかりません: {first_chapter_file}")
            return
        
        # HTMLを読み込んでリンク確認
        with open(first_chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 外部リンクと内部リンクをチェック
        external_links = []
        local_links = []
        
        # 章リンクの確認（第XXX話.htmlパターン）
        import re
        chapter_link_pattern = r'href="(第\d+話\.html)"'
        local_matches = re.findall(chapter_link_pattern, content)
        local_links.extend(local_matches)
        
        # 外部URLリンクの確認（https://syosetu.org/novel/...パターン）
        external_link_pattern = r'href="(https://syosetu\.org/novel/380014/\d+\.html)"'
        external_matches = re.findall(external_link_pattern, content)
        external_links.extend(external_matches)
        
        print(f"  ローカルリンク数: {len(local_links)}")
        if local_links:
            print(f"    例: {local_links[:3]}")
        
        print(f"  外部リンク数: {len(external_links)}")
        if external_links:
            print(f"    例: {external_links[:3]}")
        
        # 評価
        if local_links and not external_links:
            print("✓ ローカルナビゲーション修正成功: 章間リンクがローカルファイルに変換されています")
        elif local_links and external_links:
            print("⚠️ 部分的成功: 一部のリンクがローカル化されましたが、外部リンクも残っています")
        elif not local_links and external_links:
            print("❌ ローカルナビゲーション修正失敗: 章間リンクが外部URLのままです")
        else:
            print("? 章間リンクが見つかりませんでした")
        
        # Phase 3: 複数章ファイルでの確認
        print("\n3. 複数章での修正確認...")
        
        modified_files_count = 0
        total_local_links = 0
        total_external_links = 0
        
        for i in range(1, min(4, result['saved_chapters'] + 1)):  # 最初の3章を確認
            chapter_file = os.path.join(output_dir, f"第{i:03d}話.html")
            if os.path.exists(chapter_file):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    chapter_content = f.read()
                
                chapter_local = len(re.findall(chapter_link_pattern, chapter_content))
                chapter_external = len(re.findall(external_link_pattern, chapter_content))
                
                total_local_links += chapter_local
                total_external_links += chapter_external
                
                if chapter_local > 0:
                    modified_files_count += 1
                
                print(f"  第{i:03d}話: ローカル={chapter_local}, 外部={chapter_external}")
        
        print(f"\n修正済みファイル数: {modified_files_count}")
        print(f"総ローカルリンク数: {total_local_links}")
        print(f"総外部リンク数: {total_external_links}")
        
        # 最終評価
        if total_local_links > 0 and total_external_links == 0:
            print("🎉 ローカルナビゲーション機能: 完全成功!")
        elif total_local_links > 0 and total_external_links > 0:
            print("⚠️ ローカルナビゲーション機能: 部分的成功")
        elif total_external_links > 0:
            print("❌ ローカルナビゲーション機能: 修正されていません")
        else:
            print("? 章間リンクの検出ができませんでした")
    
    finally:
        scraper.close()
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_local_navigation()