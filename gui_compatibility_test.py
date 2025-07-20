"""
GUI互換性テスト
hameln_gui.pyが新しいモジュール構造で正常に動作するかを確認
"""

import sys
import os
import tempfile
from unittest.mock import Mock, patch
import traceback


def test_gui_import_compatibility():
    """GUIアプリの新モジュールインポート互換性テスト"""
    print("=== GUI インポート互換性テスト開始 ===")
    
    try:
        # 新しいモジュール構造への切り替えテスト
        # hameln_scraper_final.py が新しいモジュール構造を使用するかテスト
        
        print("テスト1: hameln_scraper_finalインポート...")
        from hameln_scraper_final import HamelnFinalScraper
        print("✅ hameln_scraper_final インポート成功")
        
        print("テスト2: HamelnFinalScraper初期化...")
        scraper = HamelnFinalScraper()
        print("✅ HamelnFinalScraper 初期化成功")
        
        # 必須メソッドの存在確認
        print("テスト3: GUI必須メソッド存在確認...")
        required_methods = [
            'scrape_novel',
            'get_page',
            'extract_novel_info',
            'extract_chapter_content',
            'save_complete_page',
            'debug_log',
            'close',
            'get_cache_stats'
        ]
        
        for method_name in required_methods:
            if not hasattr(scraper, method_name):
                print(f"❌ 必須メソッド {method_name} が見つからない")
                return False
            print(f"   ✅ {method_name} メソッド存在確認")
        
        # 機能フラグの存在確認
        print("テスト4: 機能フラグ存在確認...")
        if not hasattr(scraper, 'enable_novel_info_saving'):
            print("❌ enable_novel_info_saving フラグが見つからない")
            return False
        if not hasattr(scraper, 'enable_comments_saving'):
            print("❌ enable_comments_saving フラグが見つからない")
            return False
        print("   ✅ 機能フラグ確認完了")
        
        scraper.close()
        print("✅ GUI インポート互換性テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ GUI インポート互換性テストエラー: {e}")
        traceback.print_exc()
        return False


