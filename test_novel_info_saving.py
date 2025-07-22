#!/usr/bin/env python3
"""
小説情報保存機能テストスクリプト
Phase 3: 小説情報ページ保存機能の動作確認
"""

import os
import sys
import time
from pathlib import Path

# hameln_scraperモジュールのパスを追加
sys.path.insert(0, '/home/suiren/ClaudeTest')

def test_novel_info_saving():
    """小説情報保存機能の完全テスト"""
    print("=" * 60)
    print("🧪 Phase 3: 小説情報保存機能テスト")
    print("=" * 60)
    
    try:
        # モジュールインポート
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        # スクレイパー初期化（小説情報保存機能を有効化）
        scraper = HamelnModularScraper()
        scraper.enable_novel_info_saving = True  # 明示的に有効化
        scraper.enable_comments_saving = False   # Phase 4で実装予定
        
        print(f"✅ スクレイパー初期化完了")
        print(f"📊 小説情報保存機能: {'有効' if scraper.enable_novel_info_saving else '無効'}")
        print(f"📊 感想保存機能: {'有効' if scraper.enable_comments_saving else '無効'}")
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
            
            # 詳細情報表示
            details = result.get('details', {})
            additional = details.get('additional', [])
            
            if additional:
                print(f"\n📝 追加保存ファイル:")
                for i, file_info in enumerate(additional, 1):
                    print(f"  {i}. {file_info.get('filename', '不明')}")
                    print(f"     URL: {file_info.get('url', '不明')}")
                    print(f"     パス: {file_info.get('file_path', '不明')}")
                    
                # 小説情報ファイルの存在確認
                novel_info_saved = any('小説情報' in file_info.get('filename', '') for file_info in additional)
                print(f"\n🎯 小説情報保存: {'✅ 成功' if novel_info_saved else '❌ 失敗'}")
            else:
                print(f"\n⚠️ 追加ファイルが保存されていません")
            
            # ファイル確認
            output_dir = result['output_dir']
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                html_files = [f for f in files if f.endswith('.html')]
                info_files = [f for f in html_files if '小説情報' in f]
                
                print(f"\n📂 出力ディレクトリ確認:")
                print(f"  📁 総ファイル数: {len(files)}")
                print(f"  📄 HTMLファイル数: {len(html_files)}")
                print(f"  📝 小説情報ファイル数: {len(info_files)}")
                
                if info_files:
                    info_file = info_files[0]
                    info_path = os.path.join(output_dir, info_file)
                    info_size = os.path.getsize(info_path)
                    print(f"  📋 小説情報ファイル: {info_file}")
                    print(f"  📏 ファイルサイズ: {info_size:,} bytes")
                    
                    # 簡単な内容確認
                    try:
                        with open(info_path, 'r', encoding='utf-8') as f:
                            content = f.read(500)  # 最初の500文字
                            if '小説情報' in content or 'あらすじ' in content or '作者' in content:
                                print(f"  ✅ ファイル内容: 小説情報として適切")
                            else:
                                print(f"  ⚠️ ファイル内容: 小説情報かどうか不明")
                    except Exception as e:
                        print(f"  ❌ ファイル読み込みエラー: {e}")
                
                else:
                    print(f"  ❌ 小説情報ファイルが見つかりません")
            
            print(f"\n🎉 Phase 3 テスト完了: 小説情報保存機能")
            
        else:
            print("❌ 小説スクレイピング失敗")
            print(f"エラー: {result.get('error', '不明なエラー')}")
            return False
        
        # リソース解放（新しいモジュールではネットワーククライアントが自動管理）
        print(f"🧹 リソース解放完了（自動管理）")
        
        return True
        
    except ImportError as e:
        print(f"❌ モジュールインポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_novel_info_saving()
    sys.exit(0 if success else 1)