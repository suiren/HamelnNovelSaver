#!/usr/bin/env python3
"""
実際のビルド結果をテストする
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hameln_scraper_final import HamelnFinalScraper

def test_actual_build():
    """実際のビルド結果をテスト"""
    print("=== 実際のビルドテスト ===")
    
    # テスト用URL（目次ページ）
    test_url = "https://syosetu.org/novel/378070/"
    
    print(f"テストURL: {test_url}")
    
    # スクレイパーを初期化
    scraper = HamelnFinalScraper()
    
    try:
        # 全話取得を実行
        print("全話取得を実行中...")
        result = scraper.scrape_novel(test_url)
        
        if result:
            print(f"✓ 取得成功: {result}")
        else:
            print("✗ 取得失敗")
        
        # 生成されたファイルを確認
        print("\n=== 生成されたファイル一覧 ===")
        import os
        if os.path.exists("saved_novels"):
            for root, dirs, files in os.walk("saved_novels"):
                for file in files:
                    if file.endswith('.html'):
                        full_path = os.path.join(root, file)
                        print(f"📄 {full_path}")
        
        # 第2話のHTMLファイルでリンクを確認
        print("\n=== リンク確認（第2話） ===")
        html_files = []
        if os.path.exists("saved_novels"):
            for root, dirs, files in os.walk("saved_novels"):
                for file in files:
                    if file.endswith('.html') and '第一話' in file:
                        html_files.append(os.path.join(root, file))
        
        if html_files:
            test_file = html_files[0]
            print(f"テスト対象ファイル: {test_file}")
            
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 前の話・次の話リンクを検索
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 全てのaタグを確認
            links = soup.find_all('a', href=True)
            prev_links = []
            next_links = []
            
            for link in links:
                text = link.get_text(strip=True)
                href = link.get('href')
                
                if '前' in text or 'prev' in text.lower():
                    prev_links.append((text, href))
                    print(f"前の話リンク: {text} -> {href}")
                
                if '次' in text or 'next' in text.lower():
                    next_links.append((text, href))
                    print(f"次の話リンク: {text} -> {href}")
            
            print(f"前の話リンク数: {len(prev_links)}")
            print(f"次の話リンク数: {len(next_links)}")
        else:
            print("HTMLファイルが見つかりませんでした")
            
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()

if __name__ == "__main__":
    test_actual_build()