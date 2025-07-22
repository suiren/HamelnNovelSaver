#!/usr/bin/env python3
"""
ローカルナビゲーション修正と目次ファイル名修正のテストスクリプト
"""

import os
import sys
import time
from pathlib import Path
import re

# hameln_scraperモジュールのパスを追加
sys.path.insert(0, '/home/suiren/ClaudeTest')

def test_navigation_fix():
    """ローカルナビゲーション修正と目次ファイル名のテスト"""
    print("=" * 60)
    print("🔧 ローカルナビゲーション修正テスト")
    print("=" * 60)
    
    try:
        # モジュールインポート
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        # スクレイパー初期化
        scraper = HamelnModularScraper()
        scraper.enable_novel_info_saving = True  
        scraper.enable_comments_saving = False   
        
        print(f"✅ スクレイパー初期化完了")
        print()
        
        # テスト対象の小説URL
        test_url = "https://syosetu.org/novel/380014/"
        print(f"🎯 テスト対象URL: {test_url}")
        print()
        
        # 小説スクレイピング実行
        print("🚀 小説スクレイピング開始...")
        start_time = time.time()
        
        result = scraper.scrape_novel(test_url)
        
        elapsed_time = time.time() - start_time
        print(f"⏱️  実行時間: {elapsed_time:.2f}秒")
        print()
        
        # 結果確認
        if result.get('success', False):
            print("✅ 小説スクレイピング成功!")
            print(f"📚 タイトル: {result['title']}")
            print(f"📁 出力ディレクトリ: {result['output_dir']}")
            print(f"📖 保存章数: {result['saved_chapters']}/{result['total_chapters']}")
            print(f"🗂️  目次ページ保存: {'✅' if result.get('index_page_saved') else '❌'}")
            print(f"📄 追加ファイル数: {result['additional_files']}")
            
            # ファイル確認
            output_dir = result['output_dir']
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                html_files = [f for f in files if f.endswith('.html')]
                
                print(f"\n📂 ファイル構成確認:")
                print(f"  📁 総ファイル数: {len(files)}")
                print(f"  📄 HTMLファイル数: {len(html_files)}")
                
                # 目次ファイル名確認
                index_files = [f for f in html_files if f in ['目次.html', 'index.html']]
                print(f"  🏠 目次ファイル: {index_files}")
                
                if '目次.html' in index_files:
                    print(f"  ✅ 目次ファイル名: 正しく日本語で保存されています")
                elif 'index.html' in index_files:
                    print(f"  ⚠️ 目次ファイル名: まだ英語名で保存されています")
                else:
                    print(f"  ❌ 目次ファイル名: 目次ファイルが見つかりません")
                
                # ローカルナビゲーション確認
                print(f"\n🔗 ローカルナビゲーション確認:")
                test_chapter_file = None
                for f in html_files:
                    if f.startswith('第') and f.endswith('.html'):
                        test_chapter_file = f
                        break
                
                if test_chapter_file:
                    test_path = os.path.join(output_dir, test_chapter_file)
                    print(f"  🔍 テスト対象ファイル: {test_chapter_file}")
                    
                    with open(test_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # ローカルリンクと外部リンクを検出
                    local_links = []
                    external_links = []
                    
                    # 目次リンクのパターン
                    index_link_patterns = [
                        r'href="目次\.html"',
                        r'href="index\.html"', 
                        r'href="https://syosetu\.org/novel/380014/"'
                    ]
                    
                    for pattern in index_link_patterns:
                        matches = re.findall(pattern, content)
                        if 'syosetu.org' in pattern:
                            external_links.extend(matches)
                        else:
                            local_links.extend(matches)
                    
                    # 章間リンクのパターン
                    chapter_link_patterns = [
                        r'href="第\d+話\.html"',
                        r'href="https://syosetu\.org/novel/380014/\d+\.html"'
                    ]
                    
                    for pattern in chapter_link_patterns:
                        matches = re.findall(pattern, content)
                        if 'syosetu.org' in pattern:
                            external_links.extend(matches)
                        else:
                            local_links.extend(matches)
                    
                    print(f"  🏠 ローカルリンク数: {len(local_links)}個")
                    print(f"  🌐 外部リンク数: {len(external_links)}個")
                    
                    if len(local_links) > 0 and len(external_links) == 0:
                        print(f"  ✅ ローカルナビゲーション: 完全に修正されています！")
                    elif len(local_links) > 0:
                        print(f"  ⚠️ ローカルナビゲーション: 部分的に修正されています")
                        print(f"      外部リンク例: {external_links[:3]}")
                    else:
                        print(f"  ❌ ローカルナビゲーション: 修正されていません")
                        print(f"      外部リンク例: {external_links[:3]}")
                    
                    # 具体的なリンク内容サンプル
                    print(f"\n  📋 リンクサンプル:")
                    if local_links:
                        print(f"    ローカル: {local_links[:3]}")
                    if external_links:
                        print(f"    外部: {external_links[:3]}")
                
                else:
                    print(f"  ❌ 章ファイルが見つかりません")
            
            print(f"\n🎯 総合評価:")
            
            # 目次ファイル名評価
            index_ok = '目次.html' in index_files
            print(f"  目次ファイル名: {'✅ 合格' if index_ok else '❌ 不合格'}")
            
            # ローカルナビゲーション評価
            nav_ok = len(external_links) == 0 and len(local_links) > 0
            print(f"  ローカルナビゲーション: {'✅ 合格' if nav_ok else '❌ 不合格'}")
            
            overall_ok = index_ok and nav_ok
            print(f"  🏆 総合: {'✅ 成功' if overall_ok else '❌ 要修正'}")
            
            return overall_ok
        else:
            print("❌ 小説スクレイピング失敗")
            print(f"エラー: {result.get('error', '不明なエラー')}")
            return False
        
    except ImportError as e:
        print(f"❌ モジュールインポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_navigation_fix()
    sys.exit(0 if success else 1)