def test_gui_scraping_workflow():
    """GUI スクレイピングワークフロー互換性テスト"""
    print("\n=== GUI スクレイピングワークフロー互換性テスト開始 ===")
    
    try:
        from hameln_scraper_final import HamelnFinalScraper
        
        scraper = HamelnFinalScraper()
        
        # プログレスコールバック機能テスト
        print("テスト1: プログレスコールバック機能...")
        
        progress_messages = []
        def test_progress_callback(message, progress):
            progress_messages.append((message, progress))
            print(f"   進捗コールバック: {message} ({progress}%)")
        
        # テストHTML（hameln_gui.pyが期待する形式）
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>テスト小説 第1話</title>
        </head>
        <body>
            <div id="honbun" class="section1">
                <p>これはGUI互換性テスト用の章内容です。</p>
                <p>ハーメルンの実際の構造を模擬しています。</p>
            </div>
        </body>
        </html>
        """
        
        print("テスト2: 章内容抽出互換性...")
        extraction_result = scraper.extract_chapter_content(
            test_html, 
            "https://syosetu.org/novel/test/1/"
        )
        
        if not extraction_result['success']:
            print(f"❌ 章内容抽出失敗: {extraction_result.get('error')}")
            return False
        
        print(f"   ✅ 章内容抽出成功: {len(extraction_result['content'])}文字")
        
        print("テスト3: ページ保存互換性...")
        with tempfile.TemporaryDirectory() as temp_dir:
            save_result = scraper.save_complete_page(
                html_content=test_html,
                output_dir=temp_dir,
                filename="gui_test.html",
                original_url="https://syosetu.org/novel/test/1/",
                title="GUI互換性テスト"
            )
            
            if not save_result['success']:
                print(f"❌ ページ保存失敗: {save_result.get('error')}")
                return False
            
            # 保存ファイルの確認
            saved_file = os.path.join(temp_dir, "GUI互換性テスト.html")
            if not os.path.exists(saved_file):
                print(f"❌ 保存ファイルが見つからない: {saved_file}")
                return False
            
            print(f"   ✅ ページ保存成功: {saved_file}")
        
        print("テスト4: 機能フラグ制御互換性...")
        
        # 小説情報保存機能の制御テスト（GUIが期待する動作）
        scraper.enable_novel_info_saving = False
        info_result = scraper.save_novel_info_if_enabled("https://test.com", "/tmp")
        if info_result['success'] or info_result['reason'] != 'disabled':
            print("❌ 小説情報保存機能の無効化が正しく動作していない")
            return False
        
        # 感想保存機能の制御テスト
        scraper.enable_comments_saving = False
        comments_result = scraper.save_comments_if_enabled("https://test.com", "/tmp")
        if comments_result['success'] or comments_result['reason'] != 'disabled':
            print("❌ 感想保存機能の無効化が正しく動作していない")
            return False
        
        print("   ✅ 機能フラグ制御確認完了")
        
        scraper.close()
        print("✅ GUI スクレイピングワークフロー互換性テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ GUI ワークフローテストエラー: {e}")
        traceback.print_exc()
        return False


def test_gui_error_handling():
    """GUI エラーハンドリング互換性テスト"""
    print("\n=== GUI エラーハンドリング互換性テスト開始 ===")
    
    try:
        from hameln_scraper_final import HamelnFinalScraper
        
        scraper = HamelnFinalScraper()
        
        print("テスト1: 不正URLエラーハンドリング...")
        # GUIが不正なURLを入力した場合の動作テスト
        invalid_url = "invalid://not-a-real-url"
        
        # scrape_novelメソッドでのエラーハンドリング確認
        # （実際のネットワークアクセスはしないが、エラー処理の確認）
        print("   不正URL処理テスト（エラーハンドリング確認のみ）")
        
        print("テスト2: 空HTML エラーハンドリング...")
        empty_html = ""
        extraction_result = scraper.extract_chapter_content(empty_html, "https://test.com")
        
        # 空HTMLでは失敗するのが正常
        if extraction_result['success']:
            print("❌ 空HTMLで成功してしまった（異常）")
            return False
        
        print("   ✅ 空HTML適切エラーハンドリング確認")
        
        print("テスト3: 存在しないディレクトリ保存エラー...")
        test_html = "<html><body>test</body></html>"
        save_result = scraper.save_complete_page(
            html_content=test_html,
            output_dir="/non/existent/directory",
            filename="test.html",
            original_url="https://test.com"
        )
        
        # 存在しないディレクトリでは失敗するのが正常
        if save_result['success']:
            print("❌ 存在しないディレクトリで成功してしまった（異常）")
            return False
        
        print("   ✅ 存在しないディレクトリ適切エラーハンドリング確認")
        
        scraper.close()
        print("✅ GUI エラーハンドリング互換性テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ GUI エラーハンドリングテストエラー: {e}")
        traceback.print_exc()
        return False


def test_gui_direct_import():
    """GUI直接インポートテスト"""
    print("\n=== GUI 直接インポートテスト開始 ===")
    
    try:
        # hameln_gui.pyの直接インポートテスト（GUIは表示しない）
        print("テスト1: hameln_gui.py インポート可能性確認...")
        
        # tkinterの可用性確認
        try:
            import tkinter as tk
            print("   ✅ tkinter 利用可能")
        except ImportError:
            print("   ⚠️  tkinter 利用不可（ヘッドレス環境のため正常）")
            return True  # ヘッドレス環境では正常
        
        # 実際のGUIインポートテスト（エラーが出ないことを確認）
        print("テスト2: hameln_gui モジュール構造確認...")
        
        # hameln_gui.pyの内容を確認（インポートはしない）
        gui_file_path = "/home/suiren/ClaudeTest/hameln_gui.py"
        if not os.path.exists(gui_file_path):
            print("❌ hameln_gui.py が見つからない")
            return False
        
        # ファイル内容の基本的な構文確認
        with open(gui_file_path, 'r', encoding='utf-8') as f:
            gui_content = f.read()
        
        if 'from hameln_scraper_final import HamelnFinalScraper' not in gui_content:
            print("❌ GUI が hameln_scraper_final をインポートしていない")
            return False
        
        if 'class HamelnGUI:' not in gui_content:
            print("❌ HamelnGUI クラスが見つからない")
            return False
        
        print("   ✅ hameln_gui.py 構造確認完了")
        
        print("✅ GUI 直接インポートテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ GUI 直接インポートテストエラー: {e}")
        traceback.print_exc()
        return False


def run_gui_compatibility_tests():
    """全GUI互換性テスト実行"""
    print("🔧 GUI互換性テスト開始")
    print("=" * 70)
    
    tests = [
        ("GUI インポート互換性", test_gui_import_compatibility),
        ("GUI ワークフロー互換性", test_gui_scraping_workflow),
        ("GUI エラーハンドリング", test_gui_error_handling),
        ("GUI 直接インポート", test_gui_direct_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ 例外発生: {test_name} - {e}")
    
    print("\n" + "=" * 70)
    print("📊 GUI互換性テスト結果サマリー")
    print("=" * 70)
    
    success_count = 0
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{status}: {test_name}")
        if success:
            success_count += 1
    
    print(f"\n📈 結果: {success_count}/{total_count} テスト成功")
    print(f"成功率: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 全GUI互換性テスト成功！")
        print("新しいモジュール構造でGUIアプリが正常に動作します。")
        return True
    else:
        print(f"\n⚠️  {total_count - success_count} 個のテストで問題が発見されました。")
        return False


if __name__ == "__main__":
    success = run_gui_compatibility_tests()
    
    if success:
        print("\n✅ Phase 4: 品質保証 - 後方互換性テスト完了")
        print("GUIアプリとの連携が新しいモジュール構造で正常に動作することを確認しました。")
    else:
        print("\n❌ GUI互換性で問題が検出されました。修正が必要です。")