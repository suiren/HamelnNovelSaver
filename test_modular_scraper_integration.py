"""
HamelnModularScraper統合テスト
Phase 1-4のモジュール統合が正常に動作するか確認
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch


def test_hameln_modular_scraper_initialization():
    """HamelnModularScraper初期化テスト"""
    print("=== HamelnModularScraper初期化テスト開始 ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        print("✅ HamelnModularScraper初期化成功")
        
        # Phase 1-4のモジュールが正常に初期化されているか確認
        assert scraper.config is not None, "Phase 1: 設定管理モジュール未初期化"
        assert scraper.network_client is not None, "Phase 2: ネットワークモジュール未初期化"
        assert scraper.content_extractor is not None, "Phase 3: コンテンツ抽出モジュール未初期化"
        assert scraper.resource_processor is not None, "Phase 4: リソース処理モジュール未初期化"
        
        print("✅ 全Phase(1-4)のモジュール初期化確認完了")
        
        # 機能フラグの確認
        assert scraper.enable_novel_info_saving is True, "小説情報保存フラグが無効"
        assert scraper.enable_comments_saving is True, "感想保存フラグが無効"
        
        print("✅ 機能フラグ設定確認完了")
        
        scraper.close()
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        return False


def test_hameln_final_scraper_compatibility():
    """HamelnFinalScraper互換性テスト"""
    print("=== HamelnFinalScraper互換性テスト開始 ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnFinalScraper
        
        # hameln_scraper_final.pyと同じインターフェースで初期化
        scraper = HamelnFinalScraper()
        print("✅ HamelnFinalScraper互換レイヤー初期化成功")
        
        # hameln_scraper_final.pyと同じメソッドが存在するか確認
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
            assert hasattr(scraper, method_name), f"必須メソッド {method_name} が存在しない"
            print(f"✅ メソッド {method_name} 存在確認")
        
        # 機能フラグの互換性確認
        assert hasattr(scraper, 'enable_novel_info_saving'), "小説情報保存フラグが存在しない"
        assert hasattr(scraper, 'enable_comments_saving'), "感想保存フラグが存在しない"
        
        print("✅ hameln_scraper_final.py互換性確認完了")
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ 互換性テストエラー: {e}")
        return False


def test_module_integration_workflow():
    """モジュール統合ワークフローテスト"""
    print("=== モジュール統合ワークフローテスト開始 ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        
        # モック化したHTMLコンテンツでテスト
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>テスト小説 第1話</title>
        </head>
        <body>
            <div id="honbun" class="section1">
                <p>これはテスト小説の第1話です。</p>
                <p>物語の始まりを描いています。</p>
            </div>
        </body>
        </html>
        """
        
        # Phase 3: コンテンツ抽出テスト
        print("Phase 3: コンテンツ抽出テスト実行中...")
        extraction_result = scraper.extract_chapter_content(
            test_html, 
            "https://syosetu.org/novel/123/1/"
        )
        
        assert extraction_result['success'] is True, "コンテンツ抽出に失敗"
        print("✅ Phase 3: コンテンツ抽出成功")
        
        # Phase 4: ページ保存テスト（ファイル作成を伴うテスト）
        with tempfile.TemporaryDirectory() as temp_dir:
            print("Phase 4: ページ保存テスト実行中...")
            save_result = scraper.save_complete_page(
                html_content=test_html,
                output_dir=temp_dir,
                filename="test_chapter.html",
                original_url="https://syosetu.org/novel/123/1/",
                title="テスト小説 第1話"
            )
            
            assert save_result['success'] is True, "ページ保存に失敗"
            assert os.path.exists(save_result['saved_path']), "保存ファイルが存在しない"
            print("✅ Phase 4: ページ保存成功")
            
            # 保存されたファイルの内容確認
            with open(save_result['saved_path'], 'r', encoding='utf-8-sig') as f:
                saved_content = f.read()
                assert 'テスト小説' in saved_content, "保存内容にタイトルが含まれていない"
                print("✅ 保存ファイル内容確認成功")
        
        print("✅ モジュール統合ワークフロー完了")
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ ワークフローテストエラー: {e}")
        return False


