#!/usr/bin/env python3
"""
目次ページ保存機能のテスト
Phase 1の実装確認
"""
import sys
import os
sys.path.append('/home/suiren/ClaudeTest')

from hameln_scraper.core.scraper import HamelnModularScraper

def test_index_page_saving():
    print("=== 目次ページ保存機能テスト ===")
    
    # テスト用URL（実際のハーメルン小説）
    test_url = "https://syosetu.org/novel/380014/"
    
    # スクレイパー初期化
    scraper = HamelnModularScraper()
    
    try:
        print(f"テスト対象URL: {test_url}")
        
        # Phase 1: 章リンク取得テスト
        print("\n1. 章リンク取得テスト...")
        page_result = scraper.get_page(test_url)
        if not page_result['success']:
            print(f"❌ ページ取得失敗: {page_result.get('error')}")
            return
        
        chapter_links_result = scraper.get_chapter_links(page_result['content'], test_url)
        if not chapter_links_result['success']:
            print(f"❌ 章リンク取得失敗: {chapter_links_result.get('error')}")
            return
        
        # 新しい形式での結果確認
        chapter_links = chapter_links_result.get('chapter_links', [])
        index_page = chapter_links_result.get('index_page')
        
        print(f"✓ 章リンク取得成功: {len(chapter_links)}個")
        if index_page:
            print(f"✓ 目次ページ検出: {index_page['title']} -> {index_page['url']}")
        else:
            print("❌ 目次ページが検出されませんでした")
            return
        
        # Phase 2: 目次ページ保存テスト
        print("\n2. 目次ページ保存テスト...")
        output_dir = "./test_index_save"
        os.makedirs(output_dir, exist_ok=True)
        
        index_result = scraper.save_index_page(
            index_page['url'],
            output_dir,
            index_page['title']
        )
        
        if index_result.get('success'):
            print(f"✓ 目次ページ保存成功: {index_result['filename']}")
            print(f"  保存先: {index_result.get('file_path', 'パス不明')}")
            
            # ファイル確認
            index_file = os.path.join(output_dir, "index.html")
            if os.path.exists(index_file):
                file_size = os.path.getsize(index_file)
                print(f"✓ ファイル確認: index.html ({file_size:,} bytes)")
                
                # 簡単な内容チェック
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # 最初の1000文字のみ
                    if "ハーメルン" in content:
                        print("✓ 内容確認: ハーメルンページが正しく保存されています")
                    else:
                        print("⚠️ 内容確認: ハーメルン固有の内容が見つかりません")
            else:
                print(f"❌ ファイル確認失敗: {index_file} が見つかりません")
        else:
            print(f"❌ 目次ページ保存失敗: {index_result.get('error')}")
            
        # Phase 3: 統合テスト（小規模）
        print("\n3. 統合テスト...")
        result = scraper.scrape_novel(test_url)
        
        if result.get('success'):
            print(f"✓ 小説スクレイピング成功: {result['title']}")
            print(f"  章数: {result['saved_chapters']}/{result['total_chapters']}")
            print(f"  目次ページ保存: {'✓' if result.get('index_page_saved') else '❌'}")
            
            # index.htmlの確認
            novel_dir = result['output_dir']
            index_path = os.path.join(novel_dir, "index.html")
            if os.path.exists(index_path):
                print(f"✓ 統合テスト: index.htmlが正常に作成されました")
            else:
                print(f"❌ 統合テスト: index.htmlが作成されませんでした")
        else:
            print(f"❌ 小説スクレイピング失敗: {result.get('error')}")
    
    finally:
        scraper.close()
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_index_page_saving()