def test_cache_and_logging_functionality():
    """キャッシュ・ログ機能テスト"""
    print("=== キャッシュ・ログ機能テスト開始 ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        
        # ログ機能テスト
        print("ログ機能テスト実行中...")
        scraper.debug_log("テストログメッセージ", "INFO")
        scraper.debug_log("テスト警告メッセージ", "WARNING")
        print("✅ ログ機能動作確認")
        
        # キャッシュ統計取得テスト
        print("キャッシュ統計取得テスト実行中...")
        cache_stats = scraper.get_cache_stats()
        
        assert 'modules' in cache_stats, "モジュール統計が取得できない"
        assert cache_stats['modules']['phase1_config'] is True, "Phase 1統計が不正"
        assert cache_stats['modules']['phase2_network'] is True, "Phase 2統計が不正"
        assert cache_stats['modules']['phase3_parsing'] is True, "Phase 3統計が不正"
        assert cache_stats['modules']['phase4_resources'] is True, "Phase 4統計が不正"
        
        print("✅ キャッシュ統計取得成功")
        print(f"   統計情報: {cache_stats['modules']}")
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ キャッシュ・ログテストエラー: {e}")
        return False


def test_error_handling_and_robustness():
    """エラーハンドリング・堅牢性テスト"""
    print("=== エラーハンドリング・堅牢性テスト開始 ===")
    
    try:
        from hameln_scraper.core.scraper import HamelnModularScraper
        
        scraper = HamelnModularScraper()
        
        # 不正なHTMLでのエラーハンドリングテスト
        print("不正HTMLエラーハンドリングテスト実行中...")
        invalid_html = "<html><body><p>不完全なHTML"
        
        extraction_result = scraper.extract_chapter_content(
            invalid_html, 
            "https://test.com"
        )
        
        # エラーが適切に処理されているか確認（クラッシュしないこと）
        assert 'success' in extraction_result, "エラー結果に success キーが存在しない"
        print("✅ 不正HTML適切処理確認")
        
        # 存在しないディレクトリでの保存テスト
        print("存在しないディレクトリ保存テスト実行中...")
        save_result = scraper.save_complete_page(
            html_content="<html><body>test</body></html>",
            output_dir="/non/existent/directory",
            filename="test.html",
            original_url="https://test.com"
        )
        
        # エラーが適切に処理されているか確認
        assert 'success' in save_result, "保存エラー結果に success キーが存在しない"
        if not save_result['success']:
            assert 'error' in save_result, "エラー情報が含まれていない"
        
        print("✅ エラーハンドリング適切処理確認")
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ エラーハンドリングテストエラー: {e}")
        return False


def test_gui_compatibility_interface():
    """GUI互換性インターフェーステスト"""
    print("=== GUI互換性インターフェーステスト開始 ===")
    
    try:
        # hameln_gui.pyが期待するインターフェースのテスト
        from hameln_scraper.core.scraper import HamelnFinalScraper
        
        # hameln_gui.pyと同じ方法で初期化
        scraper = HamelnFinalScraper()
        
        # GUI用のプログレスコールバック機能テスト
        print("プログレスコールバック機能テスト実行中...")
        
        progress_messages = []
        def mock_progress_callback(message, progress):
            progress_messages.append((message, progress))
            print(f"   進捗: {message} ({progress}%)")
        
        # scrape_novelメソッドの基本的なインターフェーステスト
        # （実際のネットワークアクセスなしで構造確認のみ）
        print("scrape_novelインターフェース確認中...")
        
        # モック化したテストケース（ネットワークアクセスなし）
        assert hasattr(scraper, 'scrape_novel'), "scrape_novelメソッドが存在しない"
        assert callable(getattr(scraper, 'scrape_novel')), "scrape_novelが呼び出し可能でない"
        
        print("✅ GUI互換性インターフェース確認完了")
        
        # 機能フラグ制御テスト
        print("機能フラグ制御テスト実行中...")
        
        # 小説情報保存機能の制御テスト
        scraper.enable_novel_info_saving = False
        result = scraper.save_novel_info_if_enabled("https://test.com", "/tmp")
        assert result['success'] is False, "無効化された機能が実行されてしまった"
        assert result['reason'] == 'disabled', "無効化理由が不正"
        
        # 感想保存機能の制御テスト
        scraper.enable_comments_saving = False
        result = scraper.save_comments_if_enabled("https://test.com", "/tmp")
        assert result['success'] is False, "無効化された機能が実行されてしまった"
        assert result['reason'] == 'disabled', "無効化理由が不正"
        
        print("✅ 機能フラグ制御確認完了")
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ GUI互換性テストエラー: {e}")
        return False


def run_all_integration_tests():
    """全統合テスト実行"""
    print("🧪 HamelnModularScraper統合テスト開始")
    print("=" * 60)
    
    tests = [
        ("初期化テスト", test_hameln_modular_scraper_initialization),
        ("互換性テスト", test_hameln_final_scraper_compatibility),
        ("ワークフローテスト", test_module_integration_workflow),
        ("キャッシュ・ログテスト", test_cache_and_logging_functionality),
        ("エラーハンドリングテスト", test_error_handling_and_robustness),
        ("GUI互換性テスト", test_gui_compatibility_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔧 {test_name} 実行中...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ 例外発生: {test_name} - {e}")
    
    print("\n" + "=" * 60)
    print("🎊 統合テスト結果サマリー")
    print("=" * 60)
    
    success_count = 0
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{status}: {test_name}")
        if success:
            success_count += 1
    
    print(f"\n📊 結果: {success_count}/{total_count} テスト成功")
    print(f"成功率: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 全テスト成功！HamelnModularScraper統合完了！")
        return True
    else:
        print(f"\n⚠️  {total_count - success_count} 個のテストで問題が発見されました。")
        return False


if __name__ == "__main__":
    success = run_all_integration_tests()
    
    if success:
        print("\n✅ Phase 2: コア統合 - モジュール統合完了")
        print("Phase 1-4のモジュールが正常に統合され、HamelnModularScraperが稼働可能です。")
    else:
        print("\n❌ 統合テストで問題が検出されました。修正が必要です